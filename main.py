import os
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.middleware.sessions import SessionMiddleware
from msal import ConfidentialClientApplication
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# ✅ Add session middleware (required for login state)
app.add_middleware(SessionMiddleware, secret_key="your_secret_key_here")

# 🔐 Azure AD / Entra ID settings
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
def login(request: Request):
    """Redirect user to Microsoft login page."""
    app_msal = ConfidentialClientApplication(
        CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET
    )
    auth_url = app_msal.get_authorization_request_url(
        SCOPE, redirect_uri=REDIRECT_URI
    )
    return RedirectResponse(auth_url)


@app.get("/callback")
def callback(request: Request, code: str = None):
    """Receive the code from Microsoft login and store session."""
    if not code:
        return HTMLResponse("<h3>Login failed or canceled.</h3>")

    app_msal = ConfidentialClientApplication(
        CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET
    )
    result = app_msal.acquire_token_by_authorization_code(
        code, scopes=SCOPE, redirect_uri=REDIRECT_URI
    )

    if "id_token_claims" in result:
        user_name = result["id_token_claims"].get("name", "User")
        # ✅ Store user info in session
        request.session["user"] = user_name
        return RedirectResponse(url="/dashboard")

    return HTMLResponse("<h3>Authentication failed.</h3>")


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    """Protected route: only visible after login."""
    user = request.session.get("user")
    if not user:
        # ⚠️ Not logged in — redirect to login
        return RedirectResponse(url="/login")
    return f"<h2>Welcome {user}!</h2><p>You are in the dashboard.</p><a href='/logout'>Logout</a>"


@app.get("/logout")
def logout(request: Request):
    """Log the user out (clear session)."""
    request.session.clear()
    return RedirectResponse(url="/")
