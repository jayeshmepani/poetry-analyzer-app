import requests
import json
import time
import subprocess
import os
import sys

# Configuration
HOST = "http://localhost"
PORT = 9000
BASE_URL = f"{HOST}:{PORT}"

# Routes to test
WEB_ROUTES = [
    "/admin",
    "/admin/analyze",
    "/admin/batch",
    "/admin/results",
    "/admin/database",
    "/admin/visualize",
    "/admin/forms",
    "/admin/meters",
    "/admin/rasas",
    "/admin/settings",
    "/admin/theory",
    "/admin/touchstone",
    "/admin/constraints",
    "/admin/performance",
    "/admin/rubrics",
    "/admin/comparator",
]

API_GET_ROUTES = [
    "/api/stats",
    "/api/results",
    "/api/theory/recommendations",
    "/api/database/status",
    "/api/settings",
    "/api/forms",
    "/api/meters",
    "/api/rasas",
    "/health",
]

def test_routes(framework_name):
    print(f"\nTesting {framework_name} Framework...")
    results = {"success": [], "failed": []}
    
    # Test Web Routes
    print("\nTesting Web Routes...")
    for route in WEB_ROUTES:
        try:
            resp = requests.get(f"{BASE_URL}{route}", timeout=15)
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
            resp = requests.get(f"{BASE_URL}{route}", timeout=15)
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
        resp = requests.post(f"{BASE_URL}/api/analyze", json=payload, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            results["success"].append("POST /api/analyze")
            print("  OK: POST /api/analyze")
            
            # Test Get Single Result
            result_id = data.get("id") or data.get("uuid")
            if result_id:
                print(f"\nTesting GET Single Result ({result_id})...")
                resp_get = requests.get(f"{BASE_URL}/api/result/{result_id}", timeout=5)
                if resp_get.status_code == 200:
                    results["success"].append(f"GET /api/result/{result_id}")
                    print(f"  OK: GET /api/result/{result_id}")
                else:
                    results["failed"].append(f"GET /api/result/{result_id} (Status: {resp_get.status_code})")
                    print(f"  FAIL: GET /api/result/{result_id}")
        else:
            results["failed"].append(f"POST /api/analyze (Status: {resp.status_code})")
            print(f"  FAIL: POST /api/analyze - Status: {resp.status_code}")
    except Exception as e:
        results["failed"].append(f"POST /api/analyze (Error: {str(e)})")
        print(f"  FAIL: POST /api/analyze - Error: {str(e)}")

    # Test Constraints API
    print("\nTesting Constraints API...")
    try:
        payload = {
            "text": "The quick brown fox jumps over the lazy dog",
            "constraint_type": "n_plus_7",
            "params": {"n": 7}
        }
        resp = requests.post(f"{BASE_URL}/api/constraints/apply", json=payload, timeout=5)
        if resp.status_code == 200:
            results["success"].append("POST /api/constraints/apply")
            print("  OK: POST /api/constraints/apply")
        else:
            results["failed"].append(f"POST /api/constraints/apply (Status: {resp.status_code})")
            print(f"  FAIL: POST /api/constraints/apply - Status: {resp.status_code}")
    except Exception as e:
        results["failed"].append(f"POST /api/constraints/apply (Error: {str(e)})")
        print(f"  FAIL: POST /api/constraints/apply - Error: {str(e)}")

    return results

def run_framework(cmd):
    # Start process
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"Wait for server to start...")
    
    # Wait for health check
    max_retries = 20
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
    process.kill()
    return None

def main():
    final_report = {}
    
    # Ensure database is initialized
    print("Initializing database...")
    subprocess.run(["venv\\Scripts\\python.exe", "init_db.py"], capture_output=True)

    # 1. Test FastAPI
    print("\n" + "="*50)
    print("  PHASE 1: FastAPI VERIFICATION")
    print("="*50)
    
    fastapi_cmd = "venv\\Scripts\\uvicorn.exe app.main:app --host 0.0.0.0 --port 9000"
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
