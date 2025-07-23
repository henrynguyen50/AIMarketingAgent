import requests

def update_embed():
    try:
        api_url = "http://127.0.0.1:8000/refresh"

        response = requests.post(api_url)

        if response.status_code == 200:
            print("Backend refreshed")
        else:
            print("Failed refresh")


    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error: Could not connect to the server at {api_url}.")
        print("Please make sure your FastAPI server is running.")

