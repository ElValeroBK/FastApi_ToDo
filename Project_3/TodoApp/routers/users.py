# from typing import Annotated
# from pydantic import BaseModel, Field
# from sqlalchemy.orm import Session
# from fastapi import APIRouter, Depends, HTTPException, Path
# from starlette import status
# from models import Users
# from database import SessionLocal
# from .auth import get_current_user
# from passlib.context import CryptContext

# router = APIRouter(
#     prefix='/user',
#     tags=['user']
# )


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# db_dependency = Annotated[Session, Depends(get_db)]
# user_dependency = Annotated[dict, Depends(get_current_user)]
# bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


# class UserVerification(BaseModel):
#     password: str
#     new_password: str = Field(min_length=6)


# @router.get('/', status_code=status.HTTP_200_OK)
# async def get_user(user: user_dependency, db: db_dependency):
#     if user is None:
#         raise HTTPException(status_code=401, detail='Authentication Failed')
#     return db.query(Users).filter(Users.id == user.get('id')).first()


# @router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
# async def change_password(user: user_dependency, db: db_dependency,
#                           user_verification: UserVerification):
#     if user is None:
#         raise HTTPException(status_code=401, detail='Authentication Failed')
#     user_model = db.query(Users).filter(Users.id == user.get('id')).first()

#     if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
#         raise HTTPException(status_code=401, detail='Error on password change')
#     user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
#     db.add(user_model)
#     db.commit()







#-------------------------------------

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from starlette import status
from typing import Annotated
from .auth import get_current_user
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Users
from passlib.context import CryptContext


class PassVerification(BaseModel):
    password : str
    new_password : str = Field(min_length=8)


def get_db():
     db = SessionLocal()
     try:
         yield db
     finally:
         db.close()


router = APIRouter(
    prefix='/users',
    tags=['users']
)

user_dependency = Annotated[dict, Depends(get_current_user)]
db_dependency = Annotated[Session, Depends(get_db)]
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


@router.get('/', status_code=status.HTTP_201_CREATED)
async def get_user(user:user_dependency, db:db_dependency):
    if user == None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail= 'Authentication Failed')    
    return db.query(Users).filter(Users.id == user.get('id')).first()



@router.put('/password', status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user:user_dependency, db:db_dependency,pass_verification:PassVerification):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail= 'Authentication Failed')
    
    db_temporary = db.query(Users).filter(Users.id == user.get('id')).first()

    if not bcrypt_context.verify(db_temporary.hashed_password == pass_verification.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User Unauthorized')
    
    db_temporary.hashed_password = CryptContext.hash(pass_verification.new_password)
    db.add(db_temporary)
    db.commit()



