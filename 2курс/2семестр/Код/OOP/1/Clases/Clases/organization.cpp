#include "organization.h"
#include <string>
#include <iostream>

Organization::Organization(
	const std::string& name, 
	const std::string& inn,
	int employees) 
	: name(name), 
	  inn(inn), 
	  employees(employees) {}

void Organization::hireEmployee() {
	employees++;
	std::cout << 
		"Наняты новые сотрудники! Всего сотрудников: " 
		<< employees << std::endl;
}

void Organization::reklama() {
	std::cout << "Реклвма: "+name+" оч крутая";
}