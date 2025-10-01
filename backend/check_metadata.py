

import requests
import os

METADATA_URL = "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/?recursive=true"
HEADERS = {"Metadata-Flavor": "Google"}

try:
    response = requests.get(METADATA_URL, headers=HEADERS, timeout=5)
    response.raise_for_status()  # Raise an exception for HTTP errors

    print(f"Raw response content type: {type(response.text)}")
    print(f"Raw response content: {response.text}")

    try:
        metadata = response.json()
        print(f"Parsed metadata type: {type(metadata)}")
        print(f"Parsed metadata: {metadata}")
        if isinstance(metadata, dict) and "email" in metadata:
            print(f"Service account email: {metadata['email']}")
        else:
            print("Metadata is not a dictionary or 'email' key is missing.")
    except ValueError:
        print("Failed to parse response as JSON.")

except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")

print("\nChecking proxy environment variables:")
for var in ["http_proxy", "https_proxy", "ftp_proxy", "no_proxy", "HTTP_PROXY", "HTTPS_PROXY", "FTP_PROXY", "NO_PROXY"]:
    value = os.environ.get(var)
    if value:
        print(f"{var}: {value}")

