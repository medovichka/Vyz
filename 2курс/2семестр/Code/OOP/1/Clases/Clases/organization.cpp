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
//Сама функция конструктора, которая принимает наме инн сотрудников, со значениями по умол


void Organization::hireEmployee() {
	employees++;
	std::cout << 
		"Наняты новые сотрудники! Всего сотрудников: " 
		<< employees << std::endl;
}//функция найма сотрудника


void Organization::reklama() {
	std::cout << "Реклвма: "+name+" оч крутая";
}