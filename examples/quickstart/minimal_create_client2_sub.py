# minimal_create_client2_sub.py

from RobotRaconteur.Client import *
import time

#RRN is imported from RobotRaconteur.Client
#Create a subscription and connect to the default client.

sub=RRN.SubscribeServiceByType('experimental.minimal_create2.MinimalCreate')
obj=sub.GetDefaultClientWait(5)

#The "Create" object reference is now available for use
#Drive for a bit
obj.drive(100,5000)
time.sleep(1)
obj.drive(0,5000)