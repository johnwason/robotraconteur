/* ----------------------------------------------------------------------------
 * This file was automatically generated by SWIG (https://www.swig.org).
 * Version 4.2.1
 *
 * Do not make changes to this file unless you know what you are doing - modify
 * the SWIG interface file instead.
 * ----------------------------------------------------------------------------- */

package com.robotraconteur;

public enum RobotRaconteurNodeSetupFlags {
  RobotRaconteurNodeSetupFlags_NONE(0x0),
  RobotRaconteurNodeSetupFlags_ENABLE_NODE_DISCOVERY_LISTENING(0x1),
  RobotRaconteurNodeSetupFlags_ENABLE_NODE_ANNOUNCE(0x2),
  RobotRaconteurNodeSetupFlags_ENABLE_LOCAL_TRANSPORT(0x4),
  RobotRaconteurNodeSetupFlags_ENABLE_TCP_TRANSPORT(0x8),
  RobotRaconteurNodeSetupFlags_ENABLE_HARDWARE_TRANSPORT(0x10),
  RobotRaconteurNodeSetupFlags_LOCAL_TRANSPORT_START_SERVER(0x20),
  RobotRaconteurNodeSetupFlags_LOCAL_TRANSPORT_START_CLIENT(0x40),
  RobotRaconteurNodeSetupFlags_TCP_TRANSPORT_START_SERVER(0x80),
  RobotRaconteurNodeSetupFlags_TCP_TRANSPORT_START_SERVER_PORT_SHARER(0x100),
  RobotRaconteurNodeSetupFlags_DISABLE_MESSAGE4(0x200),
  RobotRaconteurNodeSetupFlags_DISABLE_STRINGTABLE(0x400),
  RobotRaconteurNodeSetupFlags_DISABLE_TIMEOUTS(0x800),
  RobotRaconteurNodeSetupFlags_LOAD_TLS_CERT(0x1000),
  RobotRaconteurNodeSetupFlags_REQUIRE_TLS(0x2000),
  RobotRaconteurNodeSetupFlags_LOCAL_TRANSPORT_SERVER_PUBLIC(0x4000),
  RobotRaconteurNodeSetupFlags_TCP_TRANSPORT_LISTEN_LOCALHOST(0x8000),
  RobotRaconteurNodeSetupFlags_NODENAME_OVERRIDE(0x10000),
  RobotRaconteurNodeSetupFlags_NODEID_OVERRIDE(0x20000),
  RobotRaconteurNodeSetupFlags_TCP_PORT_OVERRIDE(0x40000),
  RobotRaconteurNodeSetupFlags_TCP_WEBSOCKET_ORIGIN_OVERRIDE(0x80000),
  RobotRaconteurNodeSetupFlags_ENABLE_INTRA_TRANSPORT(0x100000),
  RobotRaconteurNodeSetupFlags_INTRA_TRANSPORT_START_SERVER(0x200000),
  RobotRaconteurNodeSetupFlags_TCP_TRANSPORT_IPV4_DISCOVERY(0x400000),
  RobotRaconteurNodeSetupFlags_TCP_TRANSPORT_IPV6_DISCOVERY(0x800000),
  RobotRaconteurNodeSetupFlags_LOCAL_TAP_ENABLE(0x1000000),
  RobotRaconteurNodeSetupFlags_LOCAL_TAP_NAME(0x2000000),
  RobotRaconteurNodeSetupFlags_JUMBO_MESSAGE(0x4000000),
  RobotRaconteurNodeSetupFlags_ENABLE_ALL_TRANSPORTS(0x10001C),
  RobotRaconteurNodeSetupFlags_CLIENT_DEFAULT(0x90004D),
  RobotRaconteurNodeSetupFlags_CLIENT_DEFAULT_ALLOWED_OVERRIDE(0x7D33E5D),
  RobotRaconteurNodeSetupFlags_SERVER_DEFAULT(0xB004AF),
  RobotRaconteurNodeSetupFlags_SERVER_DEFAULT_ALLOWED_OVERRIDE(0x7FFFFFF),
  RobotRaconteurNodeSetupFlags_SECURE_SERVER_DEFAULT(0xB034AF),
  RobotRaconteurNodeSetupFlags_SECURE_SERVER_DEFAULT_ALLOWED_OVERRIDE(0x73FCFFF);

  public final int swigValue() {
    return swigValue;
  }

  public static RobotRaconteurNodeSetupFlags swigToEnum(int swigValue) {
    RobotRaconteurNodeSetupFlags[] swigValues = RobotRaconteurNodeSetupFlags.class.getEnumConstants();
    if (swigValue < swigValues.length && swigValue >= 0 && swigValues[swigValue].swigValue == swigValue)
      return swigValues[swigValue];
    for (RobotRaconteurNodeSetupFlags swigEnum : swigValues)
      if (swigEnum.swigValue == swigValue)
        return swigEnum;
    throw new IllegalArgumentException("No enum " + RobotRaconteurNodeSetupFlags.class + " with value " + swigValue);
  }

  @SuppressWarnings("unused")
  private RobotRaconteurNodeSetupFlags() {
    this.swigValue = SwigNext.next++;
  }

  @SuppressWarnings("unused")
  private RobotRaconteurNodeSetupFlags(int swigValue) {
    this.swigValue = swigValue;
    SwigNext.next = swigValue+1;
  }

  @SuppressWarnings("unused")
  private RobotRaconteurNodeSetupFlags(RobotRaconteurNodeSetupFlags swigEnum) {
    this.swigValue = swigEnum.swigValue;
    SwigNext.next = this.swigValue+1;
  }

  private final int swigValue;

  private static class SwigNext {
    private static int next = 0;
  }
}

