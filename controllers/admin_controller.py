"""
Admin Controller
Handles Superadmin functionality: User management, dashboard

Route Convention (Laravel pattern):
  - Routes use UUID as the public identifier
  - Database JOINs / FK relationships use internal integer ID
"""

import hashlib
from fastapi import Request, Depends, HTTPException
from controllers.base_controller import BaseController
from fastapi.templating import Jinja2Templates
from app.database import SessionLocal
from app.models.db_models import User


def get_superadmin_user(request: Request):
    """
    Strict dependency for Superadmin routes (Role 0).
    Reads the session cookie uuid, looks up the User, enforces role.
    """
    auth_uuid = request.cookies.get("auth_uuid")
    if not auth_uuid:
        raise HTTPException(
            status_code=302,
            detail="Not authenticated",
            headers={"Location": "/login"}
        )

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.uuid == auth_uuid).first()
        if not user or user.status == 0:
            raise HTTPException(status_code=403, detail="Account deactivated")
        if user.role != 0:
            raise HTTPException(status_code=403, detail="Superadmin access required")
        return user
    finally:
        db.close()


def _find_by_uuid(db, user_uuid: str):
    """Helper: look up a User by public UUID, raise 404 if not found."""
    user = db.query(User).filter(User.uuid == user_uuid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


SORTABLE_FIELDS = {"id", "name", "email", "role", "status", "created_at"}


class AdminController(BaseController):
    """
    Superadmin routes — User Management

    Index Pattern  (GET  /admin/users)
    Data  Pattern  (GET  /admin/users/data)          → JSON {total, rows}
    Store Pattern  (POST /admin/users)
    Edit  Pattern  (GET  /admin/users/{uuid}/edit)   → JSON row
    Update Pattern (PUT  /admin/users/{uuid})
    Toggle Pattern (POST /admin/users/{uuid}/toggle)
    Destroy Pattern(DELETE /admin/users/{uuid})
    Multi  Pattern (POST /admin/users/delete-multiple)
    """

    def __init__(self, templates: Jinja2Templates):
        super().__init__(templates)

    # ------------------------------------------------------------------
    # index  GET /admin/users  → render HTML
    # ------------------------------------------------------------------
    async def index(self, request: Request, admin: User = Depends(get_superadmin_user)):
        return self.view("admin/dashboard.html", request, {"admin": admin})

    # ------------------------------------------------------------------
    # data   GET /admin/users/data  → JSON {total, rows}
    # ------------------------------------------------------------------
    async def data(self, request: Request, admin: User = Depends(get_superadmin_user)):
        db = SessionLocal()
        try:
            limit  = max(1, min(int(request.query_params.get("limit",  10)), 200))
            offset = max(0, int(request.query_params.get("offset", 0)))
            search = request.query_params.get("search", "").strip()
            sort   = request.query_params.get("sort",   "created_at")
            order  = request.query_params.get("order",  "desc")

            # Whitelist sortable columns
            if sort not in SORTABLE_FIELDS:
                sort = "created_at"

            query = db.query(User)

            if search:
                query = query.filter(
                    User.name.ilike(f"%{search}%") |
                    User.email.ilike(f"%{search}%")
                )

            total = query.count()

            col = getattr(User, sort)
            query = query.order_by(col.desc() if order == "desc" else col.asc())
            users = query.offset(offset).limit(limit).all()

            rows = [
                {
                    # uuid exposed publicly; id used only internally
                    "id":         u.uuid,          # custom-table uses row.id → we give uuid
                    "pk":         u.id,             # internal pk (for "am I editing myself?")
                    "uuid":       u.uuid,
                    "name":       u.name,
                    "email":      u.email,
                    "role":       u.role,
                    "status":     u.status,
                    "created_at": u.created_at.strftime("%Y-%m-%d %H:%M"),
                }
                for u in users
            ]

            return self.success({"total": total, "rows": rows})
        except HTTPException:
            raise
        except Exception as e:
            return self.error(str(e), 500)
        finally:
            db.close()

    # ------------------------------------------------------------------
    # store  POST /admin/users
    # ------------------------------------------------------------------
    async def store(self, request: Request, admin: User = Depends(get_superadmin_user)):
        db = SessionLocal()
        try:
            data  = await request.json()
            email = (data.get("email") or "").strip().lower()

            if not email or not data.get("name") or not data.get("password"):
                return self.error("Name, email, and password are required", 422)

            if db.query(User).filter(User.email == email).first():
                return self.error("Email already exists", 400)

            new_user = User(
                name=data["name"].strip(),
                email=email,
                password=hashlib.sha256(data["password"].encode()).hexdigest(),
                role=int(data.get("role", 1)),
                status=int(data.get("status", 1)),
            )
            db.add(new_user)
            db.commit()
            return self.success({"message": "User created successfully", "uuid": new_user.uuid})
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            return self.error(str(e), 500)
        finally:
            db.close()

    # ------------------------------------------------------------------
    # edit   GET /admin/users/{uuid}/edit  → JSON row for modal
    # ------------------------------------------------------------------
    async def edit(self, request: Request, user_uuid: str, admin: User = Depends(get_superadmin_user)):
        db = SessionLocal()
        try:
            user = _find_by_uuid(db, user_uuid)
            return self.success({
                "uuid":   user.uuid,
                "name":   user.name,
                "email":  user.email,
                "role":   user.role,
                "status": user.status,
            })
        finally:
            db.close()

    # ------------------------------------------------------------------
    # update PUT /admin/users/{uuid}
    # ------------------------------------------------------------------
    async def update(self, request: Request, user_uuid: str, admin: User = Depends(get_superadmin_user)):
        db = SessionLocal()
        try:
            data = await request.json()
            user = _find_by_uuid(db, user_uuid)

            new_email = (data.get("email") or "").strip().lower()
            if new_email and new_email != user.email:
                if db.query(User).filter(User.email == new_email).first():
                    return self.error("Email already in use", 400)

            # Prevent self-demotion
            if user.uuid == admin.uuid and int(data.get("role", user.role)) != 0:
                return self.error("You cannot demote yourself from Superadmin", 400)

            user.name   = data.get("name",   user.name).strip()
            user.email  = new_email or user.email
            user.role   = int(data.get("role",   user.role))
            user.status = int(data.get("status", user.status))

            if data.get("password"):
                user.password = hashlib.sha256(data["password"].encode()).hexdigest()

            db.commit()
            return self.success({"message": "User updated successfully"})
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            return self.error(str(e), 500)
        finally:
            db.close()

    # ------------------------------------------------------------------
    # toggleStatus  PATCH /admin/users/{uuid}/toggle
    # ------------------------------------------------------------------
    async def toggle_status(self, request: Request, user_uuid: str, admin: User = Depends(get_superadmin_user)):
        db = SessionLocal()
        try:
            if user_uuid == admin.uuid:
                return self.error("Cannot deactivate your own account", 400)

            user = _find_by_uuid(db, user_uuid)
            user.status = 1 if user.status == 0 else 0
            db.commit()
            return self.success({"message": "Status updated", "new_status": user.status})
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            return self.error(str(e), 500)
        finally:
            db.close()

    # ------------------------------------------------------------------
    # destroy  DELETE /admin/users/{uuid}
    # ------------------------------------------------------------------
    async def destroy(self, request: Request, user_uuid: str, admin: User = Depends(get_superadmin_user)):
        db = SessionLocal()
        try:
            if user_uuid == admin.uuid:
                return self.error("Cannot delete your own account", 400)

            user = _find_by_uuid(db, user_uuid)
            db.delete(user)
            db.commit()
            return self.success({"message": "User and all associated data permanently deleted"})
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            return self.error(str(e), 500)
        finally:
            db.close()

    # ------------------------------------------------------------------
    # destroyMultiple  POST /admin/users/delete-multiple
    # ------------------------------------------------------------------
    async def destroy_multiple(self, request: Request, admin: User = Depends(get_superadmin_user)):
        db = SessionLocal()
        try:
            data  = await request.json()
            uuids = data.get("ids", [])   # frontend sends UUID strings

            if not uuids:
                return self.error("No items selected", 400)

            if admin.uuid in uuids:
                return self.error("You cannot bulk-delete your own account", 400)

            deleted = (
                db.query(User)
                .filter(User.uuid.in_(uuids))
                .delete(synchronize_session=False)
            )
            db.commit()
            return self.success({"message": f"{deleted} users deleted successfully"})
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            return self.error(str(e), 500)
        finally:
            db.close()
