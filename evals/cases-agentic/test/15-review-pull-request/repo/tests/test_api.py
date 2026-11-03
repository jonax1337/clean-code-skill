from adminhub import api


def test_get_user_found(conn):
    response = api.get_user(conn, {"id": "1"})

    assert response["status"] == 200
    assert response["body"]["email"] == "ann@example.com"


def test_get_user_unknown_is_404(conn):
    assert api.get_user(conn, {"id": "99"})["status"] == 404


def test_get_user_with_bad_id_is_400(conn):
    assert api.get_user(conn, {"id": "abc"})["status"] == 400


def test_list_users_returns_everyone(conn):
    response = api.list_users(conn, {})

    assert [user["id"] for user in response["body"]["users"]] == [1, 2, 3, 4, 5]


def test_deactivate_user(conn):
    assert api.deactivate_user(conn, {"id": "2"}) == {"status": 200, "body": {"deactivated": 1}}
