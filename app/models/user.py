from app.database import query_db
from app.services.auth_service import hash_password, verify_password

class UserModel:
    """Data Access Object for User entities."""

    @staticmethod
    def get_by_id(user_id: int):
        return query_db(
            "SELECT id, full_name, email, phone, role, avatar_url, is_verified, is_active, created_at, updated_at "
            "FROM users WHERE id = %s",
            (user_id,), one=True
        )

    @staticmethod
    def get_by_email(email: str):
        return query_db(
            "SELECT * FROM users WHERE email = %s",
            (email.strip().lower(),), one=True
        )

    @staticmethod
    def create(full_name: str, email: str, password: str, phone: str, role: str = "tenant", avatar_url: str = None):
        email_clean = email.strip().lower()
        password_hash = hash_password(password)
        query = """
            INSERT INTO users (full_name, email, password_hash, phone, role, avatar_url, is_verified, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        user_id = query_db(
            query,
            (full_name.strip(), email_clean, password_hash, phone.strip(), role, avatar_url, False, True),
            commit=True
        )
        return UserModel.get_by_id(user_id)

    @staticmethod
    def authenticate(email: str, password: str):
        user = UserModel.get_by_email(email)
        if not user:
            return None, "No account found with this email address."
        if not user.get("is_active"):
            return None, "Your account has been deactivated. Please contact support."
        if not verify_password(user["password_hash"], password):
            return None, "Invalid password. Please check your credentials."
        return user, None

    @staticmethod
    def update_profile(user_id: int, full_name: str, phone: str, avatar_url: str = None):
        if avatar_url:
            query = "UPDATE users SET full_name = %s, phone = %s, avatar_url = %s WHERE id = %s"
            params = (full_name.strip(), phone.strip(), avatar_url, user_id)
        else:
            query = "UPDATE users SET full_name = %s, phone = %s WHERE id = %s"
            params = (full_name.strip(), phone.strip(), user_id)
        query_db(query, params, commit=True)
        return UserModel.get_by_id(user_id)

    @staticmethod
    def get_all(role_filter=None, limit=50, offset=0):
        if role_filter:
            return query_db(
                "SELECT id, full_name, email, phone, role, is_verified, is_active, created_at "
                "FROM users WHERE role = %s ORDER BY created_at DESC LIMIT %s OFFSET %s",
                (role_filter, limit, offset)
            )
        return query_db(
            "SELECT id, full_name, email, phone, role, is_verified, is_active, created_at "
            "FROM users ORDER BY created_at DESC LIMIT %s OFFSET %s",
            (limit, offset)
        )

    @staticmethod
    def toggle_active(user_id: int, is_active: bool):
        query_db("UPDATE users SET is_active = %s WHERE id = %s", (is_active, user_id), commit=True)
