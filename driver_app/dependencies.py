from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Form, Depends, status, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Response
from fastapi.templating import Jinja2Templates
import datetime
import pdfkit
import pandas as pd
from io import BytesIO


from driver_app import schemas, crud
from driver_app.utilities import get_db, get_current_active_user


router = APIRouter()

templates = Jinja2Templates(directory="driver_app/templates")


# endpoint for getting the form require to submit driver details
@router.get("/driver_registration/", response_class=HTMLResponse)
async def create_driver_details(user: Annotated[schemas.User, Depends(get_current_active_user)], request: Request):
    if user:
        if user.user_type == "super" or user.user_type == "beta":
            return templates.TemplateResponse("create_driver_details.html", {"request": request})
        else:
            return templates.TemplateResponse("denied.html", {"request": request})

# endpoint for submitting a newly registered driver
@router.post("/submit_details", response_class=HTMLResponse)
async def create_driver_details(
        user: Annotated[schemas.User, Depends(get_current_active_user)],
        request: Request,
        first_name: Annotated[str, Form()],
        last_name: Annotated[str, Form()],
        phone_number: Annotated[str, Form()],
        plate_number: Annotated[str, Form()],
        db: Session = Depends(get_db),
):
    driver_details = {
        "first_name": first_name,
        "last_name": last_name,
        "phone_number": phone_number,
        "plate_number": plate_number
    }
    driver = schemas.DriverCreate(**driver_details)
    if user:
        if user.user_type == "super" or user.user_type == "beta":
            db_user = crud.create_driver(db, driver=driver)
            return templates.TemplateResponse(
                "driver_registration_successful.html",
                {"request": request, "db_user": db_user}
            )
        else:
            return templates.TemplateResponse("denied.html", {"request": request})


# endpoint for getting trips and expense reports for different drivers
@router.get("/trip-and-expenses-report/", response_class=HTMLResponse)
async def trip_and_expenses_report(user: Annotated[schemas.User, Depends(get_current_active_user)], request: Request):
    if user:
        return templates.TemplateResponse("trip-and-expenses-report.html", {"request": request})


# this endpoint is used when you want to register driver's trips
@router.get("/fleet_record/", response_class=HTMLResponse)
async def fleet_record_page(
        user: Annotated[schemas.User, Depends(get_current_active_user)],
        request: Request,
        db: Session = Depends(get_db)
):
    if user:
        if user.user_type == "super" or user.user_type == "beta":
            fleet_records = crud.get_drivers(db)
            return templates.TemplateResponse("fleet_record.html", {"request": request, "fleet_records": fleet_records})
        else:
            return templates.TemplateResponse("denied.html", {"request": request})

# this endpoint is used to get the form require to enter new trip of a given driver
@router.get("/register_new_trip/{first_name}/{plate_number}/{driver_id}/", response_class=HTMLResponse)
async def register_new_trip(
        user: Annotated[schemas.User, Depends(get_current_active_user)],
        driver_id: int,
        plate_number: str,
        first_name: str,
        request: Request
):
    if user:
        if user.user_type == "super" or user.user_type == "beta":
            return templates.TemplateResponse(
                "enter_driver_new_trip.html",
                {
                    "request": request,
                    "driver_id": driver_id,
                    "plate_number": plate_number,
                    "first_name": first_name
                }
            )
        else:
            return templates.TemplateResponse("denied.html", {"request": request})

# endpoint for submitting a newly entered trip
@router.post("/submit_trip", response_class=HTMLResponse)
async def create_trip_details(
        user: Annotated[schemas.User, Depends(get_current_active_user)],
        request: Request,
        driver_id: Annotated[int, Form()],
        driver_name: Annotated[str, Form()],
        dispatch: Annotated[int, Form()],
        bonus: Annotated[int, Form()],
        date: datetime.date | None = Form(default=None),
        atc_order_number: str | None = Form(default=None),
        diesel_litres: float | None = Form(default=None),
        diesel_amount: int | None = Form(default=None),
        diesel_date: datetime.date | None = Form(default=None),
        customer_name: str | None = Form(default=None),
        amount: float | None = Form(default=None),
        db: Session = Depends(get_db),
):
    trip_details = {
        "date": date,
        "atc_order_number": atc_order_number,
        "customer_name": customer_name,
        "amount": amount,
        "dispatch": dispatch,
        "bonus": bonus,
        "diesel_litres": diesel_litres,
        "diesel_amount": diesel_amount,
        "diesel_date": diesel_date
    }
    trip = schemas.TripCreate(**trip_details)
    if user:
        if user.user_type == "super" or user.user_type == "beta":
            db_trip = crud.create_driver_trip(db, trip=trip, driver_id=driver_id, driver_name=driver_name)
            return templates.TemplateResponse("trip_registration_successful.html", {"request": request, "db_trip": db_trip})
        else:
            return templates.TemplateResponse("denied.html", {"request": request})

# endpoint for login out
@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token", httponly=True)
    return response


# this endpoint is used when you want to go get the trip reports for drivers
@router.get("/trip-report/", response_class=HTMLResponse)
async def fleet_report_page(
        user: Annotated[schemas.User, Depends(get_current_active_user)],
        request: Request,
        db: Session = Depends(get_db)
):
    if user:
        fleet_reports = crud.get_drivers(db)
        return templates.TemplateResponse("trip_report.html", {"request": request, "fleet_reports": fleet_reports})


# this endpoint is used to get the trips report of a given driver
@router.get("/trip-report/{plate_number}/{driver_id}/")
async def driver_trip_report(
        user: Annotated[schemas.User, Depends(get_current_active_user)],
        plate_number: str,
        driver_id: int,
        request: Request,
        db: Session = Depends(get_db),
):
    if user:
        driver_trips = crud.get_driver_trips(db, driver_id=driver_id)
        return templates.TemplateResponse(
            "driver_trip_report.html",
            {
                "request": request,
                "driver_trips": driver_trips,
                "plate_number": plate_number,
                "driver_id": driver_id
            }
        )


# this endpoint is used to download the pdf file for each driver's trip
@router.get("/trip-report/{plate_number}/{driver_id}/pdf/")
async def export_pdf_trip_report(
        user: Annotated[schemas.User, Depends(get_current_active_user)],
        plate_number: str,
        driver_id: int,
        request: Request,
        start_date: datetime.date,
        end_date: datetime.date,
        db: Session = Depends(get_db),
):
    if user:
        driver_trips = crud.get_driver_trips_between_dates(db, driver_id, start_date, end_date)
        total_bonus = sum(trip.bonus for trip in driver_trips)
        total_dispatch = sum(trip.dispatch for trip in driver_trips)
        total_amount = sum(trip.amount for trip in driver_trips)

        html_content = templates.get_template("pdf_trip_report.html").render(
            plate_number=plate_number, total_bonus=total_bonus, total_dispatch=total_dispatch,
            driver_trips=driver_trips, total_amount=total_amount, request=request
        )
        pdf = pdfkit.from_string(html_content, False)
        headers = {
            'Content-Disposition': f'attachment; filename="{plate_number} trip report.pdf"'
        }
        return Response(content=pdf, media_type="application/pdf", headers=headers)


# this endpoint is used to download the Excel file for each driver's trip
@router.get("/trip-report/{plate_number}/{driver_id}/excel/")
async def export_excel_trip_report(
        user: Annotated[schemas.User, Depends(get_current_active_user)],
        plate_number: str,
        driver_id: int,
        db: Session = Depends(get_db),
):
    if user:
        driver_trips = crud.get_driver_trips(db, driver_id=driver_id)
        data = [
            {
                "Date Loaded": trip.date,
                "ATC Order Number": trip.atc_order_number,
                "Driver Name": trip.driver_name,
                "Dispatch": trip.dispatch,
                "Bonus": trip.bonus,
                "Diesel Litres": trip.diesel_litres,
                "Diesel Amount": trip.diesel_amount,
                "Diesel Collection Date": trip.diesel_date,
                "Customer Name": trip.customer_name,
                "Trip Amount": trip.amount
            }
            for trip in driver_trips
        ]

        df = pd.DataFrame(data)

        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)

        buffer.seek(0)

        headers = {
            'Content-Disposition': f'attachment; filename="{plate_number} trip.xlsx"'
        }
        return Response(content=buffer.getvalue(), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers=headers)


# this endpoint is used to update fleet, trip, and expenses
@router.get("/update_fleet_and_trip_and_expenses/", response_class=HTMLResponse)
async def update_fleet_and_trip_and_expenses(
        user: Annotated[schemas.User, Depends(get_current_active_user)],
        request: Request,
):
    if user:
        if user.user_type == "super" or user.user_type == "beta":
            return templates.TemplateResponse("update.html", {"request": request})
        else:
            return templates.TemplateResponse("denied.html", {"request": request})

# this endpoint is used to update fleet
@router.get("/fleet_update/", response_class=HTMLResponse)
async def fleet_update_page(
        user: Annotated[schemas.User, Depends(get_current_active_user)],
        request: Request,
        db: Session = Depends(get_db)
):
    if user:
        if user.user_type == "super" or user.user_type == "beta":
            fleet_reports = crud.get_drivers(db)
            return templates.TemplateResponse("fleet_update.html", {"request": request, "fleet_reports": fleet_reports})
        else:
            return templates.TemplateResponse("denied.html", {"request": request})

# this endpoint is used to update fleet of a given driver
@router.get("/fleet_update/{driver_id}/{plate_number}/", response_class=HTMLResponse)
async def update_fleet_form(
        user: Annotated[schemas.User, Depends(get_current_active_user)],
        request: Request,
        driver_id: int,
        plate_number: str,
):
    if user:
        if user.user_type == "super" or user.user_type == "beta":
            return templates.TemplateResponse(
                "enter_updated_fleet.html",
                {
                    "request": request,
                    "driver_id": driver_id,
                    "plate_number": plate_number
                }
            )
        else:
            return templates.TemplateResponse("denied.html", {"request": request})

# this endpoint is used to submit the driver updated records and getting a successful response
@router.post("/updated/{driver_id}/{plate_number}/", response_class=HTMLResponse)
async def update_driver_details(
        user: Annotated[schemas.User, Depends(get_current_active_user)],
        request: Request,
        driver_id: int,
        first_name: str | None = Form(default=None),
        last_name: str | None = Form(default=None),
        phone_number: str | None = Form(default=None),
        db: Session = Depends(get_db),
):
    driver_details = {
        "first_name": first_name,
        "last_name": last_name,
        "phone_number": phone_number,
    }
    if user:
        if user.user_type == "super" or user.user_type == "beta":
            db_driver = crud.update_driver(db, driver_id=driver_id, driver_details=driver_details)
            return templates.TemplateResponse(
                "driver_update_successful.html",
                {
                    "request": request,
                    "db_driver": db_driver
                }
            )
        else:
            return templates.TemplateResponse("denied.html", {"request": request})

# this endpoint is used to get the fleets for updating fleets or driver's trips
@router.get("/trip_update/", response_class=HTMLResponse)
async def trip_update_page(
        user: Annotated[schemas.User, Depends(get_current_active_user)],
        request: Request,
        db: Session = Depends(get_db)
):
    if user:
        if user.user_type == "super" or user.user_type == "beta":
            fleet_reports = crud.get_drivers(db)
            return templates.TemplateResponse("trip_update.html", {"request": request, "fleet_reports": fleet_reports})
        else:
            return templates.TemplateResponse("denied.html", {"request": request})

# this endpoint is used to get the trips of a given driver before updating
@router.get("/trip/{plate_number}/{driver_id}/")
async def driver_trip_record(
        user: Annotated[schemas.User, Depends(get_current_active_user)],
        plate_number: str,
        driver_id: int,
        request: Request,
        db: Session = Depends(get_db),
):
    if user:
        if user.user_type == "super" or user.user_type == "beta":
            driver_trips = crud.get_driver_trips(db, driver_id=driver_id)
            return templates.TemplateResponse(
                "driver_trip_record.html",
                {
                    "request": request,
                    "driver_trips": driver_trips,
                    "plate_number": plate_number,
                }
            )
        else:
            return templates.TemplateResponse("denied.html", {"request": request})

# this endpoint is used to get the form require to update a given trip
@router.get("/trip_update/{plate_number}/{trip_id}", response_class=HTMLResponse)
async def update_trip_form(
        user: Annotated[schemas.User, Depends(get_current_active_user)],
        request: Request,
        trip_id: int,
        plate_number: str,
):
    if user:
        if user.user_type == "super" or user.user_type == "beta":
            return templates.TemplateResponse(
                "update_trip_form.html",
                {
                    "request": request,
                    "trip_id": trip_id,
                    "plate_number": plate_number
                }
            )
        else:
            return templates.TemplateResponse("denied.html", {"request": request})

# this endpoint is used to submit the updated trip and get a successful message response
@router.post("/trip_updated/{trip_id}/{plate_number}/", response_class=HTMLResponse)
async def updated_driver_details_message(
        user: Annotated[schemas.User, Depends(get_current_active_user)],
        request: Request,
        trip_id: int,
        plate_number: str,
        driver_name: str | None = Form(default=None),
        dispatch: int | None = Form(default=None),
        bonus: int | None = Form(default=None),
        date: datetime.date | None = Form(default=None),
        atc_order_number: str | None = Form(default=None),
        diesel_litres: float | None = Form(default=None),
        diesel_amount: int | None = Form(default=None),
        diesel_date: datetime.date | None = Form(default=None),
        customer_name: str | None = Form(default=None),
        amount: float | None = Form(default=None),
        db: Session = Depends(get_db),
):
    trip_details = {
        "date": date,
        "atc_order_number": atc_order_number,
        "customer_name": customer_name,
        "amount": amount,
        "dispatch": dispatch,
        "bonus": bonus,
        "diesel_litres": diesel_litres,
        "diesel_amount": diesel_amount,
        "diesel_date": diesel_date,
        "driver_name": driver_name
    }
    if user:
        if user.user_type == "super" or user.user_type == "beta":
            db_trip = crud.update_trip(db, trip_id=trip_id, trip_details=trip_details)
            return templates.TemplateResponse(
                "trip_update_successful.html",
                {
                    "request": request,
                    "db_trip": db_trip,
                    "plate_number": plate_number
                }
            )
        else:
            return templates.TemplateResponse("denied.html", {"request": request})

# this endpoint is use for checking the expenses report for drivers and not for recording expenses
@router.get("/expense-report/", response_class=HTMLResponse)
async def expense_report_page(
        user: Annotated[schemas.User, Depends(get_current_active_user)],
        request: Request,
        db: Session = Depends(get_db)
):
    if user:
        fleet_reports = crud.get_drivers(db)
        return templates.TemplateResponse("expense_report.html", {"request": request, "fleet_reports": fleet_reports})


# this endpoint is use for recording expenses of drivers
@router.get("/expense-fleet-record/", response_class=HTMLResponse)
async def expense_fleet_record_page(
        user: Annotated[schemas.User, Depends(get_current_active_user)],
        request: Request,
        db: Session = Depends(get_db)
):
    if user:
        if user.user_type == "super" or user.user_type == "beta":
            fleet_records = crud.get_drivers(db)
            return templates.TemplateResponse(
                "expense_fleet_record.html",
                {"request": request, "fleet_records": fleet_records}
            )
        else:
            return templates.TemplateResponse("denied.html", {"request": request})

# this endpoint is use for getting the form for entering new expense
@router.get("/register_new_expenses/{first_name}/{plate_number}/{driver_id}/", response_class=HTMLResponse)
async def register_new_trip(
        user: Annotated[schemas.User, Depends(get_current_active_user)],
        driver_id: int,
        plate_number: str,
        first_name: str,
        request: Request
):
    if user:
        if user.user_type == "super" or user.user_type == "beta":
            return templates.TemplateResponse(
                "enter_driver_new_expenses.html",
                {
                    "request": request,
                    "driver_id": driver_id,
                    "plate_number": plate_number,
                    "first_name": first_name
                }
            )
        else:
            return templates.TemplateResponse("denied.html", {"request": request})

# this endpoint is use for submitting the new expenses you have entered
@router.post("/submit_expenses", response_class=HTMLResponse)
async def create_trip_details(
        user: Annotated[schemas.User, Depends(get_current_active_user)],
        request: Request,
        driver_id: Annotated[int, Form()],
        driver_name: Annotated[str, Form()],
        date: datetime.date | None = Form(default=None),
        description: str | None = Form(default=None),
        amount: int | None = Form(default=None),
        db: Session = Depends(get_db),
):
    expenses_details = {
        "date": date,
        "description": description,
        "amount": amount,
    }
    expense = schemas.ExpenseCreate(**expenses_details)
    if user:
        if user.user_type == "super" or user.user_type == "beta":
            db_expense = crud.create_driver_expense(db, expense=expense, driver_id=driver_id, driver_name=driver_name)
            return templates.TemplateResponse(
                "expenses_registration_successful.html",
                {"request": request, "db_expense": db_expense}
            )
        else:
            return templates.TemplateResponse("denied.html", {"request": request})

# this endpoint is use for displaying the expenses report for each driver
@router.get("/expense-report/{plate_number}/{driver_id}/")
async def driver_expense_report(
        user: Annotated[schemas.User, Depends(get_current_active_user)],
        plate_number: str,
        driver_id: int,
        request: Request,
        db: Session = Depends(get_db),
):
    if user:
        driver_expenses = crud.get_driver_expense(db, driver_id=driver_id)
        return templates.TemplateResponse(
            "driver_expense_report.html",
            {
                "request": request,
                "driver_expenses": driver_expenses,
                "plate_number": plate_number,
                "driver_id": driver_id
            }
        )


# this endpoint is used to download the pdf file for each driver's expense
@router.get("/expense-report/{plate_number}/{driver_id}/pdf/")
async def export_pdf_expense_report(
        user: Annotated[schemas.User, Depends(get_current_active_user)],
        plate_number: str,
        driver_id: int,
        request: Request,
        start_date: datetime.date,
        end_date: datetime.date,
        db: Session = Depends(get_db),
):
    if user:
        driver_expenses = crud.get_driver_expenses_between_dates(db, driver_id, start_date, end_date)
        total_amount = sum(expense.amount for expense in driver_expenses)
        html_content = templates.get_template("pdf_expense_report.html").render(
            plate_number=plate_number, total_amount=total_amount, driver_expenses=driver_expenses, request=request
        )
        pdf = pdfkit.from_string(html_content, False)
        headers = {
            'Content-Disposition': f'attachment; filename="{plate_number} expenses.pdf"'
        }
        return Response(content=pdf, media_type="application/pdf", headers=headers)


# this endpoint is used to download the Excel file for each driver's expense
@router.get("/expense-report/{plate_number}/{driver_id}/excel/")
async def export_excel_expense_report(
        user: Annotated[schemas.User, Depends(get_current_active_user)],
        plate_number: str,
        driver_id: int,
        db: Session = Depends(get_db),
):
    if user:
        driver_expenses = crud.get_driver_expense(db, driver_id=driver_id)
        data = [
            {
                "date": expense.date,
                "description": expense.description,
                "Driver Name": expense.driver_name,
                "amount": expense.amount
            }
            for expense in driver_expenses
        ]

        df = pd.DataFrame(data)

        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)

        buffer.seek(0)

        headers = {
            'Content-Disposition': f'attachment; filename="{plate_number} expenses.xlsx"'
        }
        return Response(content=buffer.getvalue(), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers=headers)


# this endpoint is used to get the fleets for updating driver's expenses
@router.get("/expense_update/", response_class=HTMLResponse)
async def expense_update_page(
        user: Annotated[schemas.User, Depends(get_current_active_user)],
        request: Request,
        db: Session = Depends(get_db)
):
    if user:
        if user.user_type == "super" or user.user_type == "beta":
            fleet_record_for_expense_update = crud.get_drivers(db)
            return templates.TemplateResponse(
                "expense_update.html",
                {"request": request, "fleet_record_for_expense_update": fleet_record_for_expense_update}
            )
        else:
            return templates.TemplateResponse("denied.html", {"request": request})

# this endpoint is used to get the expenses of a given driver before updating
@router.get("/expense_update/{plate_number}/{driver_id}/")
async def driver_expenses_record(
        user: Annotated[schemas.User, Depends(get_current_active_user)],
        plate_number: str,
        driver_id: int,
        request: Request,
        db: Session = Depends(get_db),
):
    if user:
        if user.user_type == "super" or user.user_type == "beta":
            driver_expenses = crud.get_driver_expense(db, driver_id=driver_id)
            return templates.TemplateResponse(
                "driver_expense_record.html",
                {
                    "request": request,
                    "driver_expenses": driver_expenses,
                    "plate_number": plate_number,
                    "driver_id": driver_id
                }
            )
        else:
            return templates.TemplateResponse("denied.html", {"request": request})

# this endpoint is used to get the form require to update a given expense
@router.get("/expense-update/{plate_number}/{expense_id}", response_class=HTMLResponse)
async def update_expense_form(
        user: Annotated[schemas.User, Depends(get_current_active_user)],
        request: Request,
        expense_id: int,
        plate_number: str,
):
    if user:
        if user.user_type == "super" or user.user_type == "beta":
            return templates.TemplateResponse(
                "update_expense_form.html",
                {
                    "request": request,
                    "expense_id": expense_id,
                    "plate_number": plate_number
                }
            )
        else:
            return templates.TemplateResponse("denied.html", {"request": request})

# this endpoint is used to submit the updated expense and get a successful message response
@router.post("/expense_updated/{expense_id}/{plate_number}/", response_class=HTMLResponse)
async def submit_updated_driver_expense(
        user: Annotated[schemas.User, Depends(get_current_active_user)],
        request: Request,
        expense_id: int,
        plate_number: str,
        driver_name: str | None = Form(default=None),
        description: int | None = Form(default=None),
        date: datetime.date | None = Form(default=None),
        amount: int | None = Form(default=None),
        db: Session = Depends(get_db),
):
    expense_details = {
        "date": date,
        "description": description,
        "amount": amount,
        "driver_name": driver_name
    }
    if user:
        if user.user_type == "super" or user.user_type == "beta":
            db_expense = crud.update_expense(db, expense_id=expense_id, expense_details=expense_details)
            return templates.TemplateResponse(
                "expense_update_successful.html",
                {
                    "request": request,
                    "plate_number": plate_number
                }
            )
        else:
            return templates.TemplateResponse("denied.html", {"request": request})

# endpoint for getting your general trips and expenses reports not particular to a driver
@router.get("/general-trip-and-expenses-report/", response_class=HTMLResponse)
async def general_trip_and_expenses_report(user: Annotated[schemas.User, Depends(get_current_active_user)], request: Request):
    if user:
        return templates.TemplateResponse("general-trip-and-expenses-report.html", {"request": request})


# this endpoint is used when you want to go get the trip reports for drivers
@router.get("/general-trip-report/", response_class=HTMLResponse)
async def general_trip_report(
        user: Annotated[schemas.User, Depends(get_current_active_user)],
        request: Request,
        db: Session = Depends(get_db)
):
    if user:
        trip_reports = crud.get_trips(db)
        return templates.TemplateResponse("general-trip-report.html", {"request": request, "trip_reports": trip_reports})


# this endpoint is used to download the pdf file for the general trips
@router.get("/general-trip-report/pdf/")
async def export_pdf_general_trip_report(
        user: Annotated[schemas.User, Depends(get_current_active_user)],
        request: Request,
        start_date: datetime.date,
        end_date: datetime.date,
        db: Session = Depends(get_db),
):
    if user:
        general_trips = crud.get_trips_between_dates(db, start_date, end_date)
        total_bonus = sum(trip.bonus for trip in general_trips)
        total_dispatch = sum(trip.dispatch for trip in general_trips)
        total_amount = sum(trip.amount for trip in general_trips)

        html_content = templates.get_template("pdf_general_trip_report.html").render(
            general_trips=general_trips, total_bonus=total_bonus,
            total_dispatch=total_dispatch, total_amount=total_amount, request=request
        )
        pdf = pdfkit.from_string(html_content, False)
        headers = {
            'Content-Disposition': 'attachment; filename="trips.pdf"'
        }
        return Response(content=pdf, media_type="application/pdf", headers=headers)


# this endpoint is used to download the Excel file for all trips
@router.get("/general-trip-report/excel/")
async def export_excel_general_trip_report(
        user: Annotated[schemas.User, Depends(get_current_active_user)],
        db: Session = Depends(get_db),
):
    if user:
        general_trips = crud.get_trips(db)
        data = [
            {
                "Date Loaded": trip.date,
                "ATC Order Number": trip.atc_order_number,
                "Driver Name": trip.driver_name,
                "Dispatch": trip.dispatch,
                "Bonus": trip.bonus,
                "Diesel Litres": trip.diesel_litres,
                "Diesel Amount": trip.diesel_amount,
                "Diesel Collection Date": trip.diesel_date,
                "Customer Name": trip.customer_name,
                "Trip Amount": trip.amount
            }
            for trip in general_trips
        ]

        df = pd.DataFrame(data)

        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)

        buffer.seek(0)

        headers = {
            'Content-Disposition': 'attachment; filename="trip.xlsx"'
        }
        return Response(content=buffer.getvalue(), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers=headers)


# this endpoint is used when you want to go get the expenses reports for drivers
@router.get("/general-expense-report/", response_class=HTMLResponse)
async def general_expenses_report(
        user: Annotated[schemas.User, Depends(get_current_active_user)],
        request: Request,
        db: Session = Depends(get_db)
):
    if user:
        expenses_reports = crud.get_expenses(db)
        return templates.TemplateResponse("general-expense-report.html", {"request": request, "expenses_reports": expenses_reports})


# this endpoint is used to download the pdf file for the general expenses
@router.get("/general-expenses-report/pdf/")
async def export_pdf_general_expenses_report(
        user: Annotated[schemas.User, Depends(get_current_active_user)],
        request: Request,
        start_date: datetime.date,
        end_date: datetime.date,
        db: Session = Depends(get_db),
):
    if user:
        general_expenses = crud.get_expenses_between_dates(db, start_date, end_date)
        total_amount = sum(expense.amount for expense in general_expenses)
        html_content = templates.get_template("pdf_general_expenses_report.html").render(
            general_expenses=general_expenses, total_amount=total_amount, request=request
        )
        pdf = pdfkit.from_string(html_content, False)
        headers = {
            'Content-Disposition': 'attachment; filename="expenses.pdf"'
        }
        return Response(content=pdf, media_type="application/pdf", headers=headers)


# this endpoint is used to download the Excel file for all expenses
@router.get("/general-expenses-report/excel/")
async def export_excel_general_expense_report(
        user: Annotated[schemas.User, Depends(get_current_active_user)],
        db: Session = Depends(get_db),
):
    if user:
        general_expenses = crud.get_expenses(db)
        data = [
            {
                "date": expense.date,
                "description": expense.description,
                "Driver Name": expense.driver_name,
                "amount": expense.amount
            }
            for expense in general_expenses
        ]

        df = pd.DataFrame(data)

        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)

        buffer.seek(0)

        headers = {
            'Content-Disposition': f'attachment; filename="expenses.xlsx"'
        }
        return Response(content=buffer.getvalue(), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers=headers)


