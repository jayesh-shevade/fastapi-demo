import os
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from msal import ConfidentialClientApplication

app = FastAPI()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
REDIRECT_URI = os.getenv("REDIRECT_URI")
SCOPE = ["User.Read"]

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <h2>FastAPI Azure AD Auth Example</h2>
    <a href="/login">Login with Microsoft</a>
    """

@app.get("/login")
def login():
    app_msal = ConfidentialClientApplication(
        CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET
    )
    auth_url = app_msal.get_authorization_request_url(SCOPE, redirect_uri=REDIRECT_URI)
    return RedirectResponse(auth_url)

@app.get("/callback", response_class=HTMLResponse)
def callback(request: Request, code: str = None):
    if not code:
        return HTMLResponse("<h3>Login failed or canceled.</h3>")

    app_msal = ConfidentialClientApplication(
        CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET
    )
    result = app_msal.acquire_token_by_authorization_code(
        code, scopes=SCOPE, redirect_uri=REDIRECT_URI
    )

    if "id_token_claims" in result:
        return RedirectResponse(url="/dashboard")
    return HTMLResponse("<h3>Authentication failed.</h3>")

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    return "<h2>Welcome to your dashboard!</h2>"
