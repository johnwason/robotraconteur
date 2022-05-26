using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using RobotRaconteur;
using System.IO;
using System.Threading.Tasks;

namespace RobotRaconteurNETTest
{
    static class RRAssert
    {
        public static void AreEqual(object a, object b)
        {
            if (!object.Equals(a,b))
            {
                Console.WriteLine("Failure: {0} does not equal {1}", a, b);
                throw new Exception("Unit test failure");
            }
        }

        public static void AreNotEqual(object a, object b)
        {
            if (object.Equals(a, b))
            {
                Console.WriteLine("Failure: {0} does not equal {1}", a, b);
                throw new Exception("Unit test failure");
            }
        }

        public static void Fail()
        {
            throw new Exception("Unit test failure");
        }

        public static void IsTrue(bool val)
        {
            if (!val)
            {
                throw new Exception("Unit test failure");
            }
        }

        public static void IsFalse(bool val)
        {
            if (val)
            {
                throw new Exception("Unit test failure");
            }
        }

        public static void ThrowsException<T>(Action f) where T : Exception
        {
            bool thrown = false;
            try
            {
                f();
            }
            catch(T)
            {
                thrown = true;
            }
            if (!thrown)
            {
                throw new Exception("Unit test failure");
            }
        }

        public static async Task ThrowsExceptionAsync<T>(Func<Task> f) where T : Exception
        {
            bool thrown = false;
            try
            {
                await f();
            }
            catch (T)
            {
                thrown = true;
            }
            if (!thrown)
            {
                throw new Exception("Unit test failure");
            }
        }
    }
}