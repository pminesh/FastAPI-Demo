from ..config import settings
from fastapi import APIRouter, Request, Response, status, Depends, HTTPException
from . import core_models, schemas, utils
from sqlalchemy.orm import Session
from datetime import timedelta, datetime, timezone
from pydantic import EmailStr
from ..database import get_db
from ..config import settings
from .oauth2 import AuthJWT, require_user
from random import randbytes
from .email import Email
import hashlib


router = APIRouter()

ACCESS_TOKEN_EXPIRES_IN = settings.ACCESS_TOKEN_EXPIRES_IN
REFRESH_TOKEN_EXPIRES_IN = settings.REFRESH_TOKEN_EXPIRES_IN

@router.post('/register', status_code=status.HTTP_201_CREATED)
async def create_user(payload: schemas.UserCreate, request: Request, db: Session = Depends(get_db)):
    user_query = db.query(core_models.User).filter(
        core_models.User.email == EmailStr(payload.email.lower()))
    user = user_query.first()
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail='Account already exist')
    # Check if the role exists
    role = db.query(core_models.Role).filter(core_models.Role.id == payload.role_id).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Role not found')

    payload.password = utils.hash_password(payload.password)
    payload.email = EmailStr(payload.email.lower())

    # Create the user
    db_user = core_models.User(**payload.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    try:
        # Send Verification Email
        token = randbytes(10)
        hashedCode = hashlib.sha256()
        hashedCode.update(token)
        verification_code = hashedCode.hexdigest()
        user_query.update(
            {'verification_code': verification_code}, synchronize_session=False)
        db.commit()
        url = f"{request.url.scheme}://{request.client.host}:{request.url.port}/api/auth/verifyemail/{token.hex()}"
        await Email(db_user, url, [payload.email]).sendVerificationCode()
    except Exception as error:
        user_query.update(
            {'verification_code': None}, synchronize_session=False)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='There was an error sending email',
        ) from error
    return {'status': 'success', 'message': 'Verification token successfully sent to your email'}

@router.post('/login')
def login(payload: schemas.LoginUserSchema, response: Response, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    # Check if the user exist
    user = db.query(core_models.User).filter(
        core_models.User.email == EmailStr(payload.email.lower())).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Incorrect Email or Password')

    # Check if the password is valid
    if not utils.verify_password(payload.password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Incorrect Email or Password')

    # Create access token
    access_token = Authorize.create_access_token(
        subject=str(user.id), expires_time=timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN))

    # Create refresh token
    refresh_token = Authorize.create_refresh_token(
        subject=str(user.id), expires_time=timedelta(minutes=REFRESH_TOKEN_EXPIRES_IN))

    # Calculate the expiration time
    access_token_expiration_time = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRES_IN
    )
    refresh_token_expiration_time = datetime.now(timezone.utc) + timedelta(
        minutes=REFRESH_TOKEN_EXPIRES_IN
    )

    # Store refresh and access tokens in cookie
    response.set_cookie('access_token', access_token, expires=access_token_expiration_time, path='/', secure=True, httponly=True, samesite='Lax')
    response.set_cookie('refresh_token', refresh_token, expires=refresh_token_expiration_time, path='/', secure=True, httponly=True, samesite='Lax')
    response.set_cookie('logged_in', 'True', expires=access_token_expiration_time, path='/', secure=True, httponly=True, samesite='Lax')

    # Send both access
    return {'status': 'success', 'access_token': access_token}

@router.get('/logout', status_code=status.HTTP_200_OK)
def logout(response: Response, Authorize: AuthJWT = Depends(), user_id: str = Depends(require_user)):
    Authorize.unset_jwt_cookies()
    # clear cookie
    response.set_cookie('logged_in', '', -1)

    return {'status': 'success'}

@router.get('/verifyemail/{token}')
def verify_me(token: str, db: Session = Depends(get_db)):
    hashedCode = hashlib.sha256()
    hashedCode.update(bytes.fromhex(token))
    verification_code = hashedCode.hexdigest()
    user_query = db.query(core_models.User).filter(
        core_models.User.verification_code == verification_code)
    db.commit()
    user = user_query.first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid code or user doesn't exist")
    if user.verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail='Email can only be verified once')
    user_query.update(
        {'verified': True, 'verification_code': None}, synchronize_session=False)
    db.commit()
    return {
        "status": "success",
        "message": "Account verified successfully"
    }

@router.get('/refresh')
def refresh_token(response: Response, request: Request, Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    try:
        Authorize.jwt_refresh_token_required()

        user_id = Authorize.get_jwt_subject()
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not refresh access token')
        user = db.query(core_models.User).filter(core_models.User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='The user belonging to this token no logger exist')
        access_token = Authorize.create_access_token(
            subject=str(user.id), expires_time=timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN))
    except Exception as e:
        error = e.__class__.__name__
        if error == 'MissingTokenError':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Please provide refresh token',
            ) from e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=error
        ) from e
    
    access_token_expiration_time = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRES_IN
    )
    response.set_cookie('access_token', access_token, expires=access_token_expiration_time, path='/', secure=True, httponly=True, samesite='Lax')
    response.set_cookie('logged_in', 'True', expires=access_token_expiration_time, path='/', secure=True, httponly=True, samesite='Lax')

    return {'access_token': access_token}