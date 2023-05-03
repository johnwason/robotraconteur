# minimal_create_service2.py

import RobotRaconteur as RR
RRN=RR.RobotRaconteurNode.s
import threading
import serial
import struct

minimal_create_interface="""
service experimental.minimal_create2

object MinimalCreate
    function void drive(int16 velocity, int16 radius)
end
"""

class create_impl(object):
    def __init__(self, port):
        self._lock=threading.Lock()
        self._serial=serial.Serial(port=port,baudrate=57600)
        dat=struct.pack(">4B",128,132,150, 0)
        self._serial.write(dat)

    def drive(self, velocity, radius):
        with self._lock:
            dat=struct.pack(">B2h",137,velocity,radius)
            self._serial.write(dat)

with RR.ServerNodeSetup("experimental.minimal_create2", 52222):
    #Register the service type
    RRN.RegisterServiceType(minimal_create_interface)

    create_inst=create_impl("/dev/ttyUSB0")

    #Register the service
    RRN.RegisterService("create","experimental.minimal_create2.MinimalCreate",create_inst)

    #Wait for program exit to quit
    input("Press enter to quit")