from http.client import HTTPException
from src.common.utils.crud import read, by
from src.common.utils.exceptions import unauthorized
from src.common.models import UserModel
from src.common.schemas.user import *


async def authorize(username: str, password: str) -> User | HTTPException:
    user: User | None = await read(
        UserModel,
        by(UserModel.username, username)
    )
    authorized = user and user.verify_password(password)
    return (
        user
        if authorized
        else unauthorized("User with these credentials does not exist")
    )
