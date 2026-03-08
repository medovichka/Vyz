using System;
using System.Collections.Generic;
using System.Text;
namespace Lab2
{
    public abstract class Organization
    {
        private int _id;
        private string _name;
        private string _inn;
        private int _employees;


        public int Id
        {
            get
            {
                return _id;
            }
            protected set { _id = value; }
        }
        public string Name
        {
            get { return _name; }
            set { _name=value; }
        }
        public string Inn
        {
            get { return _inn; }
            set { _inn =value; }
        }
        public int Employees
        {
            get { return _employees; }
            set { _employees = value; }
        }
   
        protected Organization()
        {
            _id = 0;
            _name = "Organization";
            _inn = "1234567890";
            _employees = 0;
        }
        protected Organization(string name, string inn, int employees)
        {
            _id = 0;
            _name = name;
            _inn = inn;
            _employees = employees;
        }
        protected Organization(int id, string name, string inn, int employees)
        {
            _id = id;
            _name = name;
            _inn = inn;
            _employees = employees;
        }




        public abstract int Taxes();
        public abstract string Report();

        public virtual void Distribute() { }
        public virtual void Expand() { }
        public virtual void Program(string program) { }
        public virtual void Attract(string source) { }



        public void Hire()
        {
            _employees++;
            Console.WriteLine($"Наняты новые сотрудники! Всего сотрудников: {_employees}");

        }
        public string Reklama()
        {
            return $"{_name} оч крутая!";
        }
    }
}
