#ifndef ORGANIZATION_H
#define ORGANIZATION_H

#include <string>

class Organization
{
protected:
	const std::string name;
	const std::string inn;
	int employees;

public:
	Organization(
		const std::string &name,
		const std::string &inn,
		int employees);

	virtual int payTaxes() = 0;
	virtual std::string report() = 0;

	virtual void distributeProfit() {}
	virtual void expandBusiness() {}
	virtual void conductProgram(const std::string &programName) {}
	virtual void attractFunding(const std::string &source) {}

	void reklama();
	void hireEmployee();
};

#endif // !ORGANIZATION_H