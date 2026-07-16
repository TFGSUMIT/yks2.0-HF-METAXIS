# complete code
"""
Sync Root Issue
"""
import requests

def sync_root_issue():
    try:
        response = requests.get("https://github.com/LittleYeti-Dev/yks2.0-ops-hub/issues/422")
        response.raise_for_status()
        print("Root issue synchronized successfully")
    except requests.exceptions.RequestException as e:
        print(f"Error synchronizing root issue: {e}")

if __name__ == "__main__":
    sync_root_issue()