#ifndef ORGANIZATION_H
#define ORGANIZATION_H

#include <string>

class Organization
{
private:
	std::string name;
	std::string inn;
	int employees;

public:
	Organization();
	Organization(const std::string& name, const std::string& inn, int employees);
	Organization(const Organization& other);

	virtual ~Organization() {}
	


	std::string getName() const {
		return name;}  
	std::string getInn() const {
		return inn;}
	int getEmployees() const {
		return employees;}

	void setName(const std::string& newName) {
		name = newName;}
	void setInn(const std::string& newInn) {
		inn = newInn;}
	void setEmployees(int newEmployees) {
		employees = newEmployees;
	}

	virtual int payTaxes() = 0;
	virtual std::string report() = 0;

	void reklama();
	void hireEmployee();
};

#endif // !ORGANIZATION_H