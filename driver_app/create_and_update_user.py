from fastapi.responses import HTMLResponse
from driver_app import schemas, crud
from driver_app.dependencies import templates
from typing import Annotated
from fastapi import Request, Depends
from driver_app.utilities import get_db, get_current_active_user
from fastapi import APIRouter, Form
from sqlalchemy.orm import Session

router = APIRouter()


# this endpoint is used to get the form require to create a user
@router.get("/user/create_user", response_class=HTMLResponse)
async def create_new_user_form(
        user: Annotated[schemas.User, Depends(get_current_active_user)],
        request: Request,
):
    if user:
        if user.user_type == "super" or user.user_type == "alpha":
            return templates.TemplateResponse(
                "create_new_user_form.html",
                {
                    "request": request,
                }
            )


# endpoint for submitting a newly registered user
@router.post("/submit_user_details", response_class=HTMLResponse)
async def create_driver_details(
        user: Annotated[schemas.User, Depends(get_current_active_user)],
        request: Request,
        email: Annotated[str, Form()],
        password: Annotated[str, Form()],
        user_type: Annotated[str, Form()],
        db: Session = Depends(get_db),
):
    user_details = {
        "email": email,
        "password": password,
        "user_type": user_type,
    }
    new_user = schemas.UserCreate(**user_details)
    if user:
        if user.user_type == "super" or user.user_type == "alpha":
            db_user = crud.create_user(db, user=new_user)
            return templates.TemplateResponse(
                "user_registration_successful.html",
                {"request": request, "db_user": db_user}
            )


# this endpoint is used to get user list for updating user
@router.get("/user_update/user_list", response_class=HTMLResponse)
async def user_list_update_page(
        user: Annotated[schemas.User, Depends(get_current_active_user)],
        request: Request,
        db: Session = Depends(get_db)
):
    if user:
        if user.user_type == "super" or user.user_type == "alpha":
            user_list = crud.get_users(db)
            return templates.TemplateResponse("user_list.html", {"request": request, "user_list": user_list})
        else:
            return templates.TemplateResponse("denied.html", {"request": request})

# this endpoint is used to get the form require to update a user record
@router.get("/user_update/{user_id}", response_class=HTMLResponse)
async def update_user_form(
        user: Annotated[schemas.User, Depends(get_current_active_user)],
        request: Request,
        user_id: int
):
    if user:
        if user.user_type == "super" or user.user_type == "alpha":
            return templates.TemplateResponse(
                "update_user_form.html",
                {
                    "request": request,
                    "user_id": user_id
                }
            )
        else:
            return templates.TemplateResponse("denied.html", {"request": request})

# this endpoint is used to submit the user record you want to update records and getting a successful response
@router.post("/user_update/{user_id}/updated/", response_class=HTMLResponse)
async def submit_updated_user_details(
        user: Annotated[schemas.User, Depends(get_current_active_user)],
        request: Request,
        user_id: int,
        is_active: bool = Form(),
        user_type: str | None = Form(default=None),
        password: str | None = Form(default=None),
        email: str | None = Form(default=None),
        db: Session = Depends(get_db),
):
    user_details = {
        "is_active": is_active,
        "user_type": user_type,
        "password": password,
        "email": email,
    }
    if user:
        if user.user_type == "super" or user.user_type == "alpha":
            db_driver = crud.update_users(db, user_details=user_details, user_id=user_id)
            return templates.TemplateResponse(
                "user_registration_successful.html",
                {
                    "request": request,
                }
            )
        else:
            return templates.TemplateResponse("denied.html", {"request": request})
