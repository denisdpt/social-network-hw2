import os
import random
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from user_service.main import app, get_db, Base

BASE_LOGINS = ["alpha", "bravo", "charliechocofabric", "delta", "echomusic", "sigmaboy", "foxtrot", "golfcartian", "hotelcalifornia", "indianauser", "juliet", "perreirabomber"]
BASE_PASSWORDS = ["secret1", "secret2", "secret3", "secret4", "secret5", "secret6", "secret7", "secret8", "secret9", "secret10", "secret11", "secret12", "secret13"]
BASE_EMAILS = [
    "superpuper@example.com",
    "cooluser@example.com",
    "pulpylover@example.com",
    "antonioramalho@example.com",
    "portoowl@example.com",
    "poruchikrzhevsky@example.com",
    "bmwdrifter@example.com",
    "mementomori@example.com",
    "femboychikoraltushka@example.com",
    "jblbombom@example.com"
]
FIRST_NAMES = ["John", "Jane", "Alice", "Vasya", "Bob", "Charlie", "Denis", "Diana", "Eve", "Isabel", "Frank", "Maria", "Grace", "Henry", "Walter"]
LAST_NAMES = ["Doe", "Smith", "Nephew", "Johnson", "Williams", "White", "Brown", "Pink", "Miller", "Davis", "Garcia", "Rodriguez", "White", "Ferreira", "Silva"]
PHONE_NUMBERS = [
    "+12345678901",
    "+19876543210",
    "+11234567890",
    "+10987654321",
    "+12312312312",
    "+32132132132",
    "+14725836901",
    "+98765432109",
    "+19283746550",
    "+10293847561",
    "+79027814750",
    "+19090909090",
    "+351910573790"
]
BIRTH_DATES = [
    "1983-03-02",
    "1978-02-02",
    "1991-03-03",
    "1999-04-01",
    "2004-03-08",
    "2001-04-06",
    "2009-01-09",
    "1997-08-08",
    "2006-11-09",
    "1999-01-11"
]

def unique_login():
    return f"{random.choice(BASE_LOGINS)}_{random.randint(1000, 9999)}"

def unique_email():
    base = random.choice(BASE_EMAILS)
    name, domain = base.split("@")
    return f"{name}_{random.randint(1000, 9999)}@{domain}"

def unique_password():
    return random.choice(BASE_PASSWORDS)

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

### Тесты ###

def test_register_user():
    login = unique_login()
    password = unique_password()
    email = unique_email()
    response = client.post(
        "/register",
        json={
            "login": login,
            "password": password,
            "email": email
        }
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["login"] == login
    assert data["email"] == email
    assert "id" in data

def test_duplicate_registration(): 
    # Используем фиксированные данные для проверки дублей
    login = unique_login()
    password = unique_password()
    email = unique_email()
    # Первая регистрация
    client.post(
        "/register",
        json={
            "login": login,
            "password": password,
            "email": email
        }
    )
    # Повторная регистрация(с тем же набором данных) должна вызвать ошибку 400
    response = client.post(
        "/register",
        json={
            "login": login,
            "password": password,
            "email": email
        }
    )
    assert response.status_code == 400
    data = response.json()
    assert "используется" in data["detail"]

def test_login_and_get_profile():
    login = unique_login()
    password = unique_password()
    email = unique_email()

    reg_response = client.post(
        "/register",
        json={
            "login": login,
            "password": password,
            "email": email
        }
    )
    assert reg_response.status_code == 200

    login_response = client.post(
        "/login",
        json={"login": login, "password": password}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    profile_response = client.get("/profile", headers=headers)
    assert profile_response.status_code == 200
    profile_data = profile_response.json()
    assert profile_data["login"] == login
    assert profile_data["email"] == email

def test_update_profile():
    login = unique_login()
    password = unique_password()
    email = unique_email()

    reg_response = client.post(
        "/register",
        json={
            "login": login,
            "password": password,
            "email": email
        }
    )
    assert reg_response.status_code == 200

    login_response = client.post(
        "/login", json={"login": login, "password": password}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    new_first_name = random.choice(FIRST_NAMES)
    new_last_name = random.choice(LAST_NAMES)
    new_email = unique_email()
    new_phone = random.choice(PHONE_NUMBERS)
    new_date_of_birth = random.choice(BIRTH_DATES)

    update_payload = {
        "first_name": new_first_name,
        "last_name": new_last_name,
        "email": new_email,
        "phone_number": new_phone,
        "date_of_birth": new_date_of_birth
    }
    update_response = client.put("/profile", headers=headers, json=update_payload)
    assert update_response.status_code == 200, update_response.text
    updated_profile = update_response.json()
    assert updated_profile["first_name"] == new_first_name
    assert updated_profile["last_name"] == new_last_name
    assert updated_profile["email"] == new_email
    assert updated_profile["phone_number"] == new_phone
    assert updated_profile["date_of_birth"] == new_date_of_birth
