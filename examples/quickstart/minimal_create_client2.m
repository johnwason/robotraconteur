% minimal_create_client2.m

o=RobotRaconteur.ConnectService('rr+tcp://localhost:52222/?service=create');
o.drive(int16(100),int16(5000));
pause(1);
o.drive(int16(0),int16(0));