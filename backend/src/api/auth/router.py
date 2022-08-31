from backend.src.common.services.exceptions import unauthorized
from src.common.services.crud import create, read, destroy
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from src.core.config import AuthConfig
from fastapi_jwt_auth import AuthJWT
from src.core.schemas.user import *
from src.core.schemas.token import *
from src.common.utils import authorize
from src.core.models import TokenModel


router = APIRouter(
    tags=['Auth'],
    prefix="/auth",
)


@AuthJWT.load_config
def get_config():
    return AuthConfig()


@router.post('/login', response_model=AccessToken)
async def login(form: OAuth2PasswordRequestForm = Depends(), authorizer: AuthJWT = Depends()):
    user = await authorize(form.username, form.password)

    refresh_token = authorizer.create_refresh_token(subject=user.id)
    access_token = authorizer.create_access_token(subject=user.id)
    jwt_id = authorizer.get_jti(refresh_token)
    refresh_token = RefreshToken(id=jwt_id, user_id=user.id)
    authorizer.set_refresh_cookies(refresh_token)

    token = await read(TokenModel, user.id)
    if token:
        await destroy(TokenModel, token.id)

    await create(TokenModel, **refresh_token.dict())

    return AccessToken(
        access_token=access_token,
        token_type="bearer"
    )


@router.post('/refresh', response_model=AccessToken)
async def refresh(authorizer: AuthJWT = Depends()):
    authorizer.jwt_refresh_token_required()
    user_id = authorizer.get_jwt_subject()
    jwt_id = authorizer.get_raw_jwt()["jti"]

    token = await read(TokenModel, jwt_id)

    if token:
        new_access_token = authorizer.create_access_token(subject=user_id)
        new_refresh_token = authorizer.create_refresh_token(subject=user_id)
        new_jwt_id = authorizer.get_jti(new_refresh_token)
        refresh_token = RefreshToken(id=new_jwt_id, user_id=user_id)
        authorizer.set_refresh_cookies(new_refresh_token)
        await destroy(TokenModel, refresh_token.id)
        await create(TokenModel, **refresh_token.dict())
    else:
        return unauthorized("Invalid refresh token")

    return AccessToken(
        access_token=new_access_token,
        token_type="bearer"
    )


@router.delete('/logout')
async def logout(authorizer: AuthJWT = Depends()):
    authorizer.jwt_refresh_token_required()
    jwt_id = authorizer.get_raw_jwt()["jti"]
    authorizer.unset_refresh_cookies()

    await destroy(TokenModel, jwt_id)

    return {
        "message": "Successfully logout"
    }
