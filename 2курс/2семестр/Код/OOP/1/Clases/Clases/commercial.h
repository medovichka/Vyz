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

	Commersorg(
		const std::string &name, 
		const std::string &inn,
		int employees, 
		int revenue, 
		int taxRate);
	Commersorg();
	Commersorg(
		const std::string &name,
		const std::string &inn,
		int employees, 
		int revenue, 
		int taxRate, 
		int subscribers,
		const std::vector<std::string> &socSeti);

	int payTaxes() override;
	std::string report() override;

	void distributeProfit() override;
	bool expandBusiness() override;
};
#endif // !COMERSORG_H
