import pytest
from backend.core.security import create_access_token


@pytest.fixture
def make_token():
    """Factory fixture: generates a JWT for a given user_id/tenant_id/role."""
    def _make_token(user_id: str = "test-user-id", tenant_id: str = "test-tenant-id", role: str = "Employee"):
        return create_access_token(subject=user_id, tenant_id=tenant_id, role=role)
    return _make_token
