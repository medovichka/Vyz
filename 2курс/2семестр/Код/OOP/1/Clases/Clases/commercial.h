#ifndef COMERSORG_H
#define COMERSORG_H

#include "organization.h"
#include <string>
#include <vector>

class Commersorg : public Organization
{
private:
    int revenue;
    int taxRate;
    int subscribers;
    std::vector<std::string> socSeti;

public:
    Commersorg();
    Commersorg(
        const std::string& name,
        const std::string& inn,
        int employees,
        int revenue,
        int taxRate);
    Commersorg(
        const std::string& name,
        const std::string& inn,
        int employees,
        int revenue,
        int taxRate,
        int subscribers,
        const std::vector<std::string>& socSeti);
    Commersorg(const Commersorg& other);



    int getRevenue() const {
        return revenue;}
    int getTaxRate() const {
        return taxRate;}
    int getSubscribers() const {
        return subscribers;}
    std::vector<std::string> getSocSeti() const {
        return socSeti;}

    void setRevenue(int newRevenue) {
        revenue = newRevenue;}
    void setTaxRate(int newTaxRate) {
        taxRate = newTaxRate;}
    void setSubscribers(int newSubscribers) {
        subscribers = newSubscribers;}
    void setSocSeti(const std::vector<std::string>& newSocSeti) {
        socSeti = newSocSeti;}
    void addSocSeti(const std::string& social) {
        socSeti.push_back(social);}


    int payTaxes() override;
    std::string report() override;
    void distributeProfit() override;
    void expandBusiness() override;
};
#endif