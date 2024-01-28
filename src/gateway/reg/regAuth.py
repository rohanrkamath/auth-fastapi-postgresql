import os, httpx
from fastapi import Request
from schema import UserRegistration, TOTPValidation

async def dbCheck(user_registration: UserRegistration):
    auth_svc_url = f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/register"

    async with httpx.AsyncClient() as client:
        # Send the registration data as a JSON payload
        response = await client.post(auth_svc_url, json=user_registration.dict())

        if response.status_code == 200:
            qr_code_uri = response.json().get("qr_code_uri")
            return user_registration.username, qr_code_uri, None
        else:
            return None, None, response.json().get("detail", "Unknown error")

        
async def totpCheck(totp_validation: TOTPValidation):
    auth_svc_url = f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/validate-totp"

    async with httpx.AsyncClient() as client:
        # Send the TOTP validation data as a JSON payload
        response = await client.post(auth_svc_url, json=totp_validation.dict())

        if response.status_code == 200:
            return response.json()  # Assuming a success message is returned in JSON format
        else:
            return response.json().get("detail", "Unknown error")




# def dbCheck(request):
#     auth = request.authorization
#     if not auth:
#         return None, None, ("missing credentials", 401)
    
#     basicAuth = (auth.username, auth.password)

#     response = requests.post(
#         f"http://{os.environ.get('AUTH?_SVC_ADDRESS')}/register",
#         auth = basicAuth
#     )

#     if response.status_code == 200:
#         return auth.username, response.text, None
#     else:
#         return auth.username, None, (response.text, response.status_code)
    
    
# def totpCheck(request):
#     if not "Authorization" in request.headers:
#         return None, ("missing credentials", 401)

#     totp = request.headers["Authorization"]

#     if not totp:
#         return None, ("Invalid OTP", 401)

#     response = requests.post(
#         f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/validate-totp",
#         headers={"Authorization": totp},
#     )

#     if response.status_code == 200:
#         return response.text, None
#     else:
#         return None, (response.text, response.status_code)