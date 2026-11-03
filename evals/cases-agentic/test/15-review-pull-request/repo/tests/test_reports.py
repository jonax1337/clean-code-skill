from adminhub import reports


def test_signups_per_day_counts_each_day(conn):
    result = reports.signups_per_day(conn, "2024-03-01", "2024-03-03")

    assert result == [{"day": "2024-03-01", "signups": 2}, {"day": "2024-03-02", "signups": 1}]


def test_signups_per_day_end_is_exclusive(conn):
    assert reports.signups_per_day(conn, "2024-03-04", "2024-03-05") == [{"day": "2024-03-04", "signups": 1}]


def test_active_by_role_ignores_deactivated_users(conn):
    conn.execute("UPDATE users SET active = 0 WHERE id = 1")

    assert reports.active_by_role(conn) == {"member": 3, "viewer": 1}
