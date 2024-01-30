from fastapi import FastAPI, Depends, Path, HTTPException
import models
from database import engine, Base,SessionLocal
from routers import auth, todos, admin, users
from starlette import status

from pydantic import BaseModel, Field
from typing import Annotated
from sqlalchemy.orm import Session

app = FastAPI()

Base.metadata.create_all(bind=engine)

# app.include_router(auth.router)
# app.include_router(todos.router)
# app.include_router(admin.router)
# app.include_router(users.router)


class TodoRequest (BaseModel):
    title : str = Field(min_length=3, max_length=10)
    description : str = Field(min_length=3, max_length=20)
    priority : int = Field(gt=0,lt=5)
    complete : bool


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/todos", status_code=status.HTTP_200_OK)
async def read_all(db:Annotated[Session,Depends(get_db)]):
    todo_model =  db.query(models.Todos).all()
    if todo_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no found")
    return todo_model


@app.get("/read_todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(db:Annotated[Session,Depends(get_db)], todo_id: int = Path(gt=0,lt=100)):
    todo_data = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if todo_data is not None:
        return todo_data
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)




@app.post("/todo",status_code=status.HTTP_201_CREATED)
async def add_todo(db:Annotated[Session, Depends(get_db)], todo_request:TodoRequest ):
    db.add(models.Todos(**todo_request.model_dump()))
    db.commit()


@app.put("/todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db:Annotated[Session, Depends(get_db)], todo_request:TodoRequest, todo_id:int = Path(gt=0,lt=100)):
    update_todo = db.query(models.Todos).filter(todo_id == models.Todos.id).first()
    if update_todo is None:
        raise  HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    update_todo.title = todo_request.title
    update_todo.description = todo_request.description
    update_todo.priority = todo_request.priority
    update_todo.complete = todo_request.complete

    db.add(update_todo)
    db.commit()


@app.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delate_todo(db:Annotated[Session,Depends(get_db)], todo_id:int= Path(gt=0)):
    todo_data= db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if todo_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    db.query(models.Todos).filter(models.Todos.id == todo_id).delete()
    db.commit()


