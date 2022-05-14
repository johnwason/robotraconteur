//This file is automatically generated. DO NOT EDIT!
package com.robotraconteur.testing.TestService1;
import java.util.*;
import com.robotraconteur.*;
public interface async_testroot extends com.robotraconteur.testing.TestService2.async_baseobj
{
    void async_get_d1(Action2<Double,RuntimeException> rr_handler, int rr_timeout);
    void async_set_d1(double value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_d2(Action2<double[],RuntimeException> rr_handler, int rr_timeout);
    void async_set_d2(double[] value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_d3(Action2<double[],RuntimeException> rr_handler, int rr_timeout);
    void async_set_d3(double[] value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_d4(Action2<double[],RuntimeException> rr_handler, int rr_timeout);
    void async_set_d4(double[] value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_d5(Action2<MultiDimArray,RuntimeException> rr_handler, int rr_timeout);
    void async_set_d5(MultiDimArray value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_d6(Action2<MultiDimArray,RuntimeException> rr_handler, int rr_timeout);
    void async_set_d6(MultiDimArray value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_s1(Action2<Float,RuntimeException> rr_handler, int rr_timeout);
    void async_set_s1(float value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_s2(Action2<float[],RuntimeException> rr_handler, int rr_timeout);
    void async_set_s2(float[] value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_i8_1(Action2<Byte,RuntimeException> rr_handler, int rr_timeout);
    void async_set_i8_1(byte value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_i8_2(Action2<byte[],RuntimeException> rr_handler, int rr_timeout);
    void async_set_i8_2(byte[] value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_u8_1(Action2<UnsignedByte,RuntimeException> rr_handler, int rr_timeout);
    void async_set_u8_1(UnsignedByte value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_u8_2(Action2<UnsignedBytes,RuntimeException> rr_handler, int rr_timeout);
    void async_set_u8_2(UnsignedBytes value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_u8_3(Action2<MultiDimArray,RuntimeException> rr_handler, int rr_timeout);
    void async_set_u8_3(MultiDimArray value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_i16_1(Action2<Short,RuntimeException> rr_handler, int rr_timeout);
    void async_set_i16_1(short value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_i16_2(Action2<short[],RuntimeException> rr_handler, int rr_timeout);
    void async_set_i16_2(short[] value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_u16_1(Action2<UnsignedShort,RuntimeException> rr_handler, int rr_timeout);
    void async_set_u16_1(UnsignedShort value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_u16_2(Action2<UnsignedShorts,RuntimeException> rr_handler, int rr_timeout);
    void async_set_u16_2(UnsignedShorts value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_i32_1(Action2<Integer,RuntimeException> rr_handler, int rr_timeout);
    void async_set_i32_1(int value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_i32_2(Action2<int[],RuntimeException> rr_handler, int rr_timeout);
    void async_set_i32_2(int[] value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_i32_huge(Action2<int[],RuntimeException> rr_handler, int rr_timeout);
    void async_set_i32_huge(int[] value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_u32_1(Action2<UnsignedInt,RuntimeException> rr_handler, int rr_timeout);
    void async_set_u32_1(UnsignedInt value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_u32_2(Action2<UnsignedInts,RuntimeException> rr_handler, int rr_timeout);
    void async_set_u32_2(UnsignedInts value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_i64_1(Action2<Long,RuntimeException> rr_handler, int rr_timeout);
    void async_set_i64_1(long value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_i64_2(Action2<long[],RuntimeException> rr_handler, int rr_timeout);
    void async_set_i64_2(long[] value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_u64_1(Action2<UnsignedLong,RuntimeException> rr_handler, int rr_timeout);
    void async_set_u64_1(UnsignedLong value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_u64_2(Action2<UnsignedLongs,RuntimeException> rr_handler, int rr_timeout);
    void async_set_u64_2(UnsignedLongs value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_str1(Action2<String,RuntimeException> rr_handler, int rr_timeout);
    void async_set_str1(String value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_struct1(Action2<teststruct1,RuntimeException> rr_handler, int rr_timeout);
    void async_set_struct1(teststruct1 value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_struct2(Action2<teststruct2,RuntimeException> rr_handler, int rr_timeout);
    void async_set_struct2(teststruct2 value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_is_d1(Action2<Map<Integer,double[]>,RuntimeException> rr_handler, int rr_timeout);
    void async_set_is_d1(Map<Integer,double[]> value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_is_d2(Action2<Map<String,double[]>,RuntimeException> rr_handler, int rr_timeout);
    void async_set_is_d2(Map<String,double[]> value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_is_d3(Action2<Map<Integer,double[]>,RuntimeException> rr_handler, int rr_timeout);
    void async_set_is_d3(Map<Integer,double[]> value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_is_d4(Action2<Map<String,double[]>,RuntimeException> rr_handler, int rr_timeout);
    void async_set_is_d4(Map<String,double[]> value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_is_d5(Action2<Map<Integer,MultiDimArray>,RuntimeException> rr_handler, int rr_timeout);
    void async_set_is_d5(Map<Integer,MultiDimArray> value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_is_d6(Action2<Map<String,MultiDimArray>,RuntimeException> rr_handler, int rr_timeout);
    void async_set_is_d6(Map<String,MultiDimArray> value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_is_str1(Action2<Map<Integer,String>,RuntimeException> rr_handler, int rr_timeout);
    void async_set_is_str1(Map<Integer,String> value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_is_str2(Action2<Map<String,String>,RuntimeException> rr_handler, int rr_timeout);
    void async_set_is_str2(Map<String,String> value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_is_struct1(Action2<Map<Integer,teststruct2>,RuntimeException> rr_handler, int rr_timeout);
    void async_set_is_struct1(Map<Integer,teststruct2> value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_is_struct2(Action2<Map<String,teststruct2>,RuntimeException> rr_handler, int rr_timeout);
    void async_set_is_struct2(Map<String,teststruct2> value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_struct3(Action2<com.robotraconteur.testing.TestService2.ostruct2,RuntimeException> rr_handler, int rr_timeout);
    void async_set_struct3(com.robotraconteur.testing.TestService2.ostruct2 value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_list_d1(Action2<List<double[]>,RuntimeException> rr_handler, int rr_timeout);
    void async_set_list_d1(List<double[]> value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_list_d3(Action2<List<double[]>,RuntimeException> rr_handler, int rr_timeout);
    void async_set_list_d3(List<double[]> value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_list_d5(Action2<List<MultiDimArray>,RuntimeException> rr_handler, int rr_timeout);
    void async_set_list_d5(List<MultiDimArray> value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_list_str1(Action2<List<String>,RuntimeException> rr_handler, int rr_timeout);
    void async_set_list_str1(List<String> value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_list_struct1(Action2<List<teststruct2>,RuntimeException> rr_handler, int rr_timeout);
    void async_set_list_struct1(List<teststruct2> value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_var1(Action2<Object,RuntimeException> rr_handler, int rr_timeout);
    void async_set_var1(Object value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_var2(Action2<Map<Integer,Object>,RuntimeException> rr_handler, int rr_timeout);
    void async_set_var2(Map<Integer,Object> value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_var_num(Action2<Object,RuntimeException> rr_handler, int rr_timeout);
    void async_set_var_num(Object value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_var_str(Action2<Object,RuntimeException> rr_handler, int rr_timeout);
    void async_set_var_str(Object value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_var_struct(Action2<Object,RuntimeException> rr_handler, int rr_timeout);
    void async_set_var_struct(Object value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_var_vector(Action2<Object,RuntimeException> rr_handler, int rr_timeout);
    void async_set_var_vector(Object value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_var_dictionary(Action2<Object,RuntimeException> rr_handler, int rr_timeout);
    void async_set_var_dictionary(Object value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_var_list(Action2<Object,RuntimeException> rr_handler, int rr_timeout);
    void async_set_var_list(Object value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_var_multidimarray(Action2<Object,RuntimeException> rr_handler, int rr_timeout);
    void async_set_var_multidimarray(Object value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_errtest(Action2<Double,RuntimeException> rr_handler, int rr_timeout);
    void async_set_errtest(double value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_get_nulltest(Action2<teststruct1,RuntimeException> rr_handler, int rr_timeout);
    void async_set_nulltest(teststruct1 value, Action1<RuntimeException> rr_handler, int rr_timeout);
    void async_func1(Action1<RuntimeException> rr_handler,int rr_timeout);
    void async_func2(double d1, double d2,Action1<RuntimeException> rr_handler,int rr_timeout);
    void async_func3(double d1, double d2,Action2<Double,RuntimeException> rr_handler,int rr_timeout);
    void async_meaning_of_life(Action2<Integer,RuntimeException> rr_handler,int rr_timeout);
    void async_func_errtest(Action1<RuntimeException> rr_handler,int rr_timeout);
    void async_func_errtest1(Action1<RuntimeException> rr_handler,int rr_timeout);
    void async_func_errtest2(Action1<RuntimeException> rr_handler,int rr_timeout);
    void async_func_errtest3(Action1<RuntimeException> rr_handler,int rr_timeout);
    void async_o6_op(int op,Action1<RuntimeException> rr_handler,int rr_timeout);
    void async_pipe_check_error(Action1<RuntimeException> rr_handler,int rr_timeout);
    void async_test_callbacks(Action1<RuntimeException> rr_handler,int rr_timeout);
    void async_get_o1(Action2<sub1,RuntimeException> handler, int timeout);
    void async_get_o2(int ind, Action2<sub1,RuntimeException> handler, int timeout);
    void async_get_o3(int ind, Action2<sub1,RuntimeException> handler, int timeout);
    void async_get_o4(String ind, Action2<sub1,RuntimeException> handler, int timeout);
    void async_get_o5(Action2<com.robotraconteur.testing.TestService2.subobj,RuntimeException> handler, int timeout);
    void async_get_o6(Action2<Object,RuntimeException> handler, int timeout);
}
