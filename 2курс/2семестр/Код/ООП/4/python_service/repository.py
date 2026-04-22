from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError


class CRUDRepository:
    """Универсальный репозиторий для любых моделей SQLAlchemy"""

    def __init__(self, session: Session, model):
        self.session = session
        self.model = model

    def get_all(self):
        return self.session.query(self.model).all()

    def get_by_id(self, item_id: int):
        return self.session.query(self.model).filter(self.model.id == item_id).first()

    def create(self, data: dict):
        try:
            obj = self.model(**data)
            self.session.add(obj)
            self.session.commit()
            self.session.refresh(obj)
            return obj
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

    def delete(self, item_id: int):
        try:
            obj = self.get_by_id(item_id)
            if obj:
                self.session.delete(obj)
                self.session.commit()
            return obj
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
