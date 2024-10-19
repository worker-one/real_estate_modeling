import logging

from app.db.database import get_session
from app.db.models import Item, User
from sqlalchemy.orm import Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def read_user(user_id: int) -> User:
    db: Session = get_session()
    result = db.query(User).filter(User.id == user_id).first()
    db.close()
    return result

def get_user_by_username(username: str) -> User:
    db: Session = get_session()
    result = db.query(User).filter(User.name == username).first()
    db.close()
    return result

def create_user(username: str) -> User:
    db: Session = get_session()
    db_user = User(name=username)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    db.close()
    return db_user

def read_users() -> list[User]:
    db: Session = get_session()
    result = db.query(User).all()
    db.close()
    return result

def delete_user(user_id: int) -> bool:
    db: Session = get_session()
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        db.close()
        return True
    db.close()
    return False

def create_item(user_id: int, title: str, description: str) -> Item:
    db: Session = get_session()
    db_item = Item(owner_id=user_id, title=title, description=description)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    db.close()
    return db_item

def get_user_items(user_id: int) -> list[Item]:
    db: Session = get_session()
    result = db.query(Item).filter(Item.owner_id == user_id).all()
    db.close()
    return result

def delete_item(user_id:int, item_id: int) -> bool:
    db: Session = get_session()
    item = db.query(Item).filter(Item.id == item_id, Item.owner_id == user_id).first()
    if item:
        db.delete(item)
        db.commit()
        db.close()
        return True
    db.close()
    return False
