/* ----------------------------------------------------------------------------
 * This file was automatically generated by SWIG (https://www.swig.org).
 * Version 4.2.1
 *
 * Do not make changes to this file unless you know what you are doing - modify
 * the SWIG interface file instead.
 * ----------------------------------------------------------------------------- */

package com.robotraconteur;

public class ConstantDefinition_StructField {
  private transient long swigCPtr;
  protected transient boolean swigCMemOwn;

  protected ConstantDefinition_StructField(long cPtr, boolean cMemoryOwn) {
    swigCMemOwn = cMemoryOwn;
    swigCPtr = cPtr;
  }

  protected static long getCPtr(ConstantDefinition_StructField obj) {
    return (obj == null) ? 0 : obj.swigCPtr;
  }

  protected static long swigRelease(ConstantDefinition_StructField obj) {
    long ptr = 0;
    if (obj != null) {
      if (!obj.swigCMemOwn)
        throw new RuntimeException("Cannot release ownership as memory is not owned");
      ptr = obj.swigCPtr;
      obj.swigCMemOwn = false;
      obj.delete();
    }
    return ptr;
  }

  @SuppressWarnings({"deprecation", "removal"})
  protected void finalize() {
    delete();
  }

  public synchronized void delete() {
    if (swigCPtr != 0) {
      if (swigCMemOwn) {
        swigCMemOwn = false;
        RobotRaconteurJavaJNI.delete_ConstantDefinition_StructField(swigCPtr);
      }
      swigCPtr = 0;
    }
  }

  public void setName(String value) {
    RobotRaconteurJavaJNI.ConstantDefinition_StructField_Name_set(swigCPtr, this, value);
  }

  public String getName() {
    return RobotRaconteurJavaJNI.ConstantDefinition_StructField_Name_get(swigCPtr, this);
  }

  public void setConstantRefName(String value) {
    RobotRaconteurJavaJNI.ConstantDefinition_StructField_ConstantRefName_set(swigCPtr, this, value);
  }

  public String getConstantRefName() {
    return RobotRaconteurJavaJNI.ConstantDefinition_StructField_ConstantRefName_get(swigCPtr, this);
  }

  public ConstantDefinition_StructField() {
    this(RobotRaconteurJavaJNI.new_ConstantDefinition_StructField(), true);
  }

}