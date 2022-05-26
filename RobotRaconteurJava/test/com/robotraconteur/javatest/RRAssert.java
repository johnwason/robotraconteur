package com.robotraconteur.javatest;

class RRAssert {
    public static void areEqual(Object a, Object b)
    {
        if (a == null && b == null)
        {
            return;
        }
        if (a == null || b == null)
        {
            throw new RuntimeException("Unit test failure");
        }
        if (!a.equals(b))
        {
            throw new RuntimeException("Unit test failure");
        }
    }

    public static void areNotEqual(Object a, Object b)
    {
        if (a == null && b == null)
        {
            throw new RuntimeException("Unit test failure");
        }
        if (a == null || b == null)
        {
            return;
        }
        if (a.equals(b))
        {
            throw new RuntimeException("Unit test failure");
        }
    }

    public static void fail()
    {
        throw new RuntimeException("Unit test failure");
    }

    public static void isTrue(boolean val)
    {
        if (!val)
        {
        throw new RuntimeException("Unit test failure");
        }
    }

    public static void isFalse(boolean val)
    {
        if (val)
        {
        throw new RuntimeException("Unit test failure");
        }
    }
}