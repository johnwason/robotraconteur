//This file is automatically generated. DO NOT EDIT!
package com.robotraconteur.testing.TestService3;
import java.util.*;
import com.robotraconteur.*;
public class quaternion_stub extends NamedArrayStub<quaternion,double[]> {
    public double[] getNumericArrayFromNamedArrayStruct(quaternion s) {
    return s.getNumericArray();
    }
    public quaternion getNamedArrayStructFromNumericArray(double[] m) {
    quaternion s = new quaternion();
    s.assignFromNumericArray(m,0);
    return s;
    }
    public double[] getNumericArrayFromNamedArray(quaternion[] s) {
    return quaternion.getNumericArray(s);
    }
    public quaternion[] getNamedArrayFromNumericArray(double[] m) {
    quaternion[] s = new quaternion[m.length / 4];
    for (int i=0; i<s.length; i++) s[i] = new quaternion();
    quaternion.assignFromNumericArray(s,m,0);
    return s;
    }
    public String getTypeName() { return "com.robotraconteur.testing.TestService3.quaternion"; }}
