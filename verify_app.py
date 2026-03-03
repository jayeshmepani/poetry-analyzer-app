import requests
import json
import time
import subprocess
import os
import sys

# Configuration
HOST = "http://localhost"
PORT = 9005
BASE_URL = f"{HOST}:{PORT}"

# Routes to test
WEB_ROUTES = [
    "/dashboard",
    "/analyze",
    "/batch",
    "/results",
    "/database",
    "/visualize",
    "/forms",
    "/meters",
    "/rasas",
    "/settings",
    "/theory",
    "/touchstone",
    "/constraints",
    "/performance",
    "/rubrics",
    "/comparator",
]

API_GET_ROUTES = [
    "/stats",
    "/results/list",
    "/theory/recommendations",
    "/database/status/api",
    "/settings/get",
    "/forms/data",
    "/meters/data",
    "/rasas/data",
    "/health",
]

def test_routes(framework_name):
    print(f"\nTesting {framework_name} Framework...")
    results = {"success": [], "failed": []}
    
    # Authenticate
    session = requests.Session()
    print("\nAuthenticating...")
    try:
        login_data = {"email": "superadmin@mail.com", "password": "SuperAdmin#357"}
        resp = session.post(f"{BASE_URL}/login", data=login_data, timeout=10)
        if resp.status_code == 200 and "dashboard" in resp.url:
            print("  OK: Authenticated successfully")
        else:
            print(f"  FAIL: Authentication failed (Status: {resp.status_code}, URL: {resp.url})")
            results["failed"].append("Authentication")
    except Exception as e:
        print(f"  FAIL: Authentication error: {str(e)}")
        results["failed"].append(f"Authentication (Error: {str(e)})")

    # Test Web Routes
    print("\nTesting Web Routes...")
    for route in WEB_ROUTES:
        try:
            resp = session.get(f"{BASE_URL}{route}", timeout=15)
            if resp.status_code == 200:
                results["success"].append(f"WEB {route}")
                print(f"  OK: {route}")
            else:
                results["failed"].append(f"WEB {route} (Status: {resp.status_code})")
                print(f"  FAIL: {route} - Status: {resp.status_code}")
        except Exception as e:
            results["failed"].append(f"WEB {route} (Error: {str(e)})")
            print(f"  FAIL: {route} - Error: {str(e)}")

    # Test API GET Routes
    print("\nTesting API GET Routes...")
    for route in API_GET_ROUTES:
        try:
            resp = session.get(f"{BASE_URL}{route}", timeout=15)
            if resp.status_code == 200:
                results["success"].append(f"API {route}")
                print(f"  OK: {route}")
            else:
                results["failed"].append(f"API {route} (Status: {resp.status_code})")
                print(f"  FAIL: {route} - Status: {resp.status_code}")
        except Exception as e:
            results["failed"].append(f"API {route} (Error: {str(e)})")
            print(f"  FAIL: {route} - Error: {str(e)}")

    # Test POST Analysis
    print("\nTesting Analysis API (POST)...")
    try:
        payload = {
            "title": "Verification Poem",
            "text": "The stars shine bright in the quiet night,\nGuided by the moon's soft silver light.",
            "language": "en",
            "strictness": 7
        }
        # First run may download models, so we give it a lot of time
        resp = session.post(f"{BASE_URL}/analyze/submit", json=payload, timeout=600)
        if resp.status_code == 200:
            data = resp.json()
            results["success"].append("POST /analyze/submit")
            print("  OK: POST /analyze/submit")
            
            # Test Get Single Result
            result_id = data.get("id") or data.get("uuid")
            if result_id:
                print(f"\nTesting GET Single Result ({result_id})...")
                resp_get = session.get(f"{BASE_URL}/result/{result_id}", timeout=10)
                if resp_get.status_code == 200:
                    results["success"].append(f"GET /result/{result_id}")
                    print(f"  OK: GET /result/{result_id}")
                else:
                    results["failed"].append(f"GET /result/{result_id} (Status: {resp_get.status_code})")
                    print(f"  FAIL: GET /result/{result_id}")
        else:
            results["failed"].append(f"POST /analyze/submit (Status: {resp.status_code})")
            print(f"  FAIL: POST /analyze/submit - Status: {resp.status_code}")
    except Exception as e:
        results["failed"].append(f"POST /analyze/submit (Error: {str(e)})")
        print(f"  FAIL: POST /analyze/submit - Error: {str(e)}")

    # Test Constraints API
    print("\nTesting Constraints API...")
    try:
        payload = {
            "text": "The quick brown fox jumps over the lazy dog",
            "constraint_type": "n_plus_7",
            "params": {"n": 7}
        }
        resp = session.post(f"{BASE_URL}/constraints/apply", json=payload, timeout=30)
        if resp.status_code == 200:
            results["success"].append("POST /constraints/apply")
            print("  OK: POST /constraints/apply")
        else:
            results["failed"].append(f"POST /constraints/apply (Status: {resp.status_code})")
            print(f"  FAIL: POST /constraints/apply - Status: {resp.status_code}")
    except Exception as e:
        results["failed"].append(f"POST /constraints/apply (Error: {str(e)})")
        print(f"  FAIL: POST /constraints/apply - Error: {str(e)}")

    return results

def run_framework(cmd):
    # Start process
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"Wait for server to start at {BASE_URL}...")
    
    # Wait for health check
    max_retries = 30
    for i in range(max_retries):
        try:
            resp = requests.get(f"{BASE_URL}/health", timeout=2)
            if resp.status_code == 200:
                print("Server is UP!")
                return process
        except:
            pass
        time.sleep(1)
        print(f"  Retrying... {i+1}/{max_retries}")
    
    print("Server failed to start in time.")
    # Try to read stderr for clues
    try:
        stdout, stderr = process.communicate(timeout=1)
        if stderr:
            print(f"Server error output: {stderr.decode()}")
    except:
        pass
    process.kill()
    return None

def main():
    final_report = {}
    
    python_exe = sys.executable
    bin_dir = os.path.dirname(python_exe)
    uvicorn_exe = os.path.join(bin_dir, "uvicorn")
    if os.name == 'nt':
        uvicorn_exe += ".exe"

    # Ensure database is initialized
    print("Initializing database...")
    subprocess.run([python_exe, "init_db.py"], capture_output=True)

    # 1. Test FastAPI
    print("\n" + "="*50)
    print("  PHASE 1: FastAPI VERIFICATION")
    print("="*50)
    
    fastapi_cmd = f'"{uvicorn_exe}" app.main:app --host 0.0.0.0 --port {PORT}'
    process = run_framework(fastapi_cmd)
    
    if process:
        try:
            final_report["FastAPI"] = test_routes("FastAPI")
        finally:
            process.terminate()
            process.wait()
            print("FastAPI server stopped.")
    
    # FINAL SUMMARY
    print("\n" + "="*50)
    print("  FINAL VERIFICATION SUMMARY")
    print("="*50)
    
    if not final_report:
        print("No frameworks were tested.")
        return

    for fw, res in final_report.items():
        total = len(res["success"]) + len(res["failed"])
        success = len(res["success"])
        print(f"\n{fw}: {success}/{total} Passed")
        if res["failed"]:
            print("  Failures:")
            for f in res["failed"]:
                print(f"    - {f}")
        else:
            print("  ALL SYSTEMS FUNCTIONAL")

if __name__ == "__main__":
    main()
