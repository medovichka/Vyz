using System;
using System.Collections.Generic;
using System.Text;

namespace Lab2
{
    internal class comorg : organization
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
        public comorg
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

        public override int Taxes()
        {
            return (int)(_profit * 0.2);
        }
        public override string Report()
        {
            return $"Коммерческая организация: {Name}\nИНН: {Inn}\nСотрудников: {Employees}\nПрибыль: {_profit}\nТип бизнеса: {_businessType}";
        }
        public override void Distribute()
        {
            Console.WriteLine($"Распределяем прибыль {_profit} среди акционеров");
        }
    }
}
