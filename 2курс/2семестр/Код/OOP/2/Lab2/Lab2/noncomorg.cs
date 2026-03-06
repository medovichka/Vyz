using System;
using System.Collections.Generic;
using System.Text;

namespace Lab2
{
    internal class noncomorg : organization
    {
        private string _purpose;
        private string _foundingSource;


        public string Purpose
        {
            get { return _purpose; }
            set { _purpose = value; }
        }
        public string FoundingSource
        {
            get { return _foundingSource; }
            set { _foundingSource = value; }
        }

        public noncomorg(
            int id,
            string name, 
            string inn, 
            int employees, 
            string purpose, 
            string foundingSource
            ) : base(id,name, inn, employees)
        {
            _purpose=purpose;
            _foundingSource=foundingSource;
        }

        public override string Report()
        {
            return $"Некоммерческая организация: {Name}\n" +
                   $"Цель: {_purpose}\n" +
                   $"Источник финансирования: {_foundingSource}";
        }
        public override int Taxes()
        {
            return Employees * 10;
        }
        public override void Program(string program)
        {
            Console.WriteLine($"Программа: {program}");
        }

    } 
}
