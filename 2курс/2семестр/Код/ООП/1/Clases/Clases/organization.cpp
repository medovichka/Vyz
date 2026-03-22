#include "organization.h"
#include <string>
#include <iostream>

Organization::Organization()
    : name("Organization"), inn("1234567890"), employees(0) {}
Organization::Organization(
    const std::string& name,
    const std::string& inn,
    int employees)
    : name(name), inn(inn), employees(employees) {}

Organization::Organization(const Organization& other)
    : name(other.name), inn(other.inn), employees(other.employees) {}

void Organization::hireEmployee(){
    employees++;
    std::cout << "Наняты новые сотрудники! Всего сотрудников: "
        << employees << std::endl;}

void Organization::reklama(){
    std::cout << "Реклама: " + name + " оч крутая";}