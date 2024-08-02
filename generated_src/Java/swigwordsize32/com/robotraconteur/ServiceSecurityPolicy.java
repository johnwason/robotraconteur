/* ----------------------------------------------------------------------------
 * This file was automatically generated by SWIG (https://www.swig.org).
 * Version 4.2.1
 *
 * Do not make changes to this file unless you know what you are doing - modify
 * the SWIG interface file instead.
 * ----------------------------------------------------------------------------- */

package com.robotraconteur;

public class ServiceSecurityPolicy {
  private transient long swigCPtr;
  private transient boolean swigCMemOwn;

  protected ServiceSecurityPolicy(long cPtr, boolean cMemoryOwn) {
    swigCMemOwn = cMemoryOwn;
    swigCPtr = cPtr;
  }

  protected static long getCPtr(ServiceSecurityPolicy obj) {
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
        RobotRaconteurJavaJNI.delete_ServiceSecurityPolicy(swigCPtr);
      }
      swigCPtr = 0;
    }
  }


	static private class WrappedUserAuthenticatorDirectorNET extends WrappedUserAuthenticatorDirector
	{
		IUserAuthenticator target;

		public WrappedUserAuthenticatorDirectorNET(IUserAuthenticator target)
		{
			this.target = target;
		}


		@Override
		public AuthenticatedUser authenticateUser(String username, MessageElement credentials, ServerContext context)
		{
			IUserAuthenticator t = target;
			if (t == null) throw new AuthenticationException("Authenticator internal error");

			java.util.Map<String, Object> c2 = (java.util.Map<String, Object>)RobotRaconteurNode.s().<String, Object>unpackMapType(credentials);

			AuthenticatedUser ret = t.authenticateUser(username, c2, context);
			return ret;

		}

	}

  public ServiceSecurityPolicy(IUserAuthenticator authenticator, java.util.Map<String,String> Policies) {
	 map_strstr Policies2=new map_strstr();
	 for (java.util.Map.Entry<String,String> m : Policies.entrySet())
	 {
		 Policies2.put(m.getKey(), m.getValue());
	 }

	 NativeUserAuthenticator a2;
	 if (authenticator instanceof NativeUserAuthenticator)
	{
		a2= (NativeUserAuthenticator)authenticator;
	}
	else
	{

		WrappedUserAuthenticatorDirectorNET n = new WrappedUserAuthenticatorDirectorNET(authenticator);
		int id = RRObjectHeap.addObject(n);
		WrappedUserAuthenticator a3 = new WrappedUserAuthenticator();
		a3.setRRDirector(n, id);
		a2=a3;

	}

	 swigCPtr=RobotRaconteurJavaJNI.new_ServiceSecurityPolicy(NativeUserAuthenticator.getCPtr(a2), a2, map_strstr.getCPtr(Policies2), Policies2);

  }

  public ServiceSecurityPolicy(NativeUserAuthenticator Authenticator, map_strstr Policies) {
    this(RobotRaconteurJavaJNI.new_ServiceSecurityPolicy(NativeUserAuthenticator.getCPtr(Authenticator), Authenticator, map_strstr.getCPtr(Policies), Policies), true);
  }

}