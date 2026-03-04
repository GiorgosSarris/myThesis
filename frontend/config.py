"""User authentication configuration"""

USERS = {
    "admin": "admin123",
}

def validate_user(username: str, password: str) -> bool:
    return USERS.get(username) == password
