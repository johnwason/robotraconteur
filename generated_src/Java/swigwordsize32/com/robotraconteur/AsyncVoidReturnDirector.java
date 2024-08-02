/* ----------------------------------------------------------------------------
 * This file was automatically generated by SWIG (https://www.swig.org).
 * Version 4.2.1
 *
 * Do not make changes to this file unless you know what you are doing - modify
 * the SWIG interface file instead.
 * ----------------------------------------------------------------------------- */

package com.robotraconteur;

public class AsyncVoidReturnDirector {
  private transient long swigCPtr;
  protected transient boolean swigCMemOwn;

  protected AsyncVoidReturnDirector(long cPtr, boolean cMemoryOwn) {
    swigCMemOwn = cMemoryOwn;
    swigCPtr = cPtr;
  }

  protected static long getCPtr(AsyncVoidReturnDirector obj) {
    return (obj == null) ? 0 : obj.swigCPtr;
  }

  protected static long swigRelease(AsyncVoidReturnDirector obj) {
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
        RobotRaconteurJavaJNI.delete_AsyncVoidReturnDirector(swigCPtr);
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
    RobotRaconteurJavaJNI.AsyncVoidReturnDirector_change_ownership(this, swigCPtr, false);
  }

  public void swigTakeOwnership() {
    swigCMemOwn = true;
    RobotRaconteurJavaJNI.AsyncVoidReturnDirector_change_ownership(this, swigCPtr, true);
  }

  public void handler(HandlerErrorInfo error) {
    RobotRaconteurJavaJNI.AsyncVoidReturnDirector_handler(swigCPtr, this, HandlerErrorInfo.getCPtr(error), error);
  }

  public AsyncVoidReturnDirector() {
    this(RobotRaconteurJavaJNI.new_AsyncVoidReturnDirector(), true);
    RobotRaconteurJavaJNI.AsyncVoidReturnDirector_director_connect(this, swigCPtr, true, true);
  }

}