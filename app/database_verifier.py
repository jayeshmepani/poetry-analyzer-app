"""
Database Verification & Status Tools
Check database connection, view tables, and verify data
"""

from sqlalchemy import text, inspect
from app.database import engine, SessionLocal
from app.models.db_models import AnalysisResult, DatabaseStats, Base
from datetime import datetime
from typing import Dict, Any, List


class DatabaseVerifier:
    """
    Verify database setup and data
    """
    
    @staticmethod
    def check_connection() -> Dict[str, Any]:
        """
        Check if database connection works
        Returns: {'status': 'connected', 'database': 'poetry_analyzer', ...}
        """
        try:
            with engine.connect() as conn:
                # Test query
                result = conn.execute(text("SELECT 1 as test"))
                row = result.fetchone()
                
                if row and row[0] == 1:
                    return {
                        'status': '✅ connected',
                        'database': engine.url.database,
                        'host': engine.url.host,
                        'port': engine.url.port,
                        'driver': engine.driver,
                        'checked_at': datetime.utcnow().isoformat()
                    }
        except Exception as e:
            return {
                'status': '❌ failed',
                'error': str(e),
                'checked_at': datetime.utcnow().isoformat()
            }
        
        return {
            'status': '❌ unknown',
            'checked_at': datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def check_tables() -> Dict[str, Any]:
        """
        Check if all tables exist
        Returns: {'tables': [...], 'missing': [...], 'status': 'ok'}
        """
        # Check for our application tables
        expected_tables = ['analysis_results', 'database_stats', 'user_settings']
        
        try:
            inspector = inspect(engine)
            existing_tables = inspector.get_table_names()
            
            missing = [t for t in expected_tables if t not in existing_tables]
            
            return {
                'status': '✅ ok' if not missing else '⚠️ incomplete',
                'tables_found': len(existing_tables),
                'tables': existing_tables,
                'expected': expected_tables,
                'missing': missing,
                'checked_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'status': '❌ error',
                'error': str(e),
                'checked_at': datetime.utcnow().isoformat()
            }
    
    @staticmethod
    def get_statistics() -> Dict[str, Any]:
        """
        Get database statistics
        Returns: {'total_analyses': 10, 'avg_score': 7.5, ...}
        """
        try:
            db = SessionLocal()
            
            # Total analyses
            total = db.query(AnalysisResult).count()
            
            # Average score
            from sqlalchemy import func
            avg_score_result = db.query(func.avg(AnalysisResult.overall_score)).scalar()
            avg_score = float(avg_score_result) if avg_score_result else 0.0
            
            # By language
            by_language = db.query(
                AnalysisResult.language,
                func.count(AnalysisResult.id)
            ).group_by(AnalysisResult.language).all()
            
            languages = {lang: count for lang, count in by_language}
            
            # Recent activity (last 24 hours)
            from datetime import timedelta
            day_ago = datetime.utcnow() - timedelta(days=1)
            recent = db.query(AnalysisResult).filter(
                AnalysisResult.created_at >= day_ago
            ).count()
            
            # Storage used (estimate)
            storage_result = db.query(
                func.sum(func.length(AnalysisResult.text))
            ).scalar()
            storage_bytes = storage_result or 0
            
            db.close()
            
            return {
                'status': '✅ ok',
                'total_analyses': total,
                'average_score': round(avg_score, 2),
                'languages': languages,
                'recent_24h': recent,
                'storage_bytes': storage_bytes,
                'storage_mb': round(storage_bytes / 1048576, 2),
                'checked_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'status': '❌ error',
                'error': str(e),
                'checked_at': datetime.utcnow().isoformat()
            }
    
    @staticmethod
    def get_recent_analyses(limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent analysis results
        """
        try:
            db = SessionLocal()
            results = db.query(AnalysisResult).order_by(
                AnalysisResult.created_at.desc()
            ).limit(limit).all()
            
            data = []
            for r in results:
                data.append({
                    'id': r.id,
                    'uuid': r.uuid,
                    'title': r.title or 'Untitled',
                    'language': r.language,
                    'score': r.overall_score,
                    'words': r.word_count,
                    'created': r.created_at.isoformat() if r.created_at else None
                })
            
            db.close()
            return data
            
        except Exception as e:
            return [{'error': str(e)}]
    
    @staticmethod
    def full_status() -> Dict[str, Any]:
        """
        Get complete database status
        """
        return {
            'connection': DatabaseVerifier.check_connection(),
            'tables': DatabaseVerifier.check_tables(),
            'statistics': DatabaseVerifier.get_statistics(),
            'recent': DatabaseVerifier.get_recent_analyses(5)
        }


def init_database():
    """
    Initialize database - create all tables
    Call this on first setup
    """
    print("🔧 Initializing database...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        
        # Verify
        status = DatabaseVerifier.check_tables()
        print(f"📊 Tables status: {status['status']}")
        
        if status['missing']:
            print(f"⚠️  Missing tables: {status['missing']}")
        else:
            print("✅ All expected tables exist")
        
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False


if __name__ == "__main__":
    # Run verification
    print("="*60)
    print("DATABASE VERIFICATION")
    print("="*60)
    
    status = DatabaseVerifier.full_status()
    
    print("\n🔌 CONNECTION")
    conn = status['connection']
    print(f"   Status: {conn['status']}")
    if conn['status'] == '✅ connected':
        print(f"   Database: {conn['database']}")
        print(f"   Host: {conn['host']}:{conn['port']}")
    
    print("\n📊 TABLES")
    tables = status['tables']
    print(f"   Status: {tables['status']}")
    print(f"   Found: {tables['tables_found']} tables")
    if tables.get('tables'):
        for table in tables['tables']:
            print(f"      - {table}")
    
    print("\n📈 STATISTICS")
    stats = status['statistics']
    if stats['status'] == '✅ ok':
        print(f"   Total Analyses: {stats['total_analyses']}")
        print(f"   Average Score: {stats['average_score']}")
        print(f"   Recent (24h): {stats['recent_24h']}")
        print(f"   Storage: {stats['storage_mb']} MB")
        if stats.get('languages'):
            print(f"   Languages: {stats['languages']}")
    else:
        print(f"   {stats['status']} - {stats.get('error', 'No data yet')}")
    
    print("\n📋 RECENT ANALYSES")
    for r in status['recent']:
        if 'error' not in r:
            print(f"   • {r['title']} ({r['language']}) - Score: {r['score']}")
    
    print("\n" + "="*60)
