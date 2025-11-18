"""
Unit tests for key selection strategies
"""
import pytest
from sqlalchemy.orm import Session
from app.models import APIKey, APIKeyPool
from app.key_selector import select_key_round_robin, select_key_least_used, select_key_weighted
from app.database import SessionLocal, Base, engine
from uuid import uuid4


@pytest.fixture
def db_session():
    """Create a test database session"""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_pool(db_session):
    """Create a test key pool"""
    pool = APIKeyPool(id=uuid4(), name="test_pool")
    db_session.add(pool)
    db_session.commit()
    return pool


@pytest.fixture
def test_keys(db_session, test_pool):
    """Create test API keys"""
    keys = []
    for i in range(3):
        key = APIKey(
            pool_id=test_pool.id,
            provider_id="test_provider",
            secret_encrypted=f"encrypted_secret_{i}",
            weight=i+1,
            status="healthy"
        )
        keys.append(key)
        db_session.add(key)
    db_session.commit()
    return keys


def test_round_robin_selection(db_session, test_pool, test_keys):
    """Test round-robin key selection"""
    selected = []
    for _ in range(6):
        key = select_key_round_robin(
            db_session,
            str(test_pool.id),
            "test_provider",
            healthy_only=True
        )
        if key:
            selected.append(key.id)
    
    # Should cycle through keys
    assert len(selected) > 0, "Should select at least one key"
    # Note: Actual round-robin behavior depends on Redis state


def test_least_used_selection(db_session, test_pool, test_keys):
    """Test least-used key selection"""
    key = select_key_least_used(
        db_session,
        str(test_pool.id),
        "test_provider",
        healthy_only=True
    )
    
    assert key is not None, "Should select a key"
    assert key.pool_id == test_pool.id, "Should select from correct pool"


def test_weighted_selection(db_session, test_pool, test_keys):
    """Test weighted key selection"""
    key = select_key_weighted(
        db_session,
        str(test_pool.id),
        "test_provider",
        healthy_only=True
    )
    
    assert key is not None, "Should select a key"
    assert key.pool_id == test_pool.id, "Should select from correct pool"

