/* ----------------------------------------------------------------------------
 * This file was automatically generated by SWIG (https://www.swig.org).
 * Version 4.2.1
 *
 * Do not make changes to this file unless you know what you are doing - modify
 * the SWIG interface file instead.
 * ----------------------------------------------------------------------------- */

package com.robotraconteur;

public class WrappedServiceStubDirector {
  private transient long swigCPtr;
  protected transient boolean swigCMemOwn;

  protected WrappedServiceStubDirector(long cPtr, boolean cMemoryOwn) {
    swigCMemOwn = cMemoryOwn;
    swigCPtr = cPtr;
  }

  protected static long getCPtr(WrappedServiceStubDirector obj) {
    return (obj == null) ? 0 : obj.swigCPtr;
  }

  protected static long swigRelease(WrappedServiceStubDirector obj) {
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
        RobotRaconteurJavaJNI.delete_WrappedServiceStubDirector(swigCPtr);
      }
      swigCPtr = 0;
    }
  }

  protected void swigDirectorDisconnect() {
    swigCMemOwn = false;
    delete();
  }

  public void swigReleaseOwnership() {
    swigCMemOwn = false;
    RobotRaconteurJavaJNI.WrappedServiceStubDirector_change_ownership(this, swigCPtr, false);
  }

  public void swigTakeOwnership() {
    swigCMemOwn = true;
    RobotRaconteurJavaJNI.WrappedServiceStubDirector_change_ownership(this, swigCPtr, true);
  }

  public void dispatchEvent(String EventName, vectorptr_messageelement args) {
    RobotRaconteurJavaJNI.WrappedServiceStubDirector_dispatchEvent(swigCPtr, this, EventName, vectorptr_messageelement.getCPtr(args), args);
  }

  public MessageElement callbackCall(String CallbackName, vectorptr_messageelement args) {
    long cPtr = RobotRaconteurJavaJNI.WrappedServiceStubDirector_callbackCall(swigCPtr, this, CallbackName, vectorptr_messageelement.getCPtr(args), args);
    return (cPtr == 0) ? null : new MessageElement(cPtr, true);
  }

  public WrappedServiceStubDirector() {
    this(RobotRaconteurJavaJNI.new_WrappedServiceStubDirector(), true);
    RobotRaconteurJavaJNI.WrappedServiceStubDirector_director_connect(this, swigCPtr, true, true);
  }

}
