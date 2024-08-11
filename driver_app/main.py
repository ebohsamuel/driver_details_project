from fastapi import FastAPI, Request, Depends, HTTPException, status
from driver_app import dependencies, schemas, create_and_update_user
from fastapi.responses import HTMLResponse, RedirectResponse
from driver_app.dependencies import templates
from fastapi.security import OAuth2PasswordRequestForm
from driver_app.utilities import get_db, authenticate_user, create_access_token, get_current_active_user
from typing import Annotated
from sqlalchemy.orm import Session
from datetime import timedelta


ACCESS_TOKEN_EXPIRE_MINUTES = 660


app = FastAPI()

app.include_router(dependencies.router)
app.include_router(create_and_update_user.router)

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# endpoint for getting access token
@app.post("/token")
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: Session = Depends(get_db)
):
    user = authenticate_user(db=db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    response = RedirectResponse(url="/welcome/", status_code=302)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",  # Bearer token format
        httponly=True,
    )
    return response


# the endpoint for welcome page after login
@app.get("/welcome/", response_class=HTMLResponse)
async def welcome_page(user: Annotated[schemas.User, Depends(get_current_active_user)], request: Request):
    if user:
        return templates.TemplateResponse("welcome_page.html", {"request": request})
