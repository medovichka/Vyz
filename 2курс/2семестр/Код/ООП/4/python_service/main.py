from fastapi import FastAPI, Depends, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, Type, Any
from pydantic import BaseModel

from models import Base, ComOrg, NonComOrg, Employee

# ПОМЕНЯЙТЕ ДАННЫЕ ДЛЯ ПОДКЛЮЧЕНИЯ
DATABASE_URL = "postgresql://postgres:aklsdfjuqh3t92h3gu32h4go8h235giu23hr8g23n08ufg2h394g@localhost/lab4_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

# --- РЕПОЗИТОРИЙ (Добавлен update) ---
class CRUDRepository:
    def __init__(self, session: Session, model):
        self.session = session
        self.model = model

    def get_all(self): return self.session.query(self.model).all()

    def get_by_id(self, item_id: int):
        return self.session.query(self.model).filter(self.model.id == item_id).first()

    def create(self, data: dict):
        obj = self.model(**data)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def update(self, item_id: int, data: dict):
        obj = self.get_by_id(item_id)
        if obj:
            for key, value in data.items():
                if hasattr(obj, key) and key != 'id': # id не перезаписываем
                    setattr(obj, key, value)
            self.session.commit()
            self.session.refresh(obj)
        return obj

    def delete(self, item_id: int):
        obj = self.get_by_id(item_id)
        if obj:
            self.session.delete(obj)
            self.session.commit()
        return obj

# --- СХЕМЫ PYDANTIC ---
class ComOrgSchema(BaseModel):
    name: str; inn: str; employees_count: int; profit: str; business_type: str

class NonComOrgSchema(BaseModel):
    name: str; inn: str; employees_count: int; purpose: str; source: str

class EmployeeSchema(BaseModel):
    name: str; position: str; org_id: Optional[int] = None

# --- ФАБРИКА РОУТЕРОВ (Добавлены GET /id и PUT /id) ---
def create_crud_router(model: Type[Any], schema: Type[BaseModel], prefix: str, tags: list) -> APIRouter:
    router = APIRouter(prefix=prefix, tags=tags)

    @router.get("")
    def get_all(db: Session = Depends(get_db)):
        return CRUDRepository(db, model).get_all()

    @router.get("/{item_id}")
    def get_item(item_id: int, db: Session = Depends(get_db)):
        item = CRUDRepository(db, model).get_by_id(item_id)
        if not item: raise HTTPException(status_code=404)
        return item

    @router.post("")
    def create_item(item: schema, db: Session = Depends(get_db)):
        return CRUDRepository(db, model).create(item.dict())

    @router.put("/{item_id}")
    def update_item(item_id: int, item: schema, db: Session = Depends(get_db)):
        updated = CRUDRepository(db, model).update(item_id, item.dict())
        if not updated: raise HTTPException(status_code=404)
        return updated

    @router.delete("/{item_id}")
    def delete_item(item_id: int, db: Session = Depends(get_db)):
        if not CRUDRepository(db, model).delete(item_id):
            raise HTTPException(status_code=404)
        return {"message": "Deleted"}

    return router

app.include_router(create_crud_router(ComOrg, ComOrgSchema, "/api/comorgs", ["ComOrgs"]))
app.include_router(create_crud_router(NonComOrg, NonComOrgSchema, "/api/noncomorgs", ["NonComOrgs"]))
app.include_router(create_crud_router(Employee, EmployeeSchema, "/api/employees", ["Employees"]))