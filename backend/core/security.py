import bcrypt
import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Union, Dict, List

from jose import jwt, JWTError, jwk, exceptions

from backend.core.config import settings

logger = logging.getLogger(__name__)

_jwks_cache: Optional[Dict[str, Any]] = None
_jwks_cache_time: float = 0.0
_JWKS_CACHE_TTL: int = 300


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def create_access_token(
    subject: Union[str, Any],
    tenant_id: str,
    role: str = "Employee",
    expires_delta: Optional[timedelta] = None
) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "sub": str(subject),
        "tenant_id": str(tenant_id),
        "role": role,
        "exp": expire
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def _fetch_jwks() -> Optional[Dict[str, Any]]:
    global _jwks_cache, _jwks_cache_time
    now = time.time()

    if _jwks_cache and (now - _jwks_cache_time) < _JWKS_CACHE_TTL:
        return _jwks_cache

    try:
        import httpx
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(settings.keycloak_jwks_url)
            resp.raise_for_status()
            _jwks_cache = resp.json()
            _jwks_cache_time = now
            return _jwks_cache
    except Exception as e:
        logger.warning("Failed to fetch Keycloak JWKS: %s", e)
        return None


def _get_key_from_header(token: str) -> Optional[str]:
    try:
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        if not kid:
            return None

        jwks = _fetch_jwks()
        if not jwks:
            return None

        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                public_key = jwk.construct(key).to_pem().decode("utf-8")
                return public_key

        logger.warning("No matching key found in JWKS for kid=%s", kid)
        return None
    except Exception as e:
        logger.warning("Failed to extract key from token header: %s", e)
        return None


def _extract_keycloak_roles(payload: Dict[str, Any]) -> List[str]:
    roles: List[str] = []
    realm_access = payload.get("realm_access", {})
    if isinstance(realm_access, dict):
        roles.extend(realm_access.get("roles", []))

    resource_access = payload.get("resource_access", {})
    if isinstance(resource_access, dict):
        for _, access in resource_access.items():
            if isinstance(access, dict):
                roles.extend(access.get("roles", []))

    return roles


def _normalize_claims(payload: Dict[str, Any]) -> Dict[str, Any]:
    sub = payload.get("sub", "")
    tenant_id = (
        payload.get("tenant_id")
        or payload.get("tenantId")
        or payload.get("tenant")
        or payload.get("organization_id")
        or ""
    )

    roles_list = _extract_keycloak_roles(payload)
    primary_role = payload.get("role") or payload.get("role_name") or ""

    if not primary_role and roles_list:
        role_priority = ["Admin", "Tenant Admin", "Auditor", "Manager", "Employee"]
        for r in role_priority:
            if r in roles_list:
                primary_role = r
                break
        if not primary_role:
            primary_role = roles_list[0]

    normalized: Dict[str, Any] = {
        "sub": str(sub),
        "tenant_id": str(tenant_id) if tenant_id else "",
        "role": primary_role,
        "keycloak_id": str(sub),
        "email": payload.get("email") or payload.get("preferred_username") or "",
        "first_name": payload.get("given_name") or payload.get("firstName") or "",
        "last_name": payload.get("family_name") or payload.get("lastName") or "",
        "roles": roles_list,
        "iss": payload.get("iss"),
        "exp": payload.get("exp"),
    }

    if not normalized["role"]:
        normalized["role"] = "Employee"

    return normalized


def decode_keycloak_token(token: str) -> Optional[Dict[str, Any]]:
    if not settings.KEYCLOAK_ENABLED:
        return None

    public_key = _get_key_from_header(token)
    if not public_key:
        return None

    try:
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256", "RS384", "RS512", "ES256", "ES384", "ES512"],
            audience=None,
            issuer=settings.keycloak_realm_url,
            options={
                "verify_aud": False,
                "verify_exp": True,
                "verify_iat": True,
                "verify_iss": True,
            }
        )
        return _normalize_claims(payload)
    except exceptions.ExpiredSignatureError:
        logger.warning("Keycloak token expired")
        return None
    except exceptions.JWTClaimsError as e:
        logger.warning("Keycloak token claims error: %s", e)
        return None
    except JWTError as e:
        logger.warning("Keycloak token validation failed: %s", e)
        return None


def validate_token(token: str) -> Optional[Dict[str, Any]]:
    # Route tokens to the matching verifier so local tokens do not perform a
    # blocking JWKS request before their signature is checked.
    try:
        algorithm = jwt.get_unverified_header(token).get("alg", "")
    except JWTError:
        algorithm = ""

    if algorithm.startswith("HS"):
        local_payload = decode_token(token)
        if local_payload:
            return _normalize_claims(local_payload)

    if settings.KEYCLOAK_ENABLED and algorithm.startswith(("RS", "ES")):
        keycloak_payload = decode_keycloak_token(token)
        if keycloak_payload:
            return keycloak_payload

    # Keep a fallback for legacy tokens with an unusual or unreadable header.
    local_payload = decode_token(token)
    if local_payload:
        return _normalize_claims(local_payload)

    if settings.KEYCLOAK_ENABLED:
        keycloak_payload = decode_keycloak_token(token)
        if keycloak_payload:
            return keycloak_payload

    return None


async def keycloak_password_login(email: str, password: str) -> Optional[Dict[str, Any]]:
    if not settings.KEYCLOAK_ENABLED:
        return None

    data = {
        "grant_type": "password",
        "client_id": settings.KEYCLOAK_CLIENT_ID,
        "username": email,
        "password": password,
    }
    if settings.KEYCLOAK_CLIENT_SECRET:
        data["client_secret"] = settings.KEYCLOAK_CLIENT_SECRET

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        import httpx
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(settings.keycloak_token_url, data=data, headers=headers)
            if resp.status_code != 200:
                logger.warning("Keycloak login failed: status=%s body=%s", resp.status_code, resp.text)
                return None
            return resp.json()
    except ImportError:
        logger.error("httpx is required for Keycloak integration")
        return None
    except Exception as e:
        logger.warning("Keycloak password login error: %s", e)
        return None
