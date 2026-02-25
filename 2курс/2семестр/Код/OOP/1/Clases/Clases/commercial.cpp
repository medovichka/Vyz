#include "commercial.h"
#include <string>
#include <iostream>
#include <vector>

//Каструктарыэ
//1) Обычный
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

//2) Предустановленный
Commersorg::Commersorg() : 
    Organization("ООО Дылды", "458358238", 5),
    revenue(100),
    taxRate(1),
    subscribers(0),
    socSeti({}) {}
//3) расширенный
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


//Переопределённые
int Commersorg::payTaxes() {
    int taxes = revenue * taxRate / 100;
    return taxes;
}//функция оплаты налогов для организации


std::string Commersorg::report() {
    std::string result = "Коммерческая организация: " + name +
        ", Выручка: " + std::to_string(revenue) +
        ", Сотрудники: " + std::to_string(employees);
    if (!socSeti.empty()) {
        result += ", Соцсети: ";
        for (const auto& social : socSeti) {
            result += social + " ";
        }
    }
    return result;
}//функция отчёта для организации


//Уникальные
bool Commersorg::expandBusiness() {
    subscribers += 10;
    std::cout << "Расширение выполнено! новые подписчики: " << subscribers << std::endl;
    return true;
}//уникальная функция 

void Commersorg::distributeProfit() {
    std::cout << "Бюджет для распределения: " << revenue * 5 << std::endl;
}//функция найма сотрудника