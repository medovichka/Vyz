#ifndef NONCOMERSORG_H
#define NONCOMERSORG_H
#include "organization.h"
#include <string>

class Noncomersorg : public Organization
{
private:
	const std::string purpose;
	const std::string foundingSource;

public:
	Noncomersorg(
		const std::string &name,
		const std::string &inn,
		int employees,
		const std::string &purpose,
		const std::string &foundingSource);

	int payTaxes() override;
	std::string report() override;

	void conductProgram(
		const std::string &programName) override;
	void attractFunding(
		const std::string &source) override;
};
#endif // !NONCOMERSORG_H