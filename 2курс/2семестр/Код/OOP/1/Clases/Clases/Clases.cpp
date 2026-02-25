#include <iostream>
#include "commercial.h"
#include "noncomersorg.h"
int main() {
	Organization* komercial_kampaniya_1 = new Commersorg;

	Organization* komercial_kampaniya_2 = new Commersorg(
		"Название2",
		"234567891",
		123,
		100000,
		13);

	Organization* komercial_kampaniya_3 = new Commersorg(
		"Название3",
		"098765432",
		400,
		100000,
		13,
		2000000,
		{"Youtube","Tik TOk"});

	Organization* nekomrecheskaya = new Noncomersorg(
		"Рамашка",
		"16734890",
		123213123123123123,
		"дабро",
		"На велосипеди");

	std::vector<Organization*> ARGANIZATII{ 
		komercial_kampaniya_1,
		komercial_kampaniya_2,
		komercial_kampaniya_3,
		nekomrecheskaya}; //плохо, уникальные поля классов отрезаются
	
	
	std::cout << ARGANIZATII[2]->payTaxes();
	std::cout << "\n";
	std::cout << ARGANIZATII[2]->report();
	std::cout << "\n";
	std::cout << ARGANIZATII[2]->expandBusiness();
	std::cout << "\n";
	ARGANIZATII[2]->distributeProfit();
	for (size_t i = 0; i < ARGANIZATII.size(); i++){
		delete(ARGANIZATII[i]);
	}
	return 0;
}