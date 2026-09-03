import asyncio
from datetime import timedelta

from backend.core.security import (
    create_access_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from backend.core.dependencies import require_role
from fastapi import HTTPException
import pytest


# ---- Password hashing ----

def test_password_hash_and_verify_success():
    hashed = get_password_hash("MySecret123")
    assert verify_password("MySecret123", hashed) is True


def test_password_verify_fails_on_wrong_password():
    hashed = get_password_hash("MySecret123")
    assert verify_password("WrongPassword", hashed) is False


# ---- Token creation/decoding ----

def test_create_and_decode_token_roundtrip():
    token = create_access_token(subject="user-123", tenant_id="tenant-abc", role="Admin")
    payload = decode_token(token)

    assert payload is not None
    assert payload["sub"] == "user-123"
    assert payload["tenant_id"] == "tenant-abc"
    assert payload["role"] == "Admin"


def test_decode_token_rejects_garbage_token():
    payload = decode_token("this.is.not.a.valid.jwt")
    assert payload is None


def test_expired_token_is_rejected():
    token = create_access_token(
        subject="user-123",
        tenant_id="tenant-abc",
        role="Admin",
        expires_delta=timedelta(seconds=-1),  # already expired
    )
    payload = decode_token(token)
    assert payload is None


# ---- RBAC guard (require_role) ----

def test_require_role_allows_matching_role(make_token):
    token = make_token(role="Admin")
    checker = require_role(["Admin", "Tenant Admin"])

    result = asyncio.run(checker(authorization=f"Bearer {token}"))
    assert result == "Admin"


def test_require_role_rejects_wrong_role(make_token):
    token = make_token(role="Employee")
    checker = require_role(["Admin"])

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(checker(authorization=f"Bearer {token}"))
    assert exc_info.value.status_code == 403


def test_require_role_rejects_missing_header():
    checker = require_role(["Admin"])

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(checker(authorization=None))
    assert exc_info.value.status_code == 401


def test_require_role_rejects_malformed_header():
    checker = require_role(["Admin"])

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(checker(authorization="NotBearer sometoken"))
    assert exc_info.value.status_code == 401


# ---- Login endpoint (integration-style, no live server needed) ----

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_login_success_returns_token():
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "adminpass123"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_wrong_password_returns_401():
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_login_unknown_email_returns_401():
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@test.com", "password": "whatever"},
    )
    assert response.status_code == 401


def test_login_returns_role_in_token():
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "adminpass123"},
    )
    token = response.json()["access_token"]

    from backend.core.security import decode_token
    payload = decode_token(token)
    assert payload["role"] == "Admin"
