using System;
using System.Collections.Generic;
using System.Text;

namespace Lab2
{
    internal class ComOrg : Organization
    {
        private int _profit;
        private string _businessType;

        public int Profit
        {
            get { return _profit; }
            set { _profit = value; }
        }
        public string BusinessType
        {
            get { return _businessType; }
            set { _businessType = value; }
        }
        public ComOrg
            (
            int id,
            string name,
            string inn,
            int employees,
            int profit,
            string businessType
            ) : base(id,name,inn,employees)
        {
            _profit = profit;
            _businessType = businessType;
        }
        public ComOrg(string name, string inn, int employees, int profit, string businessType)
           : base(name, inn, employees)
        {
            _profit = profit;
            _businessType = businessType;
        }
        public ComOrg() : base("ООО Дылды", "458358238", 5)
        {
            _profit = 100;
            _businessType = "Розничная торговля";
        }




        public override int Taxes()
        {
            return (int)(_profit * 0.2);
        }
        public override string Report()
        {
            return $"Коммерческая организация: {Name}\n" +
                   $"ИНН: {Inn}\n" +
                   $"Сотрудников: {Employees}\n" +
                   $"Прибыль: {_profit}\n" +
                   $"Тип бизнеса: {_businessType}";
        }
        public void ExpandBusiness()
        {
            Console.WriteLine("Расширение бизнеса...");
        }   
        public override void Distribute()
        {
            Console.WriteLine($"Распределяем прибыль {_profit} среди акционеров");
        }
    }
}
