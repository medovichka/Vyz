#ifndef COMERSORG_H
#define COMERSORG_H

#include "organization.h"
#include <string>
#include <vector>
	
class Commersorg : public Organization
{
private:
	int revenue; //Доходы
	int taxRate; //налогообложение
	int subscribers;
	std::vector<std::string> socSeti;
public:

	//Каструктарыэ
	//1) Обычный
	Commersorg(
		const std::string &name, 
		const std::string &inn,
		int employees, 
		int revenue, 
		int taxRate);
	//2) Предустановленный
	Commersorg();
	//3) Расширенный
	Commersorg(
		const std::string &name,
		const std::string &inn,
		int employees, 
		int revenue, 
		int taxRate, 
		int subscribers,
		const std::vector<std::string> &socSeti);
	// конструктору всё равно нужно заполнить унаследованные классы


	int payTaxes() override; //тож переопр
	std::string report() override;//тож переопр


	void distributeProfit(); //уникальная функция комм
	bool expandBusiness(); //уникальная функция комм

};
#endif // !COMERSORG_H
