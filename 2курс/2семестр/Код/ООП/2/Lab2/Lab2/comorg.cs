using System;
using System.Collections.Generic;
using System.Text;

namespace Lab2
{
    internal class ComOrg : Organization
    {
        private string _profit;
        private string _businessType;

        public string Profit
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
            string profit,
            string businessType
            ) : base(id,name,inn,employees)
        {
            _profit = profit;
            _businessType = businessType;
        }
        public ComOrg(string name, string inn, int employees, string profit, string businessType)
           : base(name, inn, employees)
        {
            _profit = profit;
            _businessType = businessType;
        }
        public ComOrg() : base("ООО Дылды", "458358238", 5)
        {
            _profit = "100";
            _businessType = "Розничная торговля";
        }




        public override int Taxes()
        {
            if (string.IsNullOrEmpty(_profit))
                return 0;

            if (int.TryParse(_profit, out int profitValue))
            {
                return profitValue * 20 / 100; // 20 % налог с прибыли
            }
            else
            {
                return 0;
            }
        }

        public override string Report()
        {
            return $"Коммерческая организация: {Name}\n" +
                   $"ИНН: {Inn}\n" +
                   $"Сотрудников: {Employees}\n" +
                   $"Прибыль: {_profit}\n" +
                   $"Тип бизнеса: {_businessType}";
        }
        public string ExpandBusiness()
        {
            int.TryParse(_profit, out int profitValue);
            profitValue = profitValue + profitValue * 20;
            return profitValue.ToString();
        }   
        public string Distribute()
        {
            int.TryParse(_profit, out int profitValue);
            profitValue = profitValue / 22 * 3;
            return profitValue.ToString();
        }
    }
}
