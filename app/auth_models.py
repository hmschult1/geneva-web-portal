from flask_login import UserMixin


class User(UserMixin):
    """Simple placeholder user object for the local auth fallback."""

    def __init__(self, user_id=0):
        self.id = user_id
        # self.is_authenticated = True
        # self.is_active = True
        # self.is_anonymous = False

    def get_id(self):
        return str(self.id)
