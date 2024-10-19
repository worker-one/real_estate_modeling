import logging

from fastapi import APIRouter, HTTPException
from app.api import schemas
from app.db import crud

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/{user_id}", response_model=schemas.ItemBase)
def create_item(request: schemas.ItemCreate, user_id: int):
    logger.info(f"Creating an item for user {user_id}")

    # Check if user exists
    db_user = crud.read_user(user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} does not exist.")

    # Create item
    db_item = crud.create_item(user_id=user_id, title=request.title, description=request.description)
    return schemas.ItemBase(id=db_item.id, title=db_item.title, description=db_item.description)

@router.get("/{user_id}", response_model=list[schemas.ItemBase])
def read_user_items(user_id: int):
    logger.info(f"Getting items for user {user_id}")

    db_user = crud.read_user(user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} does not exist.")

    # Fetch user items
    db_items = crud.get_user_items(user_id)
    items = [
        schemas.ItemBase(id=db_item.id, title=db_item.title, description=db_item.description)
        for db_item in db_items
    ]
    return items

@router.delete("/{user_id}/{item_id}", response_model=schemas.Message)
def delete_item(user_id: int, item_id: int):
    logger.info(f"Deleting item {item_id} for user {user_id}")

    # Check if user exists
    db_user = crud.read_user(user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} does not exist.")

    # Delete item
    try:
        crud.delete_item(user_id=user_id, item_id=item_id)
        return schemas.Message(message=f"Item with id {item_id} deleted.")
    except Exception as e:
        logger.error(f"Error deleting item: {e}")
        raise HTTPException(status_code=500, detail="Error deleting item.")
