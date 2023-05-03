# minimal_create_client2.py

from RobotRaconteur.Client import *
import time

#RRN is imported from RobotRaconteur.Client
#Connect to the service.
obj=RRN.ConnectService('rr+tcp://localhost:52222/?service=create')

#The "Create" object reference is now available for use
#Drive for a bit
obj.drive(100,5000)
time.sleep(1)
obj.drive(0,5000)