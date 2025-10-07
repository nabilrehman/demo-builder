#!/usr/bin/env python3
"""
Script to get or create Firebase Web App configuration.
"""
import subprocess
import json
import requests

PROJECT_ID = "bq-demos-469816"

def get_access_token():
    """Get access token from gcloud."""
    result = subprocess.run(
        ["gcloud", "auth", "print-access-token"],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

def list_web_apps():
    """List existing Firebase web apps."""
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://firebase.googleapis.com/v1beta1/projects/{PROJECT_ID}/webApps"

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("apps", [])
    else:
        print(f"Error listing web apps: {response.status_code}")
        print(response.text)
        return []

def create_web_app():
    """Create a new Firebase web app."""
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    url = f"https://firebase.googleapis.com/v1beta1/projects/{PROJECT_ID}/webApps"

    data = {
        "displayName": "CAPI Demo Generator"
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error creating web app: {response.status_code}")
        print(response.text)
        return None

def get_web_app_config(app_id):
    """Get Firebase web app config."""
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://firebase.googleapis.com/v1beta1/projects/{PROJECT_ID}/webApps/{app_id}/config"

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error getting web app config: {response.status_code}")
        print(response.text)
        return None

def main():
    print("🔥 Firebase Web App Setup")
    print("=" * 50)

    # List existing web apps
    print("\n📋 Checking for existing web apps...")
    apps = list_web_apps()

    if apps:
        print(f"✅ Found {len(apps)} existing web app(s)")
        app = apps[0]  # Use the first one
        app_id = app["appId"]
        print(f"   Using: {app.get('displayName', 'Unnamed')} ({app_id})")
    else:
        print("⚠️  No web apps found. Creating new one...")
        result = create_web_app()
        if not result:
            print("❌ Failed to create web app")
            return

        # Extract app_id from the operation name
        operation_name = result.get("name", "")
        print(f"✅ Web app creation started: {operation_name}")
        print("   Waiting for operation to complete...")

        # Wait for the operation to complete
        import time
        time.sleep(5)

        # List apps again to get the newly created one
        apps = list_web_apps()
        if not apps:
            print("❌ Failed to find newly created web app")
            return
        app = apps[0]
        app_id = app["appId"]

    # Get web app config
    print(f"\n🔑 Fetching web app config for {app_id}...")
    config = get_web_app_config(app_id)

    if not config:
        print("❌ Failed to get web app config")
        return

    print("\n✅ Firebase Web App Configuration:")
    print("=" * 50)
    print(f"VITE_FIREBASE_API_KEY={config.get('apiKey', '')}")
    print(f"VITE_FIREBASE_AUTH_DOMAIN={config.get('authDomain', '')}")
    print(f"VITE_FIREBASE_PROJECT_ID={config.get('projectId', '')}")
    print(f"VITE_FIREBASE_STORAGE_BUCKET={config.get('storageBucket', '')}")
    print(f"VITE_FIREBASE_MESSAGING_SENDER_ID={config.get('messagingSenderId', '')}")
    print(f"VITE_FIREBASE_APP_ID={app_id}")
    print(f"VITE_ENABLE_AUTH=true")
    print("=" * 50)

    # Save to .env.local
    env_path = "newfrontend/conversational-api-demo-frontend/.env.local"
    print(f"\n💾 Saving to {env_path}...")

    with open(env_path, "w") as f:
        f.write("# Firebase Web App Configuration\n")
        f.write(f"VITE_FIREBASE_API_KEY={config.get('apiKey', '')}\n")
        f.write(f"VITE_FIREBASE_AUTH_DOMAIN={config.get('authDomain', '')}\n")
        f.write(f"VITE_FIREBASE_PROJECT_ID={config.get('projectId', '')}\n")
        f.write(f"VITE_FIREBASE_STORAGE_BUCKET={config.get('storageBucket', '')}\n")
        f.write(f"VITE_FIREBASE_MESSAGING_SENDER_ID={config.get('messagingSenderId', '')}\n")
        f.write(f"VITE_FIREBASE_APP_ID={app_id}\n")
        f.write(f"\n# Feature Flag: Enable Firebase Authentication\n")
        f.write(f"VITE_ENABLE_AUTH=true\n")

    print(f"✅ Configuration saved to {env_path}")
    print("\n🎉 Firebase setup complete!")
    print("\nNext steps:")
    print("1. Rebuild the frontend: cd newfrontend/conversational-api-demo-frontend && npm run build")
    print("2. Deploy with ENABLE_AUTH=true")

if __name__ == "__main__":
    main()
