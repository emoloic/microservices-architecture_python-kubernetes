import os, requests, json

def register(request):
    username = request["email"]
    password = request["password"]
    
    user_credentials = {
        "username" : username,
        "password" : password
    }

    # Make request to our auth service.
    response = requests.post(
        f"http://{os.getenv('AUTH_SVC_ADDRESS')}/registration",
        data=json.dumps(user_credentials),
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 201:
        return response.text, None
    else:
        return None, (response.text, response.status_code)

def login(request):
    auth = request.authorization
    if not auth:
        return None, ("missing credentials", 401)
    
    basicAuth = (auth.username, auth.password)

    # Make request to our auth service.
    response = requests.post(
        f"http://{os.getenv('AUTH_SVC_ADDRESS')}/login",
        auth=basicAuth
    )

    if response.status_code == 200:
        return response.text, None
    else:
        return None, (response.text, response.status_code)