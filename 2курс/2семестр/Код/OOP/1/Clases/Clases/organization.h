#ifndef ORGANIZATION_H // загружаем 1 раз
#define ORGANIZATION_H // ну типа чё у нас как нызвается

#include <string> // нужны строки для имени и ин

class Organization // класс
{
protected: // только внутри и для друзей
	const std::string name;
	const std::string inn;
	int employees;

public: //дляя всех
	Organization(
		const std::string& name, 
		const std::string& inn, 
		int employees); //конструктор с передаваемыми параметрами
	
	// переопределяемы
	virtual int payTaxes() =0; // виртуальная функция налогов (штука которая есть у класса, но она может быть переопределена у подклассов) /возвращает целое число
	virtual std::string report() =0; //тож самое только функция отчёта /возвращает строку
	
	//общие
	void reklama();
	void hireEmployee();
	//Organization(); нинадда
	//~Organization();нинадда
};
//private: это только внутри класса
//};

//Organization::Organization()
//{ это конструктор
//}

//Organization::~Organization()
//{ это деструктор, мне он не особо нужен кастомный, лучше 
//} просто по умолчанию оставить

#endif // !ORGANIZATION_H