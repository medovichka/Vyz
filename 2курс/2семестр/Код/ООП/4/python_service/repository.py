from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models import Organization, Employee


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
            if self.model == Employee:
                org_id = data.get("org_id")
                if org_id == 0 or org_id is None:
                    data["org_id"] = None
                    org_id = None

                if org_id:
                    organization = (
                        self.session.query(Organization)
                        .filter(Organization.id == org_id)
                        .first()
                    )
                    if organization:
                        organization.employees_count += 1

            obj = self.model(**data)
            self.session.add(obj)
            self.session.commit()
            self.session.refresh(obj)
            return obj
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

    def update(self, item_id: int, data: dict):
        try:
            obj = self.get_by_id(item_id)
            if not obj:
                return None

            if self.model == Employee:
                old_org_id = obj.org_id
                new_org_id = data.get("org_id")

                if new_org_id == 0:
                    new_org_id = None
                    data["org_id"] = None

                if old_org_id != new_org_id:

                    if old_org_id:
                        old_org = (
                            self.session.query(Organization)
                            .filter(Organization.id == old_org_id)
                            .first()
                        )
                        if old_org:
                            old_org.employees_count = max(
                                0, old_org.employees_count - 1
                            )

                    if new_org_id:
                        new_org = (
                            self.session.query(Organization)
                            .filter(Organization.id == new_org_id)
                            .first()
                        )
                        if new_org:
                            new_org.employees_count += 1

            for key, value in data.items():
                if hasattr(obj, key) and key != "id":
                    setattr(obj, key, value)

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
                if self.model == Employee:
                    if obj.org_id:
                        organization = (
                            self.session.query(Organization)
                            .filter(Organization.id == obj.org_id)
                            .first()
                        )
                        if organization:
                            organization.employees_count = max(
                                0, organization.employees_count - 1
                            )

                self.session.delete(obj)
                self.session.commit()
            return obj
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e