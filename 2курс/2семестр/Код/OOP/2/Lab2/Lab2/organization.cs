using System;
using System.Collections.Generic;
using System.Text;
namespace Lab2
{
    public abstract class organization
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
   
        protected organization(
            int id= 0,
            string name= "Organization",
            string inn="1234567890",
            int employees=0
            )
        {
            _id = id;
            _employees = employees;
            _name = name;
            _inn = inn;

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
        }
        public void Reklama()
        {
            string _dialog = $"{_name} оч крутая!";
        }
    }
}
