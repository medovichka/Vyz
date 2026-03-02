using System.Runtime;

namespace ConsoleApp1
{
    internal class Program
    {
        static void Main(string[] args)
        {
            var Jiguli = new Car("Жигули", 12);
            Console.WriteLine(Jiguli);
            Console.WriteLine(ValidationHelper.Pi);
        }
    }
}
