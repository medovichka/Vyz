from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Organization(Base):
    __tablename__ = "organizations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    inn = Column(String)

    employees_count = Column(Integer)

    employees = relationship(
        "Employee", back_populates="organization", cascade="all, delete-orphan"
    )


class ComOrg(Organization):
    __tablename__ = "comorganizations"
    id = Column(
        Integer, ForeignKey("organizations.id", ondelete="CASCADE"), primary_key=True
    )
    profit = Column(String)
    business_type = Column(String)


class NonComOrg(Organization):
    __tablename__ = "noncomorganizations"
    id = Column(
        Integer, ForeignKey("organizations.id", ondelete="CASCADE"), primary_key=True
    )
    purpose = Column(String)
    source = Column(String)


class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    position = Column(String)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"))

    organization = relationship("Organization", back_populates="employees")
