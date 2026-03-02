using System;
using System.Collections.Generic;
using System.Text;

namespace ConsoleApp1
{
    public class ValidationHelper
    {
        public static double Pi;
        static ValidationHelper()
        {
            Pi = 3.14;
        }
        public static void ValidateInt(int value, int left, int right)
        {
            if (value < left || value > right)
            {
                throw new ArgumentOutOfRangeException(
                    nameof(value), "Значение выходит за пределы");
            };
        }
    }
}
