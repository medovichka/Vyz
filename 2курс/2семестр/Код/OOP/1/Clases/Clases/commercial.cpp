#include "commercial.h"
#include <string>
#include <iostream>
#include <vector>

Commersorg::Commersorg()
    : Organization("ООО Мурат Насыров", "458358238", 5),
    revenue(100),
    taxRate(1),
    subscribers(0),
    socSeti({}) {}
Commersorg::Commersorg(
    const std::string& name,
    const std::string& inn,
    int employees,
    int revenue,
    int taxRate)
    : Organization(name, inn, employees),
    revenue(revenue),
    taxRate(taxRate),
    subscribers(0),
    socSeti({}) {}

Commersorg::Commersorg(
    const std::string& name,
    const std::string& inn,
    int employees,
    int revenue,
    int taxRate,
    int subscribers,
    const std::vector<std::string>& socSeti)
    : Organization(name, inn, employees),
    revenue(revenue),
    taxRate(taxRate),
    subscribers(subscribers),
    socSeti(socSeti) {}

Commersorg::Commersorg(const Commersorg& other)
    : Organization(other),
    revenue(other.revenue),
    taxRate(other.taxRate),
    subscribers(other.subscribers),
    socSeti(other.socSeti) {}

int Commersorg::payTaxes(){
    int taxes = revenue * taxRate / 100;
    return taxes;}

std::string Commersorg::report()
{
    std::string result = "Коммерческая организация: " + getName() +
        ", Выручка: " + std::to_string(revenue) +
        ", Сотрудники: " + std::to_string(getEmployees());
    if (!socSeti.empty())
    {
        result += ", Соцсети: ";
        for (const auto& social : socSeti)
        {
            result += social + " ";
        }
    }
    return result;
}

void Commersorg::expandBusiness(){
    subscribers += 100;
    std::cout << "Расширение выполнено! новые подписчики: " << subscribers;}

void Commersorg::distributeProfit(){
    std::cout << "Бюджет для распределения: " << revenue * 5 << std::endl;}