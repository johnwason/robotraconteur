/* ----------------------------------------------------------------------------
 * This file was automatically generated by SWIG (https://www.swig.org).
 * Version 4.2.1
 *
 * Do not make changes to this file unless you know what you are doing - modify
 * the SWIG interface file instead.
 * ----------------------------------------------------------------------------- */

package com.robotraconteur;

public class AsyncTimerEventReturnDirector {
  private transient long swigCPtr;
  protected transient boolean swigCMemOwn;

  protected AsyncTimerEventReturnDirector(long cPtr, boolean cMemoryOwn) {
    swigCMemOwn = cMemoryOwn;
    swigCPtr = cPtr;
  }

  protected static long getCPtr(AsyncTimerEventReturnDirector obj) {
    return (obj == null) ? 0 : obj.swigCPtr;
  }

  protected static long swigRelease(AsyncTimerEventReturnDirector obj) {
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
        RobotRaconteurJavaJNI.delete_AsyncTimerEventReturnDirector(swigCPtr);
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
    RobotRaconteurJavaJNI.AsyncTimerEventReturnDirector_change_ownership(this, swigCPtr, false);
  }

  public void swigTakeOwnership() {
    swigCMemOwn = true;
    RobotRaconteurJavaJNI.AsyncTimerEventReturnDirector_change_ownership(this, swigCPtr, true);
  }

  public void handler(TimerEvent ret, HandlerErrorInfo error) {
    RobotRaconteurJavaJNI.AsyncTimerEventReturnDirector_handler(swigCPtr, this, TimerEvent.getCPtr(ret), ret, HandlerErrorInfo.getCPtr(error), error);
  }

  public AsyncTimerEventReturnDirector() {
    this(RobotRaconteurJavaJNI.new_AsyncTimerEventReturnDirector(), true);
    RobotRaconteurJavaJNI.AsyncTimerEventReturnDirector_director_connect(this, swigCPtr, true, true);
  }

}