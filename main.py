from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <h2>Welcome to FastAPI on Azure!</h2>
    <a href="/login">Login with Microsoft</a>
    """

@app.get("/callback", response_class=HTMLResponse)
def callback():
    return "<h3>Login successful! Redirected to callback page.</h3>"
