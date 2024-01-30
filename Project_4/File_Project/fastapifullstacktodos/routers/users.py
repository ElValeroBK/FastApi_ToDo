import sys
sys.path.append("..")

from starlette import status
from starlette.responses import RedirectResponse

from fastapi import Depends, APIRouter, Request, Form
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from .auth import get_current_user, verify_password, get_password_hash

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

router = APIRouter(
    prefix="/users",
    tags=["users"],
    
)

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")


def get_db():
    try:
        db=SessionLocal()
        yield db
    finally:
        db.close()


class UserVerification(BaseModel):
    username: str
    password: str
    new_password: str




@router.get("/edit-password",response_class=HTMLResponse)
async def change_password(request:Request):

    user = await get_current_user(request=request)
    if user is None:
        return RedirectResponse("/auth",status_code=status.HTTP_302_FOUND)
    
    return templates.TemplateResponse("edit-user-password.html",{"request": request, "user": user})




@router.post("/edit-password", response_class=HTMLResponse)
async def change_password_commit(request: Request,user_name:str=Form(...),
                                 password: str = Form(...),
                                 new_password:str=Form(...),
                                 db:Session = Depends(get_db)):

    user = await get_current_user(request=request)
    if user is None:
        return RedirectResponse("/auth",status_code=status.HTTP_302_FOUND)
    
    current_user = db.query(models.Users).filter(models.Users.id == user.get("id")).first()

    msg = "User Name or Password incorrect"
    if current_user is not None:
        verify = verify_password(plain_password=password,hashed_password=current_user.hashed_password)
        if verify and user_name == current_user.username:
            current_user.hashed_password = get_password_hash(new_password)
            db.add(current_user)
            db.commit()
            msg = "Password updated"

    
    return templates.TemplateResponse("edit-user-password.html",{"request": request,"user": user, "msg" : msg})
    
    
    
   

