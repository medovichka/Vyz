using System;
using System.Collections.Generic;
using System.Drawing;
using System.Text;

namespace ConsoleApp1
{   
    public class Car
    {
        private int _id;
        public int Id
        {
            get{ return _id; }
            set{ Console.WriteLine("Иди нафек"); } 
        }

        private string _carName;

        public string CarName {
            get { return _carName; }
            set { _carName = value; }
        }

        private int _speed;

        public int Speed { 
            get { 
                return _speed; } 
            set { 
                if (value < 0)
                {
                    throw new ArgumentOutOfRangeException(
                    nameof(value),
                    "Некорректная скорость."
                  );
                }
                _speed = value; } 
        }

        private string _color;
        public string Color {
            get { return _color; }
            set { _color = value; } 
        }
        public Car(string carName="CarName", int speed=0)
        {
            _carName = carName;
            _speed = speed;
        }
    
        public override string ToString()
        //он не знает как выводить, по дефолту вызывает toString который мы перезаписываем
        {
            
            return $"Название:{_carName};\nСкорость:{_speed};";
        }
        public int speedUp(int deltaV) 
        {
            if (_speed + deltaV < 0)
            {
                throw new ArgumentOutOfRangeException(
                    nameof(deltaV),
                    "Некорректная скорость и/или ускорение."
                  );
            }
            _speed = _speed+deltaV;
            return _speed;
        }
    }
}
