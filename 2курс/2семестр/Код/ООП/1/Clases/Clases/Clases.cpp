#include <iostream>
#include <vector>
#include <memory>
#include "commercial.h"
#include "noncomersorg.h"

int main()
{
    std::vector<std::unique_ptr<Organization>> organizations;

    Commersorg com1("->com1<-", "11111", 10, 500000, 15);
    Noncomersorg com0;

    std::vector<std::string> soceti;
    soceti.push_back("TikTKo");
    soceti.push_back("Youtbe");


    organizations.push_back(std::make_unique<Commersorg>());
    organizations.push_back(std::make_unique<Commersorg>("ООО Ромашка", "12345", 50, 1000000, 20));
    organizations.push_back(std::make_unique<Commersorg>("ООО Ромашка", "12345", 50, 1000000, 20,2000000,soceti));
    organizations.push_back(std::make_unique<Commersorg>(com1));


    organizations.push_back(std::make_unique<Noncomersorg>());
    organizations.push_back(std::make_unique<Noncomersorg>("Фонд Мира", "54321", 15, "Помощь детям", "Пожертвования"));
    organizations.push_back(std::make_unique<Noncomersorg>(com0));

    static_cast<Noncomersorg*>(organizations[2].get())->conductProgram("1");
    //dynamic_cast<Noncomersorg*>(organizations[2].get())->conductProgram("2");

    static_cast<Commersorg*>(organizations[2].get())->distributeProfit();

    static_cast<Noncomersorg*>(organizations[4].get())->conductProgram("Программа");
    static_cast<Noncomersorg*>(organizations[4].get())->attractFunding("Источник");



    //std::cout << com1.report() << std::endl;


    //com1.setRevenue(600000);
    //com1.setEmployees(12);
    //com1.expandBusiness();
    //com1.addSocSeti("VK");
    //com1.addSocSeti("Telegram");


    //std::cout << com1.report() << std::endl;
    //std::cout << "|||||||||||||||||||||||||" << std::endl;
    //com1.expandBusiness();
    //std::cout << std::endl << "/////////////////////////" << std::endl;


    //for (auto org : organizations)
    //{
    //    std::cout << org->report() << std::endl;
    //    std::cout << "Налоги: " << org->payTaxes() << std::endl;
    //    org->hireEmployee();
    //    std::cout << "------------------------" << std::endl;
    //}
    //for (auto org : organizations)
    //{
    //    delete org;
    //}

    return 0;
}