# complete code
"""
Environment Status
"""
import os

def get_environment_status():
    try:
        environment = os.environ.get("ENVIRONMENT")
        if environment:
            print(f"Environment: {environment}")
        else:
            print("Environment not set")
    except Exception as e:
        print(f"Error getting environment status: {e}")

if __name__ == "__main__":
    get_environment_status()