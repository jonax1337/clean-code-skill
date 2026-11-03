import pytest

from adminhub import users
from adminhub.errors import NotFound


def test_get_user_returns_the_user(conn):
    user = users.get_user(conn, 2)

    assert (user.email, user.role, user.active) == ("bob@example.com", "member", True)


def test_get_user_raises_for_unknown_id(conn):
    with pytest.raises(NotFound):
        users.get_user(conn, 99)


def test_list_users_is_ordered_by_id(conn):
    assert [user.id for user in users.list_users(conn)] == [1, 2, 3, 4, 5]


def test_deactivate_user_marks_the_user_inactive(conn):
    users.deactivate_user(conn, 3)

    assert users.get_user(conn, 3).active is False


def test_deactivate_user_raises_for_unknown_id(conn):
    with pytest.raises(NotFound):
        users.deactivate_user(conn, 99)
