import pytest

from adminhub import db, users

SAMPLE_USERS = [
    ("ann@example.com", "Ann Lee", "admin", "2024-03-01T09:00:00"),
    ("bob@example.com", "Bob Stone", "member", "2024-03-01T17:30:00"),
    ("cy@example.com", "Cy Marsh", "member", "2024-03-02T08:15:00"),
    ("dee@example.com", "Dee Ortiz", "member", "2024-03-04T12:00:00"),
    ("eve@example.com", "Eve Hall", "viewer", "2024-03-05T23:59:00"),
]


@pytest.fixture
def conn():
    connection = db.connect(":memory:")
    for email, name, role, created_at in SAMPLE_USERS:
        users.create_user(connection, email, name, role, created_at)
    yield connection
    connection.close()
