#include "noncomersorg.h"
#include <string>
#include <iostream>

Noncomersorg::Noncomersorg(
	const std::string &name,
	const std::string &inn,
	int employees,
	const std::string &purpose,
	const std::string &foundingSource)
	: Organization(name, inn, employees),
	  purpose(purpose),
	  foundingSource(foundingSource) {}

int Noncomersorg::payTaxes()
{
	return employees * 10;
}

std::string Noncomersorg::report()
{
	std::string result = "Некоммерческая организация: " + name +
						 ", цель: " + purpose +
						 ", сотрудники: " + std::to_string(employees) +
						 ", Источники финансирования: " + foundingSource;
	return result;
}
void Noncomersorg::conductProgram(const std::string &programName)
{
	std::cout << "Программа: " << programName << std::endl;
}

void Noncomersorg::attractFunding(const std::string &source)
{
	std::cout << "Привлечение финансирования из: " << source << std::endl;
}