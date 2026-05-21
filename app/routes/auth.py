import secrets

from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse

from app.config import settings

router = APIRouter()

LOGIN_HTML = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login — CRM</title>
    <link rel="stylesheet" href="/static/style.css">
    <style>
        body {{ display: flex; align-items: center; justify-content: center; min-height: 100vh; }}
        .login-card {{ width: 100%; max-width: 400px; }}
    </style>
</head>
<body>
    <div class="card login-card">
        <h1 style="text-align: center; margin-bottom: 1.5rem;">CRM Prospection</h1>
        {error}
        <form method="post" action="/login">
            <div class="form-group">
                <label>Identifiant</label>
                <input type="text" name="username" required autofocus>
            </div>
            <div class="form-group">
                <label>Mot de passe</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit" class="btn btn-primary" style="width: 100%;">Connexion</button>
        </form>
    </div>
</body>
</html>
"""


@router.get("/login")
def login_page(request: Request):
    if request.session.get("authenticated"):
        return RedirectResponse(url="/", status_code=303)
    return HTMLResponse(LOGIN_HTML.format(error=""))


@router.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if (
        secrets.compare_digest(username, settings.auth_username)
        and secrets.compare_digest(password, settings.auth_password)
    ):
        request.session["authenticated"] = True
        return RedirectResponse(url="/", status_code=303)

    error = '<div class="alert alert-error">Identifiant ou mot de passe incorrect.</div>'
    return HTMLResponse(LOGIN_HTML.format(error=error), status_code=401)


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)
