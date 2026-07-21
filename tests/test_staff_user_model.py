from app.auth.models import User


def test_staff_user_uses_non_reserved_table_name():
    assert User.__tablename__ == "staff_users"
