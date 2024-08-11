from pydantic import BaseModel
from datetime import date
from typing import Optional


class TripBase(BaseModel):
    date: date | None
    atc_order_number: str | None
    dispatch: int
    bonus: int
    diesel_litres: float | None
    diesel_amount: int | None
    diesel_date: Optional[date]
    customer_name: str | None
    amount: float | None



class TripCreate(TripBase):
    pass


class Trip(TripBase):
    id: int
    driver_id: int
    driver_name: str

    class ConfigDict:
        from_attributes = True


class DriverBase(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    plate_number: str


class DriverCreate(DriverBase):
    pass


class Driver(DriverBase):
    id: int
    user_id: int
    is_active: bool
    trips: list[Trip] = []

    class ConfigDict:
        from_attributes = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str
    user_type: str


class User(UserBase):
    id: int
    is_active: bool

    class ConfigDict:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class ExpenseBase(BaseModel):
    date: date | None
    description: str | None
    amount: int | None


class ExpenseCreate(ExpenseBase):
    pass


class Expense(ExpenseBase):
    id: int
    driver_id: int
    driver_name: str

    class ConfigDict:
        from_attributes = True
