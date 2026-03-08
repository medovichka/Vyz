#ifndef NONCOMERSORG_H
#define NONCOMERSORG_H

#include "organization.h"
#include <string>

class Noncomersorg : public Organization
{
private:
    std::string purpose;
    std::string foundingSource;

public:
    Noncomersorg();
    Noncomersorg(
        const std::string& name,
        const std::string& inn,
        int employees,
        const std::string& purpose,
        const std::string& foundingSource);
    Noncomersorg(const Noncomersorg& other);



    std::string getPurpose() const {
        return purpose;}
    std::string getFoundingSource() const {
        return foundingSource;}



    void setPurpose(const std::string& newPurpose) {
        purpose = newPurpose;
    }
    void setFoundingSource(const std::string& newSource) {
        foundingSource = newSource;
    }



    int payTaxes() override;
    std::string report() override;
    void conductProgram(const std::string& programName) override;
    void attractFunding(const std::string& source) override;
};

#endif