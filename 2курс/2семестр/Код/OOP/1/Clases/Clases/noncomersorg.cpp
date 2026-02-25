#include "noncomersorg.h"
#include <string>
#include <iostream>

//Каструктар
Noncomersorg::Noncomersorg(
	const std::string& name,
	const std::string& inn,
	int employees,
	const std::string& purpose,
	const std::string& foundingSource)
	:	Organization(name, inn, employees),
		purpose(purpose),
		foundingSource(foundingSource){}



//Переопределённые
int Noncomersorg::payTaxes() {
	return employees * 10;
};//Переопределяем функцию т.к расчёт другой для неком.
std::string Noncomersorg::report() {
	std::string result = "Некоммерческая организация: " + name +
		", цель: " + purpose +
		", сотрудники: " + std::to_string(employees) +
		", Источники финансирования" + foundingSource;
	return result;
}; //Переопределяем функцию т.к отчёт другой для неком.


// Уникальные функции
void Noncomersorg::conductProgram(std::string& programName) {
	std::cout << "Conducting program: " << programName << std::endl;
}

bool Noncomersorg::attractFunding(std::string& source) {
	std::cout << "Attracting funding from: " << source << std::endl;
	return true;
}
