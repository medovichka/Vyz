#ifndef NONCOMERSORG_H //если не определяли, определяем
#define NONCOMERSORG_H // определяем вот эт
 
#include "organization.h" // нужен класс Organization
#include <string> // нужны строки
//#include <iostream> наверное не надо, поторополися

class Noncomersorg : public Organization // неком. орг. - наследник\дочерний класс класса Organization
{
private: // защищённые штуки класса неком.орг.
	const std::string purpose; //цель орг.
	const std::string foundingSource; // источник финансирования.
public:
	Noncomersorg(
		const std::string& name,
		const std::string& inn,
		int employees,
		const std::string& purpose,
		const std::string& foundingSource);
	// конструктору всё равно нужно заполнить унаследованные поля


	//Переопределённые
	int payTaxes() override;//Переопределяем функцию т.к расчёт другой для неком.
	std::string report() override; //Переопределяем функцию т.к отчёт другой для неком.


	//Уникалные
	void conductProgram(
		std::string& programName);
	bool attractFunding(
		std::string& source);
};
#endif // !NONCOMERSORG_H