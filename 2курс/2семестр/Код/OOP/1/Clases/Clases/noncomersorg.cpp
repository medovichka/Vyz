#include "noncomersorg.h"
#include <string>
#include <iostream>

Noncomersorg::Noncomersorg()
    : Organization("Фонд добра", "0987654321", 10),
    purpose("Цветы"),
    foundingSource("Гранты") {
}
Noncomersorg::Noncomersorg(
    const std::string& name,
    const std::string& inn,
    int employees,
    const std::string& purpose,
    const std::string& foundingSource)
    : Organization(name, inn, employees),
    purpose(purpose),
    foundingSource(foundingSource) {
}
Noncomersorg::Noncomersorg(const Noncomersorg& other)
    : Organization(other),
    purpose(other.purpose),
    foundingSource(other.foundingSource) {
}



int Noncomersorg::payTaxes()
{
    return getEmployees() * 10;
}

std::string Noncomersorg::report()
{
    std::string result = "Некоммерческая организация: " + getName() +
        ", цель: " + purpose +
        ", сотрудники: " + std::to_string(getEmployees()) +
        ", Источники финансирования: " + foundingSource;
    return result;
}

void Noncomersorg::conductProgram(const std::string& programName)
{
    std::cout << "Программа: " << programName << "| | |Организация:" << getName() << std::endl;
}

void Noncomersorg::attractFunding(const std::string& source)
{
    std::cout << "Привлечение финансирования из: " << source << "| | |Для: " << getName()<< std::endl;
    setFoundingSource(source);}