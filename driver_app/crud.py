from sqlalchemy.orm import Session
from sqlalchemy import between, desc
from passlib.context import CryptContext

from driver_app import models, schemas
from datetime import date


def get_driver_by_id(db: Session, driver_id: int):
    return db.query(models.Driver).filter(models.Driver.id == driver_id).first()


def get_driver_by_plate_number(db: Session, plate_number: str):
    return db.query(models.Driver).filter(models.Driver.plate_number == plate_number).first()


def get_drivers(db: Session):
    return db.query(models.Driver).order_by(desc(models.Driver.plate_number)).all()


def get_driver_trips(db: Session, driver_id: int):
    return db.query(models.Trip).filter(
        models.Trip.driver_id == driver_id
    ).order_by(desc(models.Trip.date)).all()


def get_driver_trips_between_dates(db: Session, driver_id: int, start_date: date, end_date: date):
    return db.query(models.Trip).filter(
        models.Trip.driver_id == driver_id,
        between(models.Trip.date, start_date, end_date)).order_by(desc(models.Trip.date)).all()


def create_driver(db: Session, driver: schemas.DriverCreate):
    db_driver = models.Driver(**driver.model_dump())
    db.add(db_driver)
    db.commit()
    db.refresh(db_driver)
    return db_driver


def update_driver(db: Session, driver_id: int, driver_details: dict):
    db_driver = get_driver_by_id(db, driver_id)
    if driver_details["first_name"]:
        db_driver.first_name = driver_details["first_name"]
    if driver_details["last_name"]:
        db_driver.last_name = driver_details["last_name"]
    if driver_details["phone_number"]:
        db_driver.phone_number = driver_details["phone_number"]

    db.commit()
    db.refresh(db_driver)
    return db_driver


def get_trip_by_id(db: Session, trip_id: int):
    return db.query(models.Trip).filter(models.Trip.id == trip_id).first()


def get_trips(db: Session):
    return db.query(models.Trip).order_by(desc(models.Trip.date)).all()


def get_trips_between_dates(db: Session, start_date: date, end_date: date):
    return db.query(models.Trip).filter(
        between(models.Trip.date, start_date, end_date)).order_by(desc(models.Trip.date)).all()


def create_driver_trip(db: Session, trip: schemas.TripCreate, driver_id: int, driver_name: str):
    db_trip = models.Trip(**trip.model_dump(exclude_none=True), driver_id=driver_id, driver_name=driver_name)
    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)
    return db_trip


def update_trip(db: Session, trip_id: int, trip_details: dict):
    db_trip = get_trip_by_id(db, trip_id)
    if trip_details["date"]:
        db_trip.date = trip_details["date"]
    if trip_details["atc_order_number"]:
        db_trip.atc_order_number = trip_details["atc_order_number"]
    if trip_details["customer_name"]:
        db_trip.customer_name = trip_details["customer_name"]
    if trip_details["amount"] is not None:
        db_trip.amount = trip_details["amount"]
    if trip_details["dispatch"] is not None:
        db_trip.dispatch = trip_details["dispatch"]
    if trip_details["bonus"] is not None:
        db_trip.bonus = trip_details["bonus"]
    if trip_details["diesel_litres"] is not None:
        db_trip.diesel_litres = trip_details["diesel_litres"]
    if trip_details["diesel_amount"] is not None:
        db_trip.diesel_amount = trip_details["diesel_amount"]
    if trip_details["diesel_date"]:
        db_trip.diesel_date = trip_details["diesel_date"]
    if trip_details["driver_name"]:
        db_trip.driver_name = trip_details["driver_name"]

    db.commit()
    db.refresh(db_trip)
    return db_trip


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password, user_type=user.user_type)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_users(db: Session):
    return db.query(models.User).all()


def update_users(db: Session, user_details: dict, user_id: int):
    db_user = get_user_by_id(db, user_id)
    if user_details["is_active"]:
        if user_details.get("is_active") == "True":
            db_user.is_active = True
        elif user_details.get("is_active") == "False":
            db_user.is_active = False
    if user_details["user_type"]:
        db_user.user_type = user_details["user_type"]
    if user_details["email"]:
        db_user.email = user_details["email"]
    if user_details["password"]:
        db_user.password = pwd_context.hash(user_details["password"])
    db.commit()
    db.refresh(db_user)
    return db_user


def create_driver_expense(db: Session, expense: schemas.ExpenseCreate, driver_id: int, driver_name: str):
    db_expense = models.Expense(**expense.model_dump(exclude_none=True), driver_id=driver_id, driver_name=driver_name)
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


def get_expense_by_id(db: Session, expense_id: int):
    return db.query(models.Expense).filter(models.Expense.id == expense_id).first()


def get_driver_expense(db: Session, driver_id: int):
    return db.query(models.Expense).filter(
        models.Expense.driver_id == driver_id
    ).order_by(desc(models.Expense.date)).all()


def update_expense(db: Session, expense_id: int, expense_details: dict):
    db_expense = get_expense_by_id(db, expense_id)
    if expense_details["date"]:
        db_expense.date = expense_details["date"]
    if expense_details["driver_name"]:
        db_expense.driver_name = expense_details["driver_name"]
    if expense_details["description"]:
        db_expense.description = expense_details["description"]
    if expense_details["amount"] is not None:
        db_expense.amount = expense_details["amount"]
    db.commit()
    db.refresh(db_expense)
    return db_expense


def get_driver_expenses_between_dates(db: Session, driver_id: int, start_date: date, end_date: date):
    return db.query(models.Expense).filter(
        models.Expense.driver_id == driver_id,
        between(models.Expense.date, start_date, end_date)).all()


def get_expenses(db: Session):
    return db.query(models.Expense).order_by(desc(models.Expense.date)).all()


def get_expenses_between_dates(db: Session, start_date: date, end_date: date):
    return db.query(models.Expense).filter(
        between(models.Expense.date, start_date, end_date)).order_by(desc(models.Expense.date)).all()

