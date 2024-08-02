/* ----------------------------------------------------------------------------
 * This file was automatically generated by SWIG (https://www.swig.org).
 * Version 4.2.1
 *
 * Do not make changes to this file unless you know what you are doing - modify
 * the SWIG interface file instead.
 * ----------------------------------------------------------------------------- */

package com.robotraconteur;

public class WrappedServiceSkelAsyncAdapter {
  private transient long swigCPtr;
  private transient boolean swigCMemOwn;

  protected WrappedServiceSkelAsyncAdapter(long cPtr, boolean cMemoryOwn) {
    swigCMemOwn = cMemoryOwn;
    swigCPtr = cPtr;
  }

  protected static long getCPtr(WrappedServiceSkelAsyncAdapter obj) {
    return (obj == null) ? 0 : obj.swigCPtr;
  }

  protected void swigSetCMemOwn(boolean own) {
    swigCMemOwn = own;
  }

  @SuppressWarnings({"deprecation", "removal"})
  protected void finalize() {
    delete();
  }

  public synchronized void delete() {
    if (swigCPtr != 0) {
      if (swigCMemOwn) {
        swigCMemOwn = false;
        RobotRaconteurJavaJNI.delete_WrappedServiceSkelAsyncAdapter(swigCPtr);
      }
      swigCPtr = 0;
    }
  }

  public void makeAsync() {
    RobotRaconteurJavaJNI.WrappedServiceSkelAsyncAdapter_makeAsync(swigCPtr, this);
  }

  public boolean isAsync() {
    return RobotRaconteurJavaJNI.WrappedServiceSkelAsyncAdapter_isAsync(swigCPtr, this);
  }

  public void end(HandlerErrorInfo err) {
    RobotRaconteurJavaJNI.WrappedServiceSkelAsyncAdapter_end__SWIG_0(swigCPtr, this, HandlerErrorInfo.getCPtr(err), err);
  }

  public void end(MessageElement ret, HandlerErrorInfo err) {
    RobotRaconteurJavaJNI.WrappedServiceSkelAsyncAdapter_end__SWIG_1(swigCPtr, this, MessageElement.getCPtr(ret), ret, HandlerErrorInfo.getCPtr(err), err);
  }

}
