import os, requests


def token(request):
    if not "Authorization" in request.headers:
        return None, ("Missing Credentials: Authorization Header Not Found", 400)

    token = request.headers["Authorization"]

    if not token:
        return None, ("Missing Credentials: Authorization Header is Empty", 400)

    response = requests.post(
        f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/validate",
        headers={"Authorization": token},
    )

    if response.status_code == 200:
        return response.text, None
    else:
        return None, (response.text, response.status_code)