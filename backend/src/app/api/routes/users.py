import logging

from fastapi import APIRouter, HTTPException
from app.api import schemas
from app.db import crud

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=schemas.User)
def create_user(user_in: schemas.UserCreate):
    print(user_in)
    user = crud.get_user_by_username(username=user_in.name)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    logger.info(f"Creating user: {user}")
    db_user = crud.create_user(user_in.name)
    return schemas.User(id=db_user.id, name=db_user.name, items=db_user.items)

@router.get("/", response_model=list[schemas.User])
def get_users():
    db_users = crud.read_users()
    users = [
        schemas.User(id=db_user.id, name=db_user.name, items=db_user.items)
        for db_user in db_users
    ]
    return users

@router.get("/{user_id}", response_model=schemas.User)
def get_user(user_in: schemas.UserCreate):
    user = crud.get_user_by_username(username=user_in.name)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    return schemas.User(id=user.id, username=user.name)

@router.delete("/{user_id}", response_model=schemas.Message)
def delete_user(user_id: int):

    # Check if user exists
    db_user = crud.read_user(user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} does not exist.")

    # Delete item
    try:
        crud.delete_user(user_id=user_id)
        return schemas.Message(message=f"User with id {user_id} deleted.")
    except Exception as e:
        logger.error(f"Error deleting User {db_user.name}: {e}")
        raise HTTPException(status_code=500, detail="Error deleting user.")
