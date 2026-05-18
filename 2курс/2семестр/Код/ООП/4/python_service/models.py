from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Organization(Base):
    __tablename__ = "organizations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    inn = Column(String)
    employees_count = Column(Integer, default=0, nullable=False)

    employees = relationship(
        "Employee", back_populates="organization", cascade="all, delete-orphan"
    )

    __mapper_args__ = {
        'polymorphic_identity': 'organization',
        'polymorphic_on': None
    }

    def reklama(self):
        return f"{self.name} оч крутая!"


class ComOrg(Organization):
    __tablename__ = "comorganizations"
    id = Column(
        Integer, ForeignKey("organizations.id", ondelete="CASCADE"), primary_key=True
    )
    profit = Column(String)
    business_type = Column(String)

    __mapper_args__ = {
        'polymorphic_identity': 'comorg'
    }

    def report(self):
        return (f"Коммерческая организация: {self.name} | ИНН: {self.inn} | Прибыль: {self.profit}")

    def expand_business(self):
        try:
            profit_value = int(self.profit)
            profit_value = profit_value + int(profit_value * 0.20)
            return str(profit_value)
        except (ValueError, TypeError):
            return self.profit

    def distribute(self):
        try:
            profit_value = int(self.profit)
            profit_value = profit_value // 22 * 3
            return str(profit_value)
        except (ValueError, TypeError):
            return "0"


class NonComOrg(Organization):
    __tablename__ = "noncomorganizations"
    id = Column(
        Integer, ForeignKey("organizations.id", ondelete="CASCADE"), primary_key=True
    )
    purpose = Column(String)
    source = Column(String)

    __mapper_args__ = {
        'polymorphic_identity': 'noncomorg'
    }

    def report(self):
        return (f"Некоммерческая организация: {self.name} | ИНН: {self.inn} Цельь: {self.purpose} | Источники: {self.source}")

    def program(self, program_name):
        return f"Запускаем программу: {program_name}"

    def attract_funding(self, new_source):
        if not new_source:
            return self.source
        if self.source:
            self.source = f"{self.source}, {new_source}"
        else:
            self.source = new_source
        return self.source


class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    position = Column(String)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"))

    organization = relationship("Organization", back_populates="employees")