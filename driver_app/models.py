from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, Float
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    user_type = Column(String(20))


class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone_number = Column(String(20), unique=True, index=True)
    plate_number = Column(String(20), unique=True, index=True)

    trips = relationship("Trip", back_populates="driver")

    expenses = relationship("Expense", back_populates="driver")


class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True)
    date = Column(Date, index=True)
    atc_order_number = Column(String, unique=True, index=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"))
    driver_name = Column(String)
    dispatch = Column(Integer)
    bonus = Column(Integer)
    diesel_litres = Column(Float)
    diesel_amount = Column(Integer)
    diesel_date = Column(Date)
    customer_name = Column(String(255))
    amount = Column(Float)

    driver = relationship("Driver", back_populates="trips")


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True)
    date = Column(Date, index=True)
    description = Column(String)
    driver_id = Column(Integer, ForeignKey("drivers.id"))
    driver_name = Column(String)
    amount = Column(Integer)

    driver = relationship("Driver", back_populates="expenses")
