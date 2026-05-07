from fastapi import FastAPI, Depends, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Optional, Type, Any
from pydantic import BaseModel

from models import Base, ComOrg, NonComOrg, Employee
from repository import CRUDRepository

DATABASE_URL = "postgresql://postgres:aklsdfjuqh3t92h3gu32h4go8h235giu23hr8g23n08ufg2h394g@localhost/lab4_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI()


class OrgRequest(BaseModel):
    id: int
    type: str


class ComOrgSchema(BaseModel):
    name: str
    inn: str
    profit: str
    business_type: str


class NonComOrgSchema(BaseModel):
    name: str
    inn: str
    purpose: str
    source: str


class EmployeeSchema(BaseModel):
    name: str
    position: str
    org_id: Optional[int] = None


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/api/getOrgEmployees")
def get_org_employees(request: OrgRequest, db: Session = Depends(get_db)):
    if request.type == 'comorgs':
        org_model = ComOrg
    elif request.type == 'noncomorgs':
        org_model = NonComOrg
    else:
        raise HTTPException(status_code=400, detail="Неизвестный тип организации")

    organization = db.query(org_model).filter(org_model.id == request.id).first()
    if not organization:
        raise HTTPException(status_code=404, detail="Организация не найдена")

    employees = db.query(Employee).filter(Employee.org_id == request.id).all()

    return {
        'success': True,
        'orgName': organization.name,
        'employees': [
            {'id': emp.id, 'name': emp.name, 'position': emp.position}
            for emp in employees
        ]
    }


def create_crud_router(
    model: Type[Any], schema: Type[BaseModel], prefix: str, tags: list
) -> APIRouter:
    router = APIRouter(prefix=prefix, tags=tags)

    @router.get("")
    def get_all(db: Session = Depends(get_db)):
        return CRUDRepository(db, model).get_all()

    @router.get("/{item_id}")
    def get_item(item_id: int, db: Session = Depends(get_db)):
        item = CRUDRepository(db, model).get_by_id(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Элемент не найден")
        return item

    @router.post("")
    def create_item(item: schema, db: Session = Depends(get_db)):
        return CRUDRepository(db, model).create(item.dict())

    @router.put("/{item_id}")
    def update_item(item_id: int, item: schema, db: Session = Depends(get_db)):
        repo = CRUDRepository(db, model)
        updated = repo.update(item_id, item.dict())
        if not updated:
            raise HTTPException(status_code=404, detail="Элемент не найден для обновления")
        return updated

    @router.delete("/{item_id}")
    def delete_item(item_id: int, db: Session = Depends(get_db)):
        if not CRUDRepository(db, model).delete(item_id):
            raise HTTPException(status_code=404, detail="Элемент не найден для удаления")
        return {"message": "Deleted"}

    return router


app.include_router(create_crud_router(ComOrg, ComOrgSchema, "/api/comorgs", ["ComOrgs"]))
app.include_router(create_crud_router(NonComOrg, NonComOrgSchema, "/api/noncomorgs", ["NonComOrgs"]))
app.include_router(create_crud_router(Employee, EmployeeSchema, "/api/employees", ["Employees"]))