"""
Pytest configuration for PlayVision
"""
import pytest
from django.conf import settings


@pytest.fixture(scope='session')
def django_db_setup():
    """Setup test database"""
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }


@pytest.fixture
def admin_user(db):
    """Create admin user for testing"""
    from apps.accounts.models import User
    return User.objects.create_superuser(
        email='admin@test.com',
        password='test123!@#'
    )


@pytest.fixture
def regular_user(db):
    """Create regular user for testing"""
    from apps.accounts.models import User
    return User.objects.create_user(
        email='user@test.com',
        password='test123!@#'
    )


@pytest.fixture
def client_authenticated(client, admin_user):
    """Authenticated client"""
    client.force_login(admin_user)
    return client

