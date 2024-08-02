/* ----------------------------------------------------------------------------
 * This file was automatically generated by SWIG (https://www.swig.org).
 * Version 4.2.1
 *
 * Do not make changes to this file unless you know what you are doing - modify
 * the SWIG interface file instead.
 * ----------------------------------------------------------------------------- */

package com.robotraconteur;

public class vectorptr_constantdefinition extends java.util.AbstractList<ConstantDefinition> implements java.util.RandomAccess {
  private transient long swigCPtr;
  protected transient boolean swigCMemOwn;

  protected vectorptr_constantdefinition(long cPtr, boolean cMemoryOwn) {
    swigCMemOwn = cMemoryOwn;
    swigCPtr = cPtr;
  }

  protected static long getCPtr(vectorptr_constantdefinition obj) {
    return (obj == null) ? 0 : obj.swigCPtr;
  }

  protected static long swigRelease(vectorptr_constantdefinition obj) {
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
        RobotRaconteurJavaJNI.delete_vectorptr_constantdefinition(swigCPtr);
      }
      swigCPtr = 0;
    }
  }

  public vectorptr_constantdefinition(ConstantDefinition[] initialElements) {
    this();
    reserve(initialElements.length);

    for (ConstantDefinition element : initialElements) {
      add(element);
    }
  }

  public vectorptr_constantdefinition(Iterable<ConstantDefinition> initialElements) {
    this();
    for (ConstantDefinition element : initialElements) {
      add(element);
    }
  }

  public ConstantDefinition get(int index) {
    return doGet(index);
  }

  public ConstantDefinition set(int index, ConstantDefinition e) {
    return doSet(index, e);
  }

  public boolean add(ConstantDefinition e) {
    modCount++;
    doAdd(e);
    return true;
  }

  public void add(int index, ConstantDefinition e) {
    modCount++;
    doAdd(index, e);
  }

  public ConstantDefinition remove(int index) {
    modCount++;
    return doRemove(index);
  }

  protected void removeRange(int fromIndex, int toIndex) {
    modCount++;
    doRemoveRange(fromIndex, toIndex);
  }

  public int size() {
    return doSize();
  }

  public int capacity() {
    return doCapacity();
  }

  public void reserve(int n) {
    doReserve(n);
  }

  public vectorptr_constantdefinition() {
    this(RobotRaconteurJavaJNI.new_vectorptr_constantdefinition__SWIG_0(), true);
  }

  public vectorptr_constantdefinition(vectorptr_constantdefinition other) {
    this(RobotRaconteurJavaJNI.new_vectorptr_constantdefinition__SWIG_1(vectorptr_constantdefinition.getCPtr(other), other), true);
  }

  public boolean isEmpty() {
    return RobotRaconteurJavaJNI.vectorptr_constantdefinition_isEmpty(swigCPtr, this);
  }

  public void clear() {
    RobotRaconteurJavaJNI.vectorptr_constantdefinition_clear(swigCPtr, this);
  }

  public vectorptr_constantdefinition(int count, ConstantDefinition value) {
    this(RobotRaconteurJavaJNI.new_vectorptr_constantdefinition__SWIG_2(count, ConstantDefinition.getCPtr(value), value), true);
  }

  private int doCapacity() {
    return RobotRaconteurJavaJNI.vectorptr_constantdefinition_doCapacity(swigCPtr, this);
  }

  private void doReserve(int n) {
    RobotRaconteurJavaJNI.vectorptr_constantdefinition_doReserve(swigCPtr, this, n);
  }

  private int doSize() {
    return RobotRaconteurJavaJNI.vectorptr_constantdefinition_doSize(swigCPtr, this);
  }

  private void doAdd(ConstantDefinition x) {
    RobotRaconteurJavaJNI.vectorptr_constantdefinition_doAdd__SWIG_0(swigCPtr, this, ConstantDefinition.getCPtr(x), x);
  }

  private void doAdd(int index, ConstantDefinition x) {
    RobotRaconteurJavaJNI.vectorptr_constantdefinition_doAdd__SWIG_1(swigCPtr, this, index, ConstantDefinition.getCPtr(x), x);
  }

  private ConstantDefinition doRemove(int index) {
    long cPtr = RobotRaconteurJavaJNI.vectorptr_constantdefinition_doRemove(swigCPtr, this, index);
    return (cPtr == 0) ? null : new ConstantDefinition(cPtr, true);
  }

  private ConstantDefinition doGet(int index) {
    long cPtr = RobotRaconteurJavaJNI.vectorptr_constantdefinition_doGet(swigCPtr, this, index);
    return (cPtr == 0) ? null : new ConstantDefinition(cPtr, true);
  }

  private ConstantDefinition doSet(int index, ConstantDefinition val) {
    long cPtr = RobotRaconteurJavaJNI.vectorptr_constantdefinition_doSet(swigCPtr, this, index, ConstantDefinition.getCPtr(val), val);
    return (cPtr == 0) ? null : new ConstantDefinition(cPtr, true);
  }

  private void doRemoveRange(int fromIndex, int toIndex) {
    RobotRaconteurJavaJNI.vectorptr_constantdefinition_doRemoveRange(swigCPtr, this, fromIndex, toIndex);
  }

}