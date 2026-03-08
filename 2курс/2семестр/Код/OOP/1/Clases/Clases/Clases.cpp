#include <iostream>
#include <vector>
#include <memory>
#include "commercial.h"
#include "noncomersorg.h"

int main()
{
    std::vector<Organization*> organizations;

    organizations.push_back(new Commersorg("ООО Ромашка", "12345", 50, 1000000, 20));
    organizations.push_back(new Commersorg());
    organizations.push_back(new Noncomersorg("Фонд Мира", "54321", 15, "Помощь детям", "Пожертвования"));


    Commersorg com1("->com1<-", "11111", 10, 500000, 15);


    std::cout << com1.report() << std::endl;


    com1.setRevenue(600000);
    com1.setEmployees(12);
    com1.expandBusiness();
    com1.addSocSeti("VK");
    com1.addSocSeti("Telegram");


    std::cout << com1.report() << std::endl;
    std::cout << "|||||||||||||||||||||||||" << std::endl;
    com1.expandBusiness();
    std::cout << std::endl << "/////////////////////////" << std::endl;


    for (auto org : organizations)
    {
        std::cout << org->report() << std::endl;
        std::cout << "Налоги: " << org->payTaxes() << std::endl;
        org->hireEmployee();
        std::cout << "------------------------" << std::endl;
    }
    for (auto org : organizations)
    {
        delete org;
    }

    return 0;
}