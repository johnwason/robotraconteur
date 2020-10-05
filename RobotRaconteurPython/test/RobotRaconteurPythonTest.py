from __future__ import print_function

import sys
import time
from os import path
import struct
import threading
import os
import traceback
import functools
import codecs
import copy
import numpy

#sys.path.append(r"C:\Users\wasonj\Documents\RobotRaconteur2\bin\out\Python")
#sys.path.append(r"C:\Users\wasonj\Documents\RobotRaconteur2\bin\out\Python\build\lib.win32-2.7")
from RobotRaconteur import *
from RobotRaconteur import RobotRaconteurPythonUtil



try: 
    xrange 
except NameError: 
    xrange = range

try: 
    raw_input
except NameError: 
    raw_input = input
    
try:
    cmp
except NameError:
    cmp = lambda a,b: (a>b) - (a<b)

print(os.getpid())
if '--wait-input' in sys.argv:
    raw_input()

def main():
    
    MultiDimArrayTest.TestDataPath=os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "testing", "testdata")
    
    if (len(sys.argv)>1):
        command=sys.argv[1]
    else:
        command="loopback"

    if (command=="loopback"):

        RobotRaconteurNode.s.SetLogLevelFromEnvVariable()

        t=TcpTransport()
        t.EnableNodeAnnounce()
        t.EnableNodeDiscoveryListening()
        t.StartServer(4564)

        RobotRaconteurNode.s.RegisterServiceTypeFromFile("com.robotraconteur.testing.TestService2")
        RobotRaconteurNode.s.RegisterServiceTypeFromFile("com.robotraconteur.testing.TestService1")        
        RobotRaconteurNode.s.RegisterTransport(t)

        t2=testroot_impl(t)
        context=RobotRaconteurNode.s.RegisterService("RobotRaconteurTestService","com.robotraconteur.testing.TestService1.testroot",t2)
        def scallback(context,code,param):
            print ("Server callback " + str(code) + " " + str(param))
        context.AddServerServiceListener(scallback)
        attributes={"testattribute" : RobotRaconteurVarValue("This is a test attribute","string")}
        context.SetServiceAttributes(attributes)

        t3=testroot_impl(t)
        authdata="testuser1 0b91dec4fe98266a03b136b59219d0d6 objectlock\ntestuser2 841c4221c2e7e0cefbc0392a35222512 objectlock\ntestsuperuser 503ed776c50169f681ad7bbc14198b68 objectlock,objectlockoverride"
        p=PasswordFileUserAuthenticator(authdata)
        policies={"requirevaliduser" : "true", "allowobjectlock" : "true"}
        s=ServiceSecurityPolicy(p,policies)

        RobotRaconteurNode.s.RegisterService("RobotRaconteurTestService_auth","com.robotraconteur.testing.TestService1.testroot",t3,s)


        s=ServiceTestClient();
        s.RunFullTest('rr+tcp://localhost:4564/?service=RobotRaconteurTestService','rr+tcp://localhost:4564/?service=RobotRaconteurTestService_auth')


        RobotRaconteurNode.s.Shutdown()

        time.sleep(1)

        print ("Test completed no errors detected")
        
        return

    if (command=="loopback2"):
        RobotRaconteurNode.s.SetLogLevelFromEnvVariable()
        with RobotRaconteurNodeSetup("com.robotraconteur.testing.test2", 4564, flags=RobotRaconteurNodeSetupFlags_ENABLE_TCP_TRANSPORT | RobotRaconteurNodeSetupFlags_TCP_TRANSPORT_START_SERVER):
        
            RobotRaconteurNode.s.RegisterServiceTypesFromFiles(["com.robotraconteur.testing.TestService2","com.robotraconteur.testing.TestService1", 
                "com.robotraconteur.testing.TestService3"])
                            
            t2=testroot3_impl()
            c = RobotRaconteurNode.s.RegisterService("RobotRaconteurTestService2","com.robotraconteur.testing.TestService3.testroot3",t2)
            c.RequestObjectLock("RobotRaconteurTestService2.nolock_test", "server")
            
            s=ServiceTestClient2();
            s.RunFullTest('rr+tcp://localhost:4564/?service=RobotRaconteurTestService2')

        print ("Test completed no errors detected")
        
        return

    if (command=="loopback3"):
        RobotRaconteurNode.s.SetLogLevelFromEnvVariable()
        with RobotRaconteurNodeSetup("com.robotraconteur.testing.test3", 4567, flags=RobotRaconteurNodeSetupFlags_ENABLE_TCP_TRANSPORT | RobotRaconteurNodeSetupFlags_TCP_TRANSPORT_START_SERVER):
        
            RobotRaconteurNode.s.RegisterServiceTypesFromFiles(["com.robotraconteur.testing.TestService2","com.robotraconteur.testing.TestService1", 
                "com.robotraconteur.testing.TestService3","com.robotraconteur.testing.TestService5"])
                            
            t3=asynctestroot_impl()
            c = RobotRaconteurNode.s.RegisterService("RobotRaconteurTestService3","com.robotraconteur.testing.TestService5.asynctestroot",t3)
                        
            s=ServiceTestClient3();
            s.RunFullTest('rr+tcp://localhost:4567/?service=RobotRaconteurTestService3')

        print ("Test completed no errors detected")
        
        return

    if (command=="client"):
        url1=sys.argv[2]
        url2=sys.argv[3]

        RobotRaconteurNode.s.SetLogLevelFromEnvVariable()

        t=TcpTransport()
        t.EnableNodeDiscoveryListening()

        RobotRaconteurNode.s.RegisterTransport(t)

        t2=LocalTransport()
        RobotRaconteurNode.s.RegisterTransport(t2)
        
        count = 1
        
        if (len(sys.argv) >= 5):
            count=int(sys.argv[4])
        
        for i in xrange(count):
            s=ServiceTestClient();
            s.RunFullTest(url1,url2)

        RobotRaconteurNode.s.Shutdown()

        print ("Test completed no errors detected")
        return

    if (command=="client2"):
        url1=sys.argv[2]
        
        RobotRaconteurNode.s.SetLogLevelFromEnvVariable()

        t=TcpTransport()
        t.EnableNodeDiscoveryListening()

        RobotRaconteurNode.s.RegisterTransport(t)

        t2=LocalTransport()
        RobotRaconteurNode.s.RegisterTransport(t2)
        
                
        s=ServiceTestClient2();
        s.RunFullTest(url1)

        RobotRaconteurNode.s.Shutdown()

        print ("Test completed no errors detected")
        return

    if (command=="server"):

        RobotRaconteurNode.s.SetExceptionHandler(errhandler)
        #MultiDimArrayTest.Test()
        if (sys.argv[2] == "sharer"):
            port = -1
        else:
            port=int(sys.argv[2])
        nodename=(sys.argv[3])

        RobotRaconteurNode.s.SetLogLevelFromEnvVariable()

        RobotRaconteurNode.s.RegisterServiceTypeFromFile("com.robotraconteur.testing.TestService2")
        RobotRaconteurNode.s.RegisterServiceTypeFromFile("com.robotraconteur.testing.TestService1")
        RobotRaconteurNode.s.RegisterServiceTypeFromFile("com.robotraconteur.testing.TestService3")  

        t1=LocalTransport()
        t1.StartServerAsNodeName(nodename)
        RobotRaconteurNode.s.RegisterTransport(t1)

        t=TcpTransport()
        t.EnableNodeAnnounce()
        if (port==-1):
            t.StartServerUsingPortSharer()
        else:
            t.StartServer(port)

        try:
            t.LoadTlsNodeCertificate()
        except:
            traceback.print_exc()
            print ("Could not load TLS certificate")

        RobotRaconteurNode.s.RegisterTransport(t)

        t2=testroot_impl(t)
        RobotRaconteurNode.s.RegisterService("RobotRaconteurTestService","com.robotraconteur.testing.TestService1.testroot",t2)

        t3=testroot_impl(t)
        authdata="testuser1 0b91dec4fe98266a03b136b59219d0d6 objectlock\ntestuser2 841c4221c2e7e0cefbc0392a35222512 objectlock\ntestsuperuser 503ed776c50169f681ad7bbc14198b68 objectlock,objectlockoverride"
        p=PasswordFileUserAuthenticator(authdata)
        policies={"requirevaliduser" : "true", "allowobjectlock" : "true"}
        s=ServiceSecurityPolicy(p,policies)

        RobotRaconteurNode.s.RegisterService("RobotRaconteurTestService_auth","com.robotraconteur.testing.TestService1.testroot",t3,s)

        t4=testroot3_impl()
        c = RobotRaconteurNode.s.RegisterService("RobotRaconteurTestService2","com.robotraconteur.testing.TestService3.testroot3",t4)
        c.RequestObjectLock("RobotRaconteurTestService2.nolock_test", "server")

        print ("Server ready")
        raw_input("Press enter to quit")
        RobotRaconteurNode.s.Shutdown()
        return

    if (command=="findservicebytype"):
        rrtype=sys.argv[2]
        transports=sys.argv[3].split(",")

        RobotRaconteurNode.s.SetLogLevelFromEnvVariable()

        t1=LocalTransport()
        RobotRaconteurNode.s.RegisterTransport(t1)

        t=TcpTransport()
        t.EnableNodeDiscoveryListening()
        RobotRaconteurNode.s.RegisterTransport(t)

        time.sleep(6)

        ret=RobotRaconteurNode.s.FindServiceByType(rrtype,transports)

        for r in ret:
            print_ServiceInfo2(r)

        def printret(ret):
            for r in ret:
                print_ServiceInfo2(r)
        RobotRaconteurNode.s.AsyncFindServiceByType(rrtype,transports,printret,1)

        time.sleep(2)

        return

    if (command=="findnodebyname"):
        rrname=sys.argv[2]
        transports=sys.argv[3].split(",")

        RobotRaconteurNode.s.SetLogLevelFromEnvVariable()
        t1=LocalTransport()
        RobotRaconteurNode.s.RegisterTransport(t1)

        t=TcpTransport()
        t.EnableNodeDiscoveryListening()
        RobotRaconteurNode.s.RegisterTransport(t)

        time.sleep(6)

        ret=RobotRaconteurNode.s.FindNodeByName(rrname,transports)

        for r in ret:
            print_NodeInfo2(r)

        def printret(ret):
            for r in ret:
                print_NodeInfo2(r)
        RobotRaconteurNode.s.AsyncFindNodeByName(rrname,transports,printret,1)

        time.sleep(2)
        return

    if (command=="findnodebyid"):
        RobotRaconteurNode.s.SetLogLevelFromEnvVariable()
        rrid=NodeID(sys.argv[2])
        transports=sys.argv[3].split(",")

        t1=LocalTransport()
        RobotRaconteurNode.s.RegisterTransport(t1)

        t=TcpTransport()
        t.EnableNodeDiscoveryListening()
        RobotRaconteurNode.s.RegisterTransport(t)

        time.sleep(6)

        ret=RobotRaconteurNode.s.FindNodeByID(rrid,transports)

        for r in ret:
            print_NodeInfo2(r)

        def printret(ret):
            for r in ret:
                print_NodeInfo2(r)
        RobotRaconteurNode.s.AsyncFindNodeByID(rrid,transports,printret,1)

        time.sleep(2)
        return

    if (command=="stresstestclient"):
        url=sys.argv[2]

        RobotRaconteurNode.s.SetLogLevelFromEnvVariable()

        RobotRaconteurNode.s.SetExceptionHandler(errhandler)

        t1=LocalTransport()
        RobotRaconteurNode.s.RegisterTransport(t1)

        t=TcpTransport()
        t.EnableNodeDiscoveryListening()
        RobotRaconteurNode.s.RegisterTransport(t)

        servicetest_count=[0]
        servicetest_connectcount=[0]
        servicetest_keepgoing=True

        servicetest_lock=threading.Lock()

        def servicetest1(o, exp):
            if (exp is not None):
                if (servicetest_keepgoing):
                    sys.exit("Got exception: " + str(exp))
            try:
                o.async_func3(1,2,functools.partial(servicetest2,o))
            except Exception as ee:
                if (servicetest_keepgoing):
                    sys.exit("Got exception: " + str(ee))

        def servicetest2(o, d, exp):
            if (exp is not None):
                if (servicetest_keepgoing):
                    sys.exit("Got exception: " + str(exp))
            try:
                o.async_func3(1,2,functools.partial(servicetest2,o))
            except Exception as ee:
                if (servicetest_keepgoing):
                    sys.exit("Got exception: " + str(ee))

        def servicetest3(url1, obj, exp):
            if (exp is not None):
                if (servicetest_keepgoing):
                    sys.exit("Got exception: " + str(exp))
            try:
                RobotRaconteurNode.s.AsyncDisconnectService(obj,functools.partial(servicetest4,url))
            except Exception as ee:
                if (servicetest_keepgoing):
                    sys.exit("Got exception: " + str(ee))

        def servicetest4(url):

            RobotRaconteurNode.s.AsyncConnectService(url,None,None,None,functools.partial(servicetest3,url))

        def servicetest5(p, w, ev):
            try:
                 if (ev.stopped): return
                 p.AsyncSendPacket(servicetest_count[0], lambda pnum, err: None)

                 for i in xrange(100):
                     d = servicetest_count[0] * 100 + i
                     w.OutValue = d

                 servicetest_count[0] += 1
            except:
                 traceback.print_exc()


        def servicetest7(e):
            with servicetest_lock:
                while p.Available > 0:
                    p.ReceivePacket()



        o=RobotRaconteurNode.s.ConnectService(url)
        o.async_func3(1,2,functools.partial(servicetest2,o))

        p=o.broadcastpipe.Connect(-1)
        p.PacketReceivedEvent+=servicetest7
        w=o.broadcastwire.Connect()



        #tt=RobotRaconteurNode.s.CreateTimer(.04,functools.partial(servicetest5,p,w))
        tt=WallTimer(.04,functools.partial(servicetest5,p,w))
        tt.Start()

        print ("Press enter to stop")
        a=raw_input()

        servicetest_keepgoing=False

        tt.Stop()
        RobotRaconteurNode.s.DisconnectService(o)
        RobotRaconteurNode.s.Shutdown()

        return


        tt.stop()

    if (command == "peeridentity"):

        if (len(sys.argv) < 3):
            print ("Usage for peeridentity:  RobotRaconteurTest peeridentity url [nodeid]")
            return

        RRN=RobotRaconteurNode.s
        RRN.SetLogLevelFromEnvVariable()

        url1=sys.argv[2]

        c=TcpTransport()

        if (len(sys.argv)>3):
            id=NodeID(sys.argv[3])

            RRN.NodeID=id

            try:
                c.LoadTlsNodeCertificate()
            except:
                print ("Warning: Could not load node certificate")
        c2=LocalTransport()        
        c4=HardwareTransport()

        RRN.RegisterTransport(c)
        RRN.RegisterTransport(c2)        
        RRN.RegisterTransport(c4)

        o=RRN.ConnectService(url1)

        o.func3(1.0, 2.4)

        if (c.IsTransportConnectionSecure(o)):
            print ("Connection is secure")

            if (c.IsSecurePeerIdentityVerified(o)):
                print ("Peer identity is verified: " + c.GetSecurePeerIdentity(o))
            else:
                print ("Peer identity is not verified")
        return

    if (command == "subscribertest"):
        
        if (len(sys.argv) < 3):
            print ("Usage for subscribertest:  RobotRaconteurTest subscribertest servicetype")
            return
        
        
        RRN=RobotRaconteurNode.s
        RRN.SetLogLevelFromEnvVariable()

        service_type=sys.argv[2]

        c=TcpTransport()
        c.EnableNodeDiscoveryListening()       
        c2=LocalTransport()        
        c2.EnableNodeDiscoveryListening()
        c4=HardwareTransport()

        RRN.RegisterTransport(c)
        RRN.RegisterTransport(c2)        
        RRN.RegisterTransport(c4)
        
        s=RRN.SubscribeServiceByType(service_type)
        def connected(s, client_id, client):
            print ("Client connected: " + str(client_id.NodeID) + "," + client_id.ServiceName)
        def disconnected(s, client_id, client):
            print ("Client disconnected: " + str(client_id.NodeID) + "," + client_id.ServiceName)
        s.ClientConnected += connected
        s.ClientDisconnected += disconnected
        
        def wire_value_changed(s, value, time):
            #print "Wire value changed: " + str(value) + ", " + str(time)
            pass
        
        w=s.SubscribeWire('broadcastwire')
        w.WireValueChanged += wire_value_changed
        
        def pipe_value_changed(s):
            while True:
                (res, p)=s.TryReceivePacket()
                if (not res):
                    break
                print (p)            
        
        p=s.SubscribePipe('broadcastpipe')
        p.PipePacketReceived += pipe_value_changed         
        time.sleep(3)        
        print (s.GetConnectedClients())
        print (w.InValue)

        try_val_res, try_val, try_val_ts = w.TryGetInValue()
        assert try_val_res
        print (try_val)
        
        raw_input("Press enter")
        
        return

    if (command == "subscriberurltest"):
        
        if (len(sys.argv) < 3):
            print ("Usage for subscriberurltest:  RobotRaconteurTest subscriberurltest url")
            return
        
        
        RRN=RobotRaconteurNode.s
        RRN.SetLogLevelFromEnvVariable()

        url=sys.argv[2]

        c=TcpTransport()
        c.EnableNodeDiscoveryListening()       
        c2=LocalTransport()        
        c2.EnableNodeDiscoveryListening()
        c4=HardwareTransport()

        RRN.RegisterTransport(c)
        RRN.RegisterTransport(c2)        
        RRN.RegisterTransport(c4)
        print(url)
        
        s=RRN.SubscribeService(url)
        def connected(s, client_id, client):
            print ("Client connected: " + str(client_id.NodeID) + "," + client_id.ServiceName)
        def disconnected(s, client_id, client):
            print ("Client disconnected: " + str(client_id.NodeID) + "," + client_id.ServiceName)
        def connect_failed(s, client_id, url, err):
            print ("Client connect failed: " + str(client_id.NodeID) + " url: " + str(url) + " error: " + str(err))
        s.ClientConnected += connected
        s.ClientDisconnected += disconnected
        s.ClientConnectFailed += connect_failed
        
        def async_get_handler(obj, err):
            if err is not None:
                print("AsyncGetDefaultClient error: " + str(err))
            else:
                print("AsyncGetDefaultClient success: " + str(obj))

        s.AsyncGetDefaultClient(async_get_handler,1)
        client1 = s.GetDefaultClientWait(6)
        print(s.TryGetDefaultClientWait(6))        
        print(s.GetConnectedClients())
        try:
            print(s.GetDefaultClient().d1)
        except:
            print("Client not connected")
        print(s.TryGetDefaultClient())
        raw_input("Press enter")
        
        return

    if (command == "subscriberfiltertest"):
        
        if (len(sys.argv) < 3):
            print ("Usage for subscriberfiltertest:  RobotRaconteurTest subscriberfiltertest servicetype")
            return
        
        
        RRN=RobotRaconteurNode.s

        service_type=sys.argv[2]

        f=ServiceSubscriptionFilter()
        if (len(sys.argv) >= 4):
            subcommand=sys.argv[3]
            
            if (subcommand == "nodeid"):
                if (len(sys.argv) < 5):
                    raise Exception("Usage for subscriberfiltertest:  RobotRaconteurTest subscriberfiltertest nodeid <nodeid>")
                
                n=ServiceSubscriptionFilterNode()
                n.NodeID=NodeID(sys.argv[4])
                f.Nodes.append(n)
            elif (subcommand == "nodename"):
                if (len(sys.argv) < 5):
                    raise Exception("Usage for subscriberfiltertest:  RobotRaconteurTest subscriberfiltertest nodename <nodename>")
                
                n=ServiceSubscriptionFilterNode()
                n.NodeName=sys.argv[4]
                f.Nodes.append(n)
            elif (subcommand == "nodeidscheme"):
                if (len(sys.argv) < 6):
                    raise Exception("Usage for subscriberfiltertest:  RobotRaconteurTest subscriberfiltertest nodeidscheme <nodeid> <schemes>")
                
                n=ServiceSubscriptionFilterNode()
                n.NodeID=NodeID(sys.argv[4])
                f.Nodes.append(n)
                f.TransportSchemes=sys.argv[5].split(',')
            elif (subcommand == "nodeidauth"):
                if (len(sys.argv) < 7):
                    raise Exception("Usage for subscriberfiltertest:  RobotRaconteurTest subscriberfiltertest nodeidauth <nodeid> <username> <password>")
                
                n=ServiceSubscriptionFilterNode()
                n.NodeID=NodeID(sys.argv[4])
                n.Username=sys.argv[5]
                n.Credentials={'password': RobotRaconteurVarValue(sys.argv[6], 'string')}
                f.Nodes.append(n)
            elif (subcommand == "servicename"):
                if (len(sys.argv) < 5):
                    raise Exception("Usage for subscriberfiltertest:  RobotRaconteurTest subscriberfiltertest servicename <servicename>")                
                f.ServiceNames.append(sys.argv[4])
            
            elif (subcommand == "predicate"):
                
                def pred(serviceinfo):
                    print(serviceinfo.NodeName)
                    return serviceinfo.NodeName == 'testprog'
                
                f.Predicate=pred
            
            else:
                raise Exception("Unknown subscriberfiltertest subcommand")

        c=TcpTransport()
        c.EnableNodeDiscoveryListening()       
        c2=LocalTransport()        
        c2.EnableNodeDiscoveryListening()
        c4=HardwareTransport()

        RRN.RegisterTransport(c)
        RRN.RegisterTransport(c2)        
        RRN.RegisterTransport(c4)
                               
        s=RRN.SubscribeServiceByType(service_type, f)
        def connected(s, client_id, client):
            print ("Client connected: " + str(client_id.NodeID) + "," + client_id.ServiceName)
        def disconnected(s, client_id, client):
            print ("Client disconnected: " + str(client_id.NodeID) + "," + client_id.ServiceName)
        s.ClientConnected += connected
        s.ClientDisconnected += disconnected
        
        raw_input("Press enter")
        
        return
    
    if (command == "serviceinfo2subscribertest"):
        
        if (len(sys.argv) < 3):
            print ("Usage for serviceinfo2subscribertest:  RobotRaconteurTest serviceinfo2subscribertest servicetype")
            return
        
        
        RRN=RobotRaconteurNode.s
        RRN.SetLogLevelFromEnvVariable()

        service_type=sys.argv[2]

        c=TcpTransport()
        c.EnableNodeDiscoveryListening()       
        c2=LocalTransport()        
        c2.EnableNodeDiscoveryListening()
        c4=HardwareTransport()

        RRN.RegisterTransport(c)
        RRN.RegisterTransport(c2)        
        RRN.RegisterTransport(c4)
        
        s=RRN.SubscribeServiceInfo2(service_type)
        def detected(s, client_id, info):
            print ("Service detected: " + str(client_id.NodeID) + "," + client_id.ServiceName + "\n")
        def lost(s, client_id, info):
            print ("Service lost: " + str(client_id.NodeID) + "," + client_id.ServiceName + "\n")
        s.ServiceDetected += detected
        s.ServiceLost += lost
                        
        time.sleep(3)        
        print (s.GetDetectedServiceInfo2())
                
        raw_input("Press enter")
        
        return

    if (command == "nowutc"):
        print(RobotRaconteurNode.s.NowUTC())
        return

    if (command == "testlogging"):
        import datetime
        r = RRLogRecord()
        print(RobotRaconteurNode.s.NodeID)
        r.Node = RobotRaconteurNode.s
        r.Time = datetime.datetime.now()
        r.Level = LogLevel_Warning
        r.Message = "This is a test warning"

        RobotRaconteurNode.s.LogRecord(r)

        print(r)

        return

    if (command == "testloghandler"):
        RRN = RobotRaconteurNode.s
        RRN.SetLogLevel(LogLevel_Debug)
        user_log_handler = UserLogRecordHandler(lambda x : print("python handler: " + str(x)))
        RRN.SetLogRecordHandler(user_log_handler)
        t = TcpTransport()
        t.StartServer(4564)

        RRN.RegisterServiceTypeFromFile("com.robotraconteur.testing.TestService2")
        RRN.RegisterServiceTypeFromFile("com.robotraconteur.testing.TestService1")        
        RRN.RegisterTransport(t)

        t2=testroot_impl(t)
        context=RRN.RegisterService("RobotRaconteurTestService","com.robotraconteur.testing.TestService1.testroot",t2)

        t3=testroot_impl(t)
        authdata="testuser1 0b91dec4fe98266a03b136b59219d0d6 objectlock\ntestuser2 841c4221c2e7e0cefbc0392a35222512 objectlock\ntestsuperuser 503ed776c50169f681ad7bbc14198b68 objectlock,objectlockoverride"
        p=PasswordFileUserAuthenticator(authdata)
        policies={"requirevaliduser" : "true", "allowobjectlock" : "true"}
        s=ServiceSecurityPolicy(p,policies)
        RRN.RegisterService("RobotRaconteurTestService_auth","com.robotraconteur.testing.TestService1.testroot",t3,s)

        s=ServiceTestClient()
        s.RunFullTest('rr+tcp://localhost:4564/?service=RobotRaconteurTestService','rr+tcp://localhost:4564/?service=RobotRaconteurTestService_auth')
        print ("Test completed no errors detected")
        return

    if (command=="server2"):

        node_setup = ServerNodeSetup("testprog", 22222, argv = sys.argv)
        with node_setup:
            RobotRaconteurNode.s.RegisterServiceTypeFromFile("com.robotraconteur.testing.TestService2")
            RobotRaconteurNode.s.RegisterServiceTypeFromFile("com.robotraconteur.testing.TestService1")
            RobotRaconteurNode.s.RegisterServiceTypeFromFile("com.robotraconteur.testing.TestService3")  

            t = node_setup.tcp_transport

            t2=testroot_impl(t)
            RobotRaconteurNode.s.RegisterService("RobotRaconteurTestService","com.robotraconteur.testing.TestService1.testroot",t2)

            t3=testroot_impl(t)
            authdata="testuser1 0b91dec4fe98266a03b136b59219d0d6 objectlock\ntestuser2 841c4221c2e7e0cefbc0392a35222512 objectlock\ntestsuperuser 503ed776c50169f681ad7bbc14198b68 objectlock,objectlockoverride"
            p=PasswordFileUserAuthenticator(authdata)
            policies={"requirevaliduser" : "true", "allowobjectlock" : "true"}
            s=ServiceSecurityPolicy(p,policies)

            RobotRaconteurNode.s.RegisterService("RobotRaconteurTestService_auth","com.robotraconteur.testing.TestService1.testroot",t3,s)

            t4=testroot3_impl()
            c = RobotRaconteurNode.s.RegisterService("RobotRaconteurTestService2","com.robotraconteur.testing.TestService3.testroot3",t4)
            c.RequestObjectLock("RobotRaconteurTestService2.nolock_test", "server")

            print ("Server ready")
            raw_input("Press enter to quit")            
            return

    if (command == "getnumpytype"):
        RobotRaconteurNode.s.RegisterServiceTypeFromFile("com.robotraconteur.testing.TestService2")
        RobotRaconteurNode.s.RegisterServiceTypeFromFile("com.robotraconteur.testing.TestService1")
        RobotRaconteurNode.s.RegisterServiceTypeFromFile("com.robotraconteur.testing.TestService3") 

        RobotRaconteurNode.s.GetNamedArrayDType('com.robotraconteur.testing.TestService3.transform')
        RobotRaconteurNode.s.GetConstants("com.robotraconteur.testing.TestService3")
        RobotRaconteurNode.s.GetPodDType('com.robotraconteur.testing.TestService3.testpod2')
        return


    raise Exception("Unknown test command")

class MultiDimArrayTest(object):

    TestDataPath="."

    
    @staticmethod
    def LoadDoubleArrayFromFile(fname):
        f =open(fname,'rb')
        a = MultiDimArrayTest.LoadDoubleArray(f)
        f.close()
        return a


    @staticmethod
    def LoadDoubleArray(s):
        r = MultiDimArrayTest.BinaryReader(s)
        dimcount = r.ReadInt32()
        dims = [0]*dimcount
        count = 1
        i = 0
        while i < dimcount:
            dims[i] = r.ReadInt32()
            count *= dims[i]
            i += 1       
        real=numpy.zeros((count,))
        i = 0
        while i < count:
            real[i] = r.ReadDouble()
            i += 1
        
        return real.reshape(dims)


    @staticmethod
    def LoadByteArrayFromFile(fname):
        f = open(fname,'rb')
        a = MultiDimArrayTest.LoadByteArray(f)
        f.close()
        return a



    @staticmethod
    def LoadByteArray(s):
        r = MultiDimArrayTest.BinaryReader(s)
        dimcount = r.ReadInt32()
        dims = [0]*dimcount
        count = 1
        i = 0
        while i < dimcount:
            dims[i] = r.ReadInt32()
            count *= dims[i]
            i += 1
        real = numpy.zeros((count,), numpy.uint8)
        i = 0
        while i < count:
            real[i] = r.ReadByte()
            i += 1
        return real.reshape(dims)

    class BinaryReader(object):
        def __init__(self,f):
            self.f=f

        def ReadByte(self):
            dat=self.f.read(1)
            return struct.unpack("<B",dat)[0]

        def ReadInt32(self):
            dat=self.f.read(4)
            return struct.unpack("<i",dat)[0]

        def ReadDouble(self):
            dat=self.f.read(8)
            return struct.unpack("<d",dat)[0]

        def Available(self):
            s=os.fstat(self.f.fileno()).st_size
            return s-self.f.tell()


def ca(a,b):
    if (len(a) != len(b)): raise Exception()
    for i in range(len(a)):
        if (isinstance(a[i],float) and isinstance(b[i],float)):
            d=a[i]
            if (a[i]==0 and b[i]==0): return
            if abs((a[i]-b[i])/a[i])>.001:
                raise Exception()
        else:

            if (a[i] != b[i]):
                print (a[i])
                print (b[i])
                raise Exception()

class ServiceTestClient:
    def __init__(self):

        self._packetnum = 0
        self._ack_recv = False


    def RunFullTest(self, url, authurl):
        self.ConnectService(url)
        self.TestProperties()
        self.TestFunctions()
        self.TestEvents()
        self.TestObjRefs()
        self.TestPipes()
        self.TestCallbacks()
        self.TestWires()
        self.TestMemories()
        self.DisconnectService()
        self.TestAuthentication(authurl)
        self.TestObjectLock(authurl)
        self.TestMonitorLock(url)
        self.TestAsync(authurl)


    def ConnectService(self, url):
        def client_listener(c, event_type, p):
            print("Client event: " + str(event_type) + " param: " + str(p))
        self._r = RobotRaconteurNode.s.ConnectService(url, None, None, client_listener)
        attributes=RobotRaconteurNode.s.GetServiceAttributes(self._r)
        print (attributes)

    def DisconnectService(self):
        RobotRaconteurNode.s.DisconnectService(self._r)

    def TestProperties(self):
        self._r.d1 = 3.456
        if self._r.d1 != 12.345:
            raise Exception()
        self._r.d2 = [8.805544e-12, 3.735066e+12, 3.491919e+17, 4.979833e+12, -4.042302e+00, 2.927731e-12, 5.945355e+11, -3.965351e+06, 4.866934e-14, 1.314597e+04, -2.059923e-11, -5.447989e-20, 1.267732e-21, -2.603983e+10, 2.417961e+03, 3.515469e-16, 1.731329e-01, -2.854408e-04, 2.908090e-06, 3.354746e+08, 9.405914e+05, -3.665276e-01, -2.036897e+02, 3.489765e-01, -3.207702e+11, -2.105708e+18, -1.485891e+13, -7.059704e+04, 3.528381e+11, 4.586056e+02, -8.107050e-16, -1.007106e+09, 2.964453e+05, -3.628810e+05, -2.816870e-14, 5.665387e+09, 8.518736e+11, -1.179981e+12, -1.506569e-21, 1.113076e-06, -4.782847e+06, 8.906463e+17, 2.729604e+03, -3.430604e+16, 2.626956e-07, 1.543395e+15, 3.407777e-21, 1.231519e+06, -4.808410e+16, 2.649811e+10, 2.546524e+01, -3.533472e-13, -3.732759e+04, 1.951505e-20, 9.338953e-21, -1.627672e-04, 1.807084e-19, -4.489206e-17, -2.654284e+08, -2.136947e+16, -3.690031e+09, 3.372245e-14, 4.946361e-11, -1.330965e-01, 2.479789e-17, 2.750331e-18, -4.301452e-03, 3.895091e+19, 2.515863e+13, 6.879298e+12, -2.925884e-15, -2.826248e+00, -4.864526e-06, 2.614765e+00, 4.488816e-19, 2.231337e+15, -7.004595e+07, 2.506835e-08, -2.187450e-02, -2.220025e-07, 1.688346e+02, 8.125250e-07, -4.819391e+10, -1.643306e-14, -4.768222e-18, -4.472162e-16, 2.487563e-01, -3.924904e-15, -1.186331e+06, 2.397369e+01, -3.137448e-02, 1.016507e+06, 2.584749e-16, 8.212180e-08, 1.631561e-12, -4.927066e-08, 1.448920e-14, -4.371505e+03, 2.050871e-21, 2.523287e+01, 7.778552e-05, -4.437786e+18, -1.118552e-07, -3.543717e-09, -5.327587e-07, -1.083197e-17, 2.578295e-10, -4.952430e-12, -3.008597e-13, 3.010829e+01, -6.109332e+09, -2.428341e-03, 9.399191e-01, -4.827230e-06, 1.013860e+10, -2.870341e-20, 4.281756e+11, 1.043519e-09, 2.378027e+06, 2.605309e+09, -4.939600e-04, -2.193966e+08, 4.022755e-03, 2.668705e-09, -1.087393e-18, 1.927676e-12, -1.694835e+10, 3.554035e-03, -1.299796e+01, -1.692862e+07, 2.818156e+07, -2.606821e-13, 1.629588e-15, -7.069991e-16, 1.205863e-19, 2.491209e-17, -3.757951e+04, 3.110266e-04, -4.339472e+11, -3.172428e+02, 1.579905e+09, 2.859499e-01, 4.241852e-06, 2.043341e-09, 2.922865e-16, -2.580974e+01, -3.147566e-02, 1.160590e+03, -2.238096e+01, -1.984601e-13, 2.636096e-03, 8.422872e-04, 2.026040e-16, -3.822500e+01, -2.190513e-18, 3.229839e-11, -2.958164e+06, -8.354021e+11, 3.625367e+08, -4.558085e-01, 1.274325e+04, -2.492750e+05, 3.739269e+18, -3.985407e-03, 3.575816e-13, 1.376847e+06, -6.682659e-20, -9.200014e+08, -2.278973e+10, -3.555184e-04, 3.821512e-10, 5.944167e+07, -2.576511e-15, 1.232459e+02, -3.187831e+02, -4.882568e+12, -1.670486e+05, -2.339878e-20, -4.985496e-16, -2.937093e+17, 8.981723e-06, -5.460686e-04, 1.090528e-11, -4.321598e+17, -3.577227e-08, 2.880194e+01, -4.277921e+00, -4.145678e-02, 4.930810e+08, -4.525745e-21, 4.648764e+07, -2.564920e+16, 1.075546e+01, 3.777591e-18, 1.419816e-08, 1.419490e+10, 1.479453e-19, -4.933130e+13, 4.580471e+15, -3.160785e+02, -2.885209e+06, 2.384424e-03, 1.030777e-12, 2.652784e+04, 4.435144e+10, 3.102484e+17, 4.725294e+11, -3.817788e-04, 4.074841e-01, -7.248042e-13, -4.502531e-08, 2.203521e+01, -4.457124e+01, -2.961745e+06, -3.237080e+14, -3.482497e-19, 1.534088e+05, 4.759060e-14, 2.333791e+04, -4.002051e-03, 3.278553e-06, -2.307217e+13, -2.999411e+19, -9.804484e+02, -1.793367e+01, 3.111735e+07, -4.457329e+10, -2.067659e-13, -5.927573e+03, 6.979879e+10, 3.556110e-06, -3.513094e-13, 1.128057e+19, 4.199038e+13, 7.553080e-20, 4.380028e-11, -2.502103e-19, 5.943049e+15, -1.266134e-10, 4.825578e-09, -2.778134e-16, 1.881866e-10, -3.677556e+08, -2.166345e-10, 3.919158e+05, 2.778912e-07, 1.822489e-05, 1.513496e-01, 9.327925e+05, -4.050132e-14, 3.311913e+01, 9.290544e+15, 1.302267e+03, -1.252080e+17, -4.208811e-04, -3.225464e+16, 2.093787e+16, -3.352116e+07, 4.797665e+15, -1.539672e-17, 4.835159e+04, 2.446236e-07, 2.355328e-17, 2.044244e-12, 3.210415e-11, -1.322741e+16, 5.538184e-14, -4.612046e-05, 4.758939e+15, -2.038208e-10, -2.451148e+18, -2.699711e-19, -2.019804e-09, 5.631634e-13, -2.288031e+05, -3.211488e+12, 7.511869e+13, -3.209453e-09, 3.806128e-18, 4.025006e-14, -1.700945e-10, 4.136280e-13, 4.517870e-04, 2.739233e+11, -3.736057e-03, 2.255379e-20, 3.122584e-16, 3.192660e-18, 4.765755e-09, 2.396494e-13, 1.625326e+02, -3.413821e-18, 3.627586e+10, 8.708108e+07, 2.244241e-09, 3.718827e-02, 1.803394e-18, 4.377806e-04, 1.593155e-04, -2.886859e+19, 2.446955e-06, 4.714172e-07, -1.444181e+14, 5.921228e-22, -3.968436e+05, 2.081487e+08, 4.200042e+18, -1.334353e-20, 1.637913e+12, -7.203262e+03, 3.510359e+09, 5.945107e-08, 2.798793e-07, 1.819020e+17, -1.331690e+02, -2.714485e+18, -2.344350e-18, -1.313232e-20, -6.739364e-22, 1.025007e-02, 1.186976e+07, -1.412268e+09, -6.194861e-18, -4.523625e-03, -4.504270e-06, 2.158726e-21, -8.330465e-17, 4.566938e+11, 6.677905e-05, -2.312717e-13, 5.325983e+16, -1.075392e-04, 1.140532e-13, 2.606136e-11, -2.815243e+16, -3.550714e-16, -1.033372e+05, -1.183041e+03, -7.872171e-21, -4.362058e-07, -3.181126e-07, -2.676671e+18, -2.674920e-15, -3.991169e-16, -4.401799e+07, -2.826847e-10, -2.033266e-20, -5.669789e-11, 3.711339e+05, -1.194584e-17, -3.310173e+10, -1.743331e-15, -2.288755e+15, 8.610375e+06, 4.796813e+07, -1.465344e+07, -4.074823e-12, 2.089962e-21, -4.171761e-18, -4.682371e+18, 4.030447e+08, 4.679856e-07, -2.662732e+15, 2.551805e-21, 2.482089e+05, -2.310281e-10, 3.533837e-08, 1.829437e-07, 3.074466e-06, -2.889997e-12, -4.203806e+01, 1.598374e-21, -1.300526e-05, 2.921093e+14, -8.847920e+14, 3.788583e-04, -4.538453e+19, -2.734893e+07, 1.351281e-04, 1.128593e-01, 3.868545e+13, -1.200438e+18, -2.641822e+10, -4.493835e-16, -6.291094e-13, 2.534337e-08, -4.063653e-03, 3.200675e-02, 2.243642e+08, 5.170843e-08, 8.984841e-14, 2.228243e-01, -6.770559e-09, 3.513375e-16, -2.512038e-14, 3.421696e+04, -4.514522e+01, -1.062799e-20, 2.853168e-19, 8.503515e-21, -1.664790e-03, -2.515606e-18, 1.237958e-21, -8.059224e-20, 4.386086e+00, 5.301466e+17, 4.388106e-12, -3.432129e+00, 2.189230e+18, -1.806446e-02, 3.266789e-18, 3.355664e-13, -1.206966e-21, -4.813560e-02, -1.352049e+18, 1.257234e-07, 2.511470e-09, -2.512775e-01, 3.613773e-10, -9.065202e+16, -1.777852e+18, 1.444606e-01, -2.857379e+00, -1.912993e+00, 3.436817e-09, -1.749039e+14, 2.215154e-18, 3.384923e+18, -4.513038e-09, 4.814904e+05, 3.730911e+15, 1.861706e+12, 3.378290e-03, 2.851468e-06, -1.577518e-04, -4.122504e-12, -2.743002e+03, 8.512568e-02, -1.333039e-09, -4.899609e-17, -1.782085e-11, 2.552482e-02, 4.200193e+10, -4.298147e+03, -1.923210e-10, -1.208889e+01, 4.606772e-21, -3.331241e+10, -3.704566e-16, -3.733178e-20, -4.950049e+16, 3.184384e+15, -4.107375e-06, 1.801875e+09, 9.632951e-16, 7.172728e-10, 2.324621e+07, 2.892586e+15, -1.582511e-17, -4.119044e-13, -1.248361e+09, 1.531907e+08, -1.795628e-19, -1.735919e-17, -4.646689e-07, -2.779304e-11, 8.048984e-10, 3.536087e-02, -6.494880e+18, 2.714073e+06, 3.374557e+18, 3.621468e-06, 2.742652e-07, 2.551176e+03, -4.420578e+18, -4.370624e-08, -4.507765e-11, 4.193746e-20, 1.206645e+13, -3.750231e+03, 4.390893e+08, -9.756466e+11, 3.392778e-06, -3.453465e+01, -1.406102e+11, -3.673526e-15, 1.417082e-03, 1.499926e+16, -4.471032e-17, -2.657920e+16, 4.792261e+09, -3.212735e+17, -3.372737e-05, -4.730048e+01, 3.365478e+07, 2.835695e+13, -3.242022e-07, 3.640288e+11, 1.862055e-08, -4.121250e-19, -3.891100e-02, -4.367058e-15, 1.364067e-17, -4.575429e-12, 3.621347e-07, 1.506864e+11, 3.715065e+18, -1.773352e+08, -3.502359e+07, -2.326890e-04, 2.948814e-17, -2.438988e+14, -2.994787e+04, -3.755515e+12, 2.708013e-13, 3.281046e-01, -3.710727e+12, -8.380304e+14, 1.062737e-05, 2.385939e+16, -4.383210e-20, -3.779417e+03, 3.080324e-03, 3.810188e+16, 3.058415e+00, -2.484879e-21, -1.951684e+01, 6.979033e-10, -3.866994e+06, 4.278936e-19, 9.365131e+10, -3.685205e+01, -2.678752e-16, 2.011434e-19, 1.884072e+08, -1.300910e+04, 2.414058e-09, -4.675979e+11, 3.583361e-19, -4.499438e+18, 1.641999e-21, -2.686795e-10, 6.136688e-20, -3.793690e+16, 4.944562e-20, -3.490443e-03, 3.080547e+02, 2.041413e-06, 2.021979e+03, 2.314233e-06, 1.564131e-01, -8.712542e+17, 7.569081e+16, -1.056907e+17, 2.095024e-14, -2.487621e+17, -3.490381e+19, -6.944641e-01, -2.892354e-08, -3.597351e+12, -1.985424e+06, -2.348859e+09, -1.657051e+01, -3.358823e+14, 3.219974e-16, -4.819092e-13, -2.905178e-11, 8.257664e+04, -4.092466e-15, -3.464711e-13, -3.956400e-14, -2.548275e-08, -8.917872e-21, 7.387291e+13, 2.300996e+16, -4.870764e+18, -9.909380e-03, 1.260429e-08, -3.409396e-12, 1.003848e+02, -4.883178e-02, -3.125474e-14, 1.005294e+11, -4.736012e+09, -1.647544e-09, -3.491431e-03, 4.619061e+07, -4.547601e-09, -3.788900e-02, -2.648380e-17, 4.601877e-16, 1.754357e+13, 4.325616e+12, 1.860822e+03, 4.080727e+15, -4.573470e-14, -1.293538e+16, 2.811449e+05, 4.032351e+06, 4.274005e+04, 3.454035e-21, 4.933014e+09, -3.712562e+08, 3.158678e+06, -1.636782e+11, -2.884298e-18, -3.685740e-17, 1.027472e-07, -3.765173e-12, 2.740894e-17, 2.634880e+02, -4.334010e+00, -3.708285e-14, -3.858731e+16, -3.956687e+13, -4.064064e-12, 2.558646e-05, 4.459143e+03, -9.661948e+03, -1.994335e+16, 1.202714e-17, -3.782707e-17, 9.099692e-04, -1.864561e+09, 3.493877e-08, 4.288188e-01, 1.767126e-14, -6.779451e-22, -1.977471e-09, -3.536454e+06, -7.319495e-04, 2.004028e-16, -3.181521e-17, 3.336202e+14, -2.752423e+07, 3.390953e+01, 4.199625e-15, 2.883232e-12, 3.122912e-06, 7.324619e-19, 3.092709e-02, -2.758364e-15, -2.489492e+12, -1.622009e-08, 2.371204e+06, -1.582081e+08, -6.382371e-17]
        ca(self._r.d2, [1.374233e+19, 2.424327e-04, -1.615609e-02, 3.342963e-21, -4.308134e+14, -1.783430e-07, 2.214302e+18, -1.091018e+17, 3.279396e-20, 2.454183e-01, 1.459922e+07, -3.494941e+16, -7.949200e-21, 1.720101e+17, -1.041015e+16, 1.453541e+05, 1.125846e+06, 1.894394e+07, 1.153038e-17, -3.283589e+06, 2.253268e-10, -3.897051e+06, 1.362011e+05, 5.501697e-19, -4.854610e+01, -1.582705e-05, 7.622313e+04, 2.104642e+08, -1.294512e-06, -1.426230e-19, -4.319619e-15, 9.837716e+03, -4.949316e-01, -2.173576e+02, 2.730509e-19, -2.123803e+05, 1.652596e-17, -2.066863e-09, 3.856560e-08, 1.379652e+18, -2.119906e+16, 4.860679e-05, -1.681801e-10, -1.569650e-15, 3.984306e-21, 3.283336e+08, -9.222510e-16, -3.579521e-02, 1.279363e-05, 3.920153e-12, 4.737275e-15, -4.427587e+06, -3.826670e-14, 2.492484e-04, 4.996082e+09, 4.643228e-11, 2.809952e-17, -2.224883e-13, -4.442602e+18, 4.422736e+11, 4.969282e-18, 4.937908e-15, 6.973867e-22, 1.908796e-19, 4.812115e-08, 1.753516e-02, -3.684764e+02, 1.557482e-17, -1.176997e-11, 1.772798e-05, 4.877622e-16, 1.107926e+11, 4.097985e-14, 2.714049e-18, 3.198732e+15, -1.052497e-01, -5.003982e+07, -1.538353e-04, 3.045308e+17, 1.176208e-18, 1.268710e-10, -1.269719e-05, -2.989599e+00, -3.721343e-11, -1.444196e-10, -2.030635e+04, 2.070258e+16, -3.001278e-14, 1.116018e+14, 4.999239e+15, 4.286177e-21, -2.972550e+10, 3.549075e-20, -2.874186e-06, 2.994430e+09, 2.978356e+10, -2.364977e+07, 2.807278e-01, -3.279567e-10, 4.567428e+05, 1.612242e+07, 4.102315e+05, -1.069501e-20, 2.887812e+10, 4.384194e-09, -2.936771e-11, -4.164448e+07, 3.391389e+04, -3.923673e+17, -2.735518e-22, -2.019257e-01, 3.014806e+15, -3.885050e-15, -2.806241e-20, 3.077066e+18, -1.574438e+14, -3.131588e+19, 4.812541e+03, 4.435881e+16, -3.843380e+02, -7.522165e+03, -3.668055e-21, 2.603478e-08, 2.928775e+08, 2.892123e+00, -1.594119e+04, -4.817379e-01, -2.121948e+03, -8.872132e-09, -3.909318e-06, -3.849648e-14, -4.554589e+18, 4.410297e-15, -2.976295e-04, -2.298802e+10, 4.981337e-07, 5.364781e-12, 1.536953e+07, -4.082889e-07, 1.670759e-21, 4.009147e-13, -4.691543e-18, -2.597887e-13, 2.368696e+18, -2.585884e-07, -5.209726e-03, -2.568300e+06, 2.184692e-20, -1.799204e+16, 1.397292e+04, 4.277966e+13, -4.072388e+09, -2.324749e+16, -4.717399e+10, -2.853124e-05, -3.664750e+11, -3.864796e-08, 3.265198e+07, -3.309827e+19, 3.222296e+03, 2.366113e-19, -3.425143e+14, 1.627821e-08, 4.987622e+00, -1.402489e-17, -1.303904e+15, -2.042850e+17, -1.399340e+09, -3.560871e+05, -4.251240e-21, -7.806581e-10, 1.723498e+00, -2.030115e+08, 4.595621e-19, 1.174387e-10, 3.474174e+14, -4.159866e+03, -1.833464e-19, -3.650925e+05, 3.757361e-03, -1.854280e-10, -1.856982e-13, 1.685338e+08, 4.051670e-11, 4.095232e+03, -2.956025e-16, 4.986423e-05, 4.941458e+10, 4.145946e+11, 3.402975e+14, -1.954363e+11, -2.274907e+10, -3.162121e-17, -5.027950e-07, 4.135173e-02, -3.777913e-04, -4.898637e+15, 2.354747e-02, -6.884549e+13, -1.896920e-05, -1.914414e+15, -1.196744e-19, -4.692974e-01, 8.586675e-10, -2.204766e-17, -3.586447e-14, 1.751276e+17, -2.546189e-05, -2.248796e+03, -9.445830e+02, 1.150138e+03, 4.586691e+11, -2.582686e-15, -2.795788e+12, -3.409768e+07, -2.172186e-03, -1.457882e+06, -4.153022e+13, -4.255977e-08, 3.216237e-07, 4.935803e+02, -4.248965e-16, 1.740357e+07, 4.635370e+19, -4.099930e-14, 2.758885e-16, -4.714106e-05, -4.556226e-20, -4.290894e-19, 1.174284e-09, -1.443257e+16, -2.279471e-08, -3.030819e-16, 1.535128e+18, -3.248271e-07, 3.079855e-21, -3.056403e-02, -1.368113e-12, 4.004190e-10, 4.955150e+07, -2.494283e-16, 2.186037e+05, -1.232946e+03, 5.586112e-05, -2.288144e+17, 2.515602e-19, -4.064132e+08, -3.217400e-02, -2.620215e+07, 2.283421e-14, -1.130075e+08, 3.304955e-03, 1.352402e+01, 6.255755e-03, -3.913649e-08, 5.474984e+01, -4.712294e-08, 3.548418e-16, 1.276896e+12, 2.007320e-08, 3.025617e+04, -2.544836e+14, -2.087825e+17, -3.285556e-09, 2.605304e+07, -1.876210e+07, 3.734943e-10, -3.862726e-15, -4.227362e-05, 1.267773e+14, -1.706991e-05, 3.737441e+10, 2.641527e+01, 4.439891e+10, -1.444933e-05, -2.190034e-12, 8.059924e-18, -1.324313e+18, -1.420214e-10, 3.940158e-20, 3.943349e-02, -2.685925e+19, 4.334133e-05, 3.171371e-21, 2.094486e+12, 1.331741e+03, 1.205892e-02, 1.791416e+04, 3.899239e+10, 6.581991e+06, -3.860368e+11, -3.853916e-02, 1.314566e+09, 3.923126e+03, -3.509905e+13, -4.332430e+06, -1.713419e+01, -1.244104e-14, -5.529613e+01, 6.630349e+06, 1.053668e+10, 3.312332e-05, -1.252220e+08, 3.997107e-07, 1.847068e-13, -2.393157e-11, -2.083719e-10, -4.927155e+11, 2.666499e-15, 4.087292e-10, 4.082567e-10, -2.017655e+07, 9.108015e+15, -4.199693e-15, -4.969705e-17, 1.769881e-02, 1.745504e+00, 2.200377e-16, -4.404838e-06, -1.317122e-15, 7.210560e+08, 1.282439e-18, -3.204957e-06, -1.624277e+05, 4.570975e-22, 1.261776e+04, 4.416193e+12, -4.343457e-18, 4.095420e-14, 4.951026e-09, 2.261753e-15, 4.125062e+05, -4.448849e+11, -3.184924e+06, -2.050956e+05, -9.895539e+09, 4.541548e+11, -4.230580e+11, -4.268059e-15, -4.393836e+09, -2.514832e-08, 3.322394e-04, 2.597384e-18, 1.316619e-11, -2.250081e+16, 2.179579e-10, -1.838295e+04, -1.995626e-17, -4.656110e+17, 3.481814e-07, -2.859273e-11, -2.011768e-06, -1.809342e-17, -3.242126e+10, -1.873723e+08, -2.833009e-12, -3.758282e+12, 2.970198e+15, -2.667738e-01, -3.689173e+11, 1.008362e-10, -1.526867e-20, -1.439753e+06, -6.154602e+16, 4.165816e+00, -1.597823e-09, -1.862803e+14, -2.222766e+15, -2.892587e+17, -4.230426e-14, 2.999121e-21, 1.642245e+00, 1.590694e-14, -4.469755e-06, 2.700655e+12, -1.822443e-02, -4.889338e-16, -3.174990e-11, 4.146024e-03, 1.313280e+01, 3.235142e+15, 3.500547e+00, -4.413708e+03, 1.485548e+16, -1.660821e-11, -4.334510e-22, -1.209739e+04, 1.149570e+12, -4.537849e+00, -3.628402e-16, 2.748853e-12, -4.818907e-21])
        self._r.d3 = [9.025110e-18, 3.567231e+17, 2.594489e+01, 2.311708e-04, 7.345164e+13, 6.550284e-01, 1.969554e+12, 9.451979e-05, 5.900637e-09, 9.975667e+03, 6.549533e-17, 2.227145e-13, 2.822132e+18, 4.332600e+18, 1.485466e+05, 5.844952e-14]
        ca(self._r.d3, [2.047398e-20, 2.091541e-20, 9.084241e+14, 1.583413e+01, 5.168067e-02, 1.360920e-11, 9.818531e-21, 6.293083e+07, 4.406956e-14, 8.540213e-09, 7.329310e-03, 5.566796e+00, 3.968358e-08, 4.928656e-08, 5.994301e-20, 8.281551e-21])
        self._r.d4 = [-4.207179e-09, -3.611333e+11, -4.155626e-06, -2.458459e+10, 2.826045e-11, 3.511191e-08, 4.759250e-07, 2.455883e+09, 4.182578e+11, 4.732337e-14, -2.967313e+02, -4.139188e+14, 6.287269e+03]
        ca(self._r.d4, [2.864760e-08, 3.900663e+13, 9.105789e+11, 2.943743e-15, -2.823159e-16, -3.481261e+19])
        d5_1 = numpy.array([-5.528040e-08, 3.832644e-01, -9.139211e-22, -4.919312e-05, 3.809620e-11, 1.751983e-09, 2.207872e-21, 1.432794e+09, -1.970313e+11, 3.405643e-18, -3.756282e+14, -4.918649e+08, -3.162526e-14, -2.853298e-09, 2.835704e+10, 4.458564e+16, 6.657007e+09, 3.640798e-10, 4.950898e-06, 3.384446e+14, -4.065667e+16, -2.243648e-05, 4.822028e-21, 4.231462e-14, -2.526315e+11, -5.626782e-05, 2.321837e+13, 1.772942e-09, 1.606989e-08, 2.669910e-04, -3.635773e+08, -3.967874e-10, 6.599470e+15, 4.612631e-08, -1.417977e-11, -8.066614e-18, 5.738945e+15, 6.408315e+13, 1.922621e+12, 3.096211e-14, -2.079924e+18, 1.664290e+09, -4.502488e+07, 3.092768e+05, 4.414553e+10, -3.673268e+02, -4.772391e+17, -1.100877e+02, -1.453900e+01, 4.293918e-13, -4.270900e-02, -3.886217e+11, -2.206806e+02, 7.034173e-07, -2.826108e-21, 3.616703e-21, -3.385765e+04, -7.027764e-11, 9.684099e+05, -4.248931e+03, -3.415720e-20, -3.315237e-11, -9.555895e+11, 3.520893e-13, 1.089514e-13, 3.591828e-21, -4.847746e-06, -2.678605e-16, -7.480139e-04, 2.208833e+01, 1.075027e-07, -1.047160e-05, 2.309356e+06, 7.308158e-19, -4.915658e+02, 4.634137e+18, -3.682525e+13, 4.124301e-06, 4.158100e-10, 2.091672e-11, -6.856023e+07, 8.418116e-07, -1.655783e-13, -2.502703e-03, 1.274299e+17, -4.784498e-20, 1.357464e-10, 4.107075e-13, -2.753087e-05, -2.594853e-14, -3.712038e-13, 1.143743e+14, -2.495491e+10, 2.331111e-15, 2.987117e+18, 2.876066e-18]).reshape([8, 6, 2], order="F")
        self._r.d5 = d5_1
        d5_2 = self._r.d5
        numpy.testing.assert_allclose(d5_2, numpy.array([4.427272e-10, -1.149547e-08, -1.134096e+16, -4.932974e-03, -7.702447e-01, -3.468374e-03, -5.037849e-14, -4.140513e-08, 4.553774e+03, 2.746211e+01, -4.388241e-17, 2.262009e+00, 5.239907e+06, 4.665437e-05, -1.662221e-05, 5.471877e-13, 2.592797e+11, -4.109763e-05, 1.797563e-04, 1.654153e+01, 4.011197e+07, -2.261820e-10, 5.836798e+02, 1.518876e-18, 4.814150e+18, -4.610985e-07, -3.126663e-07, -1.981883e+10, 4.117556e-02, 1.937380e-07, 1.397017e-10, 2.809413e-17, 9.387278e+18, 4.777753e-11, -4.248411e+15, 3.851890e-16, -1.598907e-08, 3.699930e+14, 2.763725e-08, -4.130363e+17, 3.105159e+06, -2.026574e+00, 3.956735e+01, 3.893311e-04, 3.574216e+13, 3.618918e+03, -4.027656e-09, 9.174470e-02, -8.108362e-21, 1.857260e-18, -3.540422e+13, -2.985196e+12, -3.219711e-08, -1.618670e-13, -2.648920e+12, 1.224910e-14, -4.740355e-03, 4.604337e-18, 3.809723e+05, -4.460252e+15, 1.894675e-15, -4.141572e-08, -3.939165e-09, -1.916940e-06, -2.382435e+16, -4.689458e-01, 1.498825e+17, 1.876067e-15, -1.801776e+09, -1.140569e-05, -6.881731e-08, -4.835017e-07, 3.843821e-17, 2.220728e+06, -4.321528e+10, -3.950910e+01, -1.732064e-11, 3.009556e-16, -3.509908e+18, -7.781366e-15, -2.511896e-18, -2.037492e+04, 2.656214e-19, 2.163108e+16, 4.526743e+19, 2.738915e-11, 8.491186e-16, -1.286244e+05, 3.635668e+12, -4.964943e+15, 3.725194e+05, -4.010695e-19, 2.140069e-09, 3.957374e+19, 4.478530e-06, 4.284617e-06, -3.459065e+12, 1.525227e-18, 4.892990e+06, 3.557063e+07, 2.986931e+18, 2.147683e-05, -4.190776e+17, -3.715918e-14, -3.448233e+01, 1.272542e+15, -3.900619e-06, -3.712080e+05, 3.388577e+04, -4.440968e-11, -4.395263e+18, -4.052174e-06, -3.065725e+00, 3.915471e-04, 4.863505e+12, 4.861871e-09, 4.607456e+03, -1.845908e-12, -9.985457e-11, -4.534696e-08, -1.163049e-17, 4.492446e-11, 3.078345e+06, 8.520733e+05, 2.218171e+14, -4.546400e+09, 4.641295e+09, -1.677260e-07, 9.650426e+04, -4.001218e-04, 4.761655e-22, -3.989865e+01, -5.800472e-08, -2.548565e-01, 4.648520e-08, 4.255433e-16, -2.387043e-11, 4.172928e+17, 4.194274e-12, -1.391555e-04, -1.063723e-01, 1.609824e-13, 9.196780e-10, -4.744075e+06, -4.764303e-02, -4.540535e-10, -4.361282e+00, -1.460081e+01, -2.215205e-16, 4.652514e-19]).reshape((5,6,5), order="F"))
        

        d6_1 = numpy.array([-5.528040e-08, 3.832644e-01, -9.139211e-22, -4.919312e-05, 3.809620e-11, 1.751983e-09, 2.207872e-21, 1.432794e+09, -1.970313e+11]).reshape((3,3),order="F")
        self._r.d6 = d6_1
        d6_2 = self._r.d6        
        numpy.testing.assert_allclose(d6_2, numpy.array([4.427272e-10, -1.149547e-08, -1.134096e+16, -4.932974e-03, -7.702447e-01, -3.468374e-03, -5.037849e-14, -4.140513e-08, 4.553774e+03]).reshape((3,3),order="F"))

        self._r.s1 = 3847.9283
        val=self._r.s1
        #if self._r.s1 != 7.8573:
            #raise Exception()
        self._r.s2 = [-1.374271e+12, 1.798486e-08, -4.845395e-08, -4.785331e+12, -2.914127e+04, -1.753064e-17, -4.063563e-09, 2.758058e+04, -1.988908e+11, -1.535073e-18, 2.439972e-02, -3.237377e-12, 9.760366e-12, -4.276470e-21, 1.693848e+18, -1.401259e-19, -3.140953e-11, 8.675222e-05, -2.097894e+05, -1.183071e+09, -4.405535e-14, -1.157335e+11, 1.055748e-19, 2.363738e+19, -1.404713e+19, 4.284715e+01, -3.515661e+19, -1.254196e+13, 2.076816e+19, -2.454920e+04, -2.205493e-21, -9.940678e+08, 3.818785e+03, -1.504647e-14, -2.604226e+15, -3.708269e+10, -1.633861e-19, -2.928434e+06, -3.741304e-01, 3.925411e+09, 1.135659e+05, 8.774251e-11, 8.857955e-17, 1.461853e-18, 2.228531e+18, -2.901828e-21, 2.648299e+17, -1.981382e-08, -8.234543e-19, -1.732653e+07, 1.899980e+10, -1.392906e-08, -6.839790e+14, -2.267130e+09, -4.215074e-14, 4.329019e-17, -3.351069e+09, -2.689165e-07, -4.337995e+10, 4.010095e-15, 1.340637e-05, -4.157322e-06, -1.091954e+14, 1.108454e-11, -8.934548e+08, -3.823683e+14, -3.164062e+07, 2.908637e-08, 8.450160e+02, 4.285117e+16, -2.603674e+05, -5.280737e-07, -2.589230e-05, -9.163516e+17, -3.501593e+04, -4.513991e+06, 3.740032e+11, 6.325982e+08, 4.911299e+19, -3.871696e-08, -1.641252e+00, -3.909808e-17, 4.148389e-21, 3.153334e-06, -2.737137e-07, -2.885790e-08, -2.024930e+09, 7.689509e+05, -7.910094e+00, -3.122012e-08, 2.087070e-07, 2.943975e-08, -3.637942e-05, 1.265381e-18, -3.240420e-07, -3.299393e+15, -4.534857e+15, -4.197434e+05, 2.443365e-06, -1.220755e-17, 2.294507e+06, 1.755297e-21, 9.738120e-03, 3.730024e+12, 4.634193e+11, -4.594819e-08, -1.281819e-03, 1.860462e-04, -3.678588e+18, 4.460823e-18, -1.766008e+14, -2.775941e+11, 4.325192e-07, 2.655889e+10, -1.757890e-06, -2.103859e-08, -2.269309e+12, -9.581594e-11, -2.672596e+14, -3.052604e+04, -2.464821e+18, -4.276556e+02, -4.032948e+05, -2.305644e+19, 4.750717e-04, 6.464633e+03, 7.776986e+17, -2.123569e+16, 3.016544e-07, -2.520361e-03, 2.920953e+00, 3.216560e-12, -1.880309e+10, 9.663709e+16, 1.981875e-02, 1.826399e+19, -1.218763e-21, 1.673439e-10, -1.995639e-05, -2.134349e-02, -3.101600e+11, -1.148683e-14, 1.527847e-11, -4.532247e+08, 4.120685e-21, 4.836973e+16, 4.509629e-05, 3.936905e+17, -7.068550e+07, 4.976433e+02, 2.118027e+02, 4.972063e+06, 4.601005e+16, -4.367053e-17, 1.770987e+06, 2.572953e+00, 3.020633e+12, 1.762052e+11, 4.443317e-05, -1.896787e+08, 3.349722e-14, 1.094784e+06, 2.239828e+00, -1.400895e+05, -1.098610e+09, -3.681296e-09, 2.842120e+16, 3.138041e-18, 1.993332e+07, -2.584283e-06, -4.399412e+12, -7.050502e-19, 1.079255e-10, 2.938524e-19, 4.733761e+07, 4.451092e+02, 1.326299e-17, 2.808418e+12, -2.952152e-14, 4.550734e-16, -2.399796e-04, -2.786184e+07, -3.567595e+03, -2.166879e+19, -1.804263e+04, -9.775023e+09, 4.758856e+09, 2.636609e+13, 4.132205e+10, 2.594126e-20, -3.244046e-18, -3.136448e-03, -3.446778e+08, 2.442233e-12, 1.808183e-11, -2.846331e+02, -2.933024e-10, 3.547133e+00, -9.445332e-20, -4.328694e-04, 2.748924e-12, 4.169152e+10, -3.488881e-04, -2.713158e-08, -1.549705e+15, -3.554349e-08, 2.503210e+14, 1.715581e+08, -2.047344e-10, -4.017695e+05, -1.979563e-08, 4.032794e+07, -1.670813e+07, 1.889040e+07, 4.875386e+11, -1.159781e+13, -4.023926e-21, 4.535123e-07, 4.470134e+02, -2.619788e+04, -3.454762e-09, 3.006657e+00, 1.158020e-13, 1.885629e-11, -3.766239e+15, -6.418825e-20, 3.322471e+13, 4.646194e-07, -2.817521e+13, 1.370796e-04, 4.014727e+04, 3.057565e+18, -6.171067e-12, -4.067906e-16]
        #ca(self._r.s2, [3.252887e+09, 1.028386e-04, -2.059613e+01, 1.007636e-14, -4.700457e-13, -1.090360e-22, -3.631036e-15, 2.755136e-09, 4.973340e+13, 2.387752e-15, -9.100005e+06, 1.484377e+13, -2.287445e-13, -3.718729e+18, -4.771899e+19, 8.743697e+13, 1.581741e+07, 2.095840e-09, -5.591798e-03, 6.596514e-06, -1.006281e+05, -4.126461e+12, 4.246598e-20, -1.376394e+08, -3.398176e-03, -1.360713e-21, 3.109012e+14, -8.112052e+07, -8.118389e-02, -3.455658e+14, 7.352656e+12, 4.198051e+06, 4.258925e-03, -2.634416e+12, 3.362617e+02, -4.606198e-15, 4.228381e-19, 4.209756e-15, -1.268658e+05, 3.019326e+02, 7.937019e-01, 6.225705e-09, 1.324805e-19, -4.355122e+01, -4.533376e+15, -1.584597e+01, 1.657669e-02, -3.720590e-18, 2.038227e-04, 2.890815e+04, 1.513743e-14, 4.993242e-20, -5.255463e-21, -8.084456e-14, 4.087952e-09, 2.518775e-21, 4.977447e+15, 3.363414e-19, -3.931790e-20, -7.810002e+14, -3.589876e+14, -4.969319e-18, -4.356951e-20, -3.682676e+02, -1.319524e+10, 3.805770e-11, 2.134369e-10, 3.684259e-08, -2.901651e-13, -4.486479e-01, 2.208715e-02, 3.224455e-01, -3.305078e+09, -3.326595e-02, -2.473907e+03, 3.608010e-15, -2.596035e-01, 2.594405e-01, -7.569236e-01, -3.430125e+09, 2.920327e+02, -3.763994e-12, 2.617484e-12, 4.808183e-07, 3.885462e+15, -1.201067e+00, 1.887956e+06, -4.038215e+02, -4.710561e+03, 1.659911e-16, -4.955908e-17, 4.681019e-09, 3.945566e+05, -3.433671e+19, -2.679188e+05, -2.357385e-01, 2.891702e-19, -4.464828e-06, -6.003872e-04, 1.369236e+18, -3.597765e+01, -4.246195e+08, -4.765202e+17, 4.472442e+10, -1.038235e-05, -4.632604e-09, -2.484805e-15, -7.998089e-16, -3.690202e-04, -3.276282e-04, 1.966751e+10, -5.081691e-18, -2.004207e-05, -2.756564e-03, -2.624997e+14, 2.398072e-20, -4.098639e-10, 2.930848e+01, 8.983185e+15, 1.984647e-15, 1.331362e-16, -6.519556e+15, 4.270991e+15, -9.165583e-13, 4.266535e+17, 4.238873e-21, -2.487233e+17, 4.904756e+03, 2.692900e+10, 1.467677e-18, -2.204474e+06, -1.806552e-09, 9.617557e+17, -1.988740e-20, 1.713683e-04, -2.360154e-21, 4.178035e-17, 2.600320e+12, -4.761743e+09, 3.034447e-20, 4.941916e-06, -1.373800e+04, 1.851938e-09, 1.304650e+14, 3.067267e+07, -4.100706e-06, 2.190569e-03, 5.901064e-17, -2.152004e+15, 4.050525e+04, 3.769441e-06, -4.388331e-12, 1.037797e+12, 3.512642e-19, 3.857774e-09, 1.036342e+03, 3.683616e-18, 9.785759e+10, 2.199992e+03, -2.435347e-02, 1.526312e+06, 2.569847e+14, -2.288773e-01, 4.724374e-06, -3.807381e+13, 2.924748e-10, 2.820652e-20, 4.835786e-12, 2.811112e+02, -6.431253e+02, -4.843622e-06, 1.676490e-10, -4.432839e+07, 1.661883e+19, 8.668906e+07, 2.256498e-04, 2.170563e-01, 1.013347e-17, -4.271306e+11, -2.431836e-17, 3.983056e+02, 4.236306e+05, -2.142877e-20, -2.760277e-12, -8.479624e-08, 2.903436e+05, -3.288277e-17, 4.173384e-10, -1.598824e-08, 8.702005e+05, -1.456065e+08, 2.035918e+06, -1.445426e+02, -4.148981e+05, 4.439242e+02, -1.223582e+16, -8.226224e+14, 1.690797e+16, 1.683472e-04, -4.809448e-16, 4.517499e+06, 4.369645e+02, -4.532906e+09, -3.539758e+07, -2.406254e+01, 4.396602e+00, 2.995832e-01, -2.953563e-04, 3.412885e+17, 1.386922e-17, -2.177566e-04, 2.548426e+04, -3.937000e+16, 2.578962e+02, 2.423257e+16, 3.069379e+09, -4.940417e+09, -4.618109e-13, -1.387521e-11, -2.168721e-05, 1.917758e-01, -3.144071e+03, -1.045706e-13, -2.869528e+02, 2.072101e-13, 4.267714e+12, -2.063457e-19, -3.025547e-12, 8.101894e+10, -4.196343e-04, 4.753178e+18, -2.286673e+08, -2.618986e-10, 3.949400e-10, -4.390776e+12, -2.498438e+10, 3.800599e+12, -3.704880e+15, -4.173265e+02, 3.326208e+19, -1.093729e-21, 3.042615e+16, -1.711401e-09, 3.039417e-19, -2.250917e+15, 2.195224e-01, -2.953402e+05, -1.486595e+17, -2.387631e+00, -1.634038e-14, 6.153862e-18, -3.842447e+05, 3.238062e-14, -4.341436e-11, -1.816909e-19, -3.534227e+14, 8.578481e+07, -4.067319e+09, -4.680605e-08, 4.050820e+04, 1.715798e-11, -5.232958e-12, 2.291111e-07, 1.086749e+01, -3.028170e-14, -6.277956e+13, -1.639431e+11, 4.158870e+17, -1.208390e-18, 4.835438e-05, -3.135780e-08, -4.087485e-12, 2.466489e-08, 1.949774e+00, -3.532671e-21, -1.422500e+12, 4.352509e+03, -1.444274e-17, -1.162523e+19, -4.815817e-07, -2.809045e+11, -1.212605e+03, -3.496461e-08, 6.743426e-18, -4.226437e-06, -3.627025e+07, 1.037303e-05, 2.411375e+08, -2.721538e+12, -4.809954e-06, 4.578909e+16, 9.257324e+06, 4.326725e-03, 4.416348e+12, 4.424289e+13, 3.180453e+12, -6.028285e-10, 3.344767e-14, -2.747083e+18, 1.133844e-15, 3.922737e-06, -3.199165e+00, 2.417553e+02, 3.015159e-20, 2.119116e-02, 4.019055e-09, 3.368508e-21, -1.613240e-19, 3.832120e-14, 1.202460e+17, -3.304317e+19, 1.692435e+17, -2.597919e-05, 3.916656e+17, 4.821767e+06, 4.372030e+02, 1.987821e-08, -1.976171e-08, 1.319708e-09, -4.213393e+10, 3.829773e-15, -4.762296e-21, 4.642216e-18, 1.662453e-13, 6.642151e+03, 2.539859e-02, -3.112435e+09, -3.627296e-20, -1.660860e+02, -3.678133e+07, 3.428538e-01, -2.277414e-20, 2.228723e+17, -2.833075e-06, 9.084647e+03, -2.976724e-16, 2.778621e+15, -2.806941e+07, -1.626680e-15, -4.658307e+13, 7.967425e-11, -2.793553e-21, 4.778914e+16, -6.145348e-21, -4.883096e+11, 1.338180e+04, 7.533078e-16, 3.252210e+05, -2.882071e+10, -2.754393e-06, -1.689511e-16, -1.979567e-10, 4.494219e-04, 3.285918e-15, -4.347530e+05, -1.085549e+15, 1.301914e+07, 3.855885e+13, 3.036668e-11, -4.706690e+12, 3.727706e+17, -4.446726e-12, -4.829207e-08, -1.543068e-10, -2.473439e-11, -2.718383e+13, -4.211115e-21, 3.327305e-04, -1.084328e-20, 3.849147e+06, -1.321415e+09, -3.518365e+07, 2.246762e-21, 2.482377e+11, -4.265765e+03, -4.538240e-05, 2.727905e+18, -2.383417e-13, 4.103955e+04, 8.015918e-06, -2.965433e-18, 3.156148e+03, 8.093784e+18, 4.868456e-12, 1.048517e-02, 1.112546e-19, -3.751041e-12, -3.734735e-06, 3.019242e+06, -1.480620e-17, -3.405209e+07, -1.123121e+19, 8.155940e-20, 1.406270e-17, 2.154811e-13, 9.943784e-20, 1.523222e-17, 6.987695e-21, 8.826612e-12, -2.325400e-20, 3.700035e+15, -5.559864e-11, -8.568613e+10, 1.434826e-07, -2.080666e-03, -2.548367e-03, -4.310036e-18, 3.104310e+00, -3.862149e+17, -4.092146e-13, 3.538555e-14, -4.950494e-05, 6.538592e-13, -4.196452e-11, 2.351540e-01, -1.232819e-01, -3.669909e-21, 1.528733e-14, 5.661038e-15, -1.967561e-07, -2.284653e+02, -1.834055e-10, -2.175838e+05, 4.247123e+06, 1.184396e+18, 4.156451e+15, -4.992962e-14, -2.351371e+06, -6.698828e-10, 2.897660e+17, -3.470945e-06, 4.630531e-07, -4.453066e+10, 4.069905e+09, -4.459990e-08, 4.702875e-13, -2.780085e+17, 1.293190e-05, 2.227539e-03, 1.534749e-21, 7.390197e-02, 4.522731e-10, -1.224482e-02, -3.996613e+02, -1.057415e-15, -7.371987e+14, 4.291850e-02, -4.243906e-08, -3.540067e-04, 4.535024e+09, -3.027997e+10, -3.986030e-02, 1.722268e-04, -3.140633e-20, 3.343419e+08, 4.713552e+14, -3.190084e+05, 2.449921e-01, 2.727707e+14, -3.545034e+11, 2.417031e+13, -2.231984e-09, 3.533907e+16, -4.662490e+16, 3.355255e+14, -1.567147e+17, -3.525342e+12, -3.586213e-16, -4.002334e+15, -1.928710e+08, -4.718466e+04, -1.539948e-06, 3.135775e-11, 3.862573e-10, -3.105881e+08, 4.421002e-05, -2.369372e+01, 4.758588e+13, -1.044237e-15, -4.535182e-10, 1.330691e+18, 3.636776e-01, -4.068160e-12, 2.757635e-17, 3.247733e+13, 1.247297e+06, 5.806444e-13, 3.521773e-05, 4.589556e-14, 1.582423e+00, -1.676589e+00, -3.864168e-07, -3.042233e-02, 2.007608e+14, 4.852709e+02, -2.817610e-04, -1.882581e+19, 1.057355e-14, 4.090583e-04, -1.848867e-13, -5.463239e+13, -1.041751e+05, 3.457778e-01, -2.562492e+00, -6.751192e-10, 1.688925e-21, 3.884825e-07, 1.592184e-12, -2.039492e+06, -1.196369e+19, 2.200758e+00, 2.550363e-21, 7.597233e+06, -1.929970e+09, 1.939371e+03, -3.236665e+09, -1.313563e-13, 2.007932e+02, -3.028637e-02, -1.532002e+00, 2.165843e+17, -3.511274e-04, -3.777840e+15, 1.645100e+17, 3.088818e-07, -2.793421e-11, -4.286222e-01, 4.385008e-10, -2.105222e-01, -2.212440e+08, 2.684288e-01, 1.407909e+18, -3.881776e+08, 3.505820e-09, 3.555082e-19, 3.573406e+01, 4.042915e-19, 2.066432e+08, -2.467607e+10, 3.453929e+01, 4.297309e-14, 1.256314e-11, 8.930289e+14, -3.662200e-03, 2.075690e-16, -2.866809e-17, 4.394016e+10, -2.014195e-03, -3.738633e+12, -4.953528e-05, 3.710240e+06, 3.319208e+04, -5.762511e-20, -4.690619e+16, 3.412186e+19, -1.241859e+09, -4.081991e+12, 4.622142e+03, -1.285855e-02, 1.532736e-08, -2.364101e+09, -1.369113e-18, -2.168979e+19, 2.952627e-14, -2.358172e-16, -1.992288e+00, -9.180203e+12, 1.675986e+07, 4.817708e+06, -1.624530e+06, 4.857415e-01, -5.995664e-03, 1.874911e+08, -3.320425e-17, 5.469104e-02, -3.069767e+11, 8.084999e+12, -2.321768e-20, 1.920249e-06, -4.114087e-02, 3.244903e-04, 3.203402e-17, 4.143519e+06, 4.093124e+17, 4.456464e-15, -2.262509e-13, 4.856535e-08, -4.550552e-15, -3.011803e+18, -2.882488e+13, -2.690616e-04, -3.996010e-19, -4.438855e+18, -1.942208e+03, 1.934537e+18, -1.961547e-07, 4.970021e+17, -3.531211e-17, 4.187133e+04, 2.854106e-12, -2.313257e+13, -3.471439e+16, -6.829753e-16, -4.338617e+03, 5.552258e+05, 1.520718e+19, -2.527013e+14, -2.732660e-09, -1.957740e+11, -4.767907e+12, -4.837256e+18, 3.155432e-12, -3.278156e-04, -1.117720e-13, -3.838176e+11, -7.207202e+08, -4.075808e-21, 1.659402e-14, -4.301886e-19, -4.461337e-11, 2.200979e+15, 4.339143e+07, 5.071459e-06, 1.832776e+18, -2.698948e+03, 4.682397e+01, 2.801081e-08, -3.424292e+00, -5.130555e+14, 1.229975e-14, 2.383361e-09, -3.611087e-07, -2.576595e-07, 1.295398e-08, -2.525216e-11, -2.546657e+10, 9.501518e+03, 8.325605e+04, -1.382092e+02, 2.169085e-21, 4.019485e+16, -2.404251e+17, 1.154833e+10, 9.454498e+01, -7.888753e-09, -4.907318e-20, 1.373262e+08, -2.295105e-21, 1.329034e+17, -3.403883e-20, 3.500734e-03, 2.657397e-20, 4.956090e-07, -2.191353e-03, -1.879262e+09, 4.519858e-14, 4.592234e-14, -1.473612e+11, 4.425251e+10, -3.936903e-01, -2.866089e+09, -3.046203e-09, -4.818832e+01, 2.460150e+02, 2.944622e-11, -1.675111e-20, -1.206111e+01, 5.044200e-13, 3.225861e+02, 3.170008e+12, 1.964043e-20, 3.464033e+03, 1.286135e-08, -6.425529e-10, -4.630162e-02, 2.616476e+18, 4.853669e+03, -1.851316e-03, 1.262159e-02, -1.816675e-12, 3.753560e+14, -3.033601e-18, 1.915137e-02, 3.411614e-14, 4.849348e+05, 3.033922e+13, 3.174852e-17, -4.397997e-09, -9.549484e-01, -1.706859e+11, -3.009122e-01, -8.189854e-15, 4.122789e-17, -1.351025e-13, -2.365671e-10, -1.139709e-05, -2.020593e+10, 3.664729e+14, 1.170917e+00, 1.157248e-19, -4.189734e+17, -4.407278e+13, 4.776929e+18, -3.279961e+07, -4.740186e-15, -3.764392e-02, -2.193781e+18, -4.556987e+00, -3.170243e-18, -1.755775e-16, -2.163959e-03, 2.410150e+11, 1.215874e-18, -4.927956e-05, 2.252375e-06, -3.315242e-14, -3.476357e+16, -4.545391e+00, 6.072704e-13, -4.571860e+09, -2.297081e-02, 2.401997e+10, -6.449709e+05, -3.580234e-08, -5.390535e+08, -4.891390e-19, 3.441769e-09, 4.885513e-09, -4.897531e-10, -1.792753e+08, 2.048965e+13, 3.339876e-21, 4.140957e+04, 2.022520e-21, 5.983159e+06, 1.938164e+13, 2.796107e-19, -1.975692e+09, -2.106710e+15, -4.482226e+09, -2.968068e-19, -1.171747e-03, 1.579378e-01, -4.568752e+16, 2.593340e+11, 3.441530e+10, 3.461992e-01, -5.333082e-09, -4.611969e-12, -4.262468e+19, -4.367063e+01, -2.447378e-11, -3.554859e+02, 4.824680e-05, -1.122071e+11, -2.226371e+13, 3.917182e-17, -1.308204e+10, 4.105055e-16, 5.087060e+07, 7.102691e-05, -2.872202e+03, 1.711266e+11, 3.331993e-08, -1.313944e-08, 3.648109e+11, 5.394321e+01, -4.125398e+03, 3.460645e-02, 2.573745e-18, -1.376298e+01, -3.283028e-05, 3.939711e-12, 3.986184e+17, 2.619889e-11, -4.318052e-09, 1.410821e+00, 3.547585e-07, 4.046432e-17, 1.880087e-07, 1.867841e-05, -1.383592e-21, 2.972106e-05, 2.867092e+01, 3.092781e+03, -6.897683e-02, -1.707761e-04, -4.231430e-11, -3.796784e+00, -2.953699e+11, 3.691013e+09, -3.962307e-12, -1.335633e-17, -1.759192e-01, -4.332862e+04, 1.044899e+11, -2.126883e+03, 1.948593e+14, -2.173759e-05, -4.393250e+05, 1.626217e+08, 2.832086e+18, 4.655433e+03, 2.944186e+08, 2.864233e+03, -3.565216e+05, -4.667000e+11, -3.739551e-03, 3.137195e+05, 2.044129e+19, 2.629232e+14, 3.119859e-09, 3.656121e-15, -4.844114e-03, -2.641449e-11, -3.788231e+05, 2.803203e+17, -3.764787e+09, -6.009761e-08, 4.106308e+01, -2.071363e-20, 1.884576e-20, 2.654081e+11, -3.456281e-11, -4.760486e-02, 4.096057e+11, 4.346738e-11, 2.827941e-02, -1.946717e+08, -9.067051e+15, 4.331454e-14, 4.792779e-09, -4.738308e+18, -1.228815e-09, 2.097152e+16, -4.440036e-06, -3.762990e+02, -2.642879e+12, 3.100004e+10, 3.604336e+12, -3.951650e+11, -1.023763e+15, 4.908325e+17, 2.123963e-19, -1.744445e+09, -2.874189e-06, 2.208907e-08, -2.353407e+10, -1.020581e-03, 1.689180e-01, -2.563565e-12, -1.220758e-15, -2.657970e-16, 1.140528e+10, -2.802143e+14, -3.835574e+00])
        self._r.i8_1 = 45
        if self._r.i8_1 != -66:
            raise Exception()
        self._r.i8_2 = [-66, 34, -121, -118, -12, -83, -43, 55, -53, 31, -100, -37, -116, 69, 22, -60, 59, 32, 51, 46, 109, 36, 31, 49, -99, -69, -99, -89, 27, -18, -77, -63, -101, -122, -60, 58, -76, -86, 58, 49, 48, -67, 54, 48, -30, -26, 95, 42, -13, 17, -93, -34, 28, -49, 8, 122, 22, -72, 109, 103, 15, -81, -73, -53, -112, -52, -54, -81, -126, 35, 3, -102, -125, 67, 125, 44, -48, 95, -18, -103, 114, -86, 108, -37, 70, 48, 7, 19, 0, 35, -104, 2, -51, -9, 70, 41, 118, -43, -71, 59, 32, 36, -10, -2, -76, -18, -93, -80, -27, -51, -70, -87, 48, -98, 5, 72, -120, 86, 62, 69, -94, 23, 71, -124, -88, 34, -65, 6, 33, 73, -101, 40, -104, 17, -68, 53, -55, -11, 12, 24, -63, 121, 98, 58, 125, -13, 6, 49, 71, -72, -22, 53, 83, -97, 87, -117, -26, 6, 93, -98, 82, -111, -84, 23, -73, -10, -34, -118, 64, -89, -4, -104, -83, -52, 8, 64, -81, 33, -91, 41, -43, 12, -66, 31, -17, 46, 91, 9, -124, -117, 108, -15, -39, -92, 29, 116, -93, 107, 58, -7, -35, -116, -52, -11, -35, 66, 6, 32, -34, -123, -102, 102, 123, -104, 51, 80, -84, 71, -65, -4, -121, 123, -87, -21, -124, 63, 122, 74, -31, 123, -31, -63, -106, -82, -24, -42, -30, -126, 0, -38, 127, -13, 101, 60, 104, 54, -25, 50, -19, -93, 2, -48, 99, -59, 103, 28, 44, -7, -58, -19, -55, 17, 58, 15, -23, 75, 58, 11, -2, 104, -58, -73, 56, 84, 34, -4, -101, 10, -106, 41, -88, 15, -117, 5, -63, -106, -9, 40, -115, 47, 99, -66, 120, 126, 5, -62, 8, -111, 123, 92, 122, 24, -31, -65, 115, -43, 5, 56, 49, 102, -29, 65, 97, 20, -90, -39, 40, 75, -43, -47, 86, -104, -32, -90, 14, 13, -75, 8, -9, 104, 122, -24, 77, 10, -100, 26, 0, 35, 55, -10, 17, 22, -29, 115, 117, -10, -54, 37, 46, 48, -28, -105, 20, -117, 73, 93, -63, 9, -125, -94, 57, 119, -10, 11, 49, -57, -14, -107, 90, 72, 96, 55, 86, 81, -86, -70, -125, 17, 100, -91, -70, 87, 29, 100, -19, -45, 46, 25, -49, 79, -10, -1, 22, 75, 9, -50, 114, 106, -122, -89, 41, 1, 105, 123, -69, -123, 77, -61, -100, 15, -113, -19, 46, -53, 46, -89, -97, -38, 92, 73, 68, -101, 118, 67, 23, -17, 73, 109, 36, 76, 69, -10, 7, 64, -39, -49, -4, 3, -102, -15, 117, -8, -83, 6, 117, 105, 26, 28, 19, 66, 24, -47, -64, 86, 4, 57, 95, 23, 24, 76, -15, 106, -58, 77, -10, -112, -39, 55, -4, 95, -90, 61, 64, 32, 68, -43, -108, -15, -6, 63, -105, 72, -84, -10, -11, 122, 46, -84, 26, 76, -88, -67, -95, 10, 10, -89, -121, -65, -69, 112, 37, -106, 75, -94, -60, -7, -72, 44, 71, -108, -71, 31, 99, 9, 10, -68, -56, 69, 0, -71, -4, -87, -6, 83, 7, 108, 98, -37, -60, 16, 23, 26, 3, -119, -20, 58, 102, 29, 111, -43, 26, 37, 34, 9, 82, 76, 120, 7, 51, -35, 65, -93, 38, -82, -44, -31, 120, -93, 7, 10, -76, -12, 105, 41, 13, 123, -90, 57, 84, -123, -21, 49, 104, -103, -32, -79]
        ca(self._r.i8_2, [-106, -119, 126, 87, 95, 79, -1, -15, -4, -30, 76, -121, 35, 80, 5, 7, -36, 102, 120, 105, 86, 98, 113, -62, 105, 38, 93, 20, 92, 7, -99, -121, -56, 50, -35, -95, 2, -43, -49, 73, 49, -42, -24, -3, -41, -59, 119, -108, 82, 98, 95, 111, 114, 115, 109, -125, -60, -45, -110, 31, -73, -111, 69, -108, -125, 14, -87, 61, 114, -104, -72, -67, 35, 26, 61, 59, -114, 125, -82, -34, 7, 71, -117, 125, 79, -116, -81, 3, -59, -121, 112, 64, 54, -9, -63, 37, -86, 104, -105, 7, 72, -99, 84, -3, -63, 77, 27, 36, 52, -110, 60, -119, -124, 82, -29, 107, 124, 105, 96, -34, -11, 0, 59, -39, -107, 55, 95, -26, -60, -30, -102, -94, -28, -7, 76, 56, -31, -68, 6, 101, 67, 101, -92, 120, 105, -119, 114, 6, 9, 43, 73, -64, -18, -77, -72, 84, -101, -114, -50, 28, 86, 103, -83, -109, -59, 82, 96, -70, 20, 75, -44, -3, -115, 60, 45, 94, 65, -108, 2, 12, 28, 110, -19, 20, 102, -41, 42, -61, -52, -54, 116, 114, -74, 14, -21, -43, -85, 16, 57, -62, -83, -79, 85, -7, 109, -45, 102, 28, 123, -96, 2, -37, -19, 104, 4, -43, -92, -114, 34, 44, 29, -96, -99, -95, -101, 12, 18, 107, 125, 114, -65, 126, -28, 114, -2, 9, 79, 69, 67, 78, -26, -95, 109, -81, 22, -61, 84, -16, -84, 57, 8, -88, -124, 119, 8, 35, -56, -14, -90, -73, 118, -4, -93, 35, -76, 6, -41, 98, -69, -108, -78, 16, -72, 43, -113, 71, -70, -51, -41, 62, -38, -58, 58, -127, 117, 67, 51, 34, -98, -13, -111, 13, 2, -101, -75, -22, 34, 42, -93, -106, 90, -65, -65, -82, 55, -111, -28, -114, 54, 0, 39, -46, 19, 78, 75, -116, 64, -120, -81, -116, -96, -36, 101, 67, -96, 14, 76, 74, 29, 67, 101, 68, -83, 62, 86, -64, -76, -87, 8, 44, -61, 31, 65, -120, 3, -82, 127, 105, 114, -58, -117, 52, -104, 117, 23, 4, -79, -44, -113, -65, 52, 83, 39, -120, 36, -80, 104, 46, 12, -61, 104, 99, 4, 53, 36, 91, 115, -8, -32, -111, 53, 6, 70, -70, 108, -68, 119, -3, -40, 110, -15, -94, 23, 36, -39, -87, 96, -89, -73, 119, 117, -45, -119, 48, -70, -28, -22, -127, -16, -56, -75, 72, 59, 54, -15, -57, -113, 78, -24, 63, 118, 74, -62, -101, 62, -123, 28, 0, -9, 30, 115, 47, 86, 88, -58, 91, 103, 121, 81, -78, 80, -50, -13, 33, 92, 107, -79, 55, -89, 34, -121, 82, -105, 59, 73, 59, 119, 72, -26, -122, 1, 41, 62, -11, -41, 101, -101, 79, 27, -73, -90, -2, -96, 10, 116, -86, -25, -117, -36, 13, -52, 90, -39, 113, -105, 71, -7, 2, 109, 106, 70, -86, -82, -121, 94, 58, 13, -124, 119, 34, 36, -37, 47, 23, -101, -96, -114, -37, -21, -37, -77, 121, -43, 25, -105, -6, 5, 3, -114, 30, -98, -74, -97, -43, 16, -84, -44, -56, 1, -115, -100, -46, -63, -100, 112, -106, -128, -2, -106, -116, -1, -43, -24, -73, -124, 14, 69, -90, 83, -85, -103, 52, 22, 58, -90, 77, -121, 110, 20, 114, -107, 102, -76, -6, -102, -38, 53, -100, -72, 118, -100, -113, 120, 53, -93, 61, -92, -84, -125, 81, 127, 125, -8, 99, 70, -49, -9, 86, 103, -96, -96, -40, 43, -48, 29, 28, 90, 45, -118, 111, -101, 24, -25, 123, -105, 124, 17, 27, -6, 111, -113, 21, -88, -117, 55, -7, -24, -24, 52, 39, -36, -81, 78, 95, 13, 121, -8, 116, -106, 45, -49, 19, 12, 13, -127, 109, -124, 14, 18, 84, -61, 23, 68, -102, 115, -34, 7, -10, 57, 107, -48, -53, -67, -63, -100, -84, -31, 79, -58, 56, 89, 40, 63, -37, 71, -7, -53, 91, -66, -74, -37, 48, -37, 123, -96, -11, -56, 80, -88, -53, 27, 7, -29, -124, -46, 22, -103, -67, 93, 42, -37, 18, -126, 120, -81, 74, 26, -54, 19, 86, -112, -38, -57, 119, 26, -62, -67, 126, -50, -31, -36, 120, -127, 123, -88, 43, 50, 61, 94, -80, 35, 41, -109, 71, 91, -118, 66, -60, -127, 47, 75, -52, -66, -125, -111, 44, 116, 9, 68, 115, 113, 8, -4, 39, 23, 54, 107, -119, 1, -68, -11, 103, -123, 29, -92, 15, -10, -31, 35, -91, 38, 37, 110, 9, 80, -115, -120, 112, 110, -28, -116, 63, 85, -65, 5, 122, 19, -84, 97, -16, -46, 97, 104, 28, -83, -33, 38, -18, -8, -126, 82, 81, 88, 109, 118, -56, 64, -96, 36, -10, -109, 74, -86, 105, 123, 110, -116, 91, 15, 123, -26, -121, 75, 63, 24, 94, -43, 123, 74, 79, -42, 74, -102, 57, -27, 116, 126, -100, 2, 49, 17, 28, 27, -58, -98, 39, 50, -66, -75, -23, -112, 64, -16, 60, -62, 122, 53, -42, 21, -40, 88, 2, 62, -103, 108, -74, -95, 113, -49, -73, 63, 94, 44, -41, -68, -124, 46, 13, -17, 11, -100, 58, -98, -40, -64, -56, 21, -47, -120, -7, -23, -51, 27, -99, -42, -109, -55, 106, 92, 110, 19, 32, -117, 4, -34, 65, 72, -100, -122, -69, -94, 122, 60, 23, -93, -84, 30, 118, -92, 88, -104, 23, -71, 115, 106, -118, 9, 64, -34, -71, 43, -92, -13, -82, -5, 15, 18, -11, -113, -109, -128, 104, 34, 72, -110, -59, -113, 69, -106, -74, -66, 115, -31, -27, 59, -73, 73, 120, -34, 59, 126, -93, 49, -53, 114, -122, -28, -28, 94, -37, -90, -32, 80, 15, 4, -101, -78])
        self._r.u8_1 = 232
        if self._r.u8_1 != 222:
            raise Exception()
        self._r.u8_2 = [52, 40, 13, 185, 137, 3, 173, 236, 60, 18, 206, 224, 231, 19, 31, 139, 177, 201, 100, 37, 8, 94, 145, 135, 217, 32, 59, 26, 243, 213, 97, 78, 145, 136, 142, 249, 46, 247, 20, 240, 47, 211, 60, 35, 170, 0, 119, 14, 36, 7, 165, 132, 35, 199, 33, 45, 27, 111, 135, 50, 210, 248, 118, 162, 199, 152, 28, 202, 222, 8, 191, 40, 134, 213, 36, 131, 198, 76, 82, 212, 26, 33, 219, 181, 213, 205, 104, 118, 74, 239, 226, 65, 161, 29, 158, 223, 175, 214, 160, 65, 229, 56, 207, 64, 194, 167, 85, 221, 82, 56, 182, 226, 206, 71, 203, 116, 201, 234, 16, 42, 32, 47, 149, 161, 173, 60, 195, 59, 138, 241, 52, 152, 48, 57, 137, 206, 201, 58, 242, 139, 149, 42, 185, 94, 27, 224, 249, 33, 24, 18, 148, 104, 89, 163, 94, 214, 232, 133, 74, 124, 117, 39, 0, 73, 86, 254, 186, 224, 96, 236, 113, 39, 28, 245, 218, 147, 215, 62, 191, 23, 20, 27, 32, 151, 25, 225, 3, 157, 221, 133, 124, 35, 41, 177, 93, 137, 198, 96, 129, 235, 21, 10, 110, 16, 25, 65, 153, 157, 139, 82, 24, 43, 4, 180, 238, 174, 226, 183, 56, 224, 239, 130, 62, 40, 12, 226, 219, 164, 71, 242, 179, 227, 53, 148, 38, 228, 151, 2, 249, 132, 56, 253, 10, 107, 241, 56, 97, 88, 198, 203, 33, 132, 212, 44, 239, 7, 206, 156, 144, 93, 44, 71, 40, 171, 60, 234, 89, 238, 114, 240, 145, 141, 51, 180, 85, 75, 125, 219, 2, 121, 53, 12, 223, 90, 174, 248, 45, 39, 151, 5, 155, 29, 244, 124, 156, 60, 250, 52, 54, 186, 95, 245, 18, 51, 52, 183, 105, 226, 245, 214, 94, 254, 98, 14, 46, 203, 225, 95, 126, 178, 49, 82, 159, 231, 170, 250, 63, 162, 156, 218, 184, 211, 76, 181, 97, 180, 239, 45, 135, 147, 49, 147, 0, 32, 22, 77, 209, 215, 54, 83, 29, 127, 80, 150, 50, 15, 69, 33, 118, 255, 168, 201, 2, 218, 13, 53, 164, 101, 34, 218, 110, 107, 147, 5, 78, 135, 1, 11, 242, 43, 181, 108, 107, 46, 176, 74, 2, 251, 26, 97, 254, 79, 204, 97, 41, 90, 126, 81, 202, 70, 30, 70, 50, 25, 56, 249, 245, 159, 6, 102, 21, 85, 8, 94, 115, 88, 32, 33, 111, 138, 229, 238, 152, 198, 74, 111, 86, 151, 165, 232, 2, 13, 42, 228, 219, 158, 227, 203, 47, 8, 83, 139, 184, 165, 123, 55, 29, 198, 119, 78, 182, 200, 77, 8, 5, 135, 164, 82, 235, 210, 47, 105, 53, 186, 64, 197, 24, 14, 39, 161, 187, 136, 58, 118, 225, 162, 203, 5, 214, 155, 45, 3, 111, 126, 99, 196, 82, 14, 156, 165, 134, 83, 179, 5, 226, 237, 151, 0, 219, 251, 160, 239, 224, 133, 230, 237, 221, 233, 12, 3, 189, 28, 251, 245, 89, 116, 113, 176, 40, 210, 216, 173, 154, 216, 111, 254, 183, 238, 29, 85, 142, 189, 89, 235, 184, 241, 2, 99, 138, 222, 47, 128, 97, 235, 195, 106, 118, 196, 149, 53, 188, 70, 113, 85, 90, 53, 179, 32, 23, 28, 95, 164, 49, 61, 151, 70, 214, 245, 245, 117, 172, 75, 153, 117, 226, 69, 205, 173, 139, 140, 163, 107, 214, 18, 111, 194, 115, 236, 32, 239, 168, 62, 12, 207, 220, 162, 160, 13, 147, 252, 192, 145, 150, 207, 112, 196, 114, 88, 69, 252, 193, 37, 84, 103, 108, 32, 205, 224, 216, 206, 251, 185, 17, 55, 185, 112, 24, 8, 209, 184, 156, 65, 48, 196, 236, 45, 97, 65, 218, 239, 59, 191, 137, 3, 182, 135, 46, 142, 163, 39, 63, 219, 66, 166, 8, 41, 175, 79, 77, 134, 159, 149, 118, 63, 191, 86, 103, 32, 2, 239, 107, 199, 122, 148, 93, 252, 176, 112, 130, 88, 102, 225, 199, 89, 100, 221, 177, 118, 102, 77, 192, 224, 117, 13, 213, 164, 87, 91, 157, 211, 14, 248, 15, 0, 165, 101, 185, 228, 203, 227, 44, 157, 68, 34]
        ca(self._r.u8_2, [20, 34, 154, 240, 82, 27, 230, 242, 253, 161, 17, 124, 80, 120, 210, 237, 179, 95, 224, 104, 74, 77, 148, 17, 98, 7, 13, 203, 155, 197, 223, 36, 207, 87, 56, 56, 76, 112, 100, 154, 40, 239, 13, 185, 77, 91, 107, 73, 196, 234, 3, 235, 40, 222, 224, 46, 47, 150, 167, 104, 206, 245, 20, 181, 133, 190, 255, 1, 183, 218, 5, 121, 233, 68, 72, 140, 250, 213, 199, 143, 41, 22, 238, 149, 235, 42, 170, 2, 58, 242, 91, 116, 62, 167, 113, 28, 8, 0, 199, 142, 8, 102, 60, 87, 147, 104, 125, 163, 135, 1, 186, 44, 117, 103, 186, 50, 68, 179, 203, 61, 231, 80, 45, 35, 231, 127, 93, 49, 154, 182, 1, 151, 111, 70, 127, 13, 41, 113, 170, 41, 173, 14, 129, 108, 235, 166, 153, 50, 203, 42, 43, 93, 243, 114, 190, 225, 12, 227, 24, 221, 177, 188, 218, 55, 6, 199, 162, 67, 152, 185, 216, 108, 251, 225, 146, 85, 220, 192, 36, 39, 20, 189, 24, 117, 98, 107, 215, 238, 145, 113, 40, 184, 110, 186, 66, 207, 164, 43, 70, 242, 211, 65, 232, 92, 164, 178, 3, 120, 1, 28, 247, 234, 210, 20, 61, 83, 147, 174, 177, 131, 229, 117, 211, 161, 73, 161, 224, 80, 219, 151, 131, 42, 37, 46, 68, 213, 62, 101, 8, 143, 146, 103, 52, 69, 7, 241, 55, 191, 104, 208, 100, 192, 48, 199, 30, 38, 148, 25, 252, 47, 18, 152, 142, 181, 231, 205, 166, 171, 14, 236, 15, 232, 235, 36, 66, 88, 141, 87, 66, 9, 94, 214, 100, 227, 207, 1, 6, 102, 170, 53, 53, 152, 136, 115, 251, 227, 218, 164, 20, 109, 174, 36, 135, 122, 237, 146, 226, 42, 202, 183, 112, 68, 121, 92, 23, 75, 34, 228, 131, 141, 52, 12, 132, 12, 43, 220, 33, 110, 30, 120, 244, 192, 128, 190, 89, 109, 165, 9, 25, 27, 129, 135, 80, 17, 217, 152, 237, 241, 56, 233, 78, 224, 115, 143, 214, 201, 78, 139, 50, 185, 115, 234, 31, 11, 190, 244, 28, 93, 13, 153, 78, 154, 62, 86, 40, 133, 29, 12, 133, 69, 50, 197, 127, 242, 14, 173, 70, 116, 243, 200, 197, 245, 249, 231, 139, 46, 99, 37, 55, 220, 57, 103, 163, 71, 252, 54, 52, 254, 97, 158, 155, 249, 243, 55, 112, 226, 88, 25, 29, 41, 109, 6, 219, 193, 89, 193, 164, 166, 103, 119, 69, 214, 105, 14, 20, 208, 56, 231, 59, 68, 49, 107, 119, 99, 109, 210, 234, 228, 111, 219, 32, 211, 172, 101, 172, 99, 227, 112, 137, 204, 19, 3, 111, 219, 245, 89, 106, 32, 108, 234, 81, 72, 27, 99, 151, 212, 108, 37, 248, 183, 241, 194, 37, 73, 230, 130, 11, 6, 122, 220, 192, 114, 116, 208, 187, 159, 226, 98, 191, 253, 226, 39, 212, 138, 106, 196, 153, 61, 218, 218, 20, 238, 82, 237, 196, 114, 135, 239, 221, 20, 52, 73, 208, 234, 99, 185, 218, 218, 47, 95, 218, 110, 165, 216, 121, 249, 203, 206, 213, 201, 138, 253, 43, 238, 131, 62, 229, 123, 69, 175, 61, 176, 180, 72, 120, 158, 91, 145, 16, 162, 70, 54, 170, 170, 60, 9, 226, 40, 66, 159, 139, 83, 20, 171, 32, 189, 140, 122, 1, 64, 144, 250, 94, 74, 91, 160, 146, 146, 17, 78, 43, 115, 166, 63, 81, 88, 83, 178, 177, 110, 93, 188, 29, 41, 28, 73, 40, 245, 49, 63, 134, 103, 135, 17, 172, 150, 249, 23, 230, 166, 31, 55, 203, 149, 19, 4, 101, 237])
        u8_3_1 = numpy.array([66, 135, 166, 109, 89, 156, 182, 63, 217, 36, 212, 158, 7, 212, 235, 154, 155, 52, 234, 220, 30, 251, 223, 77, 163, 204, 220, 63, 152, 39, 193, 217, 212, 4, 248, 69, 117, 164, 83, 149, 60, 44, 96, 78, 166, 212, 56, 87, 183, 20, 0, 32, 244, 16, 155, 4, 82, 217, 235, 203, 171, 188, 222, 15, 0, 109, 97, 135, 62, 185, 103, 39, 200, 198, 50, 190, 246, 161, 102, 32, 246, 11, 26, 132, 145, 141, 15, 112, 193, 105, 130, 61, 177, 104, 39, 164, 188, 131, 6, 9, 222, 109, 161, 211, 254, 73, 117, 59, 96, 146, 92, 148, 175, 82, 108, 215, 210, 4, 7, 176, 191, 129, 174, 224, 139, 166, 71, 30, 57, 246, 94, 139, 121, 190, 210, 181, 44, 71, 7, 118, 76, 223, 173, 181, 88, 138, 18, 146, 233, 135, 205, 101, 92, 222, 136, 177, 15, 167, 154, 198, 194, 185, 166, 21, 49, 193, 229, 153, 231, 101, 47, 40, 181, 138, 207, 168, 73, 19, 108, 15, 22, 193, 101, 151, 216, 153, 20, 140, 209, 15, 117, 246, 86, 210, 193, 254, 56, 41, 223, 107, 179, 130, 220, 46, 248, 200, 241, 173, 67, 147, 93, 87, 108, 13, 180, 112, 58, 210, 243, 94, 113, 140, 172, 53, 206, 186, 106, 167, 48, 43, 213, 157, 135, 243, 72, 173, 185, 62, 188, 162, 61, 19, 156, 215, 24, 216, 222, 56, 211, 151, 178, 251, 238, 47, 51, 141, 109, 214, 179, 41, 5, 190, 79, 27, 13, 208, 37, 97, 178, 83, 150, 77, 187, 179, 12, 73, 156, 167, 167, 106, 198, 157, 133, 80, 183, 15, 1, 204, 84, 250, 122, 232, 178, 103, 225, 110, 97, 23, 171, 88], dtype=numpy.uint8).reshape([30, 10], order="F")
        self._r.u8_3 = u8_3_1
        u8_3_2 = self._r.u8_3
        
        numpy.testing.assert_allclose(u8_3_2,numpy.array([23, 5, 170, 52, 174, 242, 108, 186, 30, 27, 38, 181, 184, 103, 240, 129, 69, 179, 148, 194, 57, 7, 19, 111, 244, 86, 238, 36, 31, 44, 193, 106, 229, 159, 23, 70, 184, 121, 243, 215, 187, 115, 89, 141, 233, 105, 150, 224, 245, 251, 44, 148, 149, 123, 141, 9, 77, 17, 146, 157, 112, 122, 83, 50, 156, 178, 186, 244, 234, 165, 6, 223, 148, 48, 189, 46, 209, 30, 203, 186, 4, 159, 162, 97, 97, 232, 113, 178, 244, 172, 54, 52, 252, 32, 35, 131, 178, 21, 131, 165, 203, 113, 141, 3, 195, 54, 143, 163, 15, 99, 29, 235, 125, 45, 50, 157, 255, 7, 81, 221, 70, 225, 119, 220, 98, 55, 213, 23, 219, 152, 148, 113, 89, 236, 109, 187, 7, 80, 140, 226, 71, 34, 17, 176, 15, 30, 239, 251, 10, 64, 170, 150, 245, 180, 83, 242, 138, 154, 226, 193, 119, 43, 85, 164, 187, 73, 19, 81, 119, 168, 160, 222, 100, 230, 27, 237, 43, 71, 144, 132, 212, 131, 241, 195, 181, 175, 41, 115, 149, 128, 238, 212, 134, 110, 224, 149, 217, 213, 122, 200],dtype=numpy.uint8).reshape([10, 20], order="F"))
        
        self._r.i16_1 = 2387
        if self._r.i16_1 != -13428:
            raise Exception()
        self._r.i16_2 = [-29064, 7306, 1457, -19474, -671, 22876, -14357, -18020, -23418, -10298, 1040, -2415, -22890, 4293, 25366, 12606, -31678, -15908, -11164, 20643, -239, -15149, 25272, 17505, 24037, 8264, -3888, -12405, -28698, 25222, -2506, -26405, 9561, 27093, 8022, 23338, -31489, 24117, 18018, 25324, -22192, -23413, -12544, -29675, -10752, -7108, 3021, 29238, -10332, -1818, 23363, 31568, -15057, 9565, 30520, 1064, 26637, -29070, 11149, 8534, -13775, -18359, 9626, 10662, -23713, 28470, 8840, -25279, 18175, 13675, 14955, 30323, 924, -13113, -21483, -6641, 12790, 26367, 27907, -1062, -24249, -13215, -18475, -11121, 2339, -2361, -7790, -26038, -6984, -10142, 8485, 17258, 6150, -25530, 9655, -11378, -805, 11574, 16094, 21091, -11882, 21514, 27655, -27624, -23592, 17985, 3154, -1292, 11059, 27599, -2741, -27514, -27353, -1824, -26419, -19633, 23008, 22184, 25855, -4965, -18710, -6802, 25237, -24262, 3253, -28401, -19864, -11711, -27668, 28671, -1376, -8600, -12691, -18972, -5265, 3901, -6694, 19018, 29612, 8047, -26257, 28662, -6164, 9407, -12556, 1421, 14531, 28000, 8499, 5512, 28989, -17181, -4051, 28130, 19063, 31736, -28399, -4663, 25520, -18490, -32156, -15267, 29245, -13510, 13446, -31039, 18030, 25419, 24594, 28348, 17845, -26123, 20713, 29810, -25881, -10534, 9038, -15614, 20117, 11436, 7078, 9985, -2758, -13790, 12865, -6824, 10924, -4750, 10127, -30953, -15114, -10407, 13061, -13241, 22268, 15514, -23952, -22361, 25465, -23395, -5885, 23643, 6634, 1768, -4390, -29064, -18261, -18954, 22866, -23739, -15996, -31521, -12816, -11246, -16029, 4113, -18809, -4282, -3892, -21196, 23692, 6488, -8949, 28859, 23717, -20358, -4216, 6700, -14565, 14268, -17978, -3865, 21937, 17864, -26293, -9181, 28460, -27725, -32278, -13856, -21763, 10310, -4066, 32078, -8132, -14677, -11698, -23123, -30968, -21889, -2192, 29299, 623, -26725, -29380, -18038, -25037, 26361, 22773, -31157, 22096, 10336, 26530, -74, 3820, 52, -28257, -29110, -29891, -23752, -23846, -15516, -21528, 14792, -4286, 26942, 17922, 21495, 16249, -30305, 3056, -22525, -4198, 28613, 2695, 30388, -18066, -5162, -23655, -25604, -28244, -1196, -6888, 17903, 11721, 13555, 32445, 31800, 11125, -31537, 1400, 25992, 2289, -19330, 29486, -27986, -6690, 9402, 15366, 18268, 29476, 27543, -26894, 28279, -18810, -14493, 6622, 9548, 28691, 30421, -17983, -25525, -6167, 5825, -25283, 19498, -17719, -3858, 8518, 16017, 1325, -16864, 17874, -796, 3678, -32078, -19712, -32173, -25895, 27397, 23474, 10508, -6009, 25388, 17327, 26954, -23909, 27502, -15956, -1770, 1343, -30108, -12923, -3584, -30762, 3386, 18090, -14048, 31833, -5312, -32483, -1358, -28372, -24388, -26718, -17132, 22775, 16924, -8991, -12343, 16874, 19515, 21977, -26287, -28976, -18071, -24572, -8740, 29859, -21779, -20087, -928, 31016, -11442, 16890, -12445, 26140, 23581, -18737, 16033, -16426, -27860, -4853, 6669, -2678, -14760, 15011, 25458, -24354, -4704, 1983, 20655, -3885, -6015, -20382, -6168, -8801, 21318, 21969, 15333, 26667, -15860, -20356, -4265, -19871, -30123, 8082, -5186, -5294, -7119, -23580, 600, 7195, 24630, -9810, -23846, 23416, -26102, 11875, 25362, -17002, 32482, 3733, 8434, 18377, -11770, 21843, -19779, 27194, -16918, -22013, 8387, -1686, -27228, -8013, -12979, 30682, 13008, -32188, 24547, 27126, 12811, -14996, 16305, 16467, 21204, -16620, 20671, 31564, -23123, -31995, 6335, -26234, -8852, -19185, -19636, -15411, 22541, 10295, -14022, -19669, 25371, 4407, -21395, -20754, -31164, -30944, -29004, -28877, 11049, -11492, 30171, -3452, 20020, -30618, 11178, 7734, 15658, 26485, -8697, 24391, 14520, -9994, -11594, 21221, 21327, 22058, -6275, -2272, 20061, 11315, 26569, 21368, 30729, -15573, -25453, -6160, -20236, -29377, -22591, -11045, 19992, -18369, -30261, -32159, 27646, 18350, -6134, 6723, -13437, -23761, -22496, -12447, -1184, -17634, -20936, 30815, 32042, 10621, 17252, 9705, 4169, -8075, -20113, -21095, -20310, -3917, 23438, -1628, 7291, -18739, -12603, 22036, -14198, 26960, -24387, -20204, 1370, -23683, -27522, 31684, -24806, -20567, 606, -14584, -5656, -6025, 20297, -18716, -7075, 21089, -26036, -2747, -18800, 22214, -31288, -31916, -32543, 14577, -6407, 17079, 4683, -29301, -13707, 4296, -2247, -25994, -322, -26904, -4444, 24454, -9676, 29589, 30545, 17995, 20596, 24835, 24545, -15782, 13901, -26644, 4655, -10543, -24521, 30118, -29985, 3163, -27379, 24263, 19271, 12184, 7695, -6249, -26163, -16952, -18930, -22627, 5625, -16862, -29626, 8000, -26542, -21846, 8377, -6837, -30324, 10752, 19676, -31224, -11472, 27419, 4926, -67, 7107, 3149, -18440, 18652, -32124, 26094, -7015, -10179, 3878, 28709, 4453, 20330, -27548, -18729, -7550, -29815, -3110, -14705, -16383, 16020, 15466, 5411, 23434, -14919, -1289, 24403, -2409, -28824, -5982, 21794, -26131, 11683, 28742, -21742, 7952, -9041, 28373, 12434, -17665, -19141, -31576, 650, -11103, -26587, -17144, 20830, 1468, 23981, -6189, -1574, 11151, 9314, 12189, -19801, 23310, 3132, 1145, -5231, 1387, 3230, -15314, -17253, -29867, 22979, -28009, 7686, -31739, -16295, 23702, 9141, 18300, 31485, -11124, -30999, -26289, -32371, 7900, -5057, -8202, -15209, -26424, -2712, -25152, -7174, -25019, -14712, -10703, -2809, -9, -17905, 20882, 31301, 8989, 20139, -235, 707, -23246, 4519, 5621, 9609, -10846, -1873, -17425, 30184, 23010, 18718, 24429, -2168, 23884, -19503, 9419, -24927, -16803, 11872, 16572, -30227, 4356, 18692, 3493, -29119, 16296, 1632, 8736, 7806, -13904, -26360, -27538, 6861, -8093, -6184, -445, -2181, -9581, -2722, 22857, 4100, -2585, -25935, -26353, -21284, 7497, -5385, 10974, -7747, -19865, -1205, -12806, -7505, -29792, 16793, -2743, 30123, 9379, 17381, 4947, -15940, -3652, -1797, 21012, -10333, -27953, -1716, -28455, 29598, 17497, -5363, -3990, -29921, -27210, 8825, 8046, 11062, -13647, 29708, 1335, -22559, -28213, -9634, -17768, 32543, -15641, -18576, -23375, -25305, 11930, 11338, 28057, 12085, -17504, 29366, 3513, 26451, 29229, -24338, 1541, 18497, -8424, 12969, -20692, -24323, 1876, 8233, 10893, -10761, -3855, -21938, -6268, 32120, -25120, 20729, -371, 25746, 28224, -25625, -22924, -30667, 13100, -3160, 28610, 2206, 977, -17607, -2173, 24212, 14451, 22276, 26268, -10890, -23818, 30052, -18695, 14828, -16839, -18543, 17056, -3715, -7372, -16029, 31885, -20617, 10847, -12068, 29898, 12865, 30922, 17546, -8489, 19324, 584, 9798, 2421, -17432, -10905, -14728, -7920, 6909, -11895, 1031, 18387, 20783, -28969, -535, 31095, -30709, 28734, 15322, 28585, 2100, -6234, -28704, -2813, 22201, 16682, -1576, 9351, 30508, -9447, -21309, 3023, -19963, 13739, 8398, -11148, -9348, 32285, -22925, 697, -9683, -1106, 11252, -16321, 31326, -22577, -107, 3355, 22765, -10391, -26902, 10375, -2846, -21378, 2649, 1284, 23016, 6884, -5356, -17352, -9866, -4313, 15950, 12058, -32753, 6124, -9833, 8828, -11711, -28691, -31249, -31354, 13039, 29161, -17382, -5879, -21118, 11736, -29024, -15440, 9364, 28121, 16093, 20123, -26504, 25957, 11858, 9932, -11333, -15770, 3678, -18107, -25852, -21244, 2225, -13899, 2050, -21656, -7352, -3896, 4161, -27416, 12792, -1807, 18088, -9590, 1851, -11661, -28665, 10986, 18137, 22612, -1617, -11139, 19293, 4080, 8597, -16998, 17228, 6587, 12316, 12640, 1001, 25972, 29637, 27715, 5577, -12737]
        ca(self._r.i16_2, [-31396, -31525, 21618, 420, -4709, -28067, 13158, 30433, -5226, 177, 32486, -24906, 14134, -12316, 815, 14221, 25078, 4427, -24570, -2404, 32275, 16625, -18211, 8224, 11466, -8053, 25673, -5521, -3629, -28951, 16888, 3476, 29692, -16313, -6124, 7022, 20178, 363, -26079, 6451, 26271, -9454, 7484, 9626, 18076, -32556, 8132, 22992, -22922, 21831, 9586, 30404, -24016, -22082, 17247, -120, 26786, -30338, 6445, 7710, 12192, 1787, 10373, 8221, 9130, -13265, -29233, -30762, 1430, 29737, 1503, 32216, -27766, 25651, 24365, -20157, 18077, -9909, -2427, -14841, -32092, 2606, -29807, 31676, -2674, 21400, -31068, -7881, 15682, -5497, -4695, -7670, -26719, 7180, 31393, 20250, -18099, 12591, 18352, 16854, 24663, -12445, 3967, 13535, -9324, -28110, 13977, -23172, 14216, 30378, 6653, 19203, 7298, -23065, 18301, 27111, -23775, -27934, -4797, 22319, -5834, -10073, 21636, 26423, 20007, -23826, 9433, 24251, 29231, 26264, 2698, -10085, -21536, -27028, -24687, -3768, 1511, 25182, 29258, -17177, 8345, 9571, 7512, -28872, 10123, -10644, -7612, -13232, 24346, -25900, 28049, -5366, -8968, 5589, -21840, 21891, 25327, 9095, 4382, -30532, -21172, -27251, 12320, 30065, -29933, 19371, -5654, 7815, -26289, 12614, 13834, 29357, 25201, -32309, 20042, 16706, 2312, -20975, -5346, 1820, 9166, 20644, -3811, -12569, -3711, 11580, -24719, 29072, -26433, -12475, -15326, 1071, 10750, -17120, 21953, 11265, 3513, 20747, 32085, 9898, -24426, -17231, 21523, -26126, 8783, 31762, 6629, -32554, 28071, 23409, -6423, -25261, -13387, -2606, -23878, 5003, -8970, 16999, -11501, 15402, -31573, -12730, 17823, 3018, 13959, 6305, -24676, -28537, -21613, 15353, -31686, 7264, 14978, -2702, 25179, 16061, -5220, -20419, 17023, -5104, -17836, -24537, 30832, -8236, 20473, 31052, 9467, 25660, -4882, 28392, -16236, 15059, 18409, 2709, 9637, -28754, -28261, 14474, 281, 24844, 25464, 26378, 8331, -8080, -10826, -3874, 21290, 1599, -375, 8436, -25280, 25907, 19361, 6448, -26639, -15164, -12896, 1476, -15877, 23427, -24851, -23147, -11525, 16456, -23417, 31519, -10431, -14222, -28958, 6194, -7802, 17086, -5885, 23977, 29347, 3648, 29674, -27985, 1834, 30677, -30455, 32438, -23495, -10403, 10370, 32713, 27187, -4733, -16686, -21336, 7793, 15123, 17046, 28022, -23346, 21816, 16826, 19747, 21625, 17895, -23683, -142, -27996, 6601, -13889, 24112, -19505, 24425, 11673, -3507, -9946, 20693, -28974, -30639, 25202, -24295, 27916, 5920, 17325, 29121, 12475, -1179, 5379, -21558, -8684, 7551, -8536, 8673, -13435, -3870, -6389, -26193, 13662, -17405, 3305, -15401, -10014, 6645, -9322, -15604, 7511, -8894, -2421, -21984, -12209, 16631, 19022, 11644, -3624, 25297, 6613, 4801, -17413, -12780, -28095, 17986, 11066, 22207, 17717, 3613, 14987, -19860, 12693, -13482, 10471, -24561, 32333, -25968, 7244, 7005, 17820, -18897, 13208, 16753, 32551, 21296, -15046, -3886, -13628, -2550, 16059, 1090, -27901, 21254, 21726, -17180, 5902, 30053, 31909, 25120, 3958, 18119, -25501, -4974, -11464, 24068, 19720, -8793, -9011, -11975, 7025, -15041, 21009, -15123, 3647, -28657, -7700, -10174, -16814, 4848, 13044, -20100, -17977, -29197, 31169, 15459, -27346, -23297, 1639, -27165, 25474, -4981, -16728, 24962, 6895, 16619, 12965, 10990, -13275, 1119, -10243, 10364, 3763, 3565, 31542, -22261, 15267, -31448, 13298, -8408, 511, 19296, 24390, -25118, -29033, 11413, 25520, -23675, -12986, -3952, 7133, 9587, 30652, -21444, 23859, 22577])
        self._r.u16_1 = 54732
        if self._r.u16_1 != 60981:
            raise Exception()
        self._r.u16_2 = [27153, 43996, 41432, 58304, 12942, 58876, 28186, 11185, 10827, 17769, 13091, 23017, 17671, 49113, 6987, 35547, 2024, 33499, 26956, 11772, 20498, 42863, 65021, 31883, 61940, 6622, 59235, 6137, 51350, 48773, 57425, 56027, 38431, 12927, 54445, 12445, 27087, 33727, 51305, 48371, 7488, 32356, 59057, 10185, 57955, 46571, 326, 43692, 43661, 25990, 42979, 8957, 59425, 9205, 42414, 10752, 5573, 37965, 14726, 60329, 24708, 38900, 13804, 12531, 19400, 40437, 3102, 15384, 9922, 48890, 655, 58588, 55933, 56542, 20001, 11584, 62303, 19888, 38565, 19636, 21974, 26170, 61468, 27655, 30144, 38002, 59044, 33839, 58996, 7516, 41660, 26146, 20606, 9052, 41933, 43479, 45221, 37564, 60731, 9073, 5647, 25184, 21426, 47334, 48473, 57336, 38775, 56475, 55863, 33194, 59184, 17109, 10792, 35915, 37682, 18123, 56383, 55538, 26718, 29128, 5521, 51803, 22632, 19827, 32242, 38280, 51359, 10800, 22661, 63621, 58920, 22073, 59845, 56670, 24860, 21801, 22225, 45849, 35453, 38351, 58831, 63677, 49340, 58625, 59284, 8244, 22567, 42599, 39629, 44023, 55480, 23933, 54557, 36080, 18074, 53598, 26233, 46291, 10356, 982, 20899, 9791, 43246, 40308, 38630, 40376, 23805, 35194, 45957, 56662, 38493, 50650, 41811, 40225, 20212, 10975, 38947, 14443, 62213, 16366, 55641, 20063, 28304, 34336, 48695, 11196, 20382, 32670, 61020, 27154, 60750, 42124, 64065, 45687, 32335, 60310, 14344, 39059, 31190, 12119, 57101, 13774, 58824, 54012, 32689, 12347, 13368, 42262, 15453, 61631, 51804, 27658, 53000, 30414, 42427, 61957, 16811, 19230, 23527, 24728, 60773, 28925]
        ca(self._r.u16_2, [28720, 34616, 62158, 23483, 4737, 55943, 56769, 39984, 64598, 51111, 51377, 21150, 23557, 7441, 55455, 37627, 34814, 32887, 12525, 7947, 30317, 19555, 62568, 26666, 35231, 38385, 56455, 37676, 47722, 60644, 1037, 61159, 64542, 21655, 57027, 46262, 64919, 49927, 25520, 56784, 4424, 62463, 26885, 43771, 5149, 7537, 28615, 2661, 41921, 63221, 30209, 37930, 9683, 52406, 24968, 50022, 51469, 57731, 65408, 57019, 62539, 10550, 35726, 34413, 46756, 63743, 50854, 1075, 36709, 52737, 38989, 14194, 10541, 39864, 7632, 6335, 37317, 18084, 18417, 13903, 41588, 4410, 55813, 34564, 62937, 56211, 51771, 32961, 36295, 58221, 4107, 18571, 55106, 52625, 36243, 52487, 10236, 36619, 24439, 41204, 61791, 12156, 5380, 26272, 45613, 37851, 60070, 38759, 33502, 2147, 28146, 45977, 51698, 33640, 38956, 48664, 51750, 42329, 6020, 42645, 44393, 47459, 64398, 2683, 18251, 5304, 38780, 13706, 58825, 12565, 37762, 21280, 39402, 56275, 25627, 41371, 39366, 61829, 8892, 26779, 311, 47322, 26823, 8265, 12495, 38802, 20059, 32724, 7618, 37557, 57579, 33492, 20655, 19185, 57872, 51794, 16721, 52071, 52584, 57226, 28584, 9690, 10117, 41708, 38496, 56164, 53099, 45246, 34962, 41133, 9780, 39381, 53780, 14719, 64870, 38034, 15484, 24376, 39802, 58424, 52906, 45995, 50396, 21981, 32813, 15889, 33981, 58999, 48157, 23717, 24644, 18059, 47204, 45872, 26705, 46193, 56697, 41192, 56316, 43920])
        self._r.i32_1 = -9837284
        if self._r.i32_1 != 898734:
            raise Exception()
        self._r.i32_2 = [-966485083, 547919123, -1194190604, 1550099195, -86896479, -1346998266, -111775936, 1595883280, 95277373, -483593724, -1194231658, -1664247993, -1125879490, -774112094, -908971354, 1257430739, 278831106, 2146175077, 1216734947, 108534888, 712376825, 472415212, -413092215, -186896831, -983274891, -814159203, 491332674, -1080086896, 305863740, -588641755, -1173634854, 1500595228, -1011735210, 1396816521, -1843412764, -1174697157, -2042333138, 1720132956, 1179474025, -734588992, 1928960553, 653905969, -1152761709, 206317133, 1066603916, 1788908206, 1901091544, 1610435338, -1051581785, -1953636422, 1076388567, 1462395490, -237116033, 454691362, 1619801391, 1845599647, 1868321380, 1723200218, 766619638, 105371815, -877177590, -1885723170, 434710859, -1146593520, 209995917, -1047842747, 465673729, -2084508649, 1968279245, 587205365, 1583233886, -1752333729, -114021301, 59161723, 1580036234, 345745650, -468378351, 245003371, 1673787261, 1587452615, -1303597866, 822157520, 64527339, -4281296, -64380840, 37142322, 500059241, -1469346913, 11916922, -338760031, -2025817128, 83726551, -754215578, 368103720, -821582629, 717962460, 2144471201, 223671109, -199755353, -841621639, 1540857720, 1804628518, 2118963299, -1595232224, 400238135, 933224750, -215585205, -985264044, -988901458, 986847698, -1856650438, -651146661, -978168494, -532172509, 1691932093, 1876106029, 525396768, 1743090554, -162073951, 806798458, -1403694340, 559542160, 207806919, 590536881, -1650417281, 1858408059, 1983218923, -1543131382, 1706115652, 2119926306, 1424134413, 1205448675, 1811525641, 861875958, 2007619106, -845489490, -55633190, 1816674890, -614507920, 286578932, -1342898663, -1261324825, -1506404786, -1806499804, 1974771054, -98303714, -290587554, 1090231453, -985937256, -839357172, -1416681172, -1007624128, -1578990962, -1728169897, -844916635, 506302833, 667662716, -663874058, -1362455403, -2060230793, -1319792032, -2017894569, -1689519196, 479605380, -117340189, -1052087080, 1498560347, -870303564, 1098382715, -2086046098, -1642542296, -628648039, -719920250, -2060321401, 525438216, 281529006, -459505556, -1796557506, 1024549346, 1853853925, -312303325, -1579857332, -1269984071, 473304768, 721731410, -1737559733, -438494623, 1802127802, -1731233704, -1390726345, 485787940, 943002107, -187237495, 1869312126, 442020547, -87826467, -696183927, 616713843, 945472556, -972856985, 151686386, 1488133092, 175341883, -1180397098, 948926458, -503479659, -1267580010, -388943415, -1363469783, -1527776457, 268299441, 191219066, -1024035842, -1475980660, 1828759673, -1442955646, 1790351422, 574018056, 1803848768, -2095818881, 1210053959, 1551296999, -942626269, -1321443296, -1859662526, -2071020753, -1184904851, 988848078, -412054768, 1493935320, -196557049, -704875093, 134497249, -1224190928, -2068208534, -965095455, -564081208, -1156543555, 461090533, 701882132, 910649700, -1878641070, 1446533896, 1970740772, -204663013, -1698033554, 972688594, 1110078968, 810548960, -1509538061, 1958800693, -543420990, 217640235, 1880493927, -1671735529, 1137613142, 2072545208, -414851757, -1785997391, -364718164, 450315208, -993471993, 768175939, -1566579292, 85961510, -1827000830, -1893503205, 869202084, 713571555, 680257288, 1524440291, 1741022434, 561415328, 1990319608, 1142451744, 39401847, 1221297801, -2124038766, 1215377498, -2068455826, 560063055, 383922313, 7329552, -1417241590, 1973186515, 358937975, 1808732034, 894888594, -1620703934, -1409454021, -224706429, 631015427, -701827114, -1980442971, -1243431585, 1865483925, -1340041763, 259984294, -1443453841, -885229413, 973067512, 780961235, -282514052, -1110338800, -722213025, 1714985605, -1287879595, 1509400751, 324286798, 1011968175, 1774625427, -335835050, 1241953488, -485251005, -2023480468, -1498664236, -1676758135, -2078759270, 368391173, 1770332091, 602035732, -1157125163, -726848951, -296396612, -418101410, 1516209091, -433026570, 2065899179, 286245383, -1428168800, 310716072, -563791242, -1325785953, 1826452534, -23905747, 1034013849, -1085065618, 1611085765, -60799609, 1082236453, 561831452, -1827984069, -277941810, -2097393299, 1609593516, -1947366285, 2039786925, -2039232768, 986451997, 2119304777, 49748214, -1530450382, -588012225, -142349556, 1234615466, -1482467714, 728929313, 438851997, -424861037, -1835013005, -674124377, -1634348548, 1081331853, 2111035427, 143997944, -1158230701, 4815417, 2122369877, -77009634, 282329472, 2124624001, 1395262123, -602351149, 1496495731, -522090375, -1089014497, 1060099030, -514142834, 624755360, 101709947, -259648574, -1721466978, -1470128315, 1344990842, -2138737258, 101466176, 1692425055, -1157926775, 592741389, 1813083585, -769169250, 1770253928, 1208684737, -702112980, 1001273019, 1705993099, 1407346099, -2142523547, -1355363485, -267899641, 449328343, -987691219, 438101969, 572223309, 379113218, 1466899667, -623010689, 2125548615, -145443483, 631502783, 1728343290, 1277749965, 1997442958, -1429886186, -537022197, 763891225, -1238739363, -821719020, 940172257, 114964281, 2090254185, -966856290, 1594918376, -1912990965, 1325705675, 1909184548, 837435170, -590257590, 1748272543, 65934393, 2073600222, 170572472, -1901011521, 2133543824, -1551997487, 1825478098, -941111977, 2081346119, 1276024247, -1737235139, 1172151357, 1861822828, 2017860579, 2079359170, -712881259, 353483674, 1081877284, -310138121, -1387900910, 1509477224, 321767828, -334162604, -1426416668, 122601289, 900426562, -1974038173, -187934215, 1716122553, 536633084, 653559614, -106459236, 612788932, -426096009, -407044580, -231495552, -20598604, -1049988598, 1707164387, -907341708, 1018148334, 420273830, -717817139, 746522674, -1091234728, -769304365, -1783917863, -1773360712, 1421244394, -1489877988, -1400774353, 704671809, -523850319, 107160908, 2024605373, -799692707, -2092464355, -948361722, -1132761744, 429369122, -76789764, -1551036156, -1351725409, -11045966, -1316255914, 1121595316, 1364255025, 1812124631, -1134809617, -1230048918, -1823006270, 103013418, -1985924618, 1276352832, 1604221273, -237209206, -1822616069, -1899068745, 1297703890, -240045011, 810578223, -1422419765, -1418704599, 1034032605, 2085440174, 607645733, 716362365, 1235513555, -1211579413, -261155896, 2022908495, -146539076, 1167671484, -211945140, -268072629, 40741212, -317939085, 728869511, 1342184697, -522128634, -716993901, -885638830, -1889540956, -518758183, 194076888, -263047735, -53295197, -2039369321, -1402107402, -1232069700, -860885703, 667080371, 2003791013, -1792537425, 593890515, -302918528, -371191726, 915728277, 1775934623, -1884658077, 1983888460, 298800478, 1016157169, -1717781878, -1076292572, 1732073196, 542964773, -773239025, 1070547456, 1719362726, -1490080193, -1399780184, -58541011, -1591258, -1250990694, -443129975, 1822357515, -1774941626, -1423917059, -1324183435, 1247654078, -785941226, 208759350, 1371670412, 1903510098, 2128083745, 435649658, 1127890999, -1861063799, -188564302, 1199643492, 1891452416, -217657738, -67141750, -1266789415, 2131626424, 2098938511, 1874390421, -1698831352, 1922731129, 1143118810, -2026197630, 2086052126, 842500141, 287962959, 850955114, 2012362088, -817258418, -1072214227, 978057684, 992062798, -2041866817, -1611489850, 1663409654, 112766564, -1689406122, 1616786320, 556057860, -1680102493, 867719167, 453575899, -191805706, 1712061526, -744377824, -615870979, -1980362202, 1649307499, -613527529, -514007552, -354868527, 740361284, 1191787483, 1421727561, 1066283904, -452434665, 2020141000, -1987374530, 412400833, -621803967, 20900810, 559102704, -443346658, -768206607, 1402289809, -1479041896, 1359182666, 84692384, 1919671125, 1665432592, -1427511811, 1351138729, 714150331, 1584608034, 1063897075, -470363603, 1537682572, 760337828, 270984358, -1339485809, 467876006, 1515737109, -2141726672, 1046916347, 1259950801, -835983188, -2073384503, -697440699, 1343223043, -1288734811, 27645887, -1066885181, 2063044057, -56607701, 319902811, 960858771, -423030408, -812161836, -1112301146, 132484238, 1783289397, -2018957458, 450584409, 1012115988, -2101400823, 1667035362, 1107203875, -1865977929, -723361763, -1343871789, 1135679266, -1675492453, -140706303, 1364740541, -1551211173, -2009393394, 2000971427, -344052593, 462623413, 143090848, -1640955654, 1157518396, 659813664, -165571783, -761091080, 1439584252, -52830785, -1885945630, 1884406245, -555522218, 1323853722, 930747959, 137706091, 555548831, -1337759477, -1009674506, -1977870785, 1180081172, -687421630, 194151065, 1311924712, -866937125, -137781558, -698706859, -1895205467, -1848499551, 1896490516, -6509636, 1269553250, 186532024, -955818569, 1845517066, -400727025, 1078611153, 863814973, -1229137047, 1718754324, -216510561, 1988750453, 29465919, 1428890551, -62281515, -937668540, -1508270436, -927907488, -505451885, 1033857489, -389957828, -2065486196, -352295525, -2105963968, 1299134698, 816779483, 156423679, -1354381381, 1887465750, -2105822745, 642600242, 1123616314, 188710252, -1703216607, 1459661161, -1941560289, 601336479, 1863482085, -857985266, 794305967, -1660447453, 226783646, 241199673, 583367867, 849630317, 1914170489, 565711020, -1488638620, 609086194, 1720536967, -1694564352, 692492707, -1506800749, 730802235, -157471351, 242744029, -164780657, 554729192, 826406260, 2052603794, 1509424364, 880799424, -742089480, -1122708577, 1850636033, 1672099719, 1908731732, 1738334895, -2040611202, 1682998097, 1398609974, -1324949149, -975919403, -1450888087, 1833224637, -619514125, -990582005, 1412067944, 886169183, -391523199, 607372595, -1262130460, -1519841199, -1773159746, -1708684329, 1508540061, -445129927, -861216001, 449901651, 1557438209, -1188736704, -630147206, -679376511, 1198115538, -382787307, 697875997, -22939436, 239787497, 500731101, 195546534, 1392914720, -187209041, 455847608, -2049957759, 766204445, 1368826958, -2042625013, -180992444, -713812831, -114800611, -607409323, 162793232, 2138008530, -1531267188, 868044052, -1630059848, 1621859247, -1597211643, -1129166747, -1199701638, 1770783044, 36166445, 1439401965, -994866018, -960772827, 2001685784, 441293150, 408861924, 905891633, 1537313206, 400637893, 61265814, 1571963795, 838433145, 2065601099, 778646834, 316955585, -2087195141, -1175880744, -1556081321, 1057881099, 261925029, 1208410025, -1666750702, -1564870443, -1780046839, -921180273, 1249930686, 22741986, 1111587522, 1806539596, -2004101869, -1217186294, 1838807150, 1025186692, 1739799205, -970775152, 1248070355, -507661275, 1255915477, 227039459, -1806354804, -1933273622, -1702447540, 998405321, 1478470466, -1376315847, 30712562, -2027352328, -1528293401, -1983304959, 504320567, 1291680060, -1444744047, -1127727805, 1549237293, 1204875828, -290551371, 1890491263, -60192594, -338589164, 520299155, -1570639410, 1365342605, 717971876, 2100041137, 950014485, 2111827591, -1614588413, 1565446784, -711540009, -612602607, -1878381653, 759406734, -1354242425, 1036377793, 283764256, -147639272, -280351513, -314754805, -993828539, 998353033, -1202064568, -1057618001, -395391049, 1549721165, -598972723, -982907535, 1557165381, 1891640427, 654353458, 1775642645, 935383528, -1688413182, -419838142, -1817002350, 1500587707, 439484714, -671255505, -1446765092, 1379929086, 284924340, 322973021, 517663367, 1269409562, 1635098653, -456602725, 216521789, -390880857, 22702718, -141949792]
        ca(self._r.i32_2, [-461364931, -881174363, 1190512124, -652344200, -1904465790, 654215830, -8237446, 1554134258, -1171405181, -2097329372, -1168547037, 4964041, -162499187, -1566779923, 396658647, 1372847452, 1952977117, -2055030887, 1369558008, 1159869637, -151488968, -1230916956, -1662654082, -692556634, -2108882739, 1919783279, 86726599, -479175753, 368307099, 263085896, -1297854452, -475865862, -1052798892, -195216089, -1808717864, 1435851230, 213845163, -2014435943, 1958739019, 1950538379, 195043354, -2094251280, -552928187, 212026163, 1882789473, -1701156512, 700729029, 617009319, -51379635, 1437981860, 143582562, 1759700160, -1043283958, 790685144, 1053455552, 888961142, 1884764193, -574487120, 205387093, 1706716858, -1564706331, -1119162850, -320357115, -216356729, 1133115157, -1585595150, 1163420546, 2095530513, 959051309, 1266503031, -1940662617, -1207768369, 2071048923, -247500208, 729695364, 1732441574, 919515230, -1307758899, -1362232635, -985845056, 1183002178, -967666429, 61839483, -797969544, 1019207261, -2080745651, -1493399698, 448039065, -1006260032, 547484182, -433873666, -145482008, 1266128764, -374269118, -148627528, -481205875, 28560825, 1620567461, 160877005, -152736921, 566726869, 1690610724, 1551218429, 129384906, 1756514951, -1619123979, -1635458102, 461420293, -1025697720, 1074881682, -1342853402, -2024581138, -1021476707, -979756855, -2061951658, 495595484, 1072057242, -1075816975, 634930689, 1462757877, -355459145, 113806554, -1586994022, -1759236007, 1642313755, 1844726616, 263774839, 865591847, 1137711548, 568540382, 1697402204, 1287333602, -18557107, -543522023, -747044673, -894978937, -1633590316, 1469569043, -1916659051, -245350462, 558791729, -1069756095, -1671183103, -675709621, -1496240619, 1002596182, -1049603233, 1067628357, -320684962, -1756926613, -1978637534, 2115134917, 293851213, 188870457, -2033713174, 316694162, -1680926305, 1578104820, 2019431451, 1672278268, 518272185, -366138444, 1261822504, 1003789835, -595796762, -1764183978, -1066900678, 1415600408, -173332206, 341584118, 1836086928, -77555270, -1989963843, 428500682, -489840295, -1096671034, -1915424250, -1746745758, 473428620, 1155878488, 1534484342, 1866809635, 2125417205, -356683367, -724519561, 476765866, -509611460, 1067343485, -1663160103, -1973204454, 1891962125, -1486851183, 539703058, -78175960, -1038870474, 585234261, -1015599511, -1860840029, -1939494917, 2120890829, -1396051426, 442584714, -559475888, 1852553473, 1370937853, -189979498, -1942748392, 575014321, -206759426, -31154557, -2070305927, -1863241823, 976830155, 405210820, -1810403626, 1246769487, -1690543149, 1313271912, -351123144, -169833423, 329135592, 1471013659, 1018659812, -1227714342, -191860948, -1335651686, 883360682, 836140176, 533570354, -306737045, 503171813, 1574245195, 486740175, 2103577114, 1369514515, 631086314, -1519000748, -1651625120, 2072505877, 343400009, 1919137338, 1103988337, 2071554186, 150773570, 2097705645, -130202734, 327475069, -884235865, 52111222, -1080547500, 682409781, 1559839293, -1958998234, -668500619, 1652828958, 1898194722, 1411170984, 2027809940, 2057915321, 624976316, -1590230095, -39277437, -399063086, -199887533, 1695889089, -179411470, -814891514, 441001215, 228328910, 1969824685, 1673102538, -939256124, -2021849575, 1292458519, 1963232860, -701199322, 1898059105, -2045458245, -896773856, -465102206, -1132267068, 1715928377, -1576771507, -76241412, 1187144803, -1067322651, 570283207, 1328683328, 1679817753, 1351131251, 218112167, 1288274663, 1769551475, -1459879021, 907399627, -129113618, -816814174, -281922806, 1308242407, 959061391, -643658909, -1586885260, -731576338, 872407494, -1435528398, -978470065, 561011867, 2094464646, -1961457104, -370593344, 173444003, -1787659154, 1403917210, 1314481998, -2064760703, 627159779, -1209896425, 950681678, -1599356229, 1797678336, 1407713282, -1860763990, 1818135625, -797982794, 1766490463, 146950743, -573489171, 541336457, -786031692, -823206893, 472702619, 301835709, 903962039, 334036788, 1308489144, 1982571588, -1297489003, 1027291239, -1050223998, 1301065587, -131811840, 840706119, 151612697, -1514662009, 2045477247, -78244632, 1428738052, 999845946, 632205998, -2084777797, -1263080892, -1527740973, -1052672864, -1148385231, 2118437588, 64244951, 610247700, -192213951, -1677840790, 695619117, 194487568, -1064818224, 567953693, -556351633, -358984117, -543035561, 1299534234, -1814192015, -1987974286, -251589327, -1550216573, 1039391427, -648231381, 209808513, -1809205905, 425289643, -1478441699, -499830484, 895438284, 1388891777, -141187536, -1921173432, -2109700894, -629643543, -1992180854, 1262181466, -1000112113, 1891981448, -511356474, 678112000, 231308715, -845426086, 2065931343, -690231821, -2065441467, -497137258, -288817447, -272642500, -1778307241, -206926623, -1058833162, 1207480823, -577760388, 967667904, -747757357, 1515713516, 1901169583, -43384102, -1869097267, 698722931, 1723948263, 895747277, -963077288, 2007160291, -1139652897, -1941673179, 1182316407, -1504345279, -69517474, -1337091986, 1144745436, -295343637, -368530206, 423117467, -1160707313, 606107242, 973575490, 782358427, 1225701496, 1354180679, -1819084457, 210496900, -1607248517, -100403486, 357128435, -1211000784, -1699635523, -1995757335, -2041727997, 1639346630, -1140917407, -1428441321, 1391552530, 950439976, 1536850187, 1755763383, 349315024, -1716747422, 1788059719, -956787148, 435093165, -519717781, -1185043774, 1326150846, 666841562, 977518902, -1878116663, -1052216208, -159814671, 545626237, -1161390691, 172913262, -1143147285, -711220581, -2073758388, 1347605160, -274461216, -1138600943, 1812589913, 1321776791, -654185814, -514865093, 342576025, -1227661029, 2027182643, 499090278, -1057042386, -1200362684, 1633068952, 1127338030, 66338457, 1655244407, 1091076049, 1868857534, 1902975017, 427968982, -689633450, 1869590905, 828919724, 374348665, 291496172, 369492724, -1956000730, 149774736, -283502913, 542857976, 1810830261, 1711344293, -1158072113, -1788295198, -314318981, -1029216204, 1180472328, -769273193, -1884508206, -1558495607, 19086583, 2059341589, -1133755497, -2103950715, -353373479, -330597102, 146329926, 1139012057, -1595155154, 92242787, 1758776536, -2142059846, -1016391823, 572794885, -1164070685, 936895954, -530252487, -852015578, -1387262267, -610552571, 993685216, -2060482368, -54855358, -1368415548, 1727532083, -1998919251, 1004938093, -193604754, 402127614, 15533913, -822374248, 914869992, -398825428, -1951818825, 1024562104, -1513050369, -1086194365, -1602294388, 506250848, -450950473, -1107350963, 724811630, 1667267553, -1296578611, 1797492484, 1593191271, -797438732, -1327763127, 1815794923, 968830944, -1597687229, 453031735, -311267208, -1363949093, -680526092, 2111164100, 1874373703, -737231277, -1941054345, -1943683241, 299275156, -777764717, -1580845667, -1590831315, -706883071, 1006664100, -455650726, 405499155, -1557738572, 1434435376, -476662082, -390599384, -1023097080, -462139722, 1416922513, -1243778374, 1721356353, 2052478481, 1576465185, -1753145409, -1866886190, -709091910, 1188370346, -47903041, 833750418, -714362080, -1356224125, -1264932342, -2019192812, -1865286029, -872940604, -1103730145, 960420100, -1042876502, -1376735106, 652488617, 265536834, -727122450, -1304252301, 1452309463, -345462904, -1385578434, 1005791488, -1952157450, 1535232809, 1539175065, 1764693654, 370125766, -1202518768, -1045824063, -1277351352, -209760871, 745809202, -969253860, -263968717, -1987049520, -994220477, 1014895379, 767424874, -1455749768, -1031331847, 102844430, -1853475234, 1375464119, -36893052, 738438714, -2023227099, -766955665, 917641510, 2098209786, -1217824087, 1658975849, 519874226, -253260859, -1162718483, 1786747123, -1141951794, -2107503630, 454499128, -1967565552, -1023321135, -1996284503, -752431392, 472701630, -1632851902, 410108660, -1046454863, 1967316776, 855860213, -1312902400, 2040315518, -1117439624, 493239897, -1998091182, -2034474271, -1097999735, 1318127173, 606300235, 1842233668, 575662433, -2004034017, -453132858, 575442626, 312602259, -2052800210, 1864640938, -1558226144, 1723181891, 1563560258, 1335087794, 1484455993, 1617896015, -1725417335, 1319720221, -1761963217, -699139792, -1289651408, -1107156983, 1743906484, -4909723, -1308860494, -1458950358, -1346838156, 770842123, -2015270071, -24732450, 1317412484, 713576473, -367369916, 1304052776, 249082034, -1501300599, 440635569, -1918514505, 1703744454, 1979510875, -1459719502, 2080733946, 1591601168, -1279512428, 1050916259, 506633589, 985141457, -1785288990, -264273336, -929708322, -719186799, 821741784, -672362448, 552181928, -802373915, -390543422, -343050866, -1958288614, 898584575, -2009826787, 695541207, -490634204, 1677702760, -881113644, 949838036, -1754707531, 1625802700, -2116565724, 1986923158, 755539119, -1478875610, 266787239, 1794560040, 1005034935, 1558408357, 763790383, 677517420, 2072139195, -235728628, 1725705385, -1582053707, 1113461586, 1674642759, -1414719663, -608468252, -1873260761, -1401304493, -1029303396, 1873534265, 912963743, 645715337, 1132031991, 487696799, 1110621999, 1383752223, 1018103642, 536280867, 1764666589, 1624759145, -707782673, 1407012132, 1887436609, 568473975, -758524638, 1093808445, 330404853, 240981075, -250484760, 498674002, -1126343191, -1070540555, -17257403, -1302522037, -1500566183, -706742387, 1731391627, -121892623, 1944180, 697150366, 1175869801, -1081726694, -772936078, 300113930, -1519743318, 1011619084, 966435032, -271530967, 1478437384, -2000885569, -1625488897, -30409891, -577640443, -491669659, 1721990364, 464531779, -1035520457, 1234811766, 58268492, 761680308, 338102126, -1281454585, 1554633851, -2008859178, 55616722, -2039496630, -902950403, 673529549, 1020509295, 1518665847, -478044459, -296723364, -2075845731, 1809506854, -99500436, 883142933, 289332182, 738556337, 1501633470, 2058318873, -346819242])

        """i32_huge_1=[0]*2621440
        for i in xrange(2621440):
            i32_huge_1[i]=-i
        self._r.i32_huge=i32_huge_1
        del i32_huge_1
        i32_huge_2=self._r.i32_huge
        if(len(i32_huge_2)!=2621440): raise Exception()
        for i in xrange(2621440):
            if(i32_huge_2[i]!=i): raise Exception()
        del i32_huge_2"""

        self._r.u32_1 = 1550099195
        if self._r.u32_1 != 547919123:
            raise Exception()
        self._r.u32_2 = [237099665, 1725693514, 3671290215, 2838122575, 2174235839, 1926762547, 837710207, 2675306390, 3296759548, 3236712776, 1185582523, 3424554628, 2120088772, 3672727628, 1229489468, 299615394, 2391828662, 2161918065, 3215046430, 4090719326, 4046969338, 2837195073, 1814520605, 3281278603, 2366669618, 889646058, 2889818005, 582950935, 1660657214, 3304485267, 3017091402, 4182786222, 381383578, 468232037, 4264726246, 548129943, 228487325, 1626908942, 3843628003, 340032714, 896193553, 1589965383, 421647904, 1025804481, 37483739, 314532432, 2655347560, 117434633, 503953090, 3976906518, 1323855325, 538108471, 4161859424, 1912643799, 1352908924, 3415941572, 2123957567, 2125372546, 3660361032, 2093953170, 844556942, 350952258, 3712309630, 1671728833, 1515702177, 674196370, 1804290265, 2369213421, 659681625, 3007121556, 3629421992, 2355746396, 1887771, 1763854265, 3669589284, 3060951582, 2289752966, 2753656458, 453476287, 3858397040, 1755557022, 1056528532, 1074824037, 3392115327, 959387159, 4047339053, 4055444899, 2701521116, 3269246259, 1658313101, 1191016218, 2976266754, 4058115909, 3148745595, 2255966436, 1286833652, 3846605743, 332980236, 2987111809, 2863137443, 3589002629, 3634508729, 3050304267, 426166523, 38644952, 4120741158, 3779249472, 2247004208, 3887627978, 771737466, 327488668, 2413511241, 3742352323, 1800531129, 3093397506, 119855689, 1044449337, 1621589532, 2435672368, 2249934961, 2486385468, 2733265378, 2055466545, 3463839050, 1741434858, 1937180913, 53147295, 380685724, 2147133772, 3377145922, 1696161493, 986108230, 552797714, 1030805428, 3633258771, 724378483, 1453096552, 3633745301, 722493301, 3218821892, 3672842476, 3232339885, 2194639207, 3626117658, 160139022, 1220950174, 1499215195, 2900860877, 1105932921, 2513047638, 2975567394, 2688547895, 1701949245, 494851022, 3099438803, 2302405511, 3002890773, 3694596195, 1818301109, 2241585621, 3375937719, 2173718080, 3174769392, 2332849203, 1120354034, 3688107993, 3910547603, 475511452, 165704715, 2543590060, 4279301981, 308235882, 1816022030, 2611287885, 2638354900, 1603444131, 2625463614, 2748122332, 2695819720, 3508062749, 4213882116, 1456900955, 2527945808, 1021825166, 2050461441, 2014465404, 1165369542, 1735932899, 3460204932, 1482933068, 1853558960, 3796877889, 2819245867, 1495722807, 286085468, 1232127264, 1369041740, 1203310608, 4013214417, 3662137316, 3906425458, 1886277730, 3592347464, 4124894145, 1520615672, 2057935984, 2780423261, 3807868959, 1096708615, 1133308613, 2081283278, 3031731081, 777297905, 728628197, 1045968931, 2798986608, 1441163940, 425803298, 3425923673, 3174138272, 225290447, 2789342514, 1500710940, 2214009944, 2611052505, 1511169866, 3468976229, 887023337, 3301621653, 348051316, 3413528372, 688050819, 3270149113, 2721404891, 2790531383, 1307526009, 24196953, 3323021735, 1883300819, 827261292, 1024782357, 4200877565, 961985674, 166365221, 3011947146, 3773678739, 3122249899, 4236359826, 3567170538, 164427914, 3384429677, 3901604544, 3178054797, 1736839253, 2964545385, 891428101, 1944593339, 1989423560, 1361523913, 3168022842, 3512787479, 1890231449, 1593427930, 4149710413, 206469070, 1896704648, 1231454209, 4068940405, 3271655038, 2008435184, 2914967896, 2357818161, 1859278865, 3410094777, 1298228364, 222292372, 1055108733, 4040689906, 2210549194, 1948747, 2506100330, 962472296, 1968083925, 113875684, 1936131419, 1016307414, 1060859451, 1739828182, 3346648079, 1164081840, 2485888280, 3476085289, 585721471, 390929102, 517669802, 2653223889, 1174053498, 1569525180, 3310507972, 1002962122, 2262804195, 3220775546, 3182459697, 2156503148, 4131684371, 2813459977, 1117022498, 1997829290, 2683851565, 107074302, 1419327824, 3915955155, 3780878619, 610899511, 1901058671, 4050293718, 2053491262, 1391571066, 1177627511, 743398950, 3803305715, 194123827, 3621325995, 472267748, 3375152783, 2897163902, 3462255512, 4250233830, 3994919468, 2831376517, 246739001, 2563541164, 2158887230, 3637942716, 2966210109, 47815115, 521677298, 645694605, 3228944885, 737962495, 826169136, 3548976344, 4043510480, 495863083, 777697689, 805624668, 1263172222, 3510345575, 1056092728, 2969537722, 747239264, 3369168528, 1344872701, 3335255317, 4214479629, 3890217901, 212326383, 626667851, 4084223303, 2815290146, 3385778156, 1708926854, 295550151, 494270470, 3067952778, 1533064310, 2934900292, 1705387163, 1307922285, 2193031516, 2433387564, 439649015, 2639844157, 3899988054, 3512645808, 4082111285, 39460185, 2109679546, 2807623639, 872015072, 980218181, 3396910791, 3668142418, 1001890199, 3235923562, 3566499716, 363410876, 2673237222, 573356352, 1636136151, 2224553312, 3704628010, 1623877736, 2563570732, 1232767726, 2971775467, 4216718036, 3488020769, 257411122, 1168087703, 818565641, 900860168, 1947568647, 164818961, 3931611634, 3720231207, 2690894061, 1424779930, 90538671, 131364160, 616530415, 743044912, 129491467, 4041759658, 3433286148, 4169430938, 2922959631, 3821215730, 3097046213, 3611435200, 2326824436, 184884915, 2069988071, 3914342196, 106319212, 1325869172, 3906567559, 1758481342, 1277175140, 2754342337, 1294820705, 791996734, 41241012, 3345622322, 3718866993, 1255338839, 1391956142, 3839078475, 3457508262, 551513656, 1004850662, 3795985935, 298265118, 3742037297, 3355517467, 3601723593, 3585988041, 3063759488, 3171470181, 4259702765, 3239000394, 2708065681, 4092601030, 346908933, 849213263, 2851377667, 1796454246, 2735073999, 2777745491, 2294240001, 2121652435, 2706284022, 585848169, 1936702478, 2371114722, 1541583037, 116304242, 3676364969, 3879455349, 3833621771, 3701696564, 2780518089, 1479844512, 1789233460, 2165430981, 3709637684, 1215700310, 3383152932, 2134182167, 3267525810, 4142614062, 1913035686, 299460925, 2677124325, 2261142050, 2007429043, 515722793, 25703755, 3410497288, 1661381183, 1667524384, 530887788, 3517835794, 159256235, 3805603779, 2368397, 2999883232, 39771046, 49747199, 3734347231, 185140859, 2259304947, 3389847559, 3758478898, 1438981583, 1923428196, 4294696986, 1917080172, 3599354053, 813437110]
        ca(self._r.u32_2, [4251946440, 3334867394, 1627635129, 2588419147, 4174027116, 3897125158, 80443814, 1389733726, 4117149812, 12542280, 1256007817, 1703348194, 4237384057, 1454512978, 2775061970, 3298540861, 3715621276, 2362002640, 3636980763, 3430743390, 1830381203, 1507092396, 4142499824, 4213673901, 1183960426, 1874370435, 4181283334, 2200901254, 3332790298, 3423644529, 2387935836, 952382132, 3924524172, 3719680299, 853249098, 4083610173, 2636543308, 657361882, 1525744446, 376298547, 2451684942, 3240929540, 2310416762, 730671377, 2937427586, 3563592349, 2472196520, 2147357762, 914655107, 1758244054, 3876886042, 12351564, 1679162795, 1489623257, 2455794558, 2538372341, 2057637059, 3508778762, 567682489, 283434754, 3167627543, 1915532592, 1232942381, 2754609078, 4150346060, 1663219004, 1231896519, 2755959635, 183820585, 1055352125, 2147188623, 1645909010, 1893712235, 1485051038, 870164520, 1966826561, 48501444, 2556720793, 3128066451, 790988700, 865202135, 4263049716, 2090861867, 1748977625, 2699841095, 113797990, 2481195137, 2574284167, 834141103, 476065944, 1480757910, 315080683, 350708905, 338916974, 709575589, 3077697353, 1231129412, 746021816, 2332229547, 1946675456, 583346238, 3135681244, 1842291655, 231618544, 104978643, 4086067348, 3174792638, 1543369889, 1101673653, 3023672083, 3205010661, 1536466390, 966572661, 3883854770, 3427219648, 2247096744, 4079126348, 776176295, 2599372279, 1888032134, 360725842, 3052443662, 865793013, 3084628677, 516162558, 1020425629, 2915535067, 4215116317, 2977464272, 1660722837, 3507058298, 864890045, 249379031, 3973345746, 2629825645, 771115239, 3526813236, 3106614042, 203525488, 2971666751, 2845337507, 1637317812, 1743782319, 3991795965, 3057486763, 2839184028, 2831552101, 2836007599, 14115933, 2147447119, 3904004068, 3346997713, 1322155226, 1049159718, 2520132354, 2765453431, 4205328777, 4063219623, 2238279021, 1619016803, 415896490, 3591765870, 3318597287, 1557289292, 2845067684, 89482247, 2114516871, 3464828768, 1114311788, 4215401081, 3458358731, 2736518275, 380431203, 3435888629, 4249714953, 1764633576, 1915821483, 1597234883, 111251916, 274107180, 2935452271, 4072034355, 357724805, 1550422867, 1378849275, 3264188640, 3028697235, 2805673388, 656257910, 1454961285, 188865944, 1924561757, 3184772136, 129725152, 1587697966, 106462817, 1587951867, 3192757556, 2829152265, 3270745049, 435873692, 3749929242, 2062096658, 4149869860, 2418404390, 3646774382, 343128996, 2496743364, 734565947, 3826051517, 2828517029, 962692901, 730853036, 1082602175, 298823790, 3231844899, 526460170, 2579457360, 1480606553, 1842946907, 2622701868, 3895551897, 2026981125, 3153668454, 3704749050, 1185971623, 2504477989, 1870109318, 1518600621, 14687749, 3846239097, 2613355571, 4011868731, 4273118207, 539188665, 2099254272, 1043640546, 2517454961, 4147146631, 3753370580, 3811721724, 989962603, 2211483632, 1480428764, 1954557704, 1112461942, 1569266181, 1678583802, 1646459706, 316406457, 3242999591, 3888012390, 2402113654, 746240298, 3662473135, 1260156363, 1203238376, 3061859356, 2032152659, 966717679, 2534194659, 3388402620, 3223059378, 3877902454, 2566178070, 4108564664, 2578614366, 2924743698, 3967226306, 1346866215, 4129141259, 2159606690, 237374413, 2311773278, 2936435723, 1669343609, 3835118141, 2474006294, 2312776854, 3991958455, 66050323, 2021998927, 3191454066, 2189188580, 2142686591, 262029985, 1334540897, 877178233, 322292574, 583880104, 994626866, 2643853709, 2746736170, 1819097952, 3500683162, 2717819610, 1979841756, 4158317627, 3768907483, 4144867490, 2428342768, 407254584, 3876466370, 2906963449, 2747730439, 2807429483, 390805623, 1347724002, 3708124771, 1996426487, 209852741, 3539291907, 1973958470, 930781564, 3333035683, 555854849, 540149787, 3214341438, 1165683130, 284698251, 3229514555, 1944044250, 676799831, 3415601775, 686883721, 2475380401, 2417075124, 1731220395, 2692854334, 2090593377, 2377595670, 3031508806, 24480902, 3556421449, 1940400454, 3751271557, 585927728, 2399018121, 1897248871, 4110307692, 1294121928, 2976700231, 2519149970, 2393660481, 1452332020, 1320620207, 2261085851, 2445477360, 3141380218, 1044718590, 50521930, 112491419, 4149332237, 1091423792, 1469962572, 3907732209, 3328879500, 4063642960, 3006889620, 425720040, 2842213341, 2094386140, 3171166176, 757382335, 2515418722, 2466505128, 4181749776, 3386253778, 1241141486, 3110299582, 599382492, 3361936057, 2904521896, 3463235864, 1686895148, 4096837571, 2649784396, 102145162, 4034413105, 1309891308, 1727749117, 4111125789, 3485689078, 1298526747, 3208723720, 1387080573, 3497204630, 2701756222, 866112144, 3332181807, 2824696606, 4019789661, 1393196838, 477838543, 3838343203, 2399752805, 1676970714, 2163423971, 3918831727, 2082667742, 687058482, 4132123776, 2944329588, 830337633, 3305684867, 1115400173, 1409924819, 4213431551, 101974285, 721035281, 418956469, 3537419424, 3058980494, 3735712173, 31898322, 812527641, 1412975070, 214035881, 3370497326, 275023508, 2188096928, 2698269714, 2338536560, 2217867267, 780724394, 168999967, 4028242661, 2057116599, 248770288, 142100118, 558526929, 367796080, 1613088719, 111252491, 569035372, 2444968023, 4163888313, 3008206018, 655301551, 1102089047, 2157711351, 1189565715, 1048858627, 3463105328, 1659606364, 2839652561, 311401265, 297227948, 2049718821, 1287086069, 2816817582, 753298510, 79123064, 2058422267, 1988231070, 1697021200, 3755875481, 2000787653, 372680790, 770642272, 3557979977, 3242763045, 3424268849, 2545039983, 3403101537, 804431778, 3022051943, 1799982329, 835187866, 1307679719, 795446639, 2865087004, 2503099400, 1097854687, 412079412, 2918593238, 4204336449, 3272876881, 3701287131, 215671154, 2729194459, 3828900376, 407889473, 2386020434, 1672155598, 1588439879, 2355888880, 2451706408, 2223568426, 4230924842, 1121564168, 3971399371, 2302823247, 1838239260, 4017581704, 197226193, 1773201901, 22730505, 599013585, 2360399780, 3459055993, 2359729316, 2534122212, 3338162386, 681551474, 804682591, 3684776026, 2611917837, 518924291, 3527933723, 2831363989, 2092857661, 3011292035, 2036768662, 1165948954, 3915111934, 3715091842, 3486642823, 2169348932, 2210412086, 2082504433, 218262071, 2666551070, 3844955859, 1885787522, 50919684, 30300958, 3237830009, 1004399278, 1420324202, 2995067867, 3343455201, 1341482320, 2707911315, 2322962795, 104691279, 433113543, 1673935915, 237192280, 3866873407, 3719846074, 504926120, 1585743054, 710382710, 2276436306, 2976938826, 1322735386, 1856969923, 311925360, 1497000075, 2852252785, 207694370, 3237126868, 126779936, 696212993, 3860732454, 2811018481, 3182218492, 2694262689, 954054185, 1145279765, 1827792779, 647535690, 2378645894, 1603060963, 1501639457, 967601596, 3979534574, 2129057469, 1503074666, 3455573355, 1277747107, 2364423785, 718418781, 2029920441, 3230465514, 3292224990, 796319542, 4143628522, 2357283776, 3321794845, 2371483975, 1136784117, 2757314460, 132067372, 294498845, 2989608361, 1147501898, 848670725, 3702484846, 3398317762, 274118355, 3486956662, 2414417547, 4165976855, 3707418163, 3614978249, 793009306, 4227283826, 2072607460, 2291123052, 1319566667, 3736885972, 1075733989, 2822123350, 883768237, 165340447, 2283477403, 3854687889, 2702364501, 261781101, 4253180939, 1904200988, 3670999235, 2081253795, 1013385256, 3393606543, 3915738401, 3677841368, 2222722431, 3582521284, 2184635962, 1379820344, 4132361812, 3076369748, 3111110095, 1060089765, 3951504597, 276119608, 4292130693, 1208342406, 2964718231, 1156835032, 1503506724, 17689181, 1253790050, 2052448727, 3951262449, 1045066741, 1212371757, 3864687390, 2781636814, 4164334487, 1434750495, 1015217609, 492107542, 4106176432, 4258301116, 52857279, 3601017578, 553436516, 1286022350, 2970181802, 1531473162, 615711544, 2770114226, 3807138554, 1254115612, 405024141, 2248962327, 3661682788, 3457720992, 2391719239, 3782958744, 3184983441, 1120404266, 1505151243, 2382314268, 4164517871, 782247452, 923774834, 3508260701, 2537984828, 2116287910, 3255992169, 2640296699, 614769200, 767427138, 3456406779, 1809700841, 2437468993, 642938299, 3155191374, 4074085350, 2642920857, 3189984175, 3169851773, 4086000673, 2490375684, 3948311217, 3105674217, 1698869289, 1311043867, 193634359, 3011562913, 4136987101, 3694637471, 3746665664, 984905715, 1842085529, 2014624560, 1012559384, 381626366, 3316965712, 3951018504, 1396133012, 2477956684, 3892489603, 2447107565, 1585934707, 2614794953, 4048636321, 697301886, 2382428822, 2964257243, 506994596, 1901393962, 3958702238, 930275666, 3970480891, 2137671677, 911161575, 3800494155, 278586712, 1193762952, 154795879, 3301269187, 1668521332, 444082092, 1753908500, 1687735396, 3236812133, 2861130228, 179908202, 1539423798, 1280312575, 1354412234, 890265444, 3698680851, 653081540, 3681719879, 838283359, 969405299, 1918696509, 651424255, 1081467498, 1369194422, 969636592, 1353343686, 1151142771, 622249210, 2324152022, 3419137792, 2402401643, 417315756, 2283635979, 2730135008, 945357607, 1421847419, 546033882, 3198842674, 3343416782, 1103542692, 4192435052, 2680753787, 1928123125, 1829821471, 3877076359, 2319958157, 1817991563, 3019027601, 3350099005, 122241996, 2220681659, 1867304134, 3903645175, 3926484316, 561272258, 2924762331, 1521681554, 4276247138, 4264605013, 3489960755, 90524145, 3924010437, 2159859802, 3931840385, 1622645822, 3614003481, 4142324969, 2557247602, 4114169094, 2832266442, 1338437964, 4072229872, 3375287658, 2231757313, 4020609455, 2396693058, 2794056809, 1622056246, 3798643807, 3419424563, 1469037362, 3368075234, 2696057690, 4239384736, 2499585821, 488059987, 2262538463, 1978623658, 294535630, 3609960885, 432048986, 2518665415, 576966143, 1577963777, 3672258101, 1737846056, 1033455641, 3049863102, 414818580, 2310833967, 3876593023, 1159401619, 512103557, 3929750248, 104744865, 2294284829, 700010847, 3919829947, 472148418, 2495096228, 1476352517, 3466719922, 1423170701, 1835216137, 3804324362, 3156638174, 218238460, 2122719443, 1475392811, 4191547266, 1660363531, 1752963086, 814996542, 1775564261, 2768667643, 1691944624, 2673873848, 3717015687, 4274924722, 4267842589, 3218843587, 4086630122, 2525920765, 2642512022, 2581476770, 1587395043, 2479647167, 2075617909, 2220378822, 1164751823, 1254817289, 3012514369, 535781325, 1155411560, 3470618493, 3736078399, 727696447, 3668735551, 2540239292, 1287246718, 1034530277, 3398095154, 2277784043, 1007465081, 2592218771, 2307100491, 2280001478, 3781351274, 517873620, 16783814, 376212454, 1269327062, 2190745862])
        self._r.i64_1 = 8621740821050813024
        if self._r.i64_1 != -1357833931563696072:
            raise Exception()
        self._r.i64_2 = [-1418708830105823852, -1357833931563696072, -8308127073437794904, 6203263204523798112, 7076661289157584762, -3645491092747259726, 2969229117250121621, -8403401867791621438, -5706351777107258259, 6979420050019736435, 1350986631885231652, -8626678967587677100, 8380704325304801386, 3423582193572197909, 8713973059069583959, -4562940403005824119, 9144900318464157853, -8717799056344934090, -8792498500921807539, -8345039878076898189, 5201358909840838683, -3398583150340629128, -5482869438456886726, 1644815108571813337, 7248497692538999361, -1178045319005427907, -7220532561583062381, -2882504460577706964, -3460274637164886125, 9053064536664375063, -8649931456492292885, 72282480921257410, 3058905063630457969, 8394362105178121659, 8263211448476405605, 8671703720724529690, 1117912130945798022, -7392161278301566795, 9070973456367872189, 5064083874137910433, -2216141782782730608, 6092600172408194906, -7328184273434559673, 7340896108422144895, 8041029351530593362, 3567042073657363684, 6634152186323571334, -939114094925119978, 3932918768588612631, 2223869457290740495, -1394521432769550065, -7708491921728269104, 2558409591077932690, 7323090212396920736, 4463226188281322565, -7684442752899854301, 3813932804031799733, -3061288894555894392, -8926314527654650550, -5483212417699975352, -5168152193234004511, -5252714907036148733, -8899682260331039592, -6945672564712903320, 1843836835216653982, 6265565553002088665, -9191803385169282118, 824381268893232707, -4195712559860724390, 3170122388521742267, 93238405484244323, -3808714570016938587, 7751370385159261162, -415651213975075366, -400640794129234242, -3632420176870277542, 2145224332581955327, 8408764257602201311, -5753925773175608181, 2442171188911603754, -718254550700219999, -5279112326876598860, 7731819115318618935, 7285784364016347384, 6648758251111712748, -4965048064766122366, 1799714525316551079, 5808264002475810898, -521447549589589148, 263148779791826658, -1256378489223837059, 3001523551318331984, -2133704098322946340, 9175731965505830169, -275510851941027307, -3450575930678805596, -4673869135690784872, -2779584507299050825, -6244919930307138446, 5663020090027727817, 3592337319079719462, -7699870730217589682, 3427192886285003578, -566635025493084181, 2780130284244381358, 3422425913941932991, -723427948584706426, -1731222455107826641, -3556462521989327042, -8514332474959779238, 3681987062303886320, 1266418540216073989, 4892980044242035752, -5243563662285950589, -8021867029688739836, -5712778566201121978, -2133887347488624783, -667985954315002704, 2350239843243973147, 5123432618264623922, -271741713269398666, 8726020244487579882, 3802883727236102212, 4050625489658817027, 6873081973971784099, -7507676454188557650, -675853520577120389, 4704868291861385417, 1767091830085798988, 1315143445596137295, -8400502078442130692, 4250620495159315861, 7743903342313618441, 8236285998949285411, 920705431865098656, -2187810178560173353, -5636947816335562469, -8869870121412151030]
        ca(self._r.i64_2, [8621740821050813024, -9092072209079113602, -3056007272962959794, 5895514005284775249, 4825857599917744482, 2093519537988072834, -4390907564722863586, 8598973384036716702, -1889020672280261540, -8273635663381002611, -1941314642980235766, 1812319066748738475, 4190176042918780749, -4555199367311683530, 5467393609117797644, 8359783806563259266, 3800668915803924955, -2655932873935461949, 3136675805239089308, -3633713411557631382, -672757299114219972, 3045962201700775993, -3026485644327632861, -3372272670687649520, 3387661134442604201, 3677140703283269642, 4482422720713908644, 1337692977628619063, 6948420747960198793, -2492903114419653680, -5938903035079054289, -7806446185001452553, 9040686595201532492, -2127381394247868345, 8655785215940696615, 6435851473422996010, -8509497626685383427, 1304836616586909040, -2675436555158709746, 7454381249933066408, 1631169664587044350, 6013206163109033855, -2269271257167747155, 362749191994199052, -2710425314932035541, -3130715904393787670, -4410494504975660198, 4957729582609338569, -8246870151259110017, 6845983371242614475, -2258617392930568184, -8252230642158077029, 2670510062513563636, -6653455225739816423, 3093107250382849352, 1150551445512420048, 1546949923942708166, 5021898317351658427, 3707867854662121111, -1206055501856481918, -1873593186785558123, 6775838224715797812, -1115046710372778769, 528633723916988990, -4174382295242439358, -5547557100483108777, 5731859982382023557, 2204054933203810496, 3007479017130878933, 6608694896063582073, 1503694568421070630, 1248413523206321552, -6401043893159800201, 1353202742204949340, 2304302719445899395, -1291964394378923514, -5522844881206564639, -1277367478728568636, 1849991021787670735, 478721890957105862, 7757247149420834244, -373709650675810738, -5057614129950301004, 6162983513491054102, 3145006736835504836, 5885317631158909353, -7602326138257639761, -4157450027384868646, -1360567824864190920, 229176854089967110, -2202711857284656499, -2946750387084440631, -7399092435233174868, -931278862032913506, 8725183201793225879, 4422438402418122694, 7390489870132742668, 5253764508555093227, 1198113859723757987, 7260998365611273804, 1540767319493735478, -5799740479458549922, 1136167730386243597, 1413668892541509388, -8362134679601352333, 3664237052291625965, -7059531260401496534, 244969021945500288, 7960640458120876383, -2144041369569582147, -8542531942333624037, -6912033525905196529, 7309130333167087960, -1428796488709117140, 7889412153530907816, -6519274351560620428, -7194011194445795971, -2253470711475766161, 2052913415378741465, 8349030699411536987, 2962275883196204755, -8896757719886490153, -3481651114681941922, 9178906373760388169, -2393681984948405823, -4722899724188292419, 2219571189613806132, -8736536710280581263, -6631663654879231430, 1213083601717174358, 351791283162447724, -2728467560827636562, 2174378918144416458, 748751282949822397, 4251372914295826830, -4967177568325109568, 3825916028954041329, 7303839053387841791, 8648996684183789510, -6188350610717327471, -9016026939100696370, 8366545235017906362, -4151061240351591634, -3308165752571595210, 5710967263762362072, -7116887066458274066, 6003026705335466483, -2788076296930402698, -696935785960712847, -3523035848103775545, -4808396779515182120, -4487243801299967856, -316555344628268867, 2148745648896444003, -7908465185551702581, 209478862744791304, 8329349262325078360, 2312897865550480622, 3534430375708664567, -4313813383770928446, 7798388933635693783, 423303070618897314, -6223899204612392666, -7997497118304435999, 1761514773996835425, -8886871075540730292])
        self._r.u64_1 = 1465640522145789825
        if self._r.u64_1 != 13389861970863644378:
            raise Exception()
        self._r.u64_2 = [6515978873578326855, 1465640522145789825, 14139647178981527348, 17376225719361197745, 4827355217349405315, 5237172857588412536, 11185863429255124449, 11922950710462888186, 9723873762901963012, 2360891509504070464, 17595800616336901155, 4676383109049523121, 5519403084078587651, 15199794964642249670, 10725748072798711186, 11861452006494413908, 10866242934922922899, 15599520359228044898, 4022505103249338009, 15081262745932646374, 9978655822822015426, 1893338345735521355, 8335612627840221039, 13125076221780371251, 1843608744939432450, 1877855184169582147, 360237399108374165, 14133486497511175136, 6918428392028668980, 4207262405010786686, 11882372330517522341, 2660307236802524516, 16105897257753062921, 2353931053072926625, 10173424970756197713, 3742480367255311168, 1303431584704287527, 12527899890265500372, 32220987555692133, 17556513786877588779, 14599571048880016586, 2017220613051019209, 13580232873699969747, 3864855431338072766, 10522968089599101769, 445176367690966897, 7790111520686478868, 6394442284921113988, 16995884223523288612, 11216569412804039035, 4321418227933556664, 5409834497962741327, 690550291029646943, 16074599988808644612, 11236550486638087434, 6844569081007881849, 5869987636307743707, 7778211196101597376, 15853871901637280370, 18058575643888946512, 14027203060397441285, 12712062502708340258, 4041613882264720796, 11645048579559315688, 1246226537584125354, 3474795601576826029, 11513896830487717539, 1974322205737539934, 17242471345616954213, 8678121572397745114, 17527671945381764646, 5033231148296076497, 6411880965725185093, 174473638020748044, 8158678930583416018, 9507609436552652251, 16205993571484058929, 8035338227846555833, 8791374446603527925, 14595445946451526244, 5169961786923105799, 13397974474224235898, 2364042737119390982, 5321299597050057517, 1121024914655468441, 12207167839097364776, 12619831538472755181, 4864354177058320218, 17848460798228747459, 13261044407690283599, 10209900008497671979, 6862409070349488681, 1432310611369939292, 2092522766869471913, 15058223303172327711, 4178174561433201628, 12906394038648389198, 15191542062580018441, 16452252929507747318, 11201120125455394600, 6726163449083399053, 8426476024479275017, 7026246701397961488, 9033438331677737541, 5951673483825817230, 10638919135849238472, 3252342350133602871, 15766880131631627052, 12385842632184481382, 2748643971592610065, 6396730451340699978, 13659499533346384982, 4282043305472384300, 1711405441567413160, 17992713571449412921, 3556627233283536994, 4138074248161109398, 1622144212241737621, 18087263875532968938, 14104137172003718411, 7644309790031389842, 8816844725250613052, 11421439960737023984, 10454322951672789795, 2119200398037807197, 8384409476347314289, 2527068029837223073, 4862875043870995989, 17581079332542377528, 18385625565005546141, 5262116103886681622, 14174635193688816521, 3985859099523137999, 5526499814203466410, 1239704066545123753, 5917443538249299253, 878138865084935513, 10218107935864045533, 6547939038367120283, 7353731416371741667, 5504609912290331194, 17697030959073472945, 3134771705926671223, 1308908721146697947, 10579235124105673010, 17332984836700322102, 13722665407351335633, 18423215754649979094, 3171161736406578023, 4234709098044006158, 7347564326123203638, 8195365762234651673, 7781698260938130820, 1180819293191049424, 493531138123366511, 1365828412106184272, 10313217779396245974, 7602972172978537794, 6065626025778962290, 9672897350080504270]
        ca(self._r.u64_2, [17812699909525330179, 13389861970863644378, 16257896157253761478, 14191477546208115816, 1387441194387183523, 8800889055657239662, 3787113061722336589, 2075067786453142295, 2302772129471114307, 16660993589300385169, 5227667125318999851, 17211198982499914739, 13967365476154884537, 6210802835678950626, 413837793611927178, 15016088479821729126, 14194309003275915218, 5521545037113246785, 9721585675207248367, 2487154057124779480, 4054392452442988950, 15742440468026600431, 8404041348136789525, 5704587169648799325, 8615894037736189999, 7555294940121326684, 166204857340424907, 10630415758080788319, 3699593146963368456, 15841753586674104403, 1425904355269403798, 6757749835782369274, 6484708862168533651, 14311810156028177789, 13305336491678304892, 9547219694933920657, 16939089102075290494, 13780222831094724753, 729578726262763066, 6741605646549400625, 860499368566843233, 4821657628681234936, 10629375059978179469, 12676697982045410789, 7965873501849669898, 6463814633396676710, 10304605129170106831, 17634109250944839532, 7874201956261190767, 2093432098376142516, 15162293521637815459, 14480915389905814968, 12246183009228206627, 9927056522845945393, 10708714764412026102, 12620101894595011829, 9720992984909508434, 1335165052342958298, 3842118717279685369, 5703296853718993513, 10169884007081888934, 2514628960699067131, 5254570865582417565, 9562135776312844762, 27891557900731192, 14886705471885923481, 3399688988254798568, 14640082747632735324, 12221809011211673821, 12865683977160344326, 12797396568995658538, 16277433856161229511, 5834216036130347946, 41836075316600799, 6171722505441450511, 8601242920007887523, 13624814788188880079, 7848598808818978240, 14273686016064474182, 9616131192223535887, 17907341921682029586, 10138262866472100954, 14661185914352643699, 18102813560908894003, 12307841218657619289, 14709882437025014177, 10238864911411793767, 4776457610936466600, 8782354639535937976, 18274481696525890320, 13992637006136445380, 11566349649437476293, 1209664843394078754, 14394522101288007152, 2915009092315033094, 182528511086129450, 15695741318843217573, 744918667092745933, 7146826536782008676, 13838640680680387773, 6708462726963541522, 7741352156378706754, 15062394166759350529, 10613549923461193838, 11002287295489384645, 11112868002985992483, 14972199425906445655, 15176061787056984512, 3369667758791907709, 10545737311162535909, 10549452773932875360, 977025607559254534, 8213649184128301518, 16026014660753415782, 16346803042848708719, 8641570190583236526, 10372374375551503871, 8475065376071450531, 9492316019190861724, 7258336917778003543, 7704933404615957344, 14492234026024540236])
        self._r.str1 = "Hello Server!"
        if self._r.str1 != "Hello Client!":
            raise Exception()


        #More complex stuff in the testing of properties
        s1 = self._r.struct1
        ca(s1.dat1, [2.416507e+16, 4.573981e-21, 3.468194e+10, -2.393703e-06, 4.937973e-15, 4.706768e+14, 4.286830e-10, -1.090462e-14, 2.238670e+03, -1.254407e+14, -1.275776e-21, -4.124599e-10, -4.953108e+11, 2.808033e+03, 4.685151e+14, 3.710607e-08, 3.523588e-01, -5.585682e-20, -3.290719e+08, 1.600972e+17, 4.257210e+16, 1.114490e+04, 2.739939e-10, -4.332717e+16, 3.482223e+00, -2.162451e+10, -4.527774e-04, 8.558987e-19, 3.755463e-12, 3.863392e-08, -8.351348e-05, 4.774283e+02, -4.612524e-06, 2.206343e-06, -2.767520e-17, -4.183387e+08, -2.037466e-19, -1.780912e-18, 1.656909e-07, 4.799751e+07, -3.604348e-06, -3.146762e+08, -3.709450e+15, -2.379431e-09, -3.034066e+05, -3.072796e+01, -1.057111e-14, 4.753235e+07, -2.725014e+07, -4.895406e-20, 5.339502e-20, 9.375211e-11, 1.632454e-03, 1.051386e+01, 1.915580e+17, -1.999453e-09, -3.087190e-02, -3.222377e+15, 4.219576e+03, -1.401039e+05, 3.950473e-15, -1.620577e+10])
        if s1.str2 != "Hello world!":
            raise Exception()
        if len(s1.vec3) != 3:
            raise Exception()
        print (s1.vec3)
        if s1.vec3[1] != "Hello Client!":
            raise Exception()
        if s1.vec3[2] != "Hello Client, again":
            raise Exception()
        if s1.vec3[4372] != "This is yet another test string":
            raise Exception()
        if len(s1.dict4) != 3:
            raise Exception()
        if s1.dict4["teststring1"] != "Hello Client!":
            raise Exception()
        if s1.dict4["teststring2"] != "Hello Client, again":
            raise Exception()
        if s1.dict4["anotherstr"] != "This is yet another test string":
            raise Exception()
        ca(s1.struct1.mydat, [-2.457273e-05, -3.349504e-13, 4.139542e-09, -3.944556e+04, 2.761296e+04, 8.570027e+16, -2.472613e-03, -2.096009e+03, -4.186716e+10, 4.584716e-20, 3.951344e-03, 4.557915e+05, -7.117988e+03, -4.605957e+11, 7.353630e-10, -3.303575e-19, 6.133982e+05, 4.528668e+01, -1.427778e-11, -3.509465e+15, 1.695706e-04, 1.732872e+14, -6.370107e+01, 3.269065e-06, 4.480613e+03, 2.058970e-06, -3.748223e+05, -1.507989e-09, 1.690251e+19, -2.177567e-08, -2.391641e+16, 3.617128e+03, 2.568296e+15, -3.009031e-07, -3.754976e-09, 2.458890e-06, -3.800108e-11, 1.555663e-11, -2.085887e+18, 8.574830e-22, -7.228491e-13, -3.987643e-10, -4.777544e-02, 3.908200e+04, 4.221779e+11, -7.528852e+06, -2.077042e-19, 4.478813e-02, 3.506975e-06, 1.011231e+12, -2.181961e+17, -5.098346e+16, -3.791130e+06, -2.734203e-14, 6.340994e-13, -4.582535e+07, 3.977645e-06, -3.785260e-07, -4.102542e+06, 4.751411e-16, 4.203566e-14, -3.894958e+00, -4.585783e-14, 2.432993e+15, -3.592680e+14, -1.560186e-12])
        if len(s1.dstruct2) != 2:
            raise Exception()
        ca(s1.dstruct2["test1"].mydat, [3.785355e-17, -2.518001e+17, 4.016500e+08, 6.566648e-04, 1.284318e+07, -2.674821e-13, -4.955749e-14, -1.699098e+00, 2.901400e+05, 1.499143e+13, -2.252822e-05, -2.653172e-14, -2.482811e+07, 2.353638e+18, -2.177258e+17, -4.715112e+06, 4.508858e-18, 1.205611e+17, -3.469181e+00, 2.383792e-13, 4.544766e+14, -3.029250e-05, -2.545049e+05, 3.149303e+19, -3.724982e-10, 4.066723e-02, 2.809941e-08, 1.279689e-20, -3.303471e-09, 1.846558e+08, 1.311495e-06, -1.185646e+04, -2.603100e-19, -3.519314e-17, -1.595996e+04, 9.735534e-20, 1.234003e-04, -9.697458e+08, -4.895883e-02, 4.770089e-16, 3.757918e-11, 5.253446e+18, 5.071614e-13, 3.793300e-08, -1.993536e+12, -1.846007e-11, -3.458666e+03, -3.995887e-10])
        ca(s1.dstruct2["anothertest"].mydat, [4.856615e+15, 5.981566e-22, 1.433616e+14, 1.747102e-09, 2.850376e+06, -3.748685e-08, -4.969544e-21, 2.530419e-01, 4.393913e-09, 3.837331e+04, -4.315065e-04, -1.073834e-17, 1.244057e-15, 3.901853e-10, -2.725237e+10, 2.896243e-18, 3.609897e-13, -1.937982e+02])
        numpy.testing.assert_allclose(s1.multidimarray, numpy.array([-3.949071e-09, 2.753555e+10, -2.724923e+07, -3.553170e+09, -3.674923e+08, -2.479267e-22, -4.898990e+18, -3.561455e+19, 3.890325e+13, -4.980286e+18, 1.142884e-15, 1.570587e-12, 1.398743e-14, 1.769117e+11, 2.086717e+05, 2.986916e+13, -1.204547e-17, -6.138080e-08, -1.468512e-12, 3.240537e+11, 7.476873e+15, 1.627340e+19, -2.421611e-13, 3.549785e-20, 1.469061e+05, 4.172556e-06, -3.369810e-17, -4.639587e+10, 3.776574e-13, 4.990526e-08, -1.321627e+07, 4.224942e+10, -4.515185e-03, 3.619167e-12, 3.046092e+19, 3.712879e+03, -4.019784e-13, 4.005048e+18, 2.988709e-07, -4.123078e-06, -1.064380e+09, -1.931617e-18, 4.223366e-22, 1.783661e-19, -4.153799e+16, 1.591527e-10, -3.649908e-15, 4.348772e+18, -1.470750e-14, 1.637311e+08, 3.982951e-05, -1.304963e-04, -3.522058e-06, 3.869385e+02, -4.640831e-15, 1.292954e+00, -9.474137e+13, -4.196137e-17, -1.540996e+02, -1.742881e+00, -1.597433e-02, 4.062517e-04, -2.724799e-13, -4.113398e+05, -4.704501e+02, 2.977726e+04, -2.662004e+14, -1.376497e+04, -5.993109e-22, -1.265974e-15, 6.387767e+11, -2.696841e+04, -1.983347e+11, 3.214742e-13, 1.906709e-06, -6.956937e+12, 3.637926e-07, 2.706666e-16, -9.795675e-19, 7.311871e-15, 2.343927e-09, 1.709674e+18, 2.961079e-05, 4.009574e+11, 6.468308e-18, -4.041410e+11, 2.991768e-15, 4.240906e+19, 2.260404e-12, 4.786043e-03, 2.439493e-09, 1.698043e-13, 8.655885e-18, -2.598418e-15, 6.685593e+05, 2.895287e+13, -3.098095e-05, -3.764497e-06, 3.192785e-12, 2.098857e-08]).reshape((10, 10),order="F"))
        if s1.var3.data != "This is a vartype string":
            raise Exception()
        s2 = RobotRaconteurNode.s.NewStructure("com.robotraconteur.testing.TestService1.teststruct1",self._r)
        s2.dat1 = [1.139065e-13, -1.909737e+06, 2.922498e+18, -1.566896e+15, 3.962168e+17, -3.165123e+17, -1.136212e+13, 3.041245e+16, -4.181809e-18, 3.605211e-18, -3.326815e-15, -4.686443e+05, -1.412792e+02, -3.823811e-14, -6.378268e-09, 1.260742e-14, -2.136740e-16, -4.074535e-10, 2.218924e+01, -3.400058e-08, 2.272064e+02, -2.982901e-21, 4.939616e-19, -4.745500e+03, -1.985464e+16, 3.374194e-04, -8.740159e-09, 1.470782e-06, -2.053287e+06, 4.007725e-13, -1.598806e-13, 2.693773e-06, -3.538743e-08, 4.854976e-16, -4.778583e-12, 3.069631e+06, -3.749499e+03, 3.995802e+05, -2.864014e+13, 1.276877e-13, -4.479297e-02, -9.546403e-13, 8.708525e+06, 3.800176e+04, 4.147260e+10, 2.252187e-20, 9.565646e-14, 4.177809e+13, 3.032250e+01, 3.508303e+10, -4.579380e-17, 1.128779e+05, -1.064335e+11, 1.795376e-06, -1.903884e+09, 2.699039e-03, 3.658452e+15, 4.534803e+15, 1.366079e-03, -3.557323e+07, -4.920382e+18, -3.358988e-07, -4.024967e-11, -4.784915e+16, 1.490340e-18, -4.343678e+08, -1.955643e+14]
        s2.str2 = "Hello world 2!"
        s2_3 = {}
        s2_3[10]= "Hello Server!"
        s2_3[11]= "Hello Server, again"
        s2_3[46372]= "Test string!"
        s2_3[46373]= "Test string again"
        s2.vec3 = s2_3
        s2_4 = {}
        s2_4["cteststring1"]= "Hello Server!"
        s2_4["cteststring2"]= "Hello Server, again"
        s2.dict4 = s2_4
        s2.list5=["Hello Server!","Hello Server, again"]
        s2.struct1 = RobotRaconteurNode.s.NewStructure("com.robotraconteur.testing.TestService1.teststruct2",self._r)
        s2.struct1.mydat = [1.783093e+12, -2.874045e-19, -2.311319e-19, -3.099234e-12, 1.000951e+16, 3.775247e-12, -5.853550e-18, 3.175537e-10, -3.112089e+08, -1.577799e-06, -1.379590e+00, 4.777044e+13, 4.811910e+18, 4.736088e-11, 1.770572e-08, 2.713978e-22, -1.649841e-12, -2.486590e+10, 4.092716e-18, 8.724120e-03, -1.183435e+18, -3.904438e+08, -1.251365e-11, -4.007750e+19, -2.206836e-16, 4.014728e-13, -3.960975e-12, 7.192824e+05, 1.981836e+04, 1.840814e+16, 1.488579e-16, -4.862226e-06, 1.612923e-17, -4.978203e-04, -2.305889e-02, 7.627221e+13, 4.014563e-03, 2.388221e-03, -1.129986e-02, 4.055276e+10, 3.842121e-10, -8.588514e-04, 1.299077e-12, -3.331850e-12, 4.863277e-01, -2.250328e-11, -2.261245e+04, -2.770899e+09, -4.710672e-15, -2.267765e+06, 1.582168e-09, 3.664505e-06, -1.507921e+12, 5.460120e+09, -3.256706e-15, 3.012178e-12, 2.274894e+15, -9.664342e-18, -2.770443e-15, -1.955281e-06, 4.768349e+01, -7.679375e-19, 2.774544e-17, -4.928044e-17, 7.602063e-15, 2.506718e-12, -2.794058e+11, 4.329292e+03, -4.041289e-02, 4.035282e-19, 8.577361e-04, 4.197333e-18, -3.509270e-01, -1.711871e-12, 4.578825e-02, -8.783497e-13, 3.862885e+17, 4.219735e+13, 4.281035e-21, 3.323068e-03, 4.931847e-11, 4.032955e-21, -4.373013e-03, 1.592633e-16, -4.484112e-16]
        s2_ds2 = {}
        s2_ds2_1 = RobotRaconteurNode.s.NewStructure("com.robotraconteur.testing.TestService1.teststruct2",self._r)
        s2_ds2_1.mydat = [4.122753e+13, -2.656829e-13, 1.813864e-04, -4.675181e-05, 1.759511e-19, 3.517805e+10, -7.912215e+01, 7.708557e-07, 2.434017e-21, -2.540544e+00, -9.412568e+15, -2.124215e-18, 2.797799e+13, -2.240464e-07, 2.780110e-12, -1.025574e-14, -3.762272e-09, -5.715981e-02, 1.839704e-21, -4.719538e-15, 3.148156e-06, 3.483886e-12, 3.484006e-02, -4.544817e-08, 3.200642e+00, 4.503141e+07, -4.077123e+04, -2.776985e+00, -2.900651e-18, -1.463711e+08, -3.460292e-03, 2.348911e-18, -3.704219e+08, -3.275364e+05, 4.613595e-01, 4.867108e+16, 4.114866e-10, 3.070767e+17, 4.662623e+01]
        s2_ds2["ctest1"]= s2_ds2_1
        s2_ds2_2 = RobotRaconteurNode.s.NewStructure("com.robotraconteur.testing.TestService1.teststruct2",self._r)
        s2_ds2_2.mydat = [-1.037656e+15, -3.782364e-06, 4.982303e+06, -5.510401e-07, 4.271118e-02, -1.718093e+11, -2.644457e+01, -2.374043e-08, 1.729038e-14, 3.370840e+10, 4.302550e-13, 2.643402e+14, 3.199649e+01, 4.620204e-08, 1.323645e+00, -4.337167e-07, -5.003428e+11, 4.176127e+13, 3.324907e-09, -4.207938e-09, -3.324360e-15, 3.317889e+00, 1.775668e+07, -1.295276e-15, -1.610388e-05, 3.417067e-02, -4.874588e+04, -2.109628e+12, 3.130648e+09, 1.898554e-13, 2.421724e-01, 4.227281e-08, 4.844407e+19, -4.490481e+10, 2.599780e+00, 4.039296e+06, -2.944167e-03, -7.388370e+08, -4.473409e-02]
        s2_ds2["anothertest"]= s2_ds2_2
        s2.dstruct2 = s2_ds2
        s2_ls3_1 = RobotRaconteurNode.s.NewStructure("com.robotraconteur.testing.TestService1.teststruct2",self._r)
        s2_ls3_1.mydat = [4.122753e+13, -2.656829e-13, 1.813864e-04, -4.675181e-05, 1.759511e-19, 3.517805e+10, -7.912215e+01, 7.708557e-07, 2.434017e-21, -2.540544e+00, -9.412568e+15, -2.124215e-18, 2.797799e+13, -2.240464e-07, 2.780110e-12, -1.025574e-14, -3.762272e-09, -5.715981e-02, 1.839704e-21, -4.719538e-15, 3.148156e-06, 3.483886e-12, 3.484006e-02, -4.544817e-08, 3.200642e+00, 4.503141e+07, -4.077123e+04, -2.776985e+00, -2.900651e-18, -1.463711e+08, -3.460292e-03, 2.348911e-18, -3.704219e+08, -3.275364e+05, 4.613595e-01, 4.867108e+16, 4.114866e-10, 3.070767e+17, 4.662623e+01]
        s2_ls3_2 = RobotRaconteurNode.s.NewStructure("com.robotraconteur.testing.TestService1.teststruct2",self._r)
        s2_ls3_2.mydat = [-1.037656e+15, -3.782364e-06, 4.982303e+06, -5.510401e-07, 4.271118e-02, -1.718093e+11, -2.644457e+01, -2.374043e-08, 1.729038e-14, 3.370840e+10, 4.302550e-13, 2.643402e+14, 3.199649e+01, 4.620204e-08, 1.323645e+00, -4.337167e-07, -5.003428e+11, 4.176127e+13, 3.324907e-09, -4.207938e-09, -3.324360e-15, 3.317889e+00, 1.775668e+07, -1.295276e-15, -1.610388e-05, 3.417067e-02, -4.874588e+04, -2.109628e+12, 3.130648e+09, 1.898554e-13, 2.421724e-01, 4.227281e-08, 4.844407e+19, -4.490481e+10, 2.599780e+00, 4.039296e+06, -2.944167e-03, -7.388370e+08, -4.473409e-02]
        s2.lstruct3=[s2_ls3_1,s2_ls3_2]
        s2.multidimarray = numpy.array([2.430620e+07, -3.455593e-03, 3.902400e+12, -2.638755e-03, 3.850613e+07, 4.754008e-11, 4.661031e-06, -3.707214e-19, -7.073631e+02, 2.254953e-04, -1.575093e-16, 5.197798e-13, -9.801721e+03, -1.787872e+19, -3.366880e-19, -6.242096e-19, 4.750613e+12, 2.200462e-07, 2.175487e+10, -4.574155e+13, -2.009829e-18, 4.228100e-10, -3.002835e-06, -4.486729e+06, 5.433280e-05, -1.966891e-02, -3.934083e+11, 3.893263e-01, 2.139116e-13, 2.223028e+19, -9.567949e+17, -2.740272e+16, 1.099169e-03, -1.569567e+07, 1.960769e-10, 2.839805e-11, -4.907690e-21, 2.112493e-18, -4.618149e-10, 2.613307e+14, 2.590624e-17, 3.838474e+13, 3.249062e-08, -3.456972e-02, -5.653457e-19, -3.560782e-17, 4.205253e+10, -1.775030e-11, -2.490865e+04, -2.059649e-07, 1.126958e+00, 1.236458e+16, 4.050441e+17, 3.706921e+11, -5.893431e-13, -3.802021e-05, 4.939106e-17, -2.295579e+11, 2.784939e-18, 2.251843e+07, 4.187086e+13, -8.627249e-13, -1.636854e-09, 3.436699e+05, -1.494004e-06, 1.669621e-05, 4.224858e-11, -1.206711e-21, -4.717112e-12, 2.149234e+09, 4.829485e-12, -9.782035e-03, -4.809568e+11, -2.363817e-20, -1.774867e-19, 2.675132e-08, -3.796278e+06, 8.447614e-11, -2.926861e+01, -3.179427e+19, -2.686571e+01, 4.629595e-21, -4.785666e-19, 1.189135e+05, 3.103998e-16, 9.759246e-06, 1.974804e-15, -2.446973e-18, -2.116347e-10, 3.372892e+14, 3.756516e+18, 1.818836e-01, 5.930870e+08, -2.908608e+14, -4.900761e+01, -1.467246e+11, -2.431436e-08, -2.025905e-13, 6.246066e+01, 1.601360e+13]).reshape([10, 10], order="F")
        s2.var3 =RobotRaconteurVarValue( [6.404176e-12, 9.258110e-03, 8.657620e-03, -2.064381e+00, 5.182360e-16, 4.167658e-16, -4.533051e-19, 5.357520e+18, -4.990383e-13, 2.286982e+08, -4.727256e-18, 1.465299e-17, 3.000340e-10, -2.304453e-04],"double[]")
        self._r.struct1 = s2
        s3 = RobotRaconteurNode.s.NewStructure("com.robotraconteur.testing.TestService1.teststruct2",self._r)
        s3.mydat = [-1.451096e-09, -3.762302e-18, 2.016877e+04, -4.171245e+16, 1.500851e+09, -3.071385e-05, 1.329949e+09, 9.439580e-14, 8.652806e-06, -2.729712e-17, -1.664008e-09, 3.787440e-16, -4.281157e-20, -8.703642e-07, 7.130173e-13, 1.162347e-04, -2.485922e-01, 8.924836e+13, 2.150995e+18, -1.816269e-08, 3.572064e-06, -1.020374e+19, -2.467612e-05, 1.294111e-21, 3.030328e-11, 1.736324e+04, 4.221306e+17, -2.544109e+09, 1.047630e-04, 2.082666e+04, -4.120572e-04, -4.550228e-11, -4.959645e+00, 3.988634e-06, -2.901463e-06, 4.379435e+14, 3.697324e+17, -3.285280e+00, -4.491892e-21, 4.962405e-03, -4.143004e-05, 4.447309e+01, 3.196998e-04, -1.679927e+06, -1.859794e+19, -2.749978e-17, -9.042867e+14, 3.970588e+06, -2.359863e-19, 4.923781e-03, 3.689224e-03, 1.741368e-14, -4.943555e-15, -2.473041e-09, -1.687125e-12, 4.622096e+17, 2.456838e-17, -4.076597e+07, -4.082942e-21, -4.483141e+19, 2.463502e-01, -1.818087e+04, 1.094518e+14, 7.514618e+03, -1.175704e-07, -3.071050e+18, -8.006996e-20, 1.363550e-14, -6.753529e+08, -4.661760e+15, -2.475629e-01, -1.282411e+16, -6.328699e-04, 4.898115e+00, 6.921801e-14, 9.951973e+01, 1.669967e-08, -3.750408e-19, -3.363050e-10, -2.470083e-09, 1.544354e-05, -2.844838e-09, 4.426875e+02, 3.468203e-17, -2.376018e+07, -1.431106e+08, -6.900572e-18, -4.640801e+07, 9.947893e+14, -1.166791e+10, -3.478840e+19, -3.103020e-09, -3.256701e+00, 4.374203e-14, 4.655054e-04, -4.106246e-17, 2.373568e+15, -1.319790e-04, 1.485607e+02, -4.933523e-05]
        self._r.struct2 = s3
        s4 = self._r.struct2
        ca(s4.mydat, [-4.415088e+16, -2.033093e-17, 3.634431e-17, 2.030794e-03, 4.464343e-14, -4.137056e+11, 3.609991e-16, 4.332970e-11, 1.327470e-06, -3.304680e+02, 3.184654e-08, 1.194960e-16, -2.958549e+05, -3.320274e+13, 3.486845e-05, 2.878185e-10, -2.982726e-12, -3.653410e-06, 2.059068e+00, 1.150498e+16, -3.647068e+18, -3.847760e+03, -4.333684e-21, -2.357376e-07, -2.560470e-09, 2.931250e-15, 4.966713e-21, 2.960478e-14, -1.959583e+03, 4.593629e-16, 4.193491e-07, 5.941674e+14, 2.198075e+05, 1.487817e-20, -4.643292e+06, 2.543864e-14, 9.478332e+04, 2.948237e+13, -3.144190e-17, -1.369134e+11, -4.908672e-18, -3.581399e-21, -1.682968e-14, -8.984437e-02, 3.067043e-19, -3.361220e+14, -2.591105e-10, -2.119291e-13, 7.649594e+03, -1.869427e-01, -3.403057e+11, -4.798229e-09, -4.120069e+04, 3.384741e-12, 4.697254e-10, -3.594572e-02, -1.973059e+12, -2.627069e-21, 4.096077e-20, 1.629242e-20, -1.561816e+11, 3.240449e+07, -3.967391e+08, 4.635131e-14, -3.436364e-17, 1.485817e-15, -2.145973e+18, 1.160688e+19, 3.266439e+11, 1.686854e+02, -4.048943e+00, -2.905109e+17, -3.953827e+15, -2.855712e+10, -1.197294e-02, -1.997014e+14, 3.951602e+08, 1.287972e+18, -4.228933e+08, 4.212816e-06, -1.252397e+15, 3.517842e+12, -3.315039e-17, -1.816738e+19, 3.595783e+14, -2.834015e-08, 3.436611e+04, -4.192603e+12, 1.152454e+11, -9.405739e-21, -1.862898e+17, -3.811397e-10, 4.486272e+00, 3.666408e+14, -2.681908e-10, -4.859125e+08, -3.593152e+04, -1.883343e-03, -2.445939e-08, 4.540371e+01])
        is_d1_1 = self._r.is_d1
        if len(is_d1_1) != 3:
            raise Exception()
        if is_d1_1[9285] != 1.643392e-01:
            raise Exception()
        if is_d1_1[74822] != 1.537133e+09:
            raise Exception()
        if is_d1_1[4] != 1.369505e-03:
            raise Exception()
        is_d1_2 = {}
        is_d1_2[928]= 4.074501e-07
        is_d1_2[394820]= -4.535303e+05
        is_d1_2[623]= -2.956241e-20
        self._r.is_d1 = is_d1_2
        is_d2_1 = self._r.is_d2
        if len(is_d2_1) != 2:
            raise Exception()
        if is_d2_1["testval1"] != -1.079664e+16:
            raise Exception()
        if is_d2_1["testval2"] != 2.224846e+00:
            raise Exception()
        is_d2_2 = {}
        is_d2_2["testval3"]= 5.242474e+10
        is_d2_2["testval4"]= 2.208636e+08
        self._r.is_d2 = is_d2_2
        is_d3_1 = self._r.is_d3
        if len(is_d3_1) != 2:
            raise Exception()
        ca(is_d3_1[12], [8.609080e-13, 3.946603e+03, 2.994203e-10, 3.200877e+14, 1.747361e-09, 2.827056e-16, -3.676613e-18, 1.886901e-14, -9.970511e-12, 1.932468e-18, -3.629253e-05, 4.903023e-12, -3.919949e-10, 4.982164e+07, 3.823096e-20, -4.044068e-13, 3.114078e+09, 7.572697e-12, -2.619929e+04, -3.882046e+01])
        ca(is_d3_1[832], [4.750899e+00, 3.924377e+18, -2.735066e+17, 4.095362e-21, -2.407932e+09, 4.059499e+10, 1.376975e-10, -8.547220e-21, -1.344568e-20, 2.809398e+03, 2.118944e-06, 2.435328e-03, -1.410999e-12, 9.907226e-04, -9.745948e-20, 1.270118e+15, -2.833333e+05, 1.032636e-10, 5.312574e+13, -2.651512e+02])
        is_d3_2 = {}
        is_d3_2[47]= [4.335907e-08, -3.270294e-03, 1.752801e-01, 1.235219e-20, -4.348647e+02, -4.503864e-21, -3.316231e+15, -2.080056e+17, 1.813854e+13, -3.380846e-05, 4.350998e+03, 4.539570e+11, 8.981827e+09, 3.326114e+01, 2.975688e+06, -1.017456e-12, 2.989498e-03, 2.842392e-03, -1.258677e-21, 1.068563e-15]
        is_d3_2[324]= [3.239279e+12, 1.047689e+17, -1.236114e+17, -4.002822e-17, 2.657374e-03, 7.383907e-19, -5.067889e-13, -4.195122e-12, 3.642885e-01, -2.946040e+14, 5.522403e-08, 6.603132e+04, 1.464154e+05, -1.851534e-08, 2.808294e-13, -2.702278e-11, 3.850704e-06, -2.453957e+02, -3.015401e-02, 1.654070e+05]
        self._r.is_d3 = is_d3_2
        is_d4_1 = self._r.is_d4
        if len(is_d4_1) != 2:
            raise Exception()
        ca(is_d4_1["testval1"], [1.113851e-04, 3.830104e+07, 4.571169e-21, -4.064180e-05, 2.889736e+01, -1.790060e-06, 4.608538e+00, 4.687713e-04, 1.387717e-08, 3.914187e-18, -5.618118e-06, 1.530811e+05, -5.848922e-11, -3.397558e-20, -6.597368e-08, -3.779049e-06, 2.406033e-19, 2.507939e-10, 3.246113e-20, 1.341205e+16])
        ca(is_d4_1["testval2"], [-3.088190e-13, -4.033334e-20, 4.150103e-21, -6.610855e+17, 3.688824e-13, -3.208025e+13, -5.034888e-11, -4.098363e-06, -1.272830e-03, 2.748392e-03, -2.644272e-06, -4.810065e-18, 4.629861e-19, -5.444015e-03, 4.046008e+17, -3.548079e+12, -3.455290e+16, -3.668946e-12, -3.522178e-01, -1.537583e+14])
        is_d4_2 = {}
        is_d4_2["testval3"]= [1.771838e+06, 3.037284e-01, -1.739742e-02, 1.399508e-20, 3.605232e-21, 3.517522e+14, 4.887514e+14, 3.505442e-03, -3.968972e+18, 1.422037e-20, 2.596937e-21, 4.852833e-11, 6.852955e-17, 4.765526e-12, -3.445954e+16, 2.322531e-14, -1.755122e-12, 3.941875e+00, 8.877046e-13, 2.818923e-02]
        is_d4_2["testval4"]= [4.146439e+16, 2.923439e-07, 3.549608e+16, -1.664891e-01, -4.192309e-15, 3.857317e+05, -1.101076e+00, 1.213105e+19, 3.237584e-14, -2.421219e-06, -4.603196e-05, -3.719535e-10, 1.124961e+06, 2.032849e+10, 4.639704e-22, 3.946835e+01, -9.267263e+01, -4.456188e+11, 3.470487e+08, 7.918764e+10]
        self._r.is_d4 = is_d4_2
        is_d5_1 = self._r.is_d5
        if len(is_d5_1) != 1:
            raise Exception()
        is_d5_1_1 = is_d5_1[564]
        numpy.testing.assert_allclose(is_d5_1_1, numpy.array([-2.240130e+14, 1.609980e+16, -1.794755e+07, 8.108785e+17, -2.296286e+08, -2.689029e+13, 2.036672e+07, -4.822871e-02, 4.070748e-05, -2.894952e-04, -1.728526e+17, 4.077694e-19, -2.977734e+13, -9.428667e+03, 2.672315e-08, -1.844359e+19, 4.243010e+09, 4.592716e-01, -3.792531e+10, 3.117892e+04, -1.830821e-16, -3.702984e-18, -1.957300e+12, 9.017553e+12, -2.184986e-17, 1.436890e-02, 4.008279e-12, -2.407568e+10, -3.170667e-07, -2.315539e+16, 6.646599e+09, 2.443847e-01, 1.928730e-21, 3.089540e+00, 2.813232e-02, 1.352336e-21, -3.562256e+05, 3.778036e+08, -3.726478e-13, 3.112159e+15, 3.573414e+17, 3.607559e+09, -2.923247e-19, -2.079346e+14, -4.611547e-16, 2.200040e+00, 3.670772e+07, -4.176987e-20, 2.086575e+06, -2.388241e+01, -3.759717e-19, -2.232760e-01, 9.066157e-21, 2.797633e+07, 3.455296e+00, -3.306761e-08, -2.062866e-22, -4.653724e+07, -3.694312e-17, 2.254095e-06, 3.519767e-16, 1.292737e-06, -3.840896e-08, -1.946825e-20, 2.639141e+18, 3.021503e+07, -1.834066e+18, 4.474920e-02, 3.005033e-20, -1.233782e-10, -3.260111e-08, 2.326419e-09, -2.298222e-19, 7.554873e+15, 2.378479e+19, -5.092127e-03, -4.724838e-07, 3.204184e+06, 2.713748e-12, 1.574309e-05, 6.622323e-01, -4.944461e-01, -1.559672e+19, -3.350494e+15, 2.467451e-14, -4.881873e+13, 1.031263e+15, -4.051814e+12, 1.418548e+07, 1.204368e+17, -4.113152e-02, -4.472069e+16, 4.896886e-14, 2.371633e+05, 3.543019e+04, -3.083516e-22, 1.041761e-09, -2.579812e-06, -2.937567e+09, -4.775349e-16]).reshape([10, 10],order="F"))
        is_d5_2_1 = numpy.array([2.792909e-01, 6.554477e+16, 4.240073e-13, -4.490109e+19, 5.410527e-22, -2.244599e+17, -2.656142e-02, -3.819500e+13, -7.086082e-02, 7.790729e-13, 3.375900e-12, -6.915692e+09, -2.900437e-18, 1.257280e+05, -3.810852e+15, -4.589554e-12, 2.670612e-14, 4.725686e+06, -3.018046e+07, 2.439452e+07, 2.726039e-07, -2.805143e+02, -1.870376e+03, 4.573047e-06, 1.904868e+19, -1.966383e+00, 3.426469e-11, -1.400396e+13, -1.724273e+09, -7.347198e+10, -4.081057e-12, -3.868203e+10, -2.686071e+13, -5.289107e+01, -5.574151e-09, -2.580185e-06, -8.222097e-21, -4.957833e-12, -2.491984e+03, -7.900042e+16, -4.809370e-11, -2.048332e-19, 4.984852e-21, 1.350023e+13, -4.492022e-11, -3.255594e+10, 1.495149e-09, -7.272628e+02, -4.236196e-04, 4.736990e-02, -4.030173e-11, 1.017371e+11, 1.124559e-09, 4.177431e-21, 1.026706e+06, -4.702729e-04, -2.633498e+18, -4.689724e+08, -2.593657e+05, 3.433194e-18, -1.977738e-13, -1.163773e+03, 3.424738e-20, 7.391132e-06, 1.364867e+12, -7.155727e+16, 3.078093e-21, -3.151787e-04, -4.715633e+06, 1.017894e+19, -1.121778e+14, -3.529769e-10, 4.530606e+19, 3.988296e-17, -3.469818e+06, 1.204304e+03, -1.404314e+15, -1.369871e+04, -2.796125e-03, -4.842068e-06, -2.639632e-03, 1.324740e+08, 1.440651e+07, -4.778885e+03, -4.643859e+06, 1.726955e-09, -8.160334e+05, 3.763238e+13, 1.391028e+02, -4.269393e+04, -2.698233e+02, -3.677556e+14, 1.070699e-17, 3.949376e+19, 4.503080e-06, 4.344496e-07, 1.714091e-19, -3.436426e+01, 4.914505e+15, -1.101617e+09, -1.899511e-04, 2.195951e-06, 2.402701e-12, 1.783431e-09, -7.329137e-08, 4.423889e+16, 2.812547e-19, -7.848554e+05, -3.635151e+13, 3.128605e-09, -2.858963e+08, 2.086065e-11, -2.544450e+12, 1.450579e+19, -1.508905e+13, 4.307174e+00, 1.038108e-05, 4.313281e-05, 3.647351e+05, 1.309105e-16, 4.180469e+13, -2.701332e-07, -4.033566e+14, -3.116748e-06, 2.342296e-07, 1.870335e-19, 2.312273e+01, -4.478923e+08, -4.854324e+09, 2.681828e+03, -4.280128e-01, -4.690703e-21, 3.853815e+16, 1.366639e+02, -2.944985e-11, -4.486958e-13, 3.017750e-11, 3.551437e-13, 2.263828e-12, -6.545014e-18, -7.552023e+12, 7.595238e+14, 2.810247e+12, 6.516008e+15, -3.035786e+14, 2.523040e+11, -3.766603e+09, 7.316287e+18, -2.147132e+17, 1.972210e+10, 2.906768e-13, 4.226577e-14, -2.640568e+17, 2.181408e+10, -1.043256e-08, -3.649181e+06, -2.776638e+18, 3.660147e-07, -1.415433e-17, -4.945127e-17, 2.655050e+01, -2.269828e+04, -2.585499e-01, -3.299965e+05, 3.707494e-18, -1.257923e-19, -1.321880e+14, -1.815888e-12, 9.366926e-09, 1.024923e-14, 4.494907e+04, -2.596971e-20, -3.403446e-12, 1.537084e+17, -3.850430e-17, -4.821759e+05, 4.255435e-20, -1.016978e-16, 1.430658e-09, -3.696861e-14, -4.427905e-19, -1.999724e-09, -3.489402e-06, -4.677864e-03, 1.246884e+13, -4.458271e-19, 3.551905e-04, -4.458221e-20, -3.472033e+01, -1.745714e+08, 4.396891e+03, 4.345767e+02, -1.800116e+05, -1.217318e+00, 3.605072e-08, 1.306109e-09, -2.798295e+16, 4.387728e-13, -3.284039e+11, 3.424124e+17]).reshape([10, 20], order="F")
        is_d5_2 = {}
        is_d5_2[328]= is_d5_2_1
        self._r.is_d5=is_d5_2
        is_d6_1 = self._r.is_d6
        if len(is_d6_1) != 1:
            raise Exception()
        is_d6_1_1 = is_d6_1["testval1"]
        
        numpy.testing.assert_allclose(is_d6_1_1, numpy.array([4.229153e+02, 3.406523e+03, -2.158208e+15, -7.464845e+07, -4.763504e+18, 6.777497e-20, -1.265130e+18, 2.145141e+12, -8.473642e-18, -3.780104e+17, -4.356069e+06, 1.199990e+04, -2.413259e+07, -2.609077e-12, -2.121030e-16, -1.224176e+09, -2.836294e-15, -1.975701e-18, 4.311314e-04, -4.932020e-20, -1.307735e-18, -4.000536e+02, -1.718325e+15, -3.493595e+05, 1.707089e+00, 4.416780e+01, -1.152954e-13, 8.396437e-02, -4.304750e+16, 1.154166e+02, -2.331328e-02, 4.821737e-04, 5.831989e-20, -6.887913e+06, -1.592772e+11, 4.730754e-19, 2.543760e-17, -5.864767e+14, 2.077122e-13, 2.801695e-12, -1.171678e+12, -8.854966e+18, -1.555508e-08, 3.589410e+11, -1.495443e-21, 2.876586e-06, -2.265460e-03, 2.544109e-03, 2.019117e-06, -6.458547e-21]).reshape([5, 10], order="F"))
        is_d6_2_1 = numpy.array([2.080438e+03, -2.901444e-01, 2.561452e+12, 6.760682e+14, -2.461568e-10, -4.811907e-20, 6.299564e+11, -2.660066e-19, 4.643316e+13, 3.292265e-13, 1.187460e+19, 3.054313e-07, 3.503026e-20, -1.465147e-08, 3.993039e-17, 2.469296e-10, -4.014504e+07, 1.810733e+17, -3.976509e-19, -9.166607e+15, 1.854678e+02, 2.884879e-12, -4.382521e+14, 3.064407e-05, -9.542195e+07, -3.938411e-13, -2.850416e-03, 3.042038e+14, 1.464437e-12, -1.550126e-06, 4.938341e+11, -3.517527e+19, 3.135793e+19, 1.380313e-14, -1.060961e+18, 2.833127e-10, -1.862230e+02, -2.232851e-05, 4.773548e-05, 3.746071e+13, -4.972451e+09, 4.553754e-14, -8.183438e+10, 3.739120e+18, -1.619189e+19, 4.644394e+08, -8.327578e-11, 4.080876e-02, -2.806082e-03, -1.595033e-06, 1.973067e+16, 2.989575e-07, -8.974247e+15, -4.204211e-03, 1.513025e-02, -4.604953e+03, 4.107290e+16, -3.631920e+12, -1.902472e+13, -4.186326e-14, 2.465135e+13, 5.060414e+12, 7.508582e+11, 3.233186e-14, -6.750005e+14, -9.467336e-16, 2.101440e+03, -1.162425e+08, 7.808216e+04, 4.356208e-19, -3.316834e+14, 3.299774e-19, -3.746431e-16, -3.971172e-07, 2.423744e+10, 1.542747e+17, 2.358704e-05, 4.201668e+17, -3.736856e+07, 3.585645e-07]).reshape([8, 10], order="F")
        is_d6_2 = {}
        is_d6_2["testval2"]= is_d6_2_1
        self._r.is_d6 = is_d6_2
        is_str1_1 = self._r.is_str1
        if len(is_str1_1) != 1:
            raise Exception()
        if is_str1_1[23] != "Hello server":
            raise Exception()
        is_str1_2 = {}
        is_str1_2[24]= "Hello client"
        self._r.is_str1 = is_str1_2
        is_str2_1 = self._r.is_str2
        if len(is_str2_1) != 1:
            raise Exception()
        if is_str2_1["testval1"] != "Hello server":
            raise Exception()
        is_str2_2 = {}
        is_str2_2["testval2"]= "Hello client"
        self._r.is_str2 = is_str2_2
        is_struct1_1 = self._r.is_struct1
        ca(is_struct1_1[748].mydat, [-9.692618e+00, -1.944240e+03, -2.456327e+16, 4.673405e-20, 5.147581e-14, -3.773975e+15, 2.336430e-21, 1.597144e-18, -2.609059e-03, 3.557639e-21, -1.666575e-16, -4.242788e-07, 2.686206e+07, -3.200902e-05, -1.549754e-06, -3.010796e-12, 4.638418e+01, 2.664397e-14, -2.689174e+01, 4.564584e-21])
        is_struct1_2 = {}
        is_struct1_2_1 = RobotRaconteurNode.s.NewStructure("com.robotraconteur.testing.TestService1.teststruct2",self._r)
        is_struct1_2_1.mydat = [-2.101948e-07, -2.594836e-08, 2.515710e+01, -3.834127e-14, -3.088095e+06, -3.256612e-02, -1.855481e-19, 3.801916e+07, 2.145894e+09, 4.487676e+12, 1.351202e-02, -1.125124e-16, 1.369826e-20, -2.290673e+00, 1.786029e-20, -4.991515e+08, 4.006107e-10, -4.947871e-11, -2.737020e-08, 4.123759e-20]
        is_struct1_2[372]= is_struct1_2_1
        self._r.is_struct1 = is_struct1_2
        is_struct2_1 = self._r.is_struct2
        ca(is_struct2_1["testval1"].mydat, [-4.489570e+13, 9.574895e-05, 4.081711e+06, 5.612839e-18, -1.078604e+05, 3.658139e+08, -4.748975e+05, -2.606481e+01, 3.016739e+15, 3.174709e+19, -4.572549e+17, 1.980389e-04, -3.551911e-10, 3.598401e-07, 2.659416e-12, -3.606157e+06, 2.059674e+17, -9.362336e-20, -3.299256e+17, -2.245745e+16])
        is_struct2_2 = {}
        is_struct2_2_1 = RobotRaconteurNode.s.NewStructure("com.robotraconteur.testing.TestService1.teststruct2",self._r)
        is_struct2_2_1.mydat = [6.931327e-21, 4.527137e-02, 1.260822e-18, 3.592805e-12, 1.088317e-05, 3.305865e+03, -9.798828e-20, 1.497504e+18, -3.653592e+01, 1.473952e+10, -1.003612e-20, 1.302159e+18, -8.544326e+05, 1.038521e+16, -2.845746e-18, -3.899909e-04, 4.785560e-02, -7.203365e-12, -1.500022e-14, -1.892753e-17]
        is_struct2_2["testval2"]= is_struct2_2_1
        self._r.is_struct2 = is_struct2_2

        list_d1_1 = self._r.list_d1
        if len(list_d1_1) != 3:
            raise Exception()
        if list_d1_1[0] != 1.643392e-01:
            raise Exception()
        if list_d1_1[1] != 1.537133e+09:
            raise Exception()
        if list_d1_1[2] != 1.369505e-03:
            raise Exception()
        list_d1_2 = [ 4.074501e-07, -4.535303e+05, -2.956241e-20]
        self._r.list_d1 = list_d1_2



        ca(self._r.struct3.a1, [-8.483090e-19, -4.401548e-08, 3.908118e+00, 2.063513e-18, 4.237047e+18, -1.124681e-16, 3.924541e-01, -2.184335e-10, -1.978950e+11, 1.586365e+18, 1.712393e+00, -6.314723e+00, 1.196777e-16, -2.748704e-08, -1.289967e+02, -4.051137e+17, -1.902860e+10, -2.070486e+08, 3.622651e+06, 1.315398e+17])
        struct3_1 = RobotRaconteurNode.s.NewStructure("com.robotraconteur.testing.TestService2.ostruct2",self._r)
        struct3_1.a1 = [-2.426765e+05, -9.410735e+01, -1.667915e+12, -4.084240e-05, 3.199460e+03, 8.256717e-12, -4.772119e-11, -1.061407e-13, 2.759750e+02, -1.212549e+10, 7.012690e+15, 3.953354e+04, -2.617985e-07, 1.104408e-21, -3.889366e+00, 4.549493e+16, -1.376791e+15, -3.445205e-21, 2.137830e-14, 4.620179e+18]
        self._r.struct3 = struct3_1

        list_d3_1 = self._r.list_d3
        if len(list_d3_1) != 2:
            raise Exception()
        ca(list_d3_1[0], [8.609080e-13, 3.946603e+03, 2.994203e-10, 3.200877e+14, 1.747361e-09, 2.827056e-16, -3.676613e-18, 1.886901e-14, -9.970511e-12, 1.932468e-18, -3.629253e-05, 4.903023e-12, -3.919949e-10, 4.982164e+07, 3.823096e-20, -4.044068e-13, 3.114078e+09, 7.572697e-12, -2.619929e+04, -3.882046e+01])
        ca(list_d3_1[1], [4.750899e+00, 3.924377e+18, -2.735066e+17, 4.095362e-21, -2.407932e+09, 4.059499e+10, 1.376975e-10, -8.547220e-21, -1.344568e-20, 2.809398e+03, 2.118944e-06, 2.435328e-03, -1.410999e-12, 9.907226e-04, -9.745948e-20, 1.270118e+15, -2.833333e+05, 1.032636e-10, 5.312574e+13, -2.651512e+02])
        list_d3_2 = [
        [4.335907e-08, -3.270294e-03, 1.752801e-01, 1.235219e-20, -4.348647e+02, -4.503864e-21, -3.316231e+15, -2.080056e+17, 1.813854e+13, -3.380846e-05, 4.350998e+03, 4.539570e+11, 8.981827e+09, 3.326114e+01, 2.975688e+06, -1.017456e-12, 2.989498e-03, 2.842392e-03, -1.258677e-21, 1.068563e-15]
         ,[3.239279e+12, 1.047689e+17, -1.236114e+17, -4.002822e-17, 2.657374e-03, 7.383907e-19, -5.067889e-13, -4.195122e-12, 3.642885e-01, -2.946040e+14, 5.522403e-08, 6.603132e+04, 1.464154e+05, -1.851534e-08, 2.808294e-13, -2.702278e-11, 3.850704e-06, -2.453957e+02, -3.015401e-02, 1.654070e+05]
         ]
        self._r.list_d3 = list_d3_2

        list_d5_1 = self._r.list_d5
        if len(list_d5_1) != 1:
            raise Exception()
        list_d5_1_1 = list_d5_1[0]
        numpy.testing.assert_allclose(list_d5_1_1, numpy.array([-2.240130e+14, 1.609980e+16, -1.794755e+07, 8.108785e+17, -2.296286e+08, -2.689029e+13, 2.036672e+07, -4.822871e-02, 4.070748e-05, -2.894952e-04, -1.728526e+17, 4.077694e-19, -2.977734e+13, -9.428667e+03, 2.672315e-08, -1.844359e+19, 4.243010e+09, 4.592716e-01, -3.792531e+10, 3.117892e+04, -1.830821e-16, -3.702984e-18, -1.957300e+12, 9.017553e+12, -2.184986e-17, 1.436890e-02, 4.008279e-12, -2.407568e+10, -3.170667e-07, -2.315539e+16, 6.646599e+09, 2.443847e-01, 1.928730e-21, 3.089540e+00, 2.813232e-02, 1.352336e-21, -3.562256e+05, 3.778036e+08, -3.726478e-13, 3.112159e+15, 3.573414e+17, 3.607559e+09, -2.923247e-19, -2.079346e+14, -4.611547e-16, 2.200040e+00, 3.670772e+07, -4.176987e-20, 2.086575e+06, -2.388241e+01, -3.759717e-19, -2.232760e-01, 9.066157e-21, 2.797633e+07, 3.455296e+00, -3.306761e-08, -2.062866e-22, -4.653724e+07, -3.694312e-17, 2.254095e-06, 3.519767e-16, 1.292737e-06, -3.840896e-08, -1.946825e-20, 2.639141e+18, 3.021503e+07, -1.834066e+18, 4.474920e-02, 3.005033e-20, -1.233782e-10, -3.260111e-08, 2.326419e-09, -2.298222e-19, 7.554873e+15, 2.378479e+19, -5.092127e-03, -4.724838e-07, 3.204184e+06, 2.713748e-12, 1.574309e-05, 6.622323e-01, -4.944461e-01, -1.559672e+19, -3.350494e+15, 2.467451e-14, -4.881873e+13, 1.031263e+15, -4.051814e+12, 1.418548e+07, 1.204368e+17, -4.113152e-02, -4.472069e+16, 4.896886e-14, 2.371633e+05, 3.543019e+04, -3.083516e-22, 1.041761e-09, -2.579812e-06, -2.937567e+09, -4.775349e-16]).reshape([10, 10], order="F"))
        list_d5_2_1 = numpy.array([2.792909e-01, 6.554477e+16, 4.240073e-13, -4.490109e+19, 5.410527e-22, -2.244599e+17, -2.656142e-02, -3.819500e+13, -7.086082e-02, 7.790729e-13, 3.375900e-12, -6.915692e+09, -2.900437e-18, 1.257280e+05, -3.810852e+15, -4.589554e-12, 2.670612e-14, 4.725686e+06, -3.018046e+07, 2.439452e+07, 2.726039e-07, -2.805143e+02, -1.870376e+03, 4.573047e-06, 1.904868e+19, -1.966383e+00, 3.426469e-11, -1.400396e+13, -1.724273e+09, -7.347198e+10, -4.081057e-12, -3.868203e+10, -2.686071e+13, -5.289107e+01, -5.574151e-09, -2.580185e-06, -8.222097e-21, -4.957833e-12, -2.491984e+03, -7.900042e+16, -4.809370e-11, -2.048332e-19, 4.984852e-21, 1.350023e+13, -4.492022e-11, -3.255594e+10, 1.495149e-09, -7.272628e+02, -4.236196e-04, 4.736990e-02, -4.030173e-11, 1.017371e+11, 1.124559e-09, 4.177431e-21, 1.026706e+06, -4.702729e-04, -2.633498e+18, -4.689724e+08, -2.593657e+05, 3.433194e-18, -1.977738e-13, -1.163773e+03, 3.424738e-20, 7.391132e-06, 1.364867e+12, -7.155727e+16, 3.078093e-21, -3.151787e-04, -4.715633e+06, 1.017894e+19, -1.121778e+14, -3.529769e-10, 4.530606e+19, 3.988296e-17, -3.469818e+06, 1.204304e+03, -1.404314e+15, -1.369871e+04, -2.796125e-03, -4.842068e-06, -2.639632e-03, 1.324740e+08, 1.440651e+07, -4.778885e+03, -4.643859e+06, 1.726955e-09, -8.160334e+05, 3.763238e+13, 1.391028e+02, -4.269393e+04, -2.698233e+02, -3.677556e+14, 1.070699e-17, 3.949376e+19, 4.503080e-06, 4.344496e-07, 1.714091e-19, -3.436426e+01, 4.914505e+15, -1.101617e+09, -1.899511e-04, 2.195951e-06, 2.402701e-12, 1.783431e-09, -7.329137e-08, 4.423889e+16, 2.812547e-19, -7.848554e+05, -3.635151e+13, 3.128605e-09, -2.858963e+08, 2.086065e-11, -2.544450e+12, 1.450579e+19, -1.508905e+13, 4.307174e+00, 1.038108e-05, 4.313281e-05, 3.647351e+05, 1.309105e-16, 4.180469e+13, -2.701332e-07, -4.033566e+14, -3.116748e-06, 2.342296e-07, 1.870335e-19, 2.312273e+01, -4.478923e+08, -4.854324e+09, 2.681828e+03, -4.280128e-01, -4.690703e-21, 3.853815e+16, 1.366639e+02, -2.944985e-11, -4.486958e-13, 3.017750e-11, 3.551437e-13, 2.263828e-12, -6.545014e-18, -7.552023e+12, 7.595238e+14, 2.810247e+12, 6.516008e+15, -3.035786e+14, 2.523040e+11, -3.766603e+09, 7.316287e+18, -2.147132e+17, 1.972210e+10, 2.906768e-13, 4.226577e-14, -2.640568e+17, 2.181408e+10, -1.043256e-08, -3.649181e+06, -2.776638e+18, 3.660147e-07, -1.415433e-17, -4.945127e-17, 2.655050e+01, -2.269828e+04, -2.585499e-01, -3.299965e+05, 3.707494e-18, -1.257923e-19, -1.321880e+14, -1.815888e-12, 9.366926e-09, 1.024923e-14, 4.494907e+04, -2.596971e-20, -3.403446e-12, 1.537084e+17, -3.850430e-17, -4.821759e+05, 4.255435e-20, -1.016978e-16, 1.430658e-09, -3.696861e-14, -4.427905e-19, -1.999724e-09, -3.489402e-06, -4.677864e-03, 1.246884e+13, -4.458271e-19, 3.551905e-04, -4.458221e-20, -3.472033e+01, -1.745714e+08, 4.396891e+03, 4.345767e+02, -1.800116e+05, -1.217318e+00, 3.605072e-08, 1.306109e-09, -2.798295e+16, 4.387728e-13, -3.284039e+11, 3.424124e+17]).reshape([10, 20], order="F")
        list_d5_2 = [ list_d5_2_1 ]
        self._r.list_d5=list_d5_2

        list_struct2_1 = self._r.list_struct1
        ca(list_struct2_1[0].mydat, [-9.692618e+00, -1.944240e+03, -2.456327e+16, 4.673405e-20, 5.147581e-14, -3.773975e+15, 2.336430e-21, 1.597144e-18, -2.609059e-03, 3.557639e-21, -1.666575e-16, -4.242788e-07, 2.686206e+07, -3.200902e-05, -1.549754e-06, -3.010796e-12, 4.638418e+01, 2.664397e-14, -2.689174e+01, 4.564584e-21 ])
        list_struct2_2 = []
        list_struct2_2_1 = RobotRaconteurNode.s.NewStructure("com.robotraconteur.testing.TestService1.teststruct2",self._r)
        list_struct2_2_1.mydat = [ -2.101948e-07, -2.594836e-08, 2.515710e+01, -3.834127e-14, -3.088095e+06, -3.256612e-02, -1.855481e-19, 3.801916e+07, 2.145894e+09, 4.487676e+12, 1.351202e-02, -1.125124e-16, 1.369826e-20, -2.290673e+00, 1.786029e-20, -4.991515e+08, 4.006107e-10, -4.947871e-11, -2.737020e-08, 4.123759e-20 ]
        list_struct2_2.append(list_struct2_2_1)
        self._r.list_struct1 = list_struct2_2

        #varvalue types (TODO: finish these...)

        ca(self._r.var_num.data, [-1680284833, -54562307, 732107275, 1470526962, -1389452949, 256801409, 261288152, 1728150828, 1322531658, -1640628174, 1036878614, 511108054, 2057847386, 288780916, 996595759])
        self._r.var_num = RobotRaconteurVarValue([-1046369769, 1950632347, 1140727074, -1277424443, 163999900, 970815027, 545593183, 514305170, 1896372264, 1385916382],"int32[]")
        if self._r.var_str.data != "Hello Client!":
            raise Exception()
        self._r.var_str = RobotRaconteurVarValue("Hello Server!","string")
        ca((self._r.var_struct.data).mydat, [-9.052731e+13, 4.151705e-17, -4.004463e+19, -2.838274e+03, 9.983314e+12, 2.764122e+10, -1.131486e+03, 2.418899e+12, 1.323675e-05, -4.602174e+13, 2.717530e+01, 1.193887e-10, -4.137578e+16, -1.246990e-19, 4.244315e-18, -2.833005e-08, 1.956266e-04, 4.130129e-21, 1.641708e-11, -4.488158e-19])
        var_struct_1 = RobotRaconteurNode.s.NewStructure("com.robotraconteur.testing.TestService1.teststruct2",self._r)
        var_struct_1.mydat = [-4.945426e-20, 1.763386e+13, 3.431578e-04, 4.411409e+17, -2.690201e+03, 3.025939e-10, -3.659846e+11, -4.780435e-10, -3.246816e+14, -1.815578e+04, 2.236455e+10, -4.639041e+14, 1.767930e+10, -1.636094e+05, -4.392462e-01, 2.225260e+04, -5.250245e+18, 8.755282e-12, 2.005819e-10, 2.702210e+04]
        self._r.var_struct = RobotRaconteurVarValue(var_struct_1,"com.robotraconteur.testing.TestService1.teststruct2")
        if ((self._r.var_vector.data)[10]) != "Hello Client!":
            raise Exception()
        var_vector_1 = {}
        var_vector_1[11]= RobotRaconteurVarValue("Hello Server!","string")
        self._r.var_vector = RobotRaconteurVarValue(var_vector_1,"varvalue{int32}")
        if ((self._r.var_dictionary.data)["test1"]) != "Hello Client!":
            raise Exception()
        var_dictionary_1 = {}
        var_dictionary_1["test2"]= RobotRaconteurVarValue("Hello Server!","string")
        self._r.var_dictionary = RobotRaconteurVarValue(var_dictionary_1,"varvalue{string}")
        if ((self._r.var_list.data)[0]) != "Hello Client!":
            raise Exception()
        var_list_1= [RobotRaconteurVarValue("Hello Server!","string")]
        self._r.var_list = RobotRaconteurVarValue(var_list_1,"varvalue{list}")
        var_a_1 = self._r.var_multidimarray.data
        numpy.testing.assert_allclose(var_a_1, numpy.array([-4.915597e-01, 3.892823e+00, 2.622325e+08, -7.150935e+04, 9.418756e+00, 3.633879e+18, 3.522383e-03, -4.989811e+05, 2.027383e-03, -3.153241e+12, -6.948245e-21, -3.198577e+14, 6.172905e+09, 3.849430e+15, 8.600383e+13, 4.079437e-17, 3.194775e+06, 4.222550e-18, 1.758122e+17, -1.018308e+03]).reshape([5, 4], order="F"))
        self._r.var_multidimarray = RobotRaconteurVarValue(numpy.array([3.792953e+00, 2.968121e-17, -3.976413e-15, 4.392986e+19, 2.197463e+10, -2.627743e-14, -2.184665e+17, 1.972257e-17, 9.929684e-03, -3.096821e+17, 3.598051e+11, -6.266015e-18, 1.811985e-11, 2.815232e-07, 7.469467e-06, 6.141798e+13, 3.105763e+09, -1.697809e-10, -4.141707e-17, 4.391634e+13]).reshape([5, 4], order="F"),"double[*]")


        #Test error passing
        err1 = False
        try:
            self._r.errtest = 1
        except Exception as e:
            err1 = True
        finally:
            pass
        if not err1:
            raise Exception()
        err2 = False
        try:
            d = self._r.errtest
        except Exception as e:
            err2 = True
        finally:
            pass
        if not err2:
            raise Exception()
        if self._r.nulltest != None:
            raise Exception()
        self._r.nulltest = None

    def TestFunctions(self):
        self._r.func1()
        self._r.func2(10, 20.34)
        if self._r.func3(2, 3.45) != 5.45:
            raise Exception()
        if self._r.meaning_of_life() != 42:
            raise Exception()
        errthrown = False
        try:
            self._r.func_errtest()
        except:
            errthrown = True
        finally:
            pass
        if not errthrown:
            raise Exception()

        errthrown=False
        try:
            self._r.func_errtest1()
        except DataTypeException:
            errthrown=True
        if not errthrown:
            raise Exception()

        e1=RobotRaconteurNode.s.GetExceptionType("com.robotraconteur.testing.TestService1.testexception1",self._r)
        e3=RobotRaconteurNode.s.GetExceptionType("com.robotraconteur.testing.TestService2.testexception3",self._r)

        errthrown=False
        try:
            self._r.func_errtest2()
        except e1:
            errthrown=True
        if not errthrown:
            raise Exception()

        errthrown=False
        try:
            self._r.func_errtest3()
        except e3:
            errthrown=True
        if not errthrown:
            raise Exception()


    def TestEvents(self):
        ev1=self._r.ev1
        ev1 += self.ev1_cb
        ev2=self._r.ev2
        ev2 += self.ev2_cb
        try:
            self._ev1_event = threading.Event()
            self._ev2_event = threading.Event()
            self._r.func1()
            self._r.func2(27.3, 98.23)
            if not self._ev1_event.wait(2):
                raise Exception()
            if not self._ev2_event.wait(2):
                raise Exception()
        finally:
            ev1=self._r.ev1
            ev1 -= self.ev1_cb
            ev2=self._r.ev2
            ev2 -= self.ev2_cb
            self._ev1_event = None
            self._ev2_event = None

    def ev1_cb(self):
        self._ev1_event.set()

    def ev2_cb(self, d, s):
        if d == 27.3 and s.mydat[0] == 98.23:
            self._ev2_event.set()

    def TestObjRefs(self):
        o1 = self._r.get_o1()
        o2_10 = self._r.get_o2(10)
        o2_34 = self._r.get_o2(34)
        o3_1 = self._r.get_o3(1)
        o4_myind = self._r.get_o4("myind")
        o4_specialind = self._r.get_o4("ind!@#$%^&*().<>     ")
        o2_10_o2_1_32 = o2_10.get_o2_2(32)
        o2_10_o2_1_32_o3_ind1 = o2_10_o2_1_32.get_o3_1("ind1")
        o2_10_o2_1_32_o3_ind2 = o2_10_o2_1_32.get_o3_1("ind2")
        o1.d1 = [-2.086627e+06, 3.092642e+04, -1.981667e+02, 1.963286e-20, 4.264052e-08, 3.594320e+12, -4.820517e-02, -3.629590e+06, 6.037089e-07, 3.328419e+06]
        o2_10.d1 = [4.978178e-14, 2.867603e-17, 4.471047e-21, -2.002902e+15, -2.910881e-03, -2.601092e-03, -3.043199e+16, -3.257109e-12, 1.834255e-11, -3.383015e+00]
        o2_34.d1 = [4.661927e-02, 2.334444e+02, 3.985567e+12, -2.324843e+01, -3.315866e+03, -4.442404e+10, 3.280626e-02, 2.334668e-12, -3.374202e-14, 4.809260e+02]
        o3_1.d1 = [-1.882441e-04, 2.065458e+14, -6.309214e-16, -3.181637e-07, -9.906616e+02, 1.684926e-14, 1.672252e+15, -3.950901e+01, -3.295950e-17, -3.080902e+13]
        o4_myind.d1 = [2.997950e-14, -1.077977e+17, 3.721399e-09, -1.289619e+18, 4.494844e+06, -4.918719e-15, 2.194759e+13, 2.554572e-09, 4.166299e-06, -1.409589e+04]
        o4_specialind.d1 = [3.404179e-08, -1.749189e-18, -3.219593e-09, 1.313794e+01, -4.193673e+10, -2.479829e+07, -2.617068e+04, 8.181730e+15, -2.003653e+18, -1.833401e+19]
        o2_10_o2_1_32.data = "Hello world!"
        o2_10_o2_1_32_o3_ind1.data2 = "Test string 1"
        o2_10_o2_1_32_o3_ind2.data2 = "Test string 2"
        self._r.o6_op(0)
        o6_1 = self._r.get_o6()
        o6_1_1 = o6_1.get_o2_1()
        o6_1.d1 = [0.0]
        o6_1_1.data = "Hello world!"
        self._r.o6_op(1)
        def f1():
            o6_1.d1=[0.0]
        def f2():
            o6_1_1.data="Hello world!"

        self.ShouldBeErr(f1)
        self.ShouldBeErr(f2)
        o6_2 = self._r.get_o6()
        o6_2.data = "Hello world!"
        self._r.o6_op(2)
        def f3():
            o6_2.data="Hello world!"
            self.ShouldBeErr(f3)
        o6_3 = self._r.get_o6()
        o6_3.add_val(2)


    def TestPipes(self):
        self._ee1 = threading.Event()
        self._ee2 = threading.Event()
        self._ee3 = threading.Event()
        e1 = self._r.p1.Connect(-1)
        e2 = self._r.p1.Connect(3432)
        e3 = self._r.p2.Connect(-1)

        e1.RequestPacketAck = True
        e1.PacketReceivedEvent += self.ee1_cb
        e1.PacketAckReceivedEvent += self.ee1_ack_cb
        e2.PacketReceivedEvent += self.ee2_cb
        e3.PacketReceivedEvent += self.ee3_cb
        self._packetnum = e1.SendPacket([1, 2, 3, 4])
        e1.SendPacket([5, 6, 7, 8])
        e1.SendPacket([-1, -2, -3, -5.32])
        e2.SendPacket([3.21])
        e2.SendPacket([4.72])
        e2.SendPacket([72.34])
        s1 = RobotRaconteurNode.s.NewStructure("com.robotraconteur.testing.TestService1.teststruct2",self._r)
        s1.mydat = [738.29]
        s2 = RobotRaconteurNode.s.NewStructure("com.robotraconteur.testing.TestService1.teststruct2",self._r)
        s2.mydat = [89.83]
        e3.SendPacket(s1)
        e3.SendPacket(s2)
        if not self._ee1.wait(5):
            raise Exception()
        if not self._ee2.wait(5):
            raise Exception()
        time.sleep(1)
        # if not self._ee3.wait(5):
        #    raise Exception()

        ca(e1.ReceivePacket(), [1, 2, 3, 4])
        ca(e1.ReceivePacket(), [5, 6, 7, 8])
        ca(e1.ReceivePacket(), [-1, -2, -3, -5.32])
        ca(e2.ReceivePacket(), [3.21])
        ca(e2.ReceivePacket(), [4.72])
        ca(e2.ReceivePacket(), [72.34])
        ca(e3.ReceivePacket().mydat, [738.29])
        ca(e3.ReceivePacket().mydat, [89.83])
        time.sleep(.5)
        #if not self._ack_recv:
        #    raise Exception()
        self._r.pipe_check_error()
        
        if not self._r.p1.Direction == MemberDefinition_Direction_both:
            raise Exception()
        
        if not e1.Direction == MemberDefinition_Direction_both:
            raise Exception()
        
        e1.Close()
        e2.Close()
        e3.Close()
        
    def ee1_cb(self, p):
        if p.Available < 3:
            return
        try:
            self._ee1.set()

        finally:
            pass

    def ee1_ack_cb(self, p, packetnum):

        if packetnum == self._packetnum:
            self._ack_recv = True

    def ee2_cb(self, p):
        if p.Available < 3:
            return
        try:
            self._ee2.set()

        finally:
            pass

    def ee3_cb(self, p):
        if p.Available < 2:
            return
        try:
            self._ee3.set()


        finally:
            pass

    def ShouldBeErr(self, a):
        err = False

        try:
            a()
        except:
            err = True
        finally:
            pass
        if not err:
            raise Exception()

    def TestCallbacks(self):
        self._cb1_called = False
        self._cb2_called = False
        self._cb3_called = False
        self._cb4_called = False
        self._cb5_called = False
        self._r.cb1.Function = self.cb1_func
        self._r.cb2.Function = self.cb2_func
        self._r.cb3.Function = self.cb3_func
        self._r.cb_meaning_of_life.Function = self.cb_meaning_of_life_func
        self._r.cb_errtest.Function = self.cb_errtest
        self._r.test_callbacks()
        if not self._cb1_called or not self._cb2_called or not self._cb3_called or not self._cb4_called or not self._cb5_called:
            raise Exception()

    def cb1_func(self):
        self._cb1_called = True

    def cb2_func(self, d1, d2):
        if d1 != 739.2 or d2 != 0.392:
            raise Exception()
        self._cb2_called = True

    def cb3_func(self, d1, d2):
        self._cb3_called = True
        return d1 + d2 + 3.14

    def cb_meaning_of_life_func(self):
        self._cb4_called = True
        return 42

    def cb_errtest(self):
        self._cb5_called = True
        raise Exception("This is a test")

    def TestWires(self):
        self._w1_called = False
        self._w2_called = False
        self._w3_called = False
        w1 = self._r.w1.Connect()
        w2 = self._r.w2.Connect()
        w3 = self._r.w3.Connect()

        w1.InValueLifespan=10

        w11=w1.WireValueChanged; w11 += self.w1_changed
        w21=w2.WireValueChanged; w21 += self.w2_changed
        w31=w3.WireValueChanged; w31 += self.w3_changed
        w1.OutValue = [0]
        s1 = RobotRaconteurNode.s.NewStructure("com.robotraconteur.testing.TestService1.teststruct2",self._r)
        s1.mydat = [0]
        w2.OutValue = s1
        a1 = numpy.zeros((1,1),numpy.int32)
        w3.OutValue = a1
        w1.OutValue = [-2.377683e+02, -6.760080e-08, 4.191315e-18, -4.621977e+07, -1.570323e+03, -4.163378e+03, -2.506701e+13, -4.755701e+18, -1.972380e-19, 1.791593e-11]
        s2 = RobotRaconteurNode.s.NewStructure("com.robotraconteur.testing.TestService1.teststruct2",self._r)
        s2.mydat = [-1.014645e-21, 4.743740e+11, 5.804886e-04, 2.963852e-20, 4.277621e-21, -1.168151e+13, -2.638708e-18, -5.123312e+14, 1.261123e-05, 2.552626e-10]
        w2.OutValue = s2
        a2 = numpy.array([2058500854, -611248192, 197490486, -517717939, -513450368, 296469979, 645365194, 2043654604, -1672941174, 710030901],numpy.int32).reshape([2, 5], order="F")
        w3.OutValue = a2
        time.sleep(.5)
        in1 = w1.InValue
        ca(in1, [-2.377683e+02, -6.760080e-08, 4.191315e-18, -4.621977e+07, -1.570323e+03, -4.163378e+03, -2.506701e+13, -4.755701e+18, -1.972380e-19, 1.791593e-11])
        in2 = w2.InValue
        ca(in2.mydat, [-1.014645e-21, 4.743740e+11, 5.804886e-04, 2.963852e-20, 4.277621e-21, -1.168151e+13, -2.638708e-18, -5.123312e+14, 1.261123e-05, 2.552626e-10])
        in3 = w3.InValue
        numpy.testing.assert_allclose(in3, numpy.array([2058500854, -611248192, 197490486, -517717939, -513450368, 296469979, 645365194, 2043654604, -1672941174, 710030901]).reshape([2, 5], order="F"))
        if not self._w1_called or not self._w2_called or not self._w3_called:
            raise Exception()

        (res,in1_2, in1_2_ts) = w1.TryGetInValue()
        if not res: raise Exception()
        ca(in1_2, [-2.377683e+02, -6.760080e-08, 4.191315e-18, -4.621977e+07, -1.570323e+03, -4.163378e+03, -2.506701e+13, -4.755701e+18, -1.972380e-19, 1.791593e-11])
        
        (res,out1_2, out1_2_ts) = w1.TryGetOutValue()
        if not res: raise Exception()
        ca(out1_2, [-2.377683e+02, -6.760080e-08, 4.191315e-18, -4.621977e+07, -1.570323e+03, -4.163378e+03, -2.506701e+13, -4.755701e+18, -1.972380e-19, 1.791593e-11])

        if not self._r.w1.Direction == MemberDefinition_Direction_both:
            raise Exception()
        
        if not w1.Direction == MemberDefinition_Direction_both:
            raise Exception()

        w1.InValueLifespan=0.001
        time.sleep(0.01)
        def f1():
            in1_2 = w1.InValue

        self.ShouldBeErr(f1)

        w1.Close()
        w2.Close()
        w3.Close()
      

    def w1_changed(self, c, value, t):
        self._w1_called = True

    def w2_changed(self, c, value, t):
        self._w2_called = True

    def w3_changed(self, c, value, t):
        self._w3_called = True

    def TestMemories(self):
        self.test_m1()
        #self.test_m2()
        #self.test_m3()

    def test_m1(self):
        if self._r.m1.Length != 100:
            raise Exception()
        m1_1 = [0]*11
        self._r.m1.Read(10, m1_1, 1, 10)
        ca(m1_1, [0, -1.478723e-16, 1.507042e-05, -2.046271e+13, 4.014775e+06, 4.140740e+10, 1.318907e+16, -2.312403e+17, 4.463696e-13, 9.173421e-04, 6.169183e-21])
        m1_2 = [3.462892e+10, -1.149841e-18, 4.649317e-15, -3.632280e-19, -5.252280e+07, 1.800453e-07, 3.772468e-04, -1.911891e+09, -3.018967e-14, 4.835062e-06, 5.269663e+13, 4.946221e+03]
        self._r.m1.Write(20, m1_2, 2, 8)
        m1_3 = [0]*100
        self._r.m1.Read(0, m1_3, 0, 100)
        m1_4 = [-2.675014e-13, 6.884672e-07, 4.855899e-02, 1.634267e-08, -5.346105e+06, 9.245749e+09, 2.174639e+16, -3.574166e+04, 3.063678e+16, 4.748279e-16, -1.478723e-16, 1.507042e-05, -2.046271e+13, 4.014775e+06, 4.140740e+10, 1.318907e+16, -2.312403e+17, 4.463696e-13, 9.173421e-04, 6.169183e-21, 3.643045e+09, -3.784476e+13, -1.878617e-21, -4.122785e+01, -2.477761e+15, -5.220540e-11, -3.930894e-19, 3.980082e-12, -3.681569e-20, 4.675366e+19, -7.454667e-06, -1.529932e+17, -3.707663e-04, -3.356188e-20, -2.393304e-07, 1.339372e-18, -3.735916e-15, 1.715447e+01, 1.316085e+02, 9.603036e-05, 1.458992e+16, 9.228113e+11, 1.099841e-12, -2.484793e-09, 4.826956e-19, -3.662630e-11, -3.274562e+10, 1.866042e-12, 4.061219e-13, 1.307997e-18, -1.210979e+08, 4.036328e+02, -2.713849e-11, -3.673995e-01, -4.576021e+03, 1.519751e+03, 1.792427e-16, -2.033399e+18, 4.341947e+08, -1.699292e-09, -1.007978e-21, 3.200139e-15, -3.157557e+03, -3.717883e-15, 4.337614e+02, -3.666534e-12, -1.821013e-14, -2.260577e-20, 1.722045e-06, 1.886614e+00, -1.278609e+15, 2.923499e-03, 4.969081e+02, 4.438380e-06, -3.890489e-11, -3.261564e-17, 6.172945e-10, 4.951740e+19, 3.460327e+11, -3.600349e-16, 2.419445e+11, -9.124824e+10, 4.127522e+04, 1.443468e+00, -3.968841e-21, -2.507203e+05, 2.214239e+13, -3.327687e+07, 1.167160e+09, -4.361249e-11, -4.609514e+14, -2.461408e+13, 5.584758e+06, 3.989706e-07, 2.597151e-12, -2.961640e+08, -2.173964e-02, -1.866864e-11, 4.832786e-08, 2.713705e-07]
        #Array.Copy(m1_2, 2, m1_4, 20, 8)
        m1_4[20:(20+8)]=m1_2[2:(2+8)]
        ca(m1_3, m1_4)

    def test_m2(self):        
        if self._r.m2.DimCount != 5:
            raise Exception()
        m2_dims = self._r.m2.Dimensions
        ca(m2_dims, [10, 10, 10, 10, 10])
        m1 = MultiDimArrayTest.LoadDoubleArrayFromFile(path.join(MultiDimArrayTest.TestDataPath,"testmdarray1.bin"))
        m2 = MultiDimArrayTest.LoadDoubleArrayFromFile(path.join(MultiDimArrayTest.TestDataPath,"testmdarray2.bin"))
        m3 = MultiDimArrayTest.LoadDoubleArrayFromFile(path.join(MultiDimArrayTest.TestDataPath,"testmdarray3.bin"))
        m4 = MultiDimArrayTest.LoadDoubleArrayFromFile(path.join(MultiDimArrayTest.TestDataPath,"testmdarray4.bin"))
        m5 = MultiDimArrayTest.LoadDoubleArrayFromFile(path.join(MultiDimArrayTest.TestDataPath,"testmdarray5.bin"))
        self._r.m2.Write([0, 0, 0, 0, 0], m1, [0, 0, 0, 0, 0], m1.Dims)
        m1_2 = numpy.zeros([10, 10, 10, 10, 10])
        self._r.m2.Read([0, 0, 0, 0, 0], m1_2, [0, 0, 0, 0, 0], m1.Dims)
        numpy.testing.assert_allclose(m1,m1_2)        
        self._r.m2.Write([2, 2, 3, 3, 4], m2, [0, 2, 0, 0, 0], [1, 5, 5, 2, 1])
        m2_2 = numpy.zeros([10, 10, 10, 10, 10])
        self._r.m2.Read([0, 0, 0, 0, 0], m2_2, [0, 0, 0, 0, 0], m1.Dims)
        numpy.assert_allclose(m2_2, m3)
        m6 = numpy.zeros([2, 2, 1, 1, 10])
        self._r.m2.Read([4, 2, 2, 8, 0], m6, [0, 0, 0, 0, 0], [2, 2, 1, 1, 10])
        numpy.assert_allclose(m4, m6)        
        m7 = numpy.zeros([4, 4, 4, 4, 10])
        self._r.m2.Read([4, 2, 2, 8, 0], m7, [2, 1, 2, 1, 0], [2, 2, 1, 1, 10])
        numpy.assert_allclose(m5, m7)
        
    def test_m3(self):
        m1 = MultiDimArrayTest.LoadByteArrayFromFile(path.join(MultiDimArrayTest.TestDataPath, "testmdarray_b1.bin"))
        m2 = MultiDimArrayTest.LoadByteArrayFromFile(path.join(MultiDimArrayTest.TestDataPath, "testmdarray_b2.bin"))
        m3 = MultiDimArrayTest.LoadByteArrayFromFile(path.join(MultiDimArrayTest.TestDataPath, "testmdarray_b3.bin"))
        m4 = MultiDimArrayTest.LoadByteArrayFromFile(path.join(MultiDimArrayTest.TestDataPath, "testmdarray_b4.bin"))
        m5 = MultiDimArrayTest.LoadByteArrayFromFile(path.join(MultiDimArrayTest.TestDataPath, "testmdarray_b5.bin"))
        self._r.m3.Write([0, 0], m1, [0, 0], [1024, 1024])
        m1_2 = numpy.zeros([1024, 1024], dtype=numpy.uint8)
        self._r.m3.Read([0, 0], m1_2, [0, 0], [1024, 1024])
        numpy.testing.assert_allclose(m1, m1_2)        
        self._r.m3.Write([50, 100], m2, [20, 25], [200, 200])
        m2_2 = numpy.zeros([1024, 1024], dtype=numpy.uint8)
        self._r.m3.Read([0, 0], m2_2, [0, 0], [1024, 1024])        
        numpy.testing.assert_allclose(m3, m2_2)
        m6 = numpy.zeros([200, 200], numpy.uint8)
        self._r.m3.Read([65, 800], m6, [0, 0], [200, 200])        
        numpy.testing.assert_allclose(m4, m6)
        m7 = numpy.zeros([512, 512], dtype=numpy.uint8)
        self._r.m3.Read([65, 800], m7, [100, 230], [200, 200])        
        numpy.testing.assert_allclose(m5, m7)

    def TestAuthentication(self, url):
        #Test two different logins

        cred1={"password": RobotRaconteurVarValue("testpass1","string")}
        r1 = RobotRaconteurNode.s.ConnectService(url, "testuser1", cred1)
        r1.func3(2.2, 3.3)
        RobotRaconteurNode.s.DisconnectService(r1)

        cred2={"password": RobotRaconteurVarValue("testpass2","string")}
        r2 = RobotRaconteurNode.s.ConnectService(url, "testuser2", cred2)
        r2.func3(2.2, 3.3)
        RobotRaconteurNode.s.DisconnectService(r2)
        #Check an invalid password
        err = False
        r3 = None
        try:
            r3 = RobotRaconteurNode.s.ConnectService(url, "testuser2", cred1)
            r3.func3(2.2, 3.3)
        except Exception as e:
            err = True
            try:
                if (r3 != None):
                    RobotRaconteurNode.s.DisconnectService(r3)

            except:
                pass
        finally:
            pass
        if not err:
            raise Exception()
        err2 = False
        #Check no password
        r4 = None
        try:
            r4 = RobotRaconteurNode.s.ConnectService(url)
            r4.func3(2.2, 3.3)
        except Exception as e:
            err2 = True
            try:
                RobotRaconteurNode.s.DisconnectService(r4)

            except:
                pass
        finally:
            pass
        if not err2:
            raise Exception()

    def TestObjectLock(self, url):
        #Run a test, check 6 things:
        #1. Exclusive username lock works as expected (user with lock can acces, other user can't)
        #2. Check that session-level lock works as expected (only one session can access the locked object)
        #3. Check that "sub-tree" objects lock as expected
        #5. Object lock release works
        #6. Object lock override works
        #Log in twice

        cred1={"password": RobotRaconteurVarValue("testpass1","string")}
        r1 = RobotRaconteurNode.s.ConnectService(url, "testuser1", cred1)
        #Log in again with "testuser1" username

        cred2={"password": RobotRaconteurVarValue("testpass2","string")}
        r2 = RobotRaconteurNode.s.ConnectService(url, "testuser1", cred1)
        r1_o = r1.get_o1()
        r1_o_o2 = r1_o.get_o2_1()
        r2_o = r2.get_o1()
        r2_o_o2 = r2_o.get_o2_1()
        r3 = RobotRaconteurNode.s.ConnectService(url, "testuser2", cred2)
        r3_o = r3.get_o1()
        r3_o_o2 = r3_o.get_o2_1()
        #Make sure all the objects work
        r1.func3(2.2, 3.3)
        r1_o.d1 = [1.0]
        r1_o_o2.data = "Hello world"
        r2.func3(2.2, 3.3)
        r2_o.d1 = [1.0]
        r2_o_o2.data = "Hello world"
        r3.func3(2.2, 3.3)
        r3_o.d1 = [1.0]
        r3_o_o2.data = "Hello world"
        #Lock the object by username
        RobotRaconteurNode.s.RequestObjectLock(r1_o, RobotRaconteurObjectLockFlags_USER_LOCK)
        #Check that all users that should access the objects can
        r1.func3(2.2, 3.3)
        r1_o.d1 = [1.0]
        r1_o_o2.data = "Hello world"
        r2.func3(2.2, 3.3)
        r2_o.d1 = [1.0]
        r2_o_o2.data = "Hello world"
        r3.func3(2.2, 3.3)
        #Check that objects that shouldn't be able to access the objects can't

        def f1():
            r3_o.d1=[1.0]
        def f2():
            r3_o_o2.data="Hello world"


        self.ShouldBeErr(f1)
        self.ShouldBeErr(f2)
        #Unlock and recheck all
        RobotRaconteurNode.s.ReleaseObjectLock(r1_o)
        r1.func3(2.2, 3.3)
        r1_o.d1 = [1.0]
        r1_o_o2.data = "Hello world"
        r2.func3(2.2, 3.3)
        r2_o.d1 = [1.0]
        r2_o_o2.data = "Hello world"
        r3.func3(2.2, 3.3)
        r3_o.d1 = [1.0]
        r3_o_o2.data = "Hello world"
        #Relock, test that the lock is active, and then close the connection.  The lock should release.  The
        #second session is closed first, and should not release the lock.
        RobotRaconteurNode.s.RequestObjectLock(r1_o, RobotRaconteurObjectLockFlags_USER_LOCK)
        def f3():
            r3_o.d1=[1.0]
        self.ShouldBeErr(f3)
        r2_o.d1 = [1.0]
        RobotRaconteurNode.s.DisconnectService(r2)
        #Object still should be locked

        def f4():
            r3_o.d1=[1.0]
        self.ShouldBeErr(f4)
        #Now close the session and lock should be released
        RobotRaconteurNode.s.DisconnectService(r1)
        r3_o.d1 = [1.0]
        #Reconnect the first two test sessions
        r1 = RobotRaconteurNode.s.ConnectService(url, "testuser1", cred1)
        r2 = RobotRaconteurNode.s.ConnectService(url, "testuser2", cred2)
        r1_o = r1.get_o1()
        r1_o_o2 = r1_o.get_o2_1()
        r2_o = r2.get_o1()
        r2_o_o2 = r2_o.get_o2_1()
        #Test the exclusive client lock
        RobotRaconteurNode.s.RequestObjectLock(r1_o, RobotRaconteurObjectLockFlags_CLIENT_LOCK)
        r1_o.d1 = [1.0]
        def f5():
            r2_o.d1=[1.0]
        self.ShouldBeErr(f5)
        def f6():
            r3_o.d1=[1.0]
        self.ShouldBeErr(f6)
        #Test the lock override by testsuperpass

        cred5={"password": RobotRaconteurVarValue("superpass1","string")}
        r5 = RobotRaconteurNode.s.ConnectService(url, "testsuperuser", cred5)
        r5_o = r5.get_o1()
        RobotRaconteurNode.s.ReleaseObjectLock(r5_o)
        #Make sure the lock is released
        r2_o.d1 = [1.0]
        r3_o.d1 = [1.0]
        #Close all connections
        RobotRaconteurNode.s.DisconnectService(r1)
        RobotRaconteurNode.s.DisconnectService(r2)
        RobotRaconteurNode.s.DisconnectService(r3)
        RobotRaconteurNode.s.DisconnectService(r5)

    def TestMonitorLock(self, url):
        #The monitor lock aquires an exclusive sock to a single thread on the client.
        #This lock is for a single thread, and works for all clients and the service if
        #it is checking for monitor locks.
        r1 = RobotRaconteurNode.s.ConnectService(url)
        r2 = RobotRaconteurNode.s.ConnectService(url)
        r1_o = r1.get_o1()
        r1_o_o2 = r1_o.get_o2_1()
        r2_o = r2.get_o1()
        r2_o_o2 = r2_o.get_o2_1()
        #Make sure everything works
        r1.func3(2.2, 3.3)
        r1_o.d1 = [1.0]
        r1_o_o2.data = "Hello world"
        r2.func3(2.2, 3.3)
        r2_o.d1 = [1.0]
        r2_o_o2.data = "Hello world"
        #Make sure that locks work as expected
        t1 = False
        t2 = False
        e1 = threading.Event()
        #AutoResetEvent e2 = new AutoResetEvent(false);
        threaderr = False
        def f1():
            try:
                r2.func3=(2.2,3.3)
                r2_o_o2.data="Hello world"

                e1.set()
                RobotRaconteurNode.s.MonitorEnter(r2_o)
                if (t1): raise Exception()
                t2=True

                r2_o.d1=[0.0]
                RobotRaconteurNode.s.MonitorExit(r2_o)
            except:
                import traceback
                traceback.print_exc()
                threaderr=True



        #ShouldBeErr<ObjectLockedException>(delegate() { r2_o.d1 = new double[] { 0.0 }; });
        with RobotRaconteurNode.ScopedMonitorLock(r1_o):
            RobotRaconteurNode.s.PostToThreadPool(f1)
            t1 = True

            time.sleep(0.01)
            r1.func3(2.2, 3.3)
            r1_o.d1 = [0.0]
            if t2:
                raise Exception()
            t1 = False

        time.sleep(0.5)
        if threaderr:
            raise Exception()

    def TestAsync(self, url):
        async_wait=threading.Event()
        async_err=[None]

        def TestAsync_err(err):
            async_err[0]=err
            async_wait.set()
            print (err)
            traceback.print_stack()

        def TestAsync1(r, err):

            if (err is not None):
                TestAsync_err(err)
                return
            try:
                r.async_get_d2(functools.partial(TestAsync2,r))
            except Exception as e:
                TestAsync_err(e)

        def TestAsync2(r,value,err):

            if (err is not None):
                TestAsync_err(err)
                return
            try:
                ca(value,[1.374233e+19, 2.424327e-04, -1.615609e-02, 3.342963e-21, -4.308134e+14, -1.783430e-07, 2.214302e+18, -1.091018e+17, 3.279396e-20, 2.454183e-01, 1.459922e+07, -3.494941e+16, -7.949200e-21, 1.720101e+17, -1.041015e+16, 1.453541e+05, 1.125846e+06, 1.894394e+07, 1.153038e-17, -3.283589e+06, 2.253268e-10, -3.897051e+06, 1.362011e+05, 5.501697e-19, -4.854610e+01, -1.582705e-05, 7.622313e+04, 2.104642e+08, -1.294512e-06, -1.426230e-19, -4.319619e-15, 9.837716e+03, -4.949316e-01, -2.173576e+02, 2.730509e-19, -2.123803e+05, 1.652596e-17, -2.066863e-09, 3.856560e-08, 1.379652e+18, -2.119906e+16, 4.860679e-05, -1.681801e-10, -1.569650e-15, 3.984306e-21, 3.283336e+08, -9.222510e-16, -3.579521e-02, 1.279363e-05, 3.920153e-12, 4.737275e-15, -4.427587e+06, -3.826670e-14, 2.492484e-04, 4.996082e+09, 4.643228e-11, 2.809952e-17, -2.224883e-13, -4.442602e+18, 4.422736e+11, 4.969282e-18, 4.937908e-15, 6.973867e-22, 1.908796e-19, 4.812115e-08, 1.753516e-02, -3.684764e+02, 1.557482e-17, -1.176997e-11, 1.772798e-05, 4.877622e-16, 1.107926e+11, 4.097985e-14, 2.714049e-18, 3.198732e+15, -1.052497e-01, -5.003982e+07, -1.538353e-04, 3.045308e+17, 1.176208e-18, 1.268710e-10, -1.269719e-05, -2.989599e+00, -3.721343e-11, -1.444196e-10, -2.030635e+04, 2.070258e+16, -3.001278e-14, 1.116018e+14, 4.999239e+15, 4.286177e-21, -2.972550e+10, 3.549075e-20, -2.874186e-06, 2.994430e+09, 2.978356e+10, -2.364977e+07, 2.807278e-01, -3.279567e-10, 4.567428e+05, 1.612242e+07, 4.102315e+05, -1.069501e-20, 2.887812e+10, 4.384194e-09, -2.936771e-11, -4.164448e+07, 3.391389e+04, -3.923673e+17, -2.735518e-22, -2.019257e-01, 3.014806e+15, -3.885050e-15, -2.806241e-20, 3.077066e+18, -1.574438e+14, -3.131588e+19, 4.812541e+03, 4.435881e+16, -3.843380e+02, -7.522165e+03, -3.668055e-21, 2.603478e-08, 2.928775e+08, 2.892123e+00, -1.594119e+04, -4.817379e-01, -2.121948e+03, -8.872132e-09, -3.909318e-06, -3.849648e-14, -4.554589e+18, 4.410297e-15, -2.976295e-04, -2.298802e+10, 4.981337e-07, 5.364781e-12, 1.536953e+07, -4.082889e-07, 1.670759e-21, 4.009147e-13, -4.691543e-18, -2.597887e-13, 2.368696e+18, -2.585884e-07, -5.209726e-03, -2.568300e+06, 2.184692e-20, -1.799204e+16, 1.397292e+04, 4.277966e+13, -4.072388e+09, -2.324749e+16, -4.717399e+10, -2.853124e-05, -3.664750e+11, -3.864796e-08, 3.265198e+07, -3.309827e+19, 3.222296e+03, 2.366113e-19, -3.425143e+14, 1.627821e-08, 4.987622e+00, -1.402489e-17, -1.303904e+15, -2.042850e+17, -1.399340e+09, -3.560871e+05, -4.251240e-21, -7.806581e-10, 1.723498e+00, -2.030115e+08, 4.595621e-19, 1.174387e-10, 3.474174e+14, -4.159866e+03, -1.833464e-19, -3.650925e+05, 3.757361e-03, -1.854280e-10, -1.856982e-13, 1.685338e+08, 4.051670e-11, 4.095232e+03, -2.956025e-16, 4.986423e-05, 4.941458e+10, 4.145946e+11, 3.402975e+14, -1.954363e+11, -2.274907e+10, -3.162121e-17, -5.027950e-07, 4.135173e-02, -3.777913e-04, -4.898637e+15, 2.354747e-02, -6.884549e+13, -1.896920e-05, -1.914414e+15, -1.196744e-19, -4.692974e-01, 8.586675e-10, -2.204766e-17, -3.586447e-14, 1.751276e+17, -2.546189e-05, -2.248796e+03, -9.445830e+02, 1.150138e+03, 4.586691e+11, -2.582686e-15, -2.795788e+12, -3.409768e+07, -2.172186e-03, -1.457882e+06, -4.153022e+13, -4.255977e-08, 3.216237e-07, 4.935803e+02, -4.248965e-16, 1.740357e+07, 4.635370e+19, -4.099930e-14, 2.758885e-16, -4.714106e-05, -4.556226e-20, -4.290894e-19, 1.174284e-09, -1.443257e+16, -2.279471e-08, -3.030819e-16, 1.535128e+18, -3.248271e-07, 3.079855e-21, -3.056403e-02, -1.368113e-12, 4.004190e-10, 4.955150e+07, -2.494283e-16, 2.186037e+05, -1.232946e+03, 5.586112e-05, -2.288144e+17, 2.515602e-19, -4.064132e+08, -3.217400e-02, -2.620215e+07, 2.283421e-14, -1.130075e+08, 3.304955e-03, 1.352402e+01, 6.255755e-03, -3.913649e-08, 5.474984e+01, -4.712294e-08, 3.548418e-16, 1.276896e+12, 2.007320e-08, 3.025617e+04, -2.544836e+14, -2.087825e+17, -3.285556e-09, 2.605304e+07, -1.876210e+07, 3.734943e-10, -3.862726e-15, -4.227362e-05, 1.267773e+14, -1.706991e-05, 3.737441e+10, 2.641527e+01, 4.439891e+10, -1.444933e-05, -2.190034e-12, 8.059924e-18, -1.324313e+18, -1.420214e-10, 3.940158e-20, 3.943349e-02, -2.685925e+19, 4.334133e-05, 3.171371e-21, 2.094486e+12, 1.331741e+03, 1.205892e-02, 1.791416e+04, 3.899239e+10, 6.581991e+06, -3.860368e+11, -3.853916e-02, 1.314566e+09, 3.923126e+03, -3.509905e+13, -4.332430e+06, -1.713419e+01, -1.244104e-14, -5.529613e+01, 6.630349e+06, 1.053668e+10, 3.312332e-05, -1.252220e+08, 3.997107e-07, 1.847068e-13, -2.393157e-11, -2.083719e-10, -4.927155e+11, 2.666499e-15, 4.087292e-10, 4.082567e-10, -2.017655e+07, 9.108015e+15, -4.199693e-15, -4.969705e-17, 1.769881e-02, 1.745504e+00, 2.200377e-16, -4.404838e-06, -1.317122e-15, 7.210560e+08, 1.282439e-18, -3.204957e-06, -1.624277e+05, 4.570975e-22, 1.261776e+04, 4.416193e+12, -4.343457e-18, 4.095420e-14, 4.951026e-09, 2.261753e-15, 4.125062e+05, -4.448849e+11, -3.184924e+06, -2.050956e+05, -9.895539e+09, 4.541548e+11, -4.230580e+11, -4.268059e-15, -4.393836e+09, -2.514832e-08, 3.322394e-04, 2.597384e-18, 1.316619e-11, -2.250081e+16, 2.179579e-10, -1.838295e+04, -1.995626e-17, -4.656110e+17, 3.481814e-07, -2.859273e-11, -2.011768e-06, -1.809342e-17, -3.242126e+10, -1.873723e+08, -2.833009e-12, -3.758282e+12, 2.970198e+15, -2.667738e-01, -3.689173e+11, 1.008362e-10, -1.526867e-20, -1.439753e+06, -6.154602e+16, 4.165816e+00, -1.597823e-09, -1.862803e+14, -2.222766e+15, -2.892587e+17, -4.230426e-14, 2.999121e-21, 1.642245e+00, 1.590694e-14, -4.469755e-06, 2.700655e+12, -1.822443e-02, -4.889338e-16, -3.174990e-11, 4.146024e-03, 1.313280e+01, 3.235142e+15, 3.500547e+00, -4.413708e+03, 1.485548e+16, -1.660821e-11, -4.334510e-22, -1.209739e+04, 1.149570e+12, -4.537849e+00, -3.628402e-16, 2.748853e-12, -4.818907e-21])
                r.async_set_d2([8.805544e-12, 3.735066e+12, 3.491919e+17, 4.979833e+12, -4.042302e+00, 2.927731e-12, 5.945355e+11, -3.965351e+06, 4.866934e-14, 1.314597e+04, -2.059923e-11, -5.447989e-20, 1.267732e-21, -2.603983e+10, 2.417961e+03, 3.515469e-16, 1.731329e-01, -2.854408e-04, 2.908090e-06, 3.354746e+08, 9.405914e+05, -3.665276e-01, -2.036897e+02, 3.489765e-01, -3.207702e+11, -2.105708e+18, -1.485891e+13, -7.059704e+04, 3.528381e+11, 4.586056e+02, -8.107050e-16, -1.007106e+09, 2.964453e+05, -3.628810e+05, -2.816870e-14, 5.665387e+09, 8.518736e+11, -1.179981e+12, -1.506569e-21, 1.113076e-06, -4.782847e+06, 8.906463e+17, 2.729604e+03, -3.430604e+16, 2.626956e-07, 1.543395e+15, 3.407777e-21, 1.231519e+06, -4.808410e+16, 2.649811e+10, 2.546524e+01, -3.533472e-13, -3.732759e+04, 1.951505e-20, 9.338953e-21, -1.627672e-04, 1.807084e-19, -4.489206e-17, -2.654284e+08, -2.136947e+16, -3.690031e+09, 3.372245e-14, 4.946361e-11, -1.330965e-01, 2.479789e-17, 2.750331e-18, -4.301452e-03, 3.895091e+19, 2.515863e+13, 6.879298e+12, -2.925884e-15, -2.826248e+00, -4.864526e-06, 2.614765e+00, 4.488816e-19, 2.231337e+15, -7.004595e+07, 2.506835e-08, -2.187450e-02, -2.220025e-07, 1.688346e+02, 8.125250e-07, -4.819391e+10, -1.643306e-14, -4.768222e-18, -4.472162e-16, 2.487563e-01, -3.924904e-15, -1.186331e+06, 2.397369e+01, -3.137448e-02, 1.016507e+06, 2.584749e-16, 8.212180e-08, 1.631561e-12, -4.927066e-08, 1.448920e-14, -4.371505e+03, 2.050871e-21, 2.523287e+01, 7.778552e-05, -4.437786e+18, -1.118552e-07, -3.543717e-09, -5.327587e-07, -1.083197e-17, 2.578295e-10, -4.952430e-12, -3.008597e-13, 3.010829e+01, -6.109332e+09, -2.428341e-03, 9.399191e-01, -4.827230e-06, 1.013860e+10, -2.870341e-20, 4.281756e+11, 1.043519e-09, 2.378027e+06, 2.605309e+09, -4.939600e-04, -2.193966e+08, 4.022755e-03, 2.668705e-09, -1.087393e-18, 1.927676e-12, -1.694835e+10, 3.554035e-03, -1.299796e+01, -1.692862e+07, 2.818156e+07, -2.606821e-13, 1.629588e-15, -7.069991e-16, 1.205863e-19, 2.491209e-17, -3.757951e+04, 3.110266e-04, -4.339472e+11, -3.172428e+02, 1.579905e+09, 2.859499e-01, 4.241852e-06, 2.043341e-09, 2.922865e-16, -2.580974e+01, -3.147566e-02, 1.160590e+03, -2.238096e+01, -1.984601e-13, 2.636096e-03, 8.422872e-04, 2.026040e-16, -3.822500e+01, -2.190513e-18, 3.229839e-11, -2.958164e+06, -8.354021e+11, 3.625367e+08, -4.558085e-01, 1.274325e+04, -2.492750e+05, 3.739269e+18, -3.985407e-03, 3.575816e-13, 1.376847e+06, -6.682659e-20, -9.200014e+08, -2.278973e+10, -3.555184e-04, 3.821512e-10, 5.944167e+07, -2.576511e-15, 1.232459e+02, -3.187831e+02, -4.882568e+12, -1.670486e+05, -2.339878e-20, -4.985496e-16, -2.937093e+17, 8.981723e-06, -5.460686e-04, 1.090528e-11, -4.321598e+17, -3.577227e-08, 2.880194e+01, -4.277921e+00, -4.145678e-02, 4.930810e+08, -4.525745e-21, 4.648764e+07, -2.564920e+16, 1.075546e+01, 3.777591e-18, 1.419816e-08, 1.419490e+10, 1.479453e-19, -4.933130e+13, 4.580471e+15, -3.160785e+02, -2.885209e+06, 2.384424e-03, 1.030777e-12, 2.652784e+04, 4.435144e+10, 3.102484e+17, 4.725294e+11, -3.817788e-04, 4.074841e-01, -7.248042e-13, -4.502531e-08, 2.203521e+01, -4.457124e+01, -2.961745e+06, -3.237080e+14, -3.482497e-19, 1.534088e+05, 4.759060e-14, 2.333791e+04, -4.002051e-03, 3.278553e-06, -2.307217e+13, -2.999411e+19, -9.804484e+02, -1.793367e+01, 3.111735e+07, -4.457329e+10, -2.067659e-13, -5.927573e+03, 6.979879e+10, 3.556110e-06, -3.513094e-13, 1.128057e+19, 4.199038e+13, 7.553080e-20, 4.380028e-11, -2.502103e-19, 5.943049e+15, -1.266134e-10, 4.825578e-09, -2.778134e-16, 1.881866e-10, -3.677556e+08, -2.166345e-10, 3.919158e+05, 2.778912e-07, 1.822489e-05, 1.513496e-01, 9.327925e+05, -4.050132e-14, 3.311913e+01, 9.290544e+15, 1.302267e+03, -1.252080e+17, -4.208811e-04, -3.225464e+16, 2.093787e+16, -3.352116e+07, 4.797665e+15, -1.539672e-17, 4.835159e+04, 2.446236e-07, 2.355328e-17, 2.044244e-12, 3.210415e-11, -1.322741e+16, 5.538184e-14, -4.612046e-05, 4.758939e+15, -2.038208e-10, -2.451148e+18, -2.699711e-19, -2.019804e-09, 5.631634e-13, -2.288031e+05, -3.211488e+12, 7.511869e+13, -3.209453e-09, 3.806128e-18, 4.025006e-14, -1.700945e-10, 4.136280e-13, 4.517870e-04, 2.739233e+11, -3.736057e-03, 2.255379e-20, 3.122584e-16, 3.192660e-18, 4.765755e-09, 2.396494e-13, 1.625326e+02, -3.413821e-18, 3.627586e+10, 8.708108e+07, 2.244241e-09, 3.718827e-02, 1.803394e-18, 4.377806e-04, 1.593155e-04, -2.886859e+19, 2.446955e-06, 4.714172e-07, -1.444181e+14, 5.921228e-22, -3.968436e+05, 2.081487e+08, 4.200042e+18, -1.334353e-20, 1.637913e+12, -7.203262e+03, 3.510359e+09, 5.945107e-08, 2.798793e-07, 1.819020e+17, -1.331690e+02, -2.714485e+18, -2.344350e-18, -1.313232e-20, -6.739364e-22, 1.025007e-02, 1.186976e+07, -1.412268e+09, -6.194861e-18, -4.523625e-03, -4.504270e-06, 2.158726e-21, -8.330465e-17, 4.566938e+11, 6.677905e-05, -2.312717e-13, 5.325983e+16, -1.075392e-04, 1.140532e-13, 2.606136e-11, -2.815243e+16, -3.550714e-16, -1.033372e+05, -1.183041e+03, -7.872171e-21, -4.362058e-07, -3.181126e-07, -2.676671e+18, -2.674920e-15, -3.991169e-16, -4.401799e+07, -2.826847e-10, -2.033266e-20, -5.669789e-11, 3.711339e+05, -1.194584e-17, -3.310173e+10, -1.743331e-15, -2.288755e+15, 8.610375e+06, 4.796813e+07, -1.465344e+07, -4.074823e-12, 2.089962e-21, -4.171761e-18, -4.682371e+18, 4.030447e+08, 4.679856e-07, -2.662732e+15, 2.551805e-21, 2.482089e+05, -2.310281e-10, 3.533837e-08, 1.829437e-07, 3.074466e-06, -2.889997e-12, -4.203806e+01, 1.598374e-21, -1.300526e-05, 2.921093e+14, -8.847920e+14, 3.788583e-04, -4.538453e+19, -2.734893e+07, 1.351281e-04, 1.128593e-01, 3.868545e+13, -1.200438e+18, -2.641822e+10, -4.493835e-16, -6.291094e-13, 2.534337e-08, -4.063653e-03, 3.200675e-02, 2.243642e+08, 5.170843e-08, 8.984841e-14, 2.228243e-01, -6.770559e-09, 3.513375e-16, -2.512038e-14, 3.421696e+04, -4.514522e+01, -1.062799e-20, 2.853168e-19, 8.503515e-21, -1.664790e-03, -2.515606e-18, 1.237958e-21, -8.059224e-20, 4.386086e+00, 5.301466e+17, 4.388106e-12, -3.432129e+00, 2.189230e+18, -1.806446e-02, 3.266789e-18, 3.355664e-13, -1.206966e-21, -4.813560e-02, -1.352049e+18, 1.257234e-07, 2.511470e-09, -2.512775e-01, 3.613773e-10, -9.065202e+16, -1.777852e+18, 1.444606e-01, -2.857379e+00, -1.912993e+00, 3.436817e-09, -1.749039e+14, 2.215154e-18, 3.384923e+18, -4.513038e-09, 4.814904e+05, 3.730911e+15, 1.861706e+12, 3.378290e-03, 2.851468e-06, -1.577518e-04, -4.122504e-12, -2.743002e+03, 8.512568e-02, -1.333039e-09, -4.899609e-17, -1.782085e-11, 2.552482e-02, 4.200193e+10, -4.298147e+03, -1.923210e-10, -1.208889e+01, 4.606772e-21, -3.331241e+10, -3.704566e-16, -3.733178e-20, -4.950049e+16, 3.184384e+15, -4.107375e-06, 1.801875e+09, 9.632951e-16, 7.172728e-10, 2.324621e+07, 2.892586e+15, -1.582511e-17, -4.119044e-13, -1.248361e+09, 1.531907e+08, -1.795628e-19, -1.735919e-17, -4.646689e-07, -2.779304e-11, 8.048984e-10, 3.536087e-02, -6.494880e+18, 2.714073e+06, 3.374557e+18, 3.621468e-06, 2.742652e-07, 2.551176e+03, -4.420578e+18, -4.370624e-08, -4.507765e-11, 4.193746e-20, 1.206645e+13, -3.750231e+03, 4.390893e+08, -9.756466e+11, 3.392778e-06, -3.453465e+01, -1.406102e+11, -3.673526e-15, 1.417082e-03, 1.499926e+16, -4.471032e-17, -2.657920e+16, 4.792261e+09, -3.212735e+17, -3.372737e-05, -4.730048e+01, 3.365478e+07, 2.835695e+13, -3.242022e-07, 3.640288e+11, 1.862055e-08, -4.121250e-19, -3.891100e-02, -4.367058e-15, 1.364067e-17, -4.575429e-12, 3.621347e-07, 1.506864e+11, 3.715065e+18, -1.773352e+08, -3.502359e+07, -2.326890e-04, 2.948814e-17, -2.438988e+14, -2.994787e+04, -3.755515e+12, 2.708013e-13, 3.281046e-01, -3.710727e+12, -8.380304e+14, 1.062737e-05, 2.385939e+16, -4.383210e-20, -3.779417e+03, 3.080324e-03, 3.810188e+16, 3.058415e+00, -2.484879e-21, -1.951684e+01, 6.979033e-10, -3.866994e+06, 4.278936e-19, 9.365131e+10, -3.685205e+01, -2.678752e-16, 2.011434e-19, 1.884072e+08, -1.300910e+04, 2.414058e-09, -4.675979e+11, 3.583361e-19, -4.499438e+18, 1.641999e-21, -2.686795e-10, 6.136688e-20, -3.793690e+16, 4.944562e-20, -3.490443e-03, 3.080547e+02, 2.041413e-06, 2.021979e+03, 2.314233e-06, 1.564131e-01, -8.712542e+17, 7.569081e+16, -1.056907e+17, 2.095024e-14, -2.487621e+17, -3.490381e+19, -6.944641e-01, -2.892354e-08, -3.597351e+12, -1.985424e+06, -2.348859e+09, -1.657051e+01, -3.358823e+14, 3.219974e-16, -4.819092e-13, -2.905178e-11, 8.257664e+04, -4.092466e-15, -3.464711e-13, -3.956400e-14, -2.548275e-08, -8.917872e-21, 7.387291e+13, 2.300996e+16, -4.870764e+18, -9.909380e-03, 1.260429e-08, -3.409396e-12, 1.003848e+02, -4.883178e-02, -3.125474e-14, 1.005294e+11, -4.736012e+09, -1.647544e-09, -3.491431e-03, 4.619061e+07, -4.547601e-09, -3.788900e-02, -2.648380e-17, 4.601877e-16, 1.754357e+13, 4.325616e+12, 1.860822e+03, 4.080727e+15, -4.573470e-14, -1.293538e+16, 2.811449e+05, 4.032351e+06, 4.274005e+04, 3.454035e-21, 4.933014e+09, -3.712562e+08, 3.158678e+06, -1.636782e+11, -2.884298e-18, -3.685740e-17, 1.027472e-07, -3.765173e-12, 2.740894e-17, 2.634880e+02, -4.334010e+00, -3.708285e-14, -3.858731e+16, -3.956687e+13, -4.064064e-12, 2.558646e-05, 4.459143e+03, -9.661948e+03, -1.994335e+16, 1.202714e-17, -3.782707e-17, 9.099692e-04, -1.864561e+09, 3.493877e-08, 4.288188e-01, 1.767126e-14, -6.779451e-22, -1.977471e-09, -3.536454e+06, -7.319495e-04, 2.004028e-16, -3.181521e-17, 3.336202e+14, -2.752423e+07, 3.390953e+01, 4.199625e-15, 2.883232e-12, 3.122912e-06, 7.324619e-19, 3.092709e-02, -2.758364e-15, -2.489492e+12, -1.622009e-08, 2.371204e+06, -1.582081e+08, -6.382371e-17],functools.partial(TestAsync3,r))
            except Exception as e:
                TestAsync_err(e)
        def TestAsync3(r,err):
            if (err is not None):
                TestAsync_err(err)
                return
            try:
                r.async_func1(functools.partial(TestAsync4,r))
            except Exception as e:
                TestAsync_err(e)

        def TestAsync4(r,err):
            if (err is not None):
                TestAsync_err(err)
                return
            try:
                r.async_func3(2,3.45,functools.partial(TestAsync5,r))
            except Exception as e:
                TestAsync_err(e)

        def TestAsync5(r,ret,err):
            if(err is not None):
                TestAsync_err(err)
                return
            try:
                if (ret!=5.45): raise Exception("")
                r.async_func_errtest(functools.partial(TestAsync6,r))
            except Exception as e:
                TestAsync_err(e)

        def TestAsync6(r, err):
            try:
                if (err is None): raise Exception("")
                r.async_get_o1(functools.partial(TestAsync7,r))
            except Exception as e:
                TestAsync_err(e)

        def TestAsync7(r,o1,err):
            if (err is not None):
                TestAsync_err(err)
                return
            try:
                if (o1 is None): raise Exception("")
                dd=o1.d1

                r.p1.AsyncConnect(-1,functools.partial(TestAsync8,r))
            except Exception as e:
                TestAsync_err(e)

        def TestAsync8(r, e1, err):
            if (err is not None):
                TestAsync_err(err)
                return
            try:
                e1.AsyncSendPacket([1,2,3,4],functools.partial(TestAsync9,r,e1))
            except Exception as e:
                TestAsync_err(e)

        def TestAsync9(r,e1,pnum,err):
            if (err is not None):
                TestAsync_err(err)
                return
            try:
                e1.AsyncClose(functools.partial(TestAsync10,r,e1))
            except Exception as e:
                TestAsync_err(e)
                return

        def TestAsync10(r,e1,err):
            if (err is not None):
                TestAsync_err(err)
                return
            try:
                r.w1.AsyncConnect(functools.partial(TestAsync11,r))
            except Exception as e:
                TestAsync_err(e)
                return

        def TestAsync11(r,w1,err):
            if(err is not None):
                TestAsync_err(err)
                return
            try:
                w1.OutValue=0.0
                w1.AsyncClose(functools.partial(TestAsync12,r,w1))
            except Exception as e:
                TestAsync_err(e)

        def TestAsync12(r,w1,err):
            if (err is not None):
                TestAsync_err(err)
                return
            try:
                RobotRaconteurNode.s.AsyncRequestObjectLock(r,RobotRaconteurObjectLockFlags_CLIENT_LOCK,functools.partial(TestAsync13,r))
            except Exception as e:
                TestAsync_err(e)

        def TestAsync13(r,res,err):
            if (err is not None):
                TestAsync_err(err)
                return
            if (res!="OK"):
                TestAsync_err(Exception(""))
                return
            try:
                RobotRaconteurNode.s.AsyncReleaseObjectLock(r,functools.partial(TestAsync14,r))
            except Exception as e:
                TestAsync_err(e)

        def TestAsync14(r,res,err):
            if (err is not None):
                TestAsync_err(err)
                return
            if (res!="OK"):
                TestAsync_err(Exception(""))
                return
            try:
                RobotRaconteurNode.s.AsyncDisconnectService(r,TestAsync15)
            except Exception as e:
                TestAsync_err(e)

        def TestAsync15():

            async_wait.set()

        cred1={"password": RobotRaconteurVarValue("testpass1","string")}
        RobotRaconteurNode.s.AsyncConnectService(url, "testuser1", cred1,None,TestAsync1)


        async_wait.wait()

        if (async_err[0]):
            raise async_err[0]


class testroot_impl(object):

    def __init__(self, tcptransport):
        self._o1=sub1_impl()
        self._o2={}
        self._o2_lock=threading.RLock()
        self._o3={}
        self._o3_lock=threading.RLock()
        self._o4={}
        self._o4_lock=threading.RLock()
        self._o5=sub1_impl()
        self._o6=sub1_impl()

        self._packet_sent=False
        self._p1_lock=threading.RLock()
        self._ack_recv=False
        self._p1=None

        self._p2=None
        self._p2_lock=threading.RLock()

        self.ev1=EventHook()
        self.ev2=EventHook()
        self.ev3=EventHook()

        mdat1=[-2.675014e-13, 6.884672e-07, 4.855899e-02, 1.634267e-08, -5.346105e+06, 9.245749e+09, 2.174639e+16, -3.574166e+04, 3.063678e+16, 4.748279e-16, -1.478723e-16, 1.507042e-05, -2.046271e+13, 4.014775e+06, 4.140740e+10, 1.318907e+16, -2.312403e+17, 4.463696e-13, 9.173421e-04, 6.169183e-21, 3.643045e+09, -3.784476e+13, -1.878617e-21, -4.122785e+01, -2.477761e+15, -5.220540e-11, -3.930894e-19, 3.980082e-12, -3.681569e-20, 4.675366e+19, -7.454667e-06, -1.529932e+17, -3.707663e-04, -3.356188e-20, -2.393304e-07, 1.339372e-18, -3.735916e-15, 1.715447e+01, 1.316085e+02, 9.603036e-05, 1.458992e+16, 9.228113e+11, 1.099841e-12, -2.484793e-09, 4.826956e-19, -3.662630e-11, -3.274562e+10, 1.866042e-12, 4.061219e-13, 1.307997e-18, -1.210979e+08, 4.036328e+02, -2.713849e-11, -3.673995e-01, -4.576021e+03, 1.519751e+03, 1.792427e-16, -2.033399e+18, 4.341947e+08, -1.699292e-09, -1.007978e-21, 3.200139e-15, -3.157557e+03, -3.717883e-15, 4.337614e+02, -3.666534e-12, -1.821013e-14, -2.260577e-20, 1.722045e-06, 1.886614e+00, -1.278609e+15, 2.923499e-03, 4.969081e+02, 4.438380e-06, -3.890489e-11, -3.261564e-17, 6.172945e-10, 4.951740e+19, 3.460327e+11, -3.600349e-16, 2.419445e+11, -9.124824e+10, 4.127522e+04, 1.443468e+00, -3.968841e-21, -2.507203e+05, 2.214239e+13, -3.327687e+07, 1.167160e+09, -4.361249e-11, -4.609514e+14, -2.461408e+13, 5.584758e+06, 3.989706e-07, 2.597151e-12, -2.961640e+08, -2.173964e-02, -1.866864e-11, 4.832786e-08, 2.713705e-07 ]
        self.m1=ArrayMemory(mdat1)
        self.m2=MultiDimArrayMemory(numpy.zeros([10, 10, 10, 10, 10]))
        self.m3=MultiDimArrayMemory(numpy.zeros([1024,1024],dtype=numpy.uint8))

        self._broadcastpipe=None
        self._broadcastwire=None
        self.tcptransport=tcptransport


    @property
    def d1(self):
        return 12.345

    @d1.setter
    def d1(self,value):
        if (value!=3.456):
            raise Exception()

    @property
    def d2(self):
        return [1.374233e+19, 2.424327e-04, -1.615609e-02, 3.342963e-21, -4.308134e+14, -1.783430e-07, 2.214302e+18, -1.091018e+17, 3.279396e-20, 2.454183e-01, 1.459922e+07, -3.494941e+16, -7.949200e-21, 1.720101e+17, -1.041015e+16, 1.453541e+05, 1.125846e+06, 1.894394e+07, 1.153038e-17, -3.283589e+06, 2.253268e-10, -3.897051e+06, 1.362011e+05, 5.501697e-19, -4.854610e+01, -1.582705e-05, 7.622313e+04, 2.104642e+08, -1.294512e-06, -1.426230e-19, -4.319619e-15, 9.837716e+03, -4.949316e-01, -2.173576e+02, 2.730509e-19, -2.123803e+05, 1.652596e-17, -2.066863e-09, 3.856560e-08, 1.379652e+18, -2.119906e+16, 4.860679e-05, -1.681801e-10, -1.569650e-15, 3.984306e-21, 3.283336e+08, -9.222510e-16, -3.579521e-02, 1.279363e-05, 3.920153e-12, 4.737275e-15, -4.427587e+06, -3.826670e-14, 2.492484e-04, 4.996082e+09, 4.643228e-11, 2.809952e-17, -2.224883e-13, -4.442602e+18, 4.422736e+11, 4.969282e-18, 4.937908e-15, 6.973867e-22, 1.908796e-19, 4.812115e-08, 1.753516e-02, -3.684764e+02, 1.557482e-17, -1.176997e-11, 1.772798e-05, 4.877622e-16, 1.107926e+11, 4.097985e-14, 2.714049e-18, 3.198732e+15, -1.052497e-01, -5.003982e+07, -1.538353e-04, 3.045308e+17, 1.176208e-18, 1.268710e-10, -1.269719e-05, -2.989599e+00, -3.721343e-11, -1.444196e-10, -2.030635e+04, 2.070258e+16, -3.001278e-14, 1.116018e+14, 4.999239e+15, 4.286177e-21, -2.972550e+10, 3.549075e-20, -2.874186e-06, 2.994430e+09, 2.978356e+10, -2.364977e+07, 2.807278e-01, -3.279567e-10, 4.567428e+05, 1.612242e+07, 4.102315e+05, -1.069501e-20, 2.887812e+10, 4.384194e-09, -2.936771e-11, -4.164448e+07, 3.391389e+04, -3.923673e+17, -2.735518e-22, -2.019257e-01, 3.014806e+15, -3.885050e-15, -2.806241e-20, 3.077066e+18, -1.574438e+14, -3.131588e+19, 4.812541e+03, 4.435881e+16, -3.843380e+02, -7.522165e+03, -3.668055e-21, 2.603478e-08, 2.928775e+08, 2.892123e+00, -1.594119e+04, -4.817379e-01, -2.121948e+03, -8.872132e-09, -3.909318e-06, -3.849648e-14, -4.554589e+18, 4.410297e-15, -2.976295e-04, -2.298802e+10, 4.981337e-07, 5.364781e-12, 1.536953e+07, -4.082889e-07, 1.670759e-21, 4.009147e-13, -4.691543e-18, -2.597887e-13, 2.368696e+18, -2.585884e-07, -5.209726e-03, -2.568300e+06, 2.184692e-20, -1.799204e+16, 1.397292e+04, 4.277966e+13, -4.072388e+09, -2.324749e+16, -4.717399e+10, -2.853124e-05, -3.664750e+11, -3.864796e-08, 3.265198e+07, -3.309827e+19, 3.222296e+03, 2.366113e-19, -3.425143e+14, 1.627821e-08, 4.987622e+00, -1.402489e-17, -1.303904e+15, -2.042850e+17, -1.399340e+09, -3.560871e+05, -4.251240e-21, -7.806581e-10, 1.723498e+00, -2.030115e+08, 4.595621e-19, 1.174387e-10, 3.474174e+14, -4.159866e+03, -1.833464e-19, -3.650925e+05, 3.757361e-03, -1.854280e-10, -1.856982e-13, 1.685338e+08, 4.051670e-11, 4.095232e+03, -2.956025e-16, 4.986423e-05, 4.941458e+10, 4.145946e+11, 3.402975e+14, -1.954363e+11, -2.274907e+10, -3.162121e-17, -5.027950e-07, 4.135173e-02, -3.777913e-04, -4.898637e+15, 2.354747e-02, -6.884549e+13, -1.896920e-05, -1.914414e+15, -1.196744e-19, -4.692974e-01, 8.586675e-10, -2.204766e-17, -3.586447e-14, 1.751276e+17, -2.546189e-05, -2.248796e+03, -9.445830e+02, 1.150138e+03, 4.586691e+11, -2.582686e-15, -2.795788e+12, -3.409768e+07, -2.172186e-03, -1.457882e+06, -4.153022e+13, -4.255977e-08, 3.216237e-07, 4.935803e+02, -4.248965e-16, 1.740357e+07, 4.635370e+19, -4.099930e-14, 2.758885e-16, -4.714106e-05, -4.556226e-20, -4.290894e-19, 1.174284e-09, -1.443257e+16, -2.279471e-08, -3.030819e-16, 1.535128e+18, -3.248271e-07, 3.079855e-21, -3.056403e-02, -1.368113e-12, 4.004190e-10, 4.955150e+07, -2.494283e-16, 2.186037e+05, -1.232946e+03, 5.586112e-05, -2.288144e+17, 2.515602e-19, -4.064132e+08, -3.217400e-02, -2.620215e+07, 2.283421e-14, -1.130075e+08, 3.304955e-03, 1.352402e+01, 6.255755e-03, -3.913649e-08, 5.474984e+01, -4.712294e-08, 3.548418e-16, 1.276896e+12, 2.007320e-08, 3.025617e+04, -2.544836e+14, -2.087825e+17, -3.285556e-09, 2.605304e+07, -1.876210e+07, 3.734943e-10, -3.862726e-15, -4.227362e-05, 1.267773e+14, -1.706991e-05, 3.737441e+10, 2.641527e+01, 4.439891e+10, -1.444933e-05, -2.190034e-12, 8.059924e-18, -1.324313e+18, -1.420214e-10, 3.940158e-20, 3.943349e-02, -2.685925e+19, 4.334133e-05, 3.171371e-21, 2.094486e+12, 1.331741e+03, 1.205892e-02, 1.791416e+04, 3.899239e+10, 6.581991e+06, -3.860368e+11, -3.853916e-02, 1.314566e+09, 3.923126e+03, -3.509905e+13, -4.332430e+06, -1.713419e+01, -1.244104e-14, -5.529613e+01, 6.630349e+06, 1.053668e+10, 3.312332e-05, -1.252220e+08, 3.997107e-07, 1.847068e-13, -2.393157e-11, -2.083719e-10, -4.927155e+11, 2.666499e-15, 4.087292e-10, 4.082567e-10, -2.017655e+07, 9.108015e+15, -4.199693e-15, -4.969705e-17, 1.769881e-02, 1.745504e+00, 2.200377e-16, -4.404838e-06, -1.317122e-15, 7.210560e+08, 1.282439e-18, -3.204957e-06, -1.624277e+05, 4.570975e-22, 1.261776e+04, 4.416193e+12, -4.343457e-18, 4.095420e-14, 4.951026e-09, 2.261753e-15, 4.125062e+05, -4.448849e+11, -3.184924e+06, -2.050956e+05, -9.895539e+09, 4.541548e+11, -4.230580e+11, -4.268059e-15, -4.393836e+09, -2.514832e-08, 3.322394e-04, 2.597384e-18, 1.316619e-11, -2.250081e+16, 2.179579e-10, -1.838295e+04, -1.995626e-17, -4.656110e+17, 3.481814e-07, -2.859273e-11, -2.011768e-06, -1.809342e-17, -3.242126e+10, -1.873723e+08, -2.833009e-12, -3.758282e+12, 2.970198e+15, -2.667738e-01, -3.689173e+11, 1.008362e-10, -1.526867e-20, -1.439753e+06, -6.154602e+16, 4.165816e+00, -1.597823e-09, -1.862803e+14, -2.222766e+15, -2.892587e+17, -4.230426e-14, 2.999121e-21, 1.642245e+00, 1.590694e-14, -4.469755e-06, 2.700655e+12, -1.822443e-02, -4.889338e-16, -3.174990e-11, 4.146024e-03, 1.313280e+01, 3.235142e+15, 3.500547e+00, -4.413708e+03, 1.485548e+16, -1.660821e-11, -4.334510e-22, -1.209739e+04, 1.149570e+12, -4.537849e+00, -3.628402e-16, 2.748853e-12, -4.818907e-21]
    @d2.setter
    def d2(self,value):
        ca(value,[8.805544e-12, 3.735066e+12, 3.491919e+17, 4.979833e+12, -4.042302e+00, 2.927731e-12, 5.945355e+11, -3.965351e+06, 4.866934e-14, 1.314597e+04, -2.059923e-11, -5.447989e-20, 1.267732e-21, -2.603983e+10, 2.417961e+03, 3.515469e-16, 1.731329e-01, -2.854408e-04, 2.908090e-06, 3.354746e+08, 9.405914e+05, -3.665276e-01, -2.036897e+02, 3.489765e-01, -3.207702e+11, -2.105708e+18, -1.485891e+13, -7.059704e+04, 3.528381e+11, 4.586056e+02, -8.107050e-16, -1.007106e+09, 2.964453e+05, -3.628810e+05, -2.816870e-14, 5.665387e+09, 8.518736e+11, -1.179981e+12, -1.506569e-21, 1.113076e-06, -4.782847e+06, 8.906463e+17, 2.729604e+03, -3.430604e+16, 2.626956e-07, 1.543395e+15, 3.407777e-21, 1.231519e+06, -4.808410e+16, 2.649811e+10, 2.546524e+01, -3.533472e-13, -3.732759e+04, 1.951505e-20, 9.338953e-21, -1.627672e-04, 1.807084e-19, -4.489206e-17, -2.654284e+08, -2.136947e+16, -3.690031e+09, 3.372245e-14, 4.946361e-11, -1.330965e-01, 2.479789e-17, 2.750331e-18, -4.301452e-03, 3.895091e+19, 2.515863e+13, 6.879298e+12, -2.925884e-15, -2.826248e+00, -4.864526e-06, 2.614765e+00, 4.488816e-19, 2.231337e+15, -7.004595e+07, 2.506835e-08, -2.187450e-02, -2.220025e-07, 1.688346e+02, 8.125250e-07, -4.819391e+10, -1.643306e-14, -4.768222e-18, -4.472162e-16, 2.487563e-01, -3.924904e-15, -1.186331e+06, 2.397369e+01, -3.137448e-02, 1.016507e+06, 2.584749e-16, 8.212180e-08, 1.631561e-12, -4.927066e-08, 1.448920e-14, -4.371505e+03, 2.050871e-21, 2.523287e+01, 7.778552e-05, -4.437786e+18, -1.118552e-07, -3.543717e-09, -5.327587e-07, -1.083197e-17, 2.578295e-10, -4.952430e-12, -3.008597e-13, 3.010829e+01, -6.109332e+09, -2.428341e-03, 9.399191e-01, -4.827230e-06, 1.013860e+10, -2.870341e-20, 4.281756e+11, 1.043519e-09, 2.378027e+06, 2.605309e+09, -4.939600e-04, -2.193966e+08, 4.022755e-03, 2.668705e-09, -1.087393e-18, 1.927676e-12, -1.694835e+10, 3.554035e-03, -1.299796e+01, -1.692862e+07, 2.818156e+07, -2.606821e-13, 1.629588e-15, -7.069991e-16, 1.205863e-19, 2.491209e-17, -3.757951e+04, 3.110266e-04, -4.339472e+11, -3.172428e+02, 1.579905e+09, 2.859499e-01, 4.241852e-06, 2.043341e-09, 2.922865e-16, -2.580974e+01, -3.147566e-02, 1.160590e+03, -2.238096e+01, -1.984601e-13, 2.636096e-03, 8.422872e-04, 2.026040e-16, -3.822500e+01, -2.190513e-18, 3.229839e-11, -2.958164e+06, -8.354021e+11, 3.625367e+08, -4.558085e-01, 1.274325e+04, -2.492750e+05, 3.739269e+18, -3.985407e-03, 3.575816e-13, 1.376847e+06, -6.682659e-20, -9.200014e+08, -2.278973e+10, -3.555184e-04, 3.821512e-10, 5.944167e+07, -2.576511e-15, 1.232459e+02, -3.187831e+02, -4.882568e+12, -1.670486e+05, -2.339878e-20, -4.985496e-16, -2.937093e+17, 8.981723e-06, -5.460686e-04, 1.090528e-11, -4.321598e+17, -3.577227e-08, 2.880194e+01, -4.277921e+00, -4.145678e-02, 4.930810e+08, -4.525745e-21, 4.648764e+07, -2.564920e+16, 1.075546e+01, 3.777591e-18, 1.419816e-08, 1.419490e+10, 1.479453e-19, -4.933130e+13, 4.580471e+15, -3.160785e+02, -2.885209e+06, 2.384424e-03, 1.030777e-12, 2.652784e+04, 4.435144e+10, 3.102484e+17, 4.725294e+11, -3.817788e-04, 4.074841e-01, -7.248042e-13, -4.502531e-08, 2.203521e+01, -4.457124e+01, -2.961745e+06, -3.237080e+14, -3.482497e-19, 1.534088e+05, 4.759060e-14, 2.333791e+04, -4.002051e-03, 3.278553e-06, -2.307217e+13, -2.999411e+19, -9.804484e+02, -1.793367e+01, 3.111735e+07, -4.457329e+10, -2.067659e-13, -5.927573e+03, 6.979879e+10, 3.556110e-06, -3.513094e-13, 1.128057e+19, 4.199038e+13, 7.553080e-20, 4.380028e-11, -2.502103e-19, 5.943049e+15, -1.266134e-10, 4.825578e-09, -2.778134e-16, 1.881866e-10, -3.677556e+08, -2.166345e-10, 3.919158e+05, 2.778912e-07, 1.822489e-05, 1.513496e-01, 9.327925e+05, -4.050132e-14, 3.311913e+01, 9.290544e+15, 1.302267e+03, -1.252080e+17, -4.208811e-04, -3.225464e+16, 2.093787e+16, -3.352116e+07, 4.797665e+15, -1.539672e-17, 4.835159e+04, 2.446236e-07, 2.355328e-17, 2.044244e-12, 3.210415e-11, -1.322741e+16, 5.538184e-14, -4.612046e-05, 4.758939e+15, -2.038208e-10, -2.451148e+18, -2.699711e-19, -2.019804e-09, 5.631634e-13, -2.288031e+05, -3.211488e+12, 7.511869e+13, -3.209453e-09, 3.806128e-18, 4.025006e-14, -1.700945e-10, 4.136280e-13, 4.517870e-04, 2.739233e+11, -3.736057e-03, 2.255379e-20, 3.122584e-16, 3.192660e-18, 4.765755e-09, 2.396494e-13, 1.625326e+02, -3.413821e-18, 3.627586e+10, 8.708108e+07, 2.244241e-09, 3.718827e-02, 1.803394e-18, 4.377806e-04, 1.593155e-04, -2.886859e+19, 2.446955e-06, 4.714172e-07, -1.444181e+14, 5.921228e-22, -3.968436e+05, 2.081487e+08, 4.200042e+18, -1.334353e-20, 1.637913e+12, -7.203262e+03, 3.510359e+09, 5.945107e-08, 2.798793e-07, 1.819020e+17, -1.331690e+02, -2.714485e+18, -2.344350e-18, -1.313232e-20, -6.739364e-22, 1.025007e-02, 1.186976e+07, -1.412268e+09, -6.194861e-18, -4.523625e-03, -4.504270e-06, 2.158726e-21, -8.330465e-17, 4.566938e+11, 6.677905e-05, -2.312717e-13, 5.325983e+16, -1.075392e-04, 1.140532e-13, 2.606136e-11, -2.815243e+16, -3.550714e-16, -1.033372e+05, -1.183041e+03, -7.872171e-21, -4.362058e-07, -3.181126e-07, -2.676671e+18, -2.674920e-15, -3.991169e-16, -4.401799e+07, -2.826847e-10, -2.033266e-20, -5.669789e-11, 3.711339e+05, -1.194584e-17, -3.310173e+10, -1.743331e-15, -2.288755e+15, 8.610375e+06, 4.796813e+07, -1.465344e+07, -4.074823e-12, 2.089962e-21, -4.171761e-18, -4.682371e+18, 4.030447e+08, 4.679856e-07, -2.662732e+15, 2.551805e-21, 2.482089e+05, -2.310281e-10, 3.533837e-08, 1.829437e-07, 3.074466e-06, -2.889997e-12, -4.203806e+01, 1.598374e-21, -1.300526e-05, 2.921093e+14, -8.847920e+14, 3.788583e-04, -4.538453e+19, -2.734893e+07, 1.351281e-04, 1.128593e-01, 3.868545e+13, -1.200438e+18, -2.641822e+10, -4.493835e-16, -6.291094e-13, 2.534337e-08, -4.063653e-03, 3.200675e-02, 2.243642e+08, 5.170843e-08, 8.984841e-14, 2.228243e-01, -6.770559e-09, 3.513375e-16, -2.512038e-14, 3.421696e+04, -4.514522e+01, -1.062799e-20, 2.853168e-19, 8.503515e-21, -1.664790e-03, -2.515606e-18, 1.237958e-21, -8.059224e-20, 4.386086e+00, 5.301466e+17, 4.388106e-12, -3.432129e+00, 2.189230e+18, -1.806446e-02, 3.266789e-18, 3.355664e-13, -1.206966e-21, -4.813560e-02, -1.352049e+18, 1.257234e-07, 2.511470e-09, -2.512775e-01, 3.613773e-10, -9.065202e+16, -1.777852e+18, 1.444606e-01, -2.857379e+00, -1.912993e+00, 3.436817e-09, -1.749039e+14, 2.215154e-18, 3.384923e+18, -4.513038e-09, 4.814904e+05, 3.730911e+15, 1.861706e+12, 3.378290e-03, 2.851468e-06, -1.577518e-04, -4.122504e-12, -2.743002e+03, 8.512568e-02, -1.333039e-09, -4.899609e-17, -1.782085e-11, 2.552482e-02, 4.200193e+10, -4.298147e+03, -1.923210e-10, -1.208889e+01, 4.606772e-21, -3.331241e+10, -3.704566e-16, -3.733178e-20, -4.950049e+16, 3.184384e+15, -4.107375e-06, 1.801875e+09, 9.632951e-16, 7.172728e-10, 2.324621e+07, 2.892586e+15, -1.582511e-17, -4.119044e-13, -1.248361e+09, 1.531907e+08, -1.795628e-19, -1.735919e-17, -4.646689e-07, -2.779304e-11, 8.048984e-10, 3.536087e-02, -6.494880e+18, 2.714073e+06, 3.374557e+18, 3.621468e-06, 2.742652e-07, 2.551176e+03, -4.420578e+18, -4.370624e-08, -4.507765e-11, 4.193746e-20, 1.206645e+13, -3.750231e+03, 4.390893e+08, -9.756466e+11, 3.392778e-06, -3.453465e+01, -1.406102e+11, -3.673526e-15, 1.417082e-03, 1.499926e+16, -4.471032e-17, -2.657920e+16, 4.792261e+09, -3.212735e+17, -3.372737e-05, -4.730048e+01, 3.365478e+07, 2.835695e+13, -3.242022e-07, 3.640288e+11, 1.862055e-08, -4.121250e-19, -3.891100e-02, -4.367058e-15, 1.364067e-17, -4.575429e-12, 3.621347e-07, 1.506864e+11, 3.715065e+18, -1.773352e+08, -3.502359e+07, -2.326890e-04, 2.948814e-17, -2.438988e+14, -2.994787e+04, -3.755515e+12, 2.708013e-13, 3.281046e-01, -3.710727e+12, -8.380304e+14, 1.062737e-05, 2.385939e+16, -4.383210e-20, -3.779417e+03, 3.080324e-03, 3.810188e+16, 3.058415e+00, -2.484879e-21, -1.951684e+01, 6.979033e-10, -3.866994e+06, 4.278936e-19, 9.365131e+10, -3.685205e+01, -2.678752e-16, 2.011434e-19, 1.884072e+08, -1.300910e+04, 2.414058e-09, -4.675979e+11, 3.583361e-19, -4.499438e+18, 1.641999e-21, -2.686795e-10, 6.136688e-20, -3.793690e+16, 4.944562e-20, -3.490443e-03, 3.080547e+02, 2.041413e-06, 2.021979e+03, 2.314233e-06, 1.564131e-01, -8.712542e+17, 7.569081e+16, -1.056907e+17, 2.095024e-14, -2.487621e+17, -3.490381e+19, -6.944641e-01, -2.892354e-08, -3.597351e+12, -1.985424e+06, -2.348859e+09, -1.657051e+01, -3.358823e+14, 3.219974e-16, -4.819092e-13, -2.905178e-11, 8.257664e+04, -4.092466e-15, -3.464711e-13, -3.956400e-14, -2.548275e-08, -8.917872e-21, 7.387291e+13, 2.300996e+16, -4.870764e+18, -9.909380e-03, 1.260429e-08, -3.409396e-12, 1.003848e+02, -4.883178e-02, -3.125474e-14, 1.005294e+11, -4.736012e+09, -1.647544e-09, -3.491431e-03, 4.619061e+07, -4.547601e-09, -3.788900e-02, -2.648380e-17, 4.601877e-16, 1.754357e+13, 4.325616e+12, 1.860822e+03, 4.080727e+15, -4.573470e-14, -1.293538e+16, 2.811449e+05, 4.032351e+06, 4.274005e+04, 3.454035e-21, 4.933014e+09, -3.712562e+08, 3.158678e+06, -1.636782e+11, -2.884298e-18, -3.685740e-17, 1.027472e-07, -3.765173e-12, 2.740894e-17, 2.634880e+02, -4.334010e+00, -3.708285e-14, -3.858731e+16, -3.956687e+13, -4.064064e-12, 2.558646e-05, 4.459143e+03, -9.661948e+03, -1.994335e+16, 1.202714e-17, -3.782707e-17, 9.099692e-04, -1.864561e+09, 3.493877e-08, 4.288188e-01, 1.767126e-14, -6.779451e-22, -1.977471e-09, -3.536454e+06, -7.319495e-04, 2.004028e-16, -3.181521e-17, 3.336202e+14, -2.752423e+07, 3.390953e+01, 4.199625e-15, 2.883232e-12, 3.122912e-06, 7.324619e-19, 3.092709e-02, -2.758364e-15, -2.489492e+12, -1.622009e-08, 2.371204e+06, -1.582081e+08, -6.382371e-17])

    @property
    def d3(self):
        return [2.047398e-20, 2.091541e-20, 9.084241e+14, 1.583413e+01, 5.168067e-02, 1.360920e-11, 9.818531e-21, 6.293083e+07, 4.406956e-14, 8.540213e-09, 7.329310e-03, 5.566796e+00, 3.968358e-08, 4.928656e-08, 5.994301e-20, 8.281551e-21]
    @d3.setter
    def d3(self,value):
        ca(value,[9.025110e-18, 3.567231e+17, 2.594489e+01, 2.311708e-04, 7.345164e+13, 6.550284e-01, 1.969554e+12, 9.451979e-05, 5.900637e-09, 9.975667e+03, 6.549533e-17, 2.227145e-13, 2.822132e+18, 4.332600e+18, 1.485466e+05, 5.844952e-14])

    @property
    def d4(self):
        return [2.864760e-08, 3.900663e+13, 9.105789e+11, 2.943743e-15, -2.823159e-16, -3.481261e+19]
    @d4.setter
    def d4(self,value):
        ca(value,[-4.207179e-09, -3.611333e+11, -4.155626e-06, -2.458459e+10, 2.826045e-11, 3.511191e-08, 4.759250e-07, 2.455883e+09, 4.182578e+11, 4.732337e-14, -2.967313e+02, -4.139188e+14, 6.287269e+03])

    @property
    def d5(self):
        return numpy.array([4.427272e-10, -1.149547e-08, -1.134096e+16, -4.932974e-03, -7.702447e-01, -3.468374e-03, -5.037849e-14, -4.140513e-08, 4.553774e+03, 2.746211e+01, -4.388241e-17, 2.262009e+00, 5.239907e+06, 4.665437e-05, -1.662221e-05, 5.471877e-13, 2.592797e+11, -4.109763e-05, 1.797563e-04, 1.654153e+01, 4.011197e+07, -2.261820e-10, 5.836798e+02, 1.518876e-18, 4.814150e+18, -4.610985e-07, -3.126663e-07, -1.981883e+10, 4.117556e-02, 1.937380e-07, 1.397017e-10, 2.809413e-17, 9.387278e+18, 4.777753e-11, -4.248411e+15, 3.851890e-16, -1.598907e-08, 3.699930e+14, 2.763725e-08, -4.130363e+17, 3.105159e+06, -2.026574e+00, 3.956735e+01, 3.893311e-04, 3.574216e+13, 3.618918e+03, -4.027656e-09, 9.174470e-02, -8.108362e-21, 1.857260e-18, -3.540422e+13, -2.985196e+12, -3.219711e-08, -1.618670e-13, -2.648920e+12, 1.224910e-14, -4.740355e-03, 4.604337e-18, 3.809723e+05, -4.460252e+15, 1.894675e-15, -4.141572e-08, -3.939165e-09, -1.916940e-06, -2.382435e+16, -4.689458e-01, 1.498825e+17, 1.876067e-15, -1.801776e+09, -1.140569e-05, -6.881731e-08, -4.835017e-07, 3.843821e-17, 2.220728e+06, -4.321528e+10, -3.950910e+01, -1.732064e-11, 3.009556e-16, -3.509908e+18, -7.781366e-15, -2.511896e-18, -2.037492e+04, 2.656214e-19, 2.163108e+16, 4.526743e+19, 2.738915e-11, 8.491186e-16, -1.286244e+05, 3.635668e+12, -4.964943e+15, 3.725194e+05, -4.010695e-19, 2.140069e-09, 3.957374e+19, 4.478530e-06, 4.284617e-06, -3.459065e+12, 1.525227e-18, 4.892990e+06, 3.557063e+07, 2.986931e+18, 2.147683e-05, -4.190776e+17, -3.715918e-14, -3.448233e+01, 1.272542e+15, -3.900619e-06, -3.712080e+05, 3.388577e+04, -4.440968e-11, -4.395263e+18, -4.052174e-06, -3.065725e+00, 3.915471e-04, 4.863505e+12, 4.861871e-09, 4.607456e+03, -1.845908e-12, -9.985457e-11, -4.534696e-08, -1.163049e-17, 4.492446e-11, 3.078345e+06, 8.520733e+05, 2.218171e+14, -4.546400e+09, 4.641295e+09, -1.677260e-07, 9.650426e+04, -4.001218e-04, 4.761655e-22, -3.989865e+01, -5.800472e-08, -2.548565e-01, 4.648520e-08, 4.255433e-16, -2.387043e-11, 4.172928e+17, 4.194274e-12, -1.391555e-04, -1.063723e-01, 1.609824e-13, 9.196780e-10, -4.744075e+06, -4.764303e-02, -4.540535e-10, -4.361282e+00, -1.460081e+01, -2.215205e-16, 4.652514e-19]).reshape([5, 6, 5], order="F")
    @d5.setter
    def d5(self,value):
        numpy.testing.assert_allclose(value,numpy.array([-5.528040e-08, 3.832644e-01, -9.139211e-22, -4.919312e-05, 3.809620e-11, 1.751983e-09, 2.207872e-21, 1.432794e+09, -1.970313e+11, 3.405643e-18, -3.756282e+14, -4.918649e+08, -3.162526e-14, -2.853298e-09, 2.835704e+10, 4.458564e+16, 6.657007e+09, 3.640798e-10, 4.950898e-06, 3.384446e+14, -4.065667e+16, -2.243648e-05, 4.822028e-21, 4.231462e-14, -2.526315e+11, -5.626782e-05, 2.321837e+13, 1.772942e-09, 1.606989e-08, 2.669910e-04, -3.635773e+08, -3.967874e-10, 6.599470e+15, 4.612631e-08, -1.417977e-11, -8.066614e-18, 5.738945e+15, 6.408315e+13, 1.922621e+12, 3.096211e-14, -2.079924e+18, 1.664290e+09, -4.502488e+07, 3.092768e+05, 4.414553e+10, -3.673268e+02, -4.772391e+17, -1.100877e+02, -1.453900e+01, 4.293918e-13, -4.270900e-02, -3.886217e+11, -2.206806e+02, 7.034173e-07, -2.826108e-21, 3.616703e-21, -3.385765e+04, -7.027764e-11, 9.684099e+05, -4.248931e+03, -3.415720e-20, -3.315237e-11, -9.555895e+11, 3.520893e-13, 1.089514e-13, 3.591828e-21, -4.847746e-06, -2.678605e-16, -7.480139e-04, 2.208833e+01, 1.075027e-07, -1.047160e-05, 2.309356e+06, 7.308158e-19, -4.915658e+02, 4.634137e+18, -3.682525e+13, 4.124301e-06, 4.158100e-10, 2.091672e-11, -6.856023e+07, 8.418116e-07, -1.655783e-13, -2.502703e-03, 1.274299e+17, -4.784498e-20, 1.357464e-10, 4.107075e-13, -2.753087e-05, -2.594853e-14, -3.712038e-13, 1.143743e+14, -2.495491e+10, 2.331111e-15, 2.987117e+18, 2.876066e-18]).reshape([8, 6, 2], order="F"))
        

    @property
    def d6(self):
        return numpy.array([4.427272e-10, -1.149547e-08, -1.134096e+16, -4.932974e-03, -7.702447e-01, -3.468374e-03, -5.037849e-14, -4.140513e-08, 4.553774e+03]).reshape([3,3],order="F")
    @d6.setter
    def d6(self,value):
        numpy.testing.assert_allclose(value,numpy.array([-5.528040e-08, 3.832644e-01, -9.139211e-22, -4.919312e-05, 3.809620e-11, 1.751983e-09, 2.207872e-21, 1.432794e+09, -1.970313e+11]).reshape([3,3], order="F"))



    @property
    def s1(self):
        return 7.8573
    @s1.setter
    def s1(self,value):
        pass

    @property
    def s2(self):
        return [3.252887e+09, 1.028386e-04, -2.059613e+01, 1.007636e-14, -4.700457e-13, -1.090360e-22, -3.631036e-15, 2.755136e-09, 4.973340e+13, 2.387752e-15, -9.100005e+06, 1.484377e+13, -2.287445e-13, -3.718729e+18, -4.771899e+19, 8.743697e+13, 1.581741e+07, 2.095840e-09, -5.591798e-03, 6.596514e-06, -1.006281e+05, -4.126461e+12, 4.246598e-20, -1.376394e+08, -3.398176e-03, -1.360713e-21, 3.109012e+14, -8.112052e+07, -8.118389e-02, -3.455658e+14, 7.352656e+12, 4.198051e+06, 4.258925e-03, -2.634416e+12, 3.362617e+02, -4.606198e-15, 4.228381e-19, 4.209756e-15, -1.268658e+05, 3.019326e+02, 7.937019e-01, 6.225705e-09, 1.324805e-19, -4.355122e+01, -4.533376e+15, -1.584597e+01, 1.657669e-02, -3.720590e-18, 2.038227e-04, 2.890815e+04, 1.513743e-14, 4.993242e-20, -5.255463e-21, -8.084456e-14, 4.087952e-09, 2.518775e-21, 4.977447e+15, 3.363414e-19, -3.931790e-20, -7.810002e+14, -3.589876e+14, -4.969319e-18, -4.356951e-20, -3.682676e+02, -1.319524e+10, 3.805770e-11, 2.134369e-10, 3.684259e-08, -2.901651e-13, -4.486479e-01, 2.208715e-02, 3.224455e-01, -3.305078e+09, -3.326595e-02, -2.473907e+03, 3.608010e-15, -2.596035e-01, 2.594405e-01, -7.569236e-01, -3.430125e+09, 2.920327e+02, -3.763994e-12, 2.617484e-12, 4.808183e-07, 3.885462e+15, -1.201067e+00, 1.887956e+06, -4.038215e+02, -4.710561e+03, 1.659911e-16, -4.955908e-17, 4.681019e-09, 3.945566e+05, -3.433671e+19, -2.679188e+05, -2.357385e-01, 2.891702e-19, -4.464828e-06, -6.003872e-04, 1.369236e+18, -3.597765e+01, -4.246195e+08, -4.765202e+17, 4.472442e+10, -1.038235e-05, -4.632604e-09, -2.484805e-15, -7.998089e-16, -3.690202e-04, -3.276282e-04, 1.966751e+10, -5.081691e-18, -2.004207e-05, -2.756564e-03, -2.624997e+14, 2.398072e-20, -4.098639e-10, 2.930848e+01, 8.983185e+15, 1.984647e-15, 1.331362e-16, -6.519556e+15, 4.270991e+15, -9.165583e-13, 4.266535e+17, 4.238873e-21, -2.487233e+17, 4.904756e+03, 2.692900e+10, 1.467677e-18, -2.204474e+06, -1.806552e-09, 9.617557e+17, -1.988740e-20, 1.713683e-04, -2.360154e-21, 4.178035e-17, 2.600320e+12, -4.761743e+09, 3.034447e-20, 4.941916e-06, -1.373800e+04, 1.851938e-09, 1.304650e+14, 3.067267e+07, -4.100706e-06, 2.190569e-03, 5.901064e-17, -2.152004e+15, 4.050525e+04, 3.769441e-06, -4.388331e-12, 1.037797e+12, 3.512642e-19, 3.857774e-09, 1.036342e+03, 3.683616e-18, 9.785759e+10, 2.199992e+03, -2.435347e-02, 1.526312e+06, 2.569847e+14, -2.288773e-01, 4.724374e-06, -3.807381e+13, 2.924748e-10, 2.820652e-20, 4.835786e-12, 2.811112e+02, -6.431253e+02, -4.843622e-06, 1.676490e-10, -4.432839e+07, 1.661883e+19, 8.668906e+07, 2.256498e-04, 2.170563e-01, 1.013347e-17, -4.271306e+11, -2.431836e-17, 3.983056e+02, 4.236306e+05, -2.142877e-20, -2.760277e-12, -8.479624e-08, 2.903436e+05, -3.288277e-17, 4.173384e-10, -1.598824e-08, 8.702005e+05, -1.456065e+08, 2.035918e+06, -1.445426e+02, -4.148981e+05, 4.439242e+02, -1.223582e+16, -8.226224e+14, 1.690797e+16, 1.683472e-04, -4.809448e-16, 4.517499e+06, 4.369645e+02, -4.532906e+09, -3.539758e+07, -2.406254e+01, 4.396602e+00, 2.995832e-01, -2.953563e-04, 3.412885e+17, 1.386922e-17, -2.177566e-04, 2.548426e+04, -3.937000e+16, 2.578962e+02, 2.423257e+16, 3.069379e+09, -4.940417e+09, -4.618109e-13, -1.387521e-11, -2.168721e-05, 1.917758e-01, -3.144071e+03, -1.045706e-13, -2.869528e+02, 2.072101e-13, 4.267714e+12, -2.063457e-19, -3.025547e-12, 8.101894e+10, -4.196343e-04, 4.753178e+18, -2.286673e+08, -2.618986e-10, 3.949400e-10, -4.390776e+12, -2.498438e+10, 3.800599e+12, -3.704880e+15, -4.173265e+02, 3.326208e+19, -1.093729e-21, 3.042615e+16, -1.711401e-09, 3.039417e-19, -2.250917e+15, 2.195224e-01, -2.953402e+05, -1.486595e+17, -2.387631e+00, -1.634038e-14, 6.153862e-18, -3.842447e+05, 3.238062e-14, -4.341436e-11, -1.816909e-19, -3.534227e+14, 8.578481e+07, -4.067319e+09, -4.680605e-08, 4.050820e+04, 1.715798e-11, -5.232958e-12, 2.291111e-07, 1.086749e+01, -3.028170e-14, -6.277956e+13, -1.639431e+11, 4.158870e+17, -1.208390e-18, 4.835438e-05, -3.135780e-08, -4.087485e-12, 2.466489e-08, 1.949774e+00, -3.532671e-21, -1.422500e+12, 4.352509e+03, -1.444274e-17, -1.162523e+19, -4.815817e-07, -2.809045e+11, -1.212605e+03, -3.496461e-08, 6.743426e-18, -4.226437e-06, -3.627025e+07, 1.037303e-05, 2.411375e+08, -2.721538e+12, -4.809954e-06, 4.578909e+16, 9.257324e+06, 4.326725e-03, 4.416348e+12, 4.424289e+13, 3.180453e+12, -6.028285e-10, 3.344767e-14, -2.747083e+18, 1.133844e-15, 3.922737e-06, -3.199165e+00, 2.417553e+02, 3.015159e-20, 2.119116e-02, 4.019055e-09, 3.368508e-21, -1.613240e-19, 3.832120e-14, 1.202460e+17, -3.304317e+19, 1.692435e+17, -2.597919e-05, 3.916656e+17, 4.821767e+06, 4.372030e+02, 1.987821e-08, -1.976171e-08, 1.319708e-09, -4.213393e+10, 3.829773e-15, -4.762296e-21, 4.642216e-18, 1.662453e-13, 6.642151e+03, 2.539859e-02, -3.112435e+09, -3.627296e-20, -1.660860e+02, -3.678133e+07, 3.428538e-01, -2.277414e-20, 2.228723e+17, -2.833075e-06, 9.084647e+03, -2.976724e-16, 2.778621e+15, -2.806941e+07, -1.626680e-15, -4.658307e+13, 7.967425e-11, -2.793553e-21, 4.778914e+16, -6.145348e-21, -4.883096e+11, 1.338180e+04, 7.533078e-16, 3.252210e+05, -2.882071e+10, -2.754393e-06, -1.689511e-16, -1.979567e-10, 4.494219e-04, 3.285918e-15, -4.347530e+05, -1.085549e+15, 1.301914e+07, 3.855885e+13, 3.036668e-11, -4.706690e+12, 3.727706e+17, -4.446726e-12, -4.829207e-08, -1.543068e-10, -2.473439e-11, -2.718383e+13, -4.211115e-21, 3.327305e-04, -1.084328e-20, 3.849147e+06, -1.321415e+09, -3.518365e+07, 2.246762e-21, 2.482377e+11, -4.265765e+03, -4.538240e-05, 2.727905e+18, -2.383417e-13, 4.103955e+04, 8.015918e-06, -2.965433e-18, 3.156148e+03, 8.093784e+18, 4.868456e-12, 1.048517e-02, 1.112546e-19, -3.751041e-12, -3.734735e-06, 3.019242e+06, -1.480620e-17, -3.405209e+07, -1.123121e+19, 8.155940e-20, 1.406270e-17, 2.154811e-13, 9.943784e-20, 1.523222e-17, 6.987695e-21, 8.826612e-12, -2.325400e-20, 3.700035e+15, -5.559864e-11, -8.568613e+10, 1.434826e-07, -2.080666e-03, -2.548367e-03, -4.310036e-18, 3.104310e+00, -3.862149e+17, -4.092146e-13, 3.538555e-14, -4.950494e-05, 6.538592e-13, -4.196452e-11, 2.351540e-01, -1.232819e-01, -3.669909e-21, 1.528733e-14, 5.661038e-15, -1.967561e-07, -2.284653e+02, -1.834055e-10, -2.175838e+05, 4.247123e+06, 1.184396e+18, 4.156451e+15, -4.992962e-14, -2.351371e+06, -6.698828e-10, 2.897660e+17, -3.470945e-06, 4.630531e-07, -4.453066e+10, 4.069905e+09, -4.459990e-08, 4.702875e-13, -2.780085e+17, 1.293190e-05, 2.227539e-03, 1.534749e-21, 7.390197e-02, 4.522731e-10, -1.224482e-02, -3.996613e+02, -1.057415e-15, -7.371987e+14, 4.291850e-02, -4.243906e-08, -3.540067e-04, 4.535024e+09, -3.027997e+10, -3.986030e-02, 1.722268e-04, -3.140633e-20, 3.343419e+08, 4.713552e+14, -3.190084e+05, 2.449921e-01, 2.727707e+14, -3.545034e+11, 2.417031e+13, -2.231984e-09, 3.533907e+16, -4.662490e+16, 3.355255e+14, -1.567147e+17, -3.525342e+12, -3.586213e-16, -4.002334e+15, -1.928710e+08, -4.718466e+04, -1.539948e-06, 3.135775e-11, 3.862573e-10, -3.105881e+08, 4.421002e-05, -2.369372e+01, 4.758588e+13, -1.044237e-15, -4.535182e-10, 1.330691e+18, 3.636776e-01, -4.068160e-12, 2.757635e-17, 3.247733e+13, 1.247297e+06, 5.806444e-13, 3.521773e-05, 4.589556e-14, 1.582423e+00, -1.676589e+00, -3.864168e-07, -3.042233e-02, 2.007608e+14, 4.852709e+02, -2.817610e-04, -1.882581e+19, 1.057355e-14, 4.090583e-04, -1.848867e-13, -5.463239e+13, -1.041751e+05, 3.457778e-01, -2.562492e+00, -6.751192e-10, 1.688925e-21, 3.884825e-07, 1.592184e-12, -2.039492e+06, -1.196369e+19, 2.200758e+00, 2.550363e-21, 7.597233e+06, -1.929970e+09, 1.939371e+03, -3.236665e+09, -1.313563e-13, 2.007932e+02, -3.028637e-02, -1.532002e+00, 2.165843e+17, -3.511274e-04, -3.777840e+15, 1.645100e+17, 3.088818e-07, -2.793421e-11, -4.286222e-01, 4.385008e-10, -2.105222e-01, -2.212440e+08, 2.684288e-01, 1.407909e+18, -3.881776e+08, 3.505820e-09, 3.555082e-19, 3.573406e+01, 4.042915e-19, 2.066432e+08, -2.467607e+10, 3.453929e+01, 4.297309e-14, 1.256314e-11, 8.930289e+14, -3.662200e-03, 2.075690e-16, -2.866809e-17, 4.394016e+10, -2.014195e-03, -3.738633e+12, -4.953528e-05, 3.710240e+06, 3.319208e+04, -5.762511e-20, -4.690619e+16, 3.412186e+19, -1.241859e+09, -4.081991e+12, 4.622142e+03, -1.285855e-02, 1.532736e-08, -2.364101e+09, -1.369113e-18, -2.168979e+19, 2.952627e-14, -2.358172e-16, -1.992288e+00, -9.180203e+12, 1.675986e+07, 4.817708e+06, -1.624530e+06, 4.857415e-01, -5.995664e-03, 1.874911e+08, -3.320425e-17, 5.469104e-02, -3.069767e+11, 8.084999e+12, -2.321768e-20, 1.920249e-06, -4.114087e-02, 3.244903e-04, 3.203402e-17, 4.143519e+06, 4.093124e+17, 4.456464e-15, -2.262509e-13, 4.856535e-08, -4.550552e-15, -3.011803e+18, -2.882488e+13, -2.690616e-04, -3.996010e-19, -4.438855e+18, -1.942208e+03, 1.934537e+18, -1.961547e-07, 4.970021e+17, -3.531211e-17, 4.187133e+04, 2.854106e-12, -2.313257e+13, -3.471439e+16, -6.829753e-16, -4.338617e+03, 5.552258e+05, 1.520718e+19, -2.527013e+14, -2.732660e-09, -1.957740e+11, -4.767907e+12, -4.837256e+18, 3.155432e-12, -3.278156e-04, -1.117720e-13, -3.838176e+11, -7.207202e+08, -4.075808e-21, 1.659402e-14, -4.301886e-19, -4.461337e-11, 2.200979e+15, 4.339143e+07, 5.071459e-06, 1.832776e+18, -2.698948e+03, 4.682397e+01, 2.801081e-08, -3.424292e+00, -5.130555e+14, 1.229975e-14, 2.383361e-09, -3.611087e-07, -2.576595e-07, 1.295398e-08, -2.525216e-11, -2.546657e+10, 9.501518e+03, 8.325605e+04, -1.382092e+02, 2.169085e-21, 4.019485e+16, -2.404251e+17, 1.154833e+10, 9.454498e+01, -7.888753e-09, -4.907318e-20, 1.373262e+08, -2.295105e-21, 1.329034e+17, -3.403883e-20, 3.500734e-03, 2.657397e-20, 4.956090e-07, -2.191353e-03, -1.879262e+09, 4.519858e-14, 4.592234e-14, -1.473612e+11, 4.425251e+10, -3.936903e-01, -2.866089e+09, -3.046203e-09, -4.818832e+01, 2.460150e+02, 2.944622e-11, -1.675111e-20, -1.206111e+01, 5.044200e-13, 3.225861e+02, 3.170008e+12, 1.964043e-20, 3.464033e+03, 1.286135e-08, -6.425529e-10, -4.630162e-02, 2.616476e+18, 4.853669e+03, -1.851316e-03, 1.262159e-02, -1.816675e-12, 3.753560e+14, -3.033601e-18, 1.915137e-02, 3.411614e-14, 4.849348e+05, 3.033922e+13, 3.174852e-17, -4.397997e-09, -9.549484e-01, -1.706859e+11, -3.009122e-01, -8.189854e-15, 4.122789e-17, -1.351025e-13, -2.365671e-10, -1.139709e-05, -2.020593e+10, 3.664729e+14, 1.170917e+00, 1.157248e-19, -4.189734e+17, -4.407278e+13, 4.776929e+18, -3.279961e+07, -4.740186e-15, -3.764392e-02, -2.193781e+18, -4.556987e+00, -3.170243e-18, -1.755775e-16, -2.163959e-03, 2.410150e+11, 1.215874e-18, -4.927956e-05, 2.252375e-06, -3.315242e-14, -3.476357e+16, -4.545391e+00, 6.072704e-13, -4.571860e+09, -2.297081e-02, 2.401997e+10, -6.449709e+05, -3.580234e-08, -5.390535e+08, -4.891390e-19, 3.441769e-09, 4.885513e-09, -4.897531e-10, -1.792753e+08, 2.048965e+13, 3.339876e-21, 4.140957e+04, 2.022520e-21, 5.983159e+06, 1.938164e+13, 2.796107e-19, -1.975692e+09, -2.106710e+15, -4.482226e+09, -2.968068e-19, -1.171747e-03, 1.579378e-01, -4.568752e+16, 2.593340e+11, 3.441530e+10, 3.461992e-01, -5.333082e-09, -4.611969e-12, -4.262468e+19, -4.367063e+01, -2.447378e-11, -3.554859e+02, 4.824680e-05, -1.122071e+11, -2.226371e+13, 3.917182e-17, -1.308204e+10, 4.105055e-16, 5.087060e+07, 7.102691e-05, -2.872202e+03, 1.711266e+11, 3.331993e-08, -1.313944e-08, 3.648109e+11, 5.394321e+01, -4.125398e+03, 3.460645e-02, 2.573745e-18, -1.376298e+01, -3.283028e-05, 3.939711e-12, 3.986184e+17, 2.619889e-11, -4.318052e-09, 1.410821e+00, 3.547585e-07, 4.046432e-17, 1.880087e-07, 1.867841e-05, -1.383592e-21, 2.972106e-05, 2.867092e+01, 3.092781e+03, -6.897683e-02, -1.707761e-04, -4.231430e-11, -3.796784e+00, -2.953699e+11, 3.691013e+09, -3.962307e-12, -1.335633e-17, -1.759192e-01, -4.332862e+04, 1.044899e+11, -2.126883e+03, 1.948593e+14, -2.173759e-05, -4.393250e+05, 1.626217e+08, 2.832086e+18, 4.655433e+03, 2.944186e+08, 2.864233e+03, -3.565216e+05, -4.667000e+11, -3.739551e-03, 3.137195e+05, 2.044129e+19, 2.629232e+14, 3.119859e-09, 3.656121e-15, -4.844114e-03, -2.641449e-11, -3.788231e+05, 2.803203e+17, -3.764787e+09, -6.009761e-08, 4.106308e+01, -2.071363e-20, 1.884576e-20, 2.654081e+11, -3.456281e-11, -4.760486e-02, 4.096057e+11, 4.346738e-11, 2.827941e-02, -1.946717e+08, -9.067051e+15, 4.331454e-14, 4.792779e-09, -4.738308e+18, -1.228815e-09, 2.097152e+16, -4.440036e-06, -3.762990e+02, -2.642879e+12, 3.100004e+10, 3.604336e+12, -3.951650e+11, -1.023763e+15, 4.908325e+17, 2.123963e-19, -1.744445e+09, -2.874189e-06, 2.208907e-08, -2.353407e+10, -1.020581e-03, 1.689180e-01, -2.563565e-12, -1.220758e-15, -2.657970e-16, 1.140528e+10, -2.802143e+14, -3.835574e+00]
    @s2.setter
    def s2(self,value):
        pass

    @property
    def i8_1(self):
        return -66
    @i8_1.setter
    def i8_1(self,value):
        if (value!=45): raise Exception()

    @property
    def i8_2(self):
        return [-106, -119, 126, 87, 95, 79, -1, -15, -4, -30, 76, -121, 35, 80, 5, 7, -36, 102, 120, 105, 86, 98, 113, -62, 105, 38, 93, 20, 92, 7, -99, -121, -56, 50, -35, -95, 2, -43, -49, 73, 49, -42, -24, -3, -41, -59, 119, -108, 82, 98, 95, 111, 114, 115, 109, -125, -60, -45, -110, 31, -73, -111, 69, -108, -125, 14, -87, 61, 114, -104, -72, -67, 35, 26, 61, 59, -114, 125, -82, -34, 7, 71, -117, 125, 79, -116, -81, 3, -59, -121, 112, 64, 54, -9, -63, 37, -86, 104, -105, 7, 72, -99, 84, -3, -63, 77, 27, 36, 52, -110, 60, -119, -124, 82, -29, 107, 124, 105, 96, -34, -11, 0, 59, -39, -107, 55, 95, -26, -60, -30, -102, -94, -28, -7, 76, 56, -31, -68, 6, 101, 67, 101, -92, 120, 105, -119, 114, 6, 9, 43, 73, -64, -18, -77, -72, 84, -101, -114, -50, 28, 86, 103, -83, -109, -59, 82, 96, -70, 20, 75, -44, -3, -115, 60, 45, 94, 65, -108, 2, 12, 28, 110, -19, 20, 102, -41, 42, -61, -52, -54, 116, 114, -74, 14, -21, -43, -85, 16, 57, -62, -83, -79, 85, -7, 109, -45, 102, 28, 123, -96, 2, -37, -19, 104, 4, -43, -92, -114, 34, 44, 29, -96, -99, -95, -101, 12, 18, 107, 125, 114, -65, 126, -28, 114, -2, 9, 79, 69, 67, 78, -26, -95, 109, -81, 22, -61, 84, -16, -84, 57, 8, -88, -124, 119, 8, 35, -56, -14, -90, -73, 118, -4, -93, 35, -76, 6, -41, 98, -69, -108, -78, 16, -72, 43, -113, 71, -70, -51, -41, 62, -38, -58, 58, -127, 117, 67, 51, 34, -98, -13, -111, 13, 2, -101, -75, -22, 34, 42, -93, -106, 90, -65, -65, -82, 55, -111, -28, -114, 54, 0, 39, -46, 19, 78, 75, -116, 64, -120, -81, -116, -96, -36, 101, 67, -96, 14, 76, 74, 29, 67, 101, 68, -83, 62, 86, -64, -76, -87, 8, 44, -61, 31, 65, -120, 3, -82, 127, 105, 114, -58, -117, 52, -104, 117, 23, 4, -79, -44, -113, -65, 52, 83, 39, -120, 36, -80, 104, 46, 12, -61, 104, 99, 4, 53, 36, 91, 115, -8, -32, -111, 53, 6, 70, -70, 108, -68, 119, -3, -40, 110, -15, -94, 23, 36, -39, -87, 96, -89, -73, 119, 117, -45, -119, 48, -70, -28, -22, -127, -16, -56, -75, 72, 59, 54, -15, -57, -113, 78, -24, 63, 118, 74, -62, -101, 62, -123, 28, 0, -9, 30, 115, 47, 86, 88, -58, 91, 103, 121, 81, -78, 80, -50, -13, 33, 92, 107, -79, 55, -89, 34, -121, 82, -105, 59, 73, 59, 119, 72, -26, -122, 1, 41, 62, -11, -41, 101, -101, 79, 27, -73, -90, -2, -96, 10, 116, -86, -25, -117, -36, 13, -52, 90, -39, 113, -105, 71, -7, 2, 109, 106, 70, -86, -82, -121, 94, 58, 13, -124, 119, 34, 36, -37, 47, 23, -101, -96, -114, -37, -21, -37, -77, 121, -43, 25, -105, -6, 5, 3, -114, 30, -98, -74, -97, -43, 16, -84, -44, -56, 1, -115, -100, -46, -63, -100, 112, -106, -128, -2, -106, -116, -1, -43, -24, -73, -124, 14, 69, -90, 83, -85, -103, 52, 22, 58, -90, 77, -121, 110, 20, 114, -107, 102, -76, -6, -102, -38, 53, -100, -72, 118, -100, -113, 120, 53, -93, 61, -92, -84, -125, 81, 127, 125, -8, 99, 70, -49, -9, 86, 103, -96, -96, -40, 43, -48, 29, 28, 90, 45, -118, 111, -101, 24, -25, 123, -105, 124, 17, 27, -6, 111, -113, 21, -88, -117, 55, -7, -24, -24, 52, 39, -36, -81, 78, 95, 13, 121, -8, 116, -106, 45, -49, 19, 12, 13, -127, 109, -124, 14, 18, 84, -61, 23, 68, -102, 115, -34, 7, -10, 57, 107, -48, -53, -67, -63, -100, -84, -31, 79, -58, 56, 89, 40, 63, -37, 71, -7, -53, 91, -66, -74, -37, 48, -37, 123, -96, -11, -56, 80, -88, -53, 27, 7, -29, -124, -46, 22, -103, -67, 93, 42, -37, 18, -126, 120, -81, 74, 26, -54, 19, 86, -112, -38, -57, 119, 26, -62, -67, 126, -50, -31, -36, 120, -127, 123, -88, 43, 50, 61, 94, -80, 35, 41, -109, 71, 91, -118, 66, -60, -127, 47, 75, -52, -66, -125, -111, 44, 116, 9, 68, 115, 113, 8, -4, 39, 23, 54, 107, -119, 1, -68, -11, 103, -123, 29, -92, 15, -10, -31, 35, -91, 38, 37, 110, 9, 80, -115, -120, 112, 110, -28, -116, 63, 85, -65, 5, 122, 19, -84, 97, -16, -46, 97, 104, 28, -83, -33, 38, -18, -8, -126, 82, 81, 88, 109, 118, -56, 64, -96, 36, -10, -109, 74, -86, 105, 123, 110, -116, 91, 15, 123, -26, -121, 75, 63, 24, 94, -43, 123, 74, 79, -42, 74, -102, 57, -27, 116, 126, -100, 2, 49, 17, 28, 27, -58, -98, 39, 50, -66, -75, -23, -112, 64, -16, 60, -62, 122, 53, -42, 21, -40, 88, 2, 62, -103, 108, -74, -95, 113, -49, -73, 63, 94, 44, -41, -68, -124, 46, 13, -17, 11, -100, 58, -98, -40, -64, -56, 21, -47, -120, -7, -23, -51, 27, -99, -42, -109, -55, 106, 92, 110, 19, 32, -117, 4, -34, 65, 72, -100, -122, -69, -94, 122, 60, 23, -93, -84, 30, 118, -92, 88, -104, 23, -71, 115, 106, -118, 9, 64, -34, -71, 43, -92, -13, -82, -5, 15, 18, -11, -113, -109, -128, 104, 34, 72, -110, -59, -113, 69, -106, -74, -66, 115, -31, -27, 59, -73, 73, 120, -34, 59, 126, -93, 49, -53, 114, -122, -28, -28, 94, -37, -90, -32, 80, 15, 4, -101, -78]
    @i8_2.setter
    def i8_2(self,value):
        ca(value,[-66, 34, -121, -118, -12, -83, -43, 55, -53, 31, -100, -37, -116, 69, 22, -60, 59, 32, 51, 46, 109, 36, 31, 49, -99, -69, -99, -89, 27, -18, -77, -63, -101, -122, -60, 58, -76, -86, 58, 49, 48, -67, 54, 48, -30, -26, 95, 42, -13, 17, -93, -34, 28, -49, 8, 122, 22, -72, 109, 103, 15, -81, -73, -53, -112, -52, -54, -81, -126, 35, 3, -102, -125, 67, 125, 44, -48, 95, -18, -103, 114, -86, 108, -37, 70, 48, 7, 19, 0, 35, -104, 2, -51, -9, 70, 41, 118, -43, -71, 59, 32, 36, -10, -2, -76, -18, -93, -80, -27, -51, -70, -87, 48, -98, 5, 72, -120, 86, 62, 69, -94, 23, 71, -124, -88, 34, -65, 6, 33, 73, -101, 40, -104, 17, -68, 53, -55, -11, 12, 24, -63, 121, 98, 58, 125, -13, 6, 49, 71, -72, -22, 53, 83, -97, 87, -117, -26, 6, 93, -98, 82, -111, -84, 23, -73, -10, -34, -118, 64, -89, -4, -104, -83, -52, 8, 64, -81, 33, -91, 41, -43, 12, -66, 31, -17, 46, 91, 9, -124, -117, 108, -15, -39, -92, 29, 116, -93, 107, 58, -7, -35, -116, -52, -11, -35, 66, 6, 32, -34, -123, -102, 102, 123, -104, 51, 80, -84, 71, -65, -4, -121, 123, -87, -21, -124, 63, 122, 74, -31, 123, -31, -63, -106, -82, -24, -42, -30, -126, 0, -38, 127, -13, 101, 60, 104, 54, -25, 50, -19, -93, 2, -48, 99, -59, 103, 28, 44, -7, -58, -19, -55, 17, 58, 15, -23, 75, 58, 11, -2, 104, -58, -73, 56, 84, 34, -4, -101, 10, -106, 41, -88, 15, -117, 5, -63, -106, -9, 40, -115, 47, 99, -66, 120, 126, 5, -62, 8, -111, 123, 92, 122, 24, -31, -65, 115, -43, 5, 56, 49, 102, -29, 65, 97, 20, -90, -39, 40, 75, -43, -47, 86, -104, -32, -90, 14, 13, -75, 8, -9, 104, 122, -24, 77, 10, -100, 26, 0, 35, 55, -10, 17, 22, -29, 115, 117, -10, -54, 37, 46, 48, -28, -105, 20, -117, 73, 93, -63, 9, -125, -94, 57, 119, -10, 11, 49, -57, -14, -107, 90, 72, 96, 55, 86, 81, -86, -70, -125, 17, 100, -91, -70, 87, 29, 100, -19, -45, 46, 25, -49, 79, -10, -1, 22, 75, 9, -50, 114, 106, -122, -89, 41, 1, 105, 123, -69, -123, 77, -61, -100, 15, -113, -19, 46, -53, 46, -89, -97, -38, 92, 73, 68, -101, 118, 67, 23, -17, 73, 109, 36, 76, 69, -10, 7, 64, -39, -49, -4, 3, -102, -15, 117, -8, -83, 6, 117, 105, 26, 28, 19, 66, 24, -47, -64, 86, 4, 57, 95, 23, 24, 76, -15, 106, -58, 77, -10, -112, -39, 55, -4, 95, -90, 61, 64, 32, 68, -43, -108, -15, -6, 63, -105, 72, -84, -10, -11, 122, 46, -84, 26, 76, -88, -67, -95, 10, 10, -89, -121, -65, -69, 112, 37, -106, 75, -94, -60, -7, -72, 44, 71, -108, -71, 31, 99, 9, 10, -68, -56, 69, 0, -71, -4, -87, -6, 83, 7, 108, 98, -37, -60, 16, 23, 26, 3, -119, -20, 58, 102, 29, 111, -43, 26, 37, 34, 9, 82, 76, 120, 7, 51, -35, 65, -93, 38, -82, -44, -31, 120, -93, 7, 10, -76, -12, 105, 41, 13, 123, -90, 57, 84, -123, -21, 49, 104, -103, -32, -79])

    @property
    def u8_1(self):
        return 222
    @u8_1.setter
    def u8_1(self,value):
        if (value!=232): raise Exception()

    @property
    def u8_2(self):
        return [20, 34, 154, 240, 82, 27, 230, 242, 253, 161, 17, 124, 80, 120, 210, 237, 179, 95, 224, 104, 74, 77, 148, 17, 98, 7, 13, 203, 155, 197, 223, 36, 207, 87, 56, 56, 76, 112, 100, 154, 40, 239, 13, 185, 77, 91, 107, 73, 196, 234, 3, 235, 40, 222, 224, 46, 47, 150, 167, 104, 206, 245, 20, 181, 133, 190, 255, 1, 183, 218, 5, 121, 233, 68, 72, 140, 250, 213, 199, 143, 41, 22, 238, 149, 235, 42, 170, 2, 58, 242, 91, 116, 62, 167, 113, 28, 8, 0, 199, 142, 8, 102, 60, 87, 147, 104, 125, 163, 135, 1, 186, 44, 117, 103, 186, 50, 68, 179, 203, 61, 231, 80, 45, 35, 231, 127, 93, 49, 154, 182, 1, 151, 111, 70, 127, 13, 41, 113, 170, 41, 173, 14, 129, 108, 235, 166, 153, 50, 203, 42, 43, 93, 243, 114, 190, 225, 12, 227, 24, 221, 177, 188, 218, 55, 6, 199, 162, 67, 152, 185, 216, 108, 251, 225, 146, 85, 220, 192, 36, 39, 20, 189, 24, 117, 98, 107, 215, 238, 145, 113, 40, 184, 110, 186, 66, 207, 164, 43, 70, 242, 211, 65, 232, 92, 164, 178, 3, 120, 1, 28, 247, 234, 210, 20, 61, 83, 147, 174, 177, 131, 229, 117, 211, 161, 73, 161, 224, 80, 219, 151, 131, 42, 37, 46, 68, 213, 62, 101, 8, 143, 146, 103, 52, 69, 7, 241, 55, 191, 104, 208, 100, 192, 48, 199, 30, 38, 148, 25, 252, 47, 18, 152, 142, 181, 231, 205, 166, 171, 14, 236, 15, 232, 235, 36, 66, 88, 141, 87, 66, 9, 94, 214, 100, 227, 207, 1, 6, 102, 170, 53, 53, 152, 136, 115, 251, 227, 218, 164, 20, 109, 174, 36, 135, 122, 237, 146, 226, 42, 202, 183, 112, 68, 121, 92, 23, 75, 34, 228, 131, 141, 52, 12, 132, 12, 43, 220, 33, 110, 30, 120, 244, 192, 128, 190, 89, 109, 165, 9, 25, 27, 129, 135, 80, 17, 217, 152, 237, 241, 56, 233, 78, 224, 115, 143, 214, 201, 78, 139, 50, 185, 115, 234, 31, 11, 190, 244, 28, 93, 13, 153, 78, 154, 62, 86, 40, 133, 29, 12, 133, 69, 50, 197, 127, 242, 14, 173, 70, 116, 243, 200, 197, 245, 249, 231, 139, 46, 99, 37, 55, 220, 57, 103, 163, 71, 252, 54, 52, 254, 97, 158, 155, 249, 243, 55, 112, 226, 88, 25, 29, 41, 109, 6, 219, 193, 89, 193, 164, 166, 103, 119, 69, 214, 105, 14, 20, 208, 56, 231, 59, 68, 49, 107, 119, 99, 109, 210, 234, 228, 111, 219, 32, 211, 172, 101, 172, 99, 227, 112, 137, 204, 19, 3, 111, 219, 245, 89, 106, 32, 108, 234, 81, 72, 27, 99, 151, 212, 108, 37, 248, 183, 241, 194, 37, 73, 230, 130, 11, 6, 122, 220, 192, 114, 116, 208, 187, 159, 226, 98, 191, 253, 226, 39, 212, 138, 106, 196, 153, 61, 218, 218, 20, 238, 82, 237, 196, 114, 135, 239, 221, 20, 52, 73, 208, 234, 99, 185, 218, 218, 47, 95, 218, 110, 165, 216, 121, 249, 203, 206, 213, 201, 138, 253, 43, 238, 131, 62, 229, 123, 69, 175, 61, 176, 180, 72, 120, 158, 91, 145, 16, 162, 70, 54, 170, 170, 60, 9, 226, 40, 66, 159, 139, 83, 20, 171, 32, 189, 140, 122, 1, 64, 144, 250, 94, 74, 91, 160, 146, 146, 17, 78, 43, 115, 166, 63, 81, 88, 83, 178, 177, 110, 93, 188, 29, 41, 28, 73, 40, 245, 49, 63, 134, 103, 135, 17, 172, 150, 249, 23, 230, 166, 31, 55, 203, 149, 19, 4, 101, 237]
    @u8_2.setter
    def u8_2(self,value):
        ca(value,[52, 40, 13, 185, 137, 3, 173, 236, 60, 18, 206, 224, 231, 19, 31, 139, 177, 201, 100, 37, 8, 94, 145, 135, 217, 32, 59, 26, 243, 213, 97, 78, 145, 136, 142, 249, 46, 247, 20, 240, 47, 211, 60, 35, 170, 0, 119, 14, 36, 7, 165, 132, 35, 199, 33, 45, 27, 111, 135, 50, 210, 248, 118, 162, 199, 152, 28, 202, 222, 8, 191, 40, 134, 213, 36, 131, 198, 76, 82, 212, 26, 33, 219, 181, 213, 205, 104, 118, 74, 239, 226, 65, 161, 29, 158, 223, 175, 214, 160, 65, 229, 56, 207, 64, 194, 167, 85, 221, 82, 56, 182, 226, 206, 71, 203, 116, 201, 234, 16, 42, 32, 47, 149, 161, 173, 60, 195, 59, 138, 241, 52, 152, 48, 57, 137, 206, 201, 58, 242, 139, 149, 42, 185, 94, 27, 224, 249, 33, 24, 18, 148, 104, 89, 163, 94, 214, 232, 133, 74, 124, 117, 39, 0, 73, 86, 254, 186, 224, 96, 236, 113, 39, 28, 245, 218, 147, 215, 62, 191, 23, 20, 27, 32, 151, 25, 225, 3, 157, 221, 133, 124, 35, 41, 177, 93, 137, 198, 96, 129, 235, 21, 10, 110, 16, 25, 65, 153, 157, 139, 82, 24, 43, 4, 180, 238, 174, 226, 183, 56, 224, 239, 130, 62, 40, 12, 226, 219, 164, 71, 242, 179, 227, 53, 148, 38, 228, 151, 2, 249, 132, 56, 253, 10, 107, 241, 56, 97, 88, 198, 203, 33, 132, 212, 44, 239, 7, 206, 156, 144, 93, 44, 71, 40, 171, 60, 234, 89, 238, 114, 240, 145, 141, 51, 180, 85, 75, 125, 219, 2, 121, 53, 12, 223, 90, 174, 248, 45, 39, 151, 5, 155, 29, 244, 124, 156, 60, 250, 52, 54, 186, 95, 245, 18, 51, 52, 183, 105, 226, 245, 214, 94, 254, 98, 14, 46, 203, 225, 95, 126, 178, 49, 82, 159, 231, 170, 250, 63, 162, 156, 218, 184, 211, 76, 181, 97, 180, 239, 45, 135, 147, 49, 147, 0, 32, 22, 77, 209, 215, 54, 83, 29, 127, 80, 150, 50, 15, 69, 33, 118, 255, 168, 201, 2, 218, 13, 53, 164, 101, 34, 218, 110, 107, 147, 5, 78, 135, 1, 11, 242, 43, 181, 108, 107, 46, 176, 74, 2, 251, 26, 97, 254, 79, 204, 97, 41, 90, 126, 81, 202, 70, 30, 70, 50, 25, 56, 249, 245, 159, 6, 102, 21, 85, 8, 94, 115, 88, 32, 33, 111, 138, 229, 238, 152, 198, 74, 111, 86, 151, 165, 232, 2, 13, 42, 228, 219, 158, 227, 203, 47, 8, 83, 139, 184, 165, 123, 55, 29, 198, 119, 78, 182, 200, 77, 8, 5, 135, 164, 82, 235, 210, 47, 105, 53, 186, 64, 197, 24, 14, 39, 161, 187, 136, 58, 118, 225, 162, 203, 5, 214, 155, 45, 3, 111, 126, 99, 196, 82, 14, 156, 165, 134, 83, 179, 5, 226, 237, 151, 0, 219, 251, 160, 239, 224, 133, 230, 237, 221, 233, 12, 3, 189, 28, 251, 245, 89, 116, 113, 176, 40, 210, 216, 173, 154, 216, 111, 254, 183, 238, 29, 85, 142, 189, 89, 235, 184, 241, 2, 99, 138, 222, 47, 128, 97, 235, 195, 106, 118, 196, 149, 53, 188, 70, 113, 85, 90, 53, 179, 32, 23, 28, 95, 164, 49, 61, 151, 70, 214, 245, 245, 117, 172, 75, 153, 117, 226, 69, 205, 173, 139, 140, 163, 107, 214, 18, 111, 194, 115, 236, 32, 239, 168, 62, 12, 207, 220, 162, 160, 13, 147, 252, 192, 145, 150, 207, 112, 196, 114, 88, 69, 252, 193, 37, 84, 103, 108, 32, 205, 224, 216, 206, 251, 185, 17, 55, 185, 112, 24, 8, 209, 184, 156, 65, 48, 196, 236, 45, 97, 65, 218, 239, 59, 191, 137, 3, 182, 135, 46, 142, 163, 39, 63, 219, 66, 166, 8, 41, 175, 79, 77, 134, 159, 149, 118, 63, 191, 86, 103, 32, 2, 239, 107, 199, 122, 148, 93, 252, 176, 112, 130, 88, 102, 225, 199, 89, 100, 221, 177, 118, 102, 77, 192, 224, 117, 13, 213, 164, 87, 91, 157, 211, 14, 248, 15, 0, 165, 101, 185, 228, 203, 227, 44, 157, 68, 34])

    @property
    def u8_3(self):
        return numpy.array([23, 5, 170, 52, 174, 242, 108, 186, 30, 27, 38, 181, 184, 103, 240, 129, 69, 179, 148, 194, 57, 7, 19, 111, 244, 86, 238, 36, 31, 44, 193, 106, 229, 159, 23, 70, 184, 121, 243, 215, 187, 115, 89, 141, 233, 105, 150, 224, 245, 251, 44, 148, 149, 123, 141, 9, 77, 17, 146, 157, 112, 122, 83, 50, 156, 178, 186, 244, 234, 165, 6, 223, 148, 48, 189, 46, 209, 30, 203, 186, 4, 159, 162, 97, 97, 232, 113, 178, 244, 172, 54, 52, 252, 32, 35, 131, 178, 21, 131, 165, 203, 113, 141, 3, 195, 54, 143, 163, 15, 99, 29, 235, 125, 45, 50, 157, 255, 7, 81, 221, 70, 225, 119, 220, 98, 55, 213, 23, 219, 152, 148, 113, 89, 236, 109, 187, 7, 80, 140, 226, 71, 34, 17, 176, 15, 30, 239, 251, 10, 64, 170, 150, 245, 180, 83, 242, 138, 154, 226, 193, 119, 43, 85, 164, 187, 73, 19, 81, 119, 168, 160, 222, 100, 230, 27, 237, 43, 71, 144, 132, 212, 131, 241, 195, 181, 175, 41, 115, 149, 128, 238, 212, 134, 110, 224, 149, 217, 213, 122, 200],dtype=numpy.uint8).reshape([10, 20],order="F")
    @u8_3.setter
    def u8_3(self,value):
        
        numpy.testing.assert_allclose(value, numpy.array([66, 135, 166, 109, 89, 156, 182, 63, 217, 36, 212, 158, 7, 212, 235, 154, 155, 52, 234, 220, 30, 251, 223, 77, 163, 204, 220, 63, 152, 39, 193, 217, 212, 4, 248, 69, 117, 164, 83, 149, 60, 44, 96, 78, 166, 212, 56, 87, 183, 20, 0, 32, 244, 16, 155, 4, 82, 217, 235, 203, 171, 188, 222, 15, 0, 109, 97, 135, 62, 185, 103, 39, 200, 198, 50, 190, 246, 161, 102, 32, 246, 11, 26, 132, 145, 141, 15, 112, 193, 105, 130, 61, 177, 104, 39, 164, 188, 131, 6, 9, 222, 109, 161, 211, 254, 73, 117, 59, 96, 146, 92, 148, 175, 82, 108, 215, 210, 4, 7, 176, 191, 129, 174, 224, 139, 166, 71, 30, 57, 246, 94, 139, 121, 190, 210, 181, 44, 71, 7, 118, 76, 223, 173, 181, 88, 138, 18, 146, 233, 135, 205, 101, 92, 222, 136, 177, 15, 167, 154, 198, 194, 185, 166, 21, 49, 193, 229, 153, 231, 101, 47, 40, 181, 138, 207, 168, 73, 19, 108, 15, 22, 193, 101, 151, 216, 153, 20, 140, 209, 15, 117, 246, 86, 210, 193, 254, 56, 41, 223, 107, 179, 130, 220, 46, 248, 200, 241, 173, 67, 147, 93, 87, 108, 13, 180, 112, 58, 210, 243, 94, 113, 140, 172, 53, 206, 186, 106, 167, 48, 43, 213, 157, 135, 243, 72, 173, 185, 62, 188, 162, 61, 19, 156, 215, 24, 216, 222, 56, 211, 151, 178, 251, 238, 47, 51, 141, 109, 214, 179, 41, 5, 190, 79, 27, 13, 208, 37, 97, 178, 83, 150, 77, 187, 179, 12, 73, 156, 167, 167, 106, 198, 157, 133, 80, 183, 15, 1, 204, 84, 250, 122, 232, 178, 103, 225, 110, 97, 23, 171, 88]).reshape([30, 10], order="F"))

    @property
    def i16_1(self):
        return -13428
    @i16_1.setter
    def i16_1(self,value):
        if (value!=2387): raise Exception()

    @property
    def i16_2(self):
        return [-31396, -31525, 21618, 420, -4709, -28067, 13158, 30433, -5226, 177, 32486, -24906, 14134, -12316, 815, 14221, 25078, 4427, -24570, -2404, 32275, 16625, -18211, 8224, 11466, -8053, 25673, -5521, -3629, -28951, 16888, 3476, 29692, -16313, -6124, 7022, 20178, 363, -26079, 6451, 26271, -9454, 7484, 9626, 18076, -32556, 8132, 22992, -22922, 21831, 9586, 30404, -24016, -22082, 17247, -120, 26786, -30338, 6445, 7710, 12192, 1787, 10373, 8221, 9130, -13265, -29233, -30762, 1430, 29737, 1503, 32216, -27766, 25651, 24365, -20157, 18077, -9909, -2427, -14841, -32092, 2606, -29807, 31676, -2674, 21400, -31068, -7881, 15682, -5497, -4695, -7670, -26719, 7180, 31393, 20250, -18099, 12591, 18352, 16854, 24663, -12445, 3967, 13535, -9324, -28110, 13977, -23172, 14216, 30378, 6653, 19203, 7298, -23065, 18301, 27111, -23775, -27934, -4797, 22319, -5834, -10073, 21636, 26423, 20007, -23826, 9433, 24251, 29231, 26264, 2698, -10085, -21536, -27028, -24687, -3768, 1511, 25182, 29258, -17177, 8345, 9571, 7512, -28872, 10123, -10644, -7612, -13232, 24346, -25900, 28049, -5366, -8968, 5589, -21840, 21891, 25327, 9095, 4382, -30532, -21172, -27251, 12320, 30065, -29933, 19371, -5654, 7815, -26289, 12614, 13834, 29357, 25201, -32309, 20042, 16706, 2312, -20975, -5346, 1820, 9166, 20644, -3811, -12569, -3711, 11580, -24719, 29072, -26433, -12475, -15326, 1071, 10750, -17120, 21953, 11265, 3513, 20747, 32085, 9898, -24426, -17231, 21523, -26126, 8783, 31762, 6629, -32554, 28071, 23409, -6423, -25261, -13387, -2606, -23878, 5003, -8970, 16999, -11501, 15402, -31573, -12730, 17823, 3018, 13959, 6305, -24676, -28537, -21613, 15353, -31686, 7264, 14978, -2702, 25179, 16061, -5220, -20419, 17023, -5104, -17836, -24537, 30832, -8236, 20473, 31052, 9467, 25660, -4882, 28392, -16236, 15059, 18409, 2709, 9637, -28754, -28261, 14474, 281, 24844, 25464, 26378, 8331, -8080, -10826, -3874, 21290, 1599, -375, 8436, -25280, 25907, 19361, 6448, -26639, -15164, -12896, 1476, -15877, 23427, -24851, -23147, -11525, 16456, -23417, 31519, -10431, -14222, -28958, 6194, -7802, 17086, -5885, 23977, 29347, 3648, 29674, -27985, 1834, 30677, -30455, 32438, -23495, -10403, 10370, 32713, 27187, -4733, -16686, -21336, 7793, 15123, 17046, 28022, -23346, 21816, 16826, 19747, 21625, 17895, -23683, -142, -27996, 6601, -13889, 24112, -19505, 24425, 11673, -3507, -9946, 20693, -28974, -30639, 25202, -24295, 27916, 5920, 17325, 29121, 12475, -1179, 5379, -21558, -8684, 7551, -8536, 8673, -13435, -3870, -6389, -26193, 13662, -17405, 3305, -15401, -10014, 6645, -9322, -15604, 7511, -8894, -2421, -21984, -12209, 16631, 19022, 11644, -3624, 25297, 6613, 4801, -17413, -12780, -28095, 17986, 11066, 22207, 17717, 3613, 14987, -19860, 12693, -13482, 10471, -24561, 32333, -25968, 7244, 7005, 17820, -18897, 13208, 16753, 32551, 21296, -15046, -3886, -13628, -2550, 16059, 1090, -27901, 21254, 21726, -17180, 5902, 30053, 31909, 25120, 3958, 18119, -25501, -4974, -11464, 24068, 19720, -8793, -9011, -11975, 7025, -15041, 21009, -15123, 3647, -28657, -7700, -10174, -16814, 4848, 13044, -20100, -17977, -29197, 31169, 15459, -27346, -23297, 1639, -27165, 25474, -4981, -16728, 24962, 6895, 16619, 12965, 10990, -13275, 1119, -10243, 10364, 3763, 3565, 31542, -22261, 15267, -31448, 13298, -8408, 511, 19296, 24390, -25118, -29033, 11413, 25520, -23675, -12986, -3952, 7133, 9587, 30652, -21444, 23859, 22577]
    @i16_2.setter
    def i16_2(self,value):
        ca(value,[-29064, 7306, 1457, -19474, -671, 22876, -14357, -18020, -23418, -10298, 1040, -2415, -22890, 4293, 25366, 12606, -31678, -15908, -11164, 20643, -239, -15149, 25272, 17505, 24037, 8264, -3888, -12405, -28698, 25222, -2506, -26405, 9561, 27093, 8022, 23338, -31489, 24117, 18018, 25324, -22192, -23413, -12544, -29675, -10752, -7108, 3021, 29238, -10332, -1818, 23363, 31568, -15057, 9565, 30520, 1064, 26637, -29070, 11149, 8534, -13775, -18359, 9626, 10662, -23713, 28470, 8840, -25279, 18175, 13675, 14955, 30323, 924, -13113, -21483, -6641, 12790, 26367, 27907, -1062, -24249, -13215, -18475, -11121, 2339, -2361, -7790, -26038, -6984, -10142, 8485, 17258, 6150, -25530, 9655, -11378, -805, 11574, 16094, 21091, -11882, 21514, 27655, -27624, -23592, 17985, 3154, -1292, 11059, 27599, -2741, -27514, -27353, -1824, -26419, -19633, 23008, 22184, 25855, -4965, -18710, -6802, 25237, -24262, 3253, -28401, -19864, -11711, -27668, 28671, -1376, -8600, -12691, -18972, -5265, 3901, -6694, 19018, 29612, 8047, -26257, 28662, -6164, 9407, -12556, 1421, 14531, 28000, 8499, 5512, 28989, -17181, -4051, 28130, 19063, 31736, -28399, -4663, 25520, -18490, -32156, -15267, 29245, -13510, 13446, -31039, 18030, 25419, 24594, 28348, 17845, -26123, 20713, 29810, -25881, -10534, 9038, -15614, 20117, 11436, 7078, 9985, -2758, -13790, 12865, -6824, 10924, -4750, 10127, -30953, -15114, -10407, 13061, -13241, 22268, 15514, -23952, -22361, 25465, -23395, -5885, 23643, 6634, 1768, -4390, -29064, -18261, -18954, 22866, -23739, -15996, -31521, -12816, -11246, -16029, 4113, -18809, -4282, -3892, -21196, 23692, 6488, -8949, 28859, 23717, -20358, -4216, 6700, -14565, 14268, -17978, -3865, 21937, 17864, -26293, -9181, 28460, -27725, -32278, -13856, -21763, 10310, -4066, 32078, -8132, -14677, -11698, -23123, -30968, -21889, -2192, 29299, 623, -26725, -29380, -18038, -25037, 26361, 22773, -31157, 22096, 10336, 26530, -74, 3820, 52, -28257, -29110, -29891, -23752, -23846, -15516, -21528, 14792, -4286, 26942, 17922, 21495, 16249, -30305, 3056, -22525, -4198, 28613, 2695, 30388, -18066, -5162, -23655, -25604, -28244, -1196, -6888, 17903, 11721, 13555, 32445, 31800, 11125, -31537, 1400, 25992, 2289, -19330, 29486, -27986, -6690, 9402, 15366, 18268, 29476, 27543, -26894, 28279, -18810, -14493, 6622, 9548, 28691, 30421, -17983, -25525, -6167, 5825, -25283, 19498, -17719, -3858, 8518, 16017, 1325, -16864, 17874, -796, 3678, -32078, -19712, -32173, -25895, 27397, 23474, 10508, -6009, 25388, 17327, 26954, -23909, 27502, -15956, -1770, 1343, -30108, -12923, -3584, -30762, 3386, 18090, -14048, 31833, -5312, -32483, -1358, -28372, -24388, -26718, -17132, 22775, 16924, -8991, -12343, 16874, 19515, 21977, -26287, -28976, -18071, -24572, -8740, 29859, -21779, -20087, -928, 31016, -11442, 16890, -12445, 26140, 23581, -18737, 16033, -16426, -27860, -4853, 6669, -2678, -14760, 15011, 25458, -24354, -4704, 1983, 20655, -3885, -6015, -20382, -6168, -8801, 21318, 21969, 15333, 26667, -15860, -20356, -4265, -19871, -30123, 8082, -5186, -5294, -7119, -23580, 600, 7195, 24630, -9810, -23846, 23416, -26102, 11875, 25362, -17002, 32482, 3733, 8434, 18377, -11770, 21843, -19779, 27194, -16918, -22013, 8387, -1686, -27228, -8013, -12979, 30682, 13008, -32188, 24547, 27126, 12811, -14996, 16305, 16467, 21204, -16620, 20671, 31564, -23123, -31995, 6335, -26234, -8852, -19185, -19636, -15411, 22541, 10295, -14022, -19669, 25371, 4407, -21395, -20754, -31164, -30944, -29004, -28877, 11049, -11492, 30171, -3452, 20020, -30618, 11178, 7734, 15658, 26485, -8697, 24391, 14520, -9994, -11594, 21221, 21327, 22058, -6275, -2272, 20061, 11315, 26569, 21368, 30729, -15573, -25453, -6160, -20236, -29377, -22591, -11045, 19992, -18369, -30261, -32159, 27646, 18350, -6134, 6723, -13437, -23761, -22496, -12447, -1184, -17634, -20936, 30815, 32042, 10621, 17252, 9705, 4169, -8075, -20113, -21095, -20310, -3917, 23438, -1628, 7291, -18739, -12603, 22036, -14198, 26960, -24387, -20204, 1370, -23683, -27522, 31684, -24806, -20567, 606, -14584, -5656, -6025, 20297, -18716, -7075, 21089, -26036, -2747, -18800, 22214, -31288, -31916, -32543, 14577, -6407, 17079, 4683, -29301, -13707, 4296, -2247, -25994, -322, -26904, -4444, 24454, -9676, 29589, 30545, 17995, 20596, 24835, 24545, -15782, 13901, -26644, 4655, -10543, -24521, 30118, -29985, 3163, -27379, 24263, 19271, 12184, 7695, -6249, -26163, -16952, -18930, -22627, 5625, -16862, -29626, 8000, -26542, -21846, 8377, -6837, -30324, 10752, 19676, -31224, -11472, 27419, 4926, -67, 7107, 3149, -18440, 18652, -32124, 26094, -7015, -10179, 3878, 28709, 4453, 20330, -27548, -18729, -7550, -29815, -3110, -14705, -16383, 16020, 15466, 5411, 23434, -14919, -1289, 24403, -2409, -28824, -5982, 21794, -26131, 11683, 28742, -21742, 7952, -9041, 28373, 12434, -17665, -19141, -31576, 650, -11103, -26587, -17144, 20830, 1468, 23981, -6189, -1574, 11151, 9314, 12189, -19801, 23310, 3132, 1145, -5231, 1387, 3230, -15314, -17253, -29867, 22979, -28009, 7686, -31739, -16295, 23702, 9141, 18300, 31485, -11124, -30999, -26289, -32371, 7900, -5057, -8202, -15209, -26424, -2712, -25152, -7174, -25019, -14712, -10703, -2809, -9, -17905, 20882, 31301, 8989, 20139, -235, 707, -23246, 4519, 5621, 9609, -10846, -1873, -17425, 30184, 23010, 18718, 24429, -2168, 23884, -19503, 9419, -24927, -16803, 11872, 16572, -30227, 4356, 18692, 3493, -29119, 16296, 1632, 8736, 7806, -13904, -26360, -27538, 6861, -8093, -6184, -445, -2181, -9581, -2722, 22857, 4100, -2585, -25935, -26353, -21284, 7497, -5385, 10974, -7747, -19865, -1205, -12806, -7505, -29792, 16793, -2743, 30123, 9379, 17381, 4947, -15940, -3652, -1797, 21012, -10333, -27953, -1716, -28455, 29598, 17497, -5363, -3990, -29921, -27210, 8825, 8046, 11062, -13647, 29708, 1335, -22559, -28213, -9634, -17768, 32543, -15641, -18576, -23375, -25305, 11930, 11338, 28057, 12085, -17504, 29366, 3513, 26451, 29229, -24338, 1541, 18497, -8424, 12969, -20692, -24323, 1876, 8233, 10893, -10761, -3855, -21938, -6268, 32120, -25120, 20729, -371, 25746, 28224, -25625, -22924, -30667, 13100, -3160, 28610, 2206, 977, -17607, -2173, 24212, 14451, 22276, 26268, -10890, -23818, 30052, -18695, 14828, -16839, -18543, 17056, -3715, -7372, -16029, 31885, -20617, 10847, -12068, 29898, 12865, 30922, 17546, -8489, 19324, 584, 9798, 2421, -17432, -10905, -14728, -7920, 6909, -11895, 1031, 18387, 20783, -28969, -535, 31095, -30709, 28734, 15322, 28585, 2100, -6234, -28704, -2813, 22201, 16682, -1576, 9351, 30508, -9447, -21309, 3023, -19963, 13739, 8398, -11148, -9348, 32285, -22925, 697, -9683, -1106, 11252, -16321, 31326, -22577, -107, 3355, 22765, -10391, -26902, 10375, -2846, -21378, 2649, 1284, 23016, 6884, -5356, -17352, -9866, -4313, 15950, 12058, -32753, 6124, -9833, 8828, -11711, -28691, -31249, -31354, 13039, 29161, -17382, -5879, -21118, 11736, -29024, -15440, 9364, 28121, 16093, 20123, -26504, 25957, 11858, 9932, -11333, -15770, 3678, -18107, -25852, -21244, 2225, -13899, 2050, -21656, -7352, -3896, 4161, -27416, 12792, -1807, 18088, -9590, 1851, -11661, -28665, 10986, 18137, 22612, -1617, -11139, 19293, 4080, 8597, -16998, 17228, 6587, 12316, 12640, 1001, 25972, 29637, 27715, 5577, -12737])

    @property
    def u16_1(self):
        return 60981
    @u16_1.setter
    def u16_1(self,value):
        if (value!=54732): raise Exception()

    @property
    def u16_2(self):
        return [28720, 34616, 62158, 23483, 4737, 55943, 56769, 39984, 64598, 51111, 51377, 21150, 23557, 7441, 55455, 37627, 34814, 32887, 12525, 7947, 30317, 19555, 62568, 26666, 35231, 38385, 56455, 37676, 47722, 60644, 1037, 61159, 64542, 21655, 57027, 46262, 64919, 49927, 25520, 56784, 4424, 62463, 26885, 43771, 5149, 7537, 28615, 2661, 41921, 63221, 30209, 37930, 9683, 52406, 24968, 50022, 51469, 57731, 65408, 57019, 62539, 10550, 35726, 34413, 46756, 63743, 50854, 1075, 36709, 52737, 38989, 14194, 10541, 39864, 7632, 6335, 37317, 18084, 18417, 13903, 41588, 4410, 55813, 34564, 62937, 56211, 51771, 32961, 36295, 58221, 4107, 18571, 55106, 52625, 36243, 52487, 10236, 36619, 24439, 41204, 61791, 12156, 5380, 26272, 45613, 37851, 60070, 38759, 33502, 2147, 28146, 45977, 51698, 33640, 38956, 48664, 51750, 42329, 6020, 42645, 44393, 47459, 64398, 2683, 18251, 5304, 38780, 13706, 58825, 12565, 37762, 21280, 39402, 56275, 25627, 41371, 39366, 61829, 8892, 26779, 311, 47322, 26823, 8265, 12495, 38802, 20059, 32724, 7618, 37557, 57579, 33492, 20655, 19185, 57872, 51794, 16721, 52071, 52584, 57226, 28584, 9690, 10117, 41708, 38496, 56164, 53099, 45246, 34962, 41133, 9780, 39381, 53780, 14719, 64870, 38034, 15484, 24376, 39802, 58424, 52906, 45995, 50396, 21981, 32813, 15889, 33981, 58999, 48157, 23717, 24644, 18059, 47204, 45872, 26705, 46193, 56697, 41192, 56316, 43920]
    @u16_2.setter
    def u16_2(self,value):
        ca(value,[27153, 43996, 41432, 58304, 12942, 58876, 28186, 11185, 10827, 17769, 13091, 23017, 17671, 49113, 6987, 35547, 2024, 33499, 26956, 11772, 20498, 42863, 65021, 31883, 61940, 6622, 59235, 6137, 51350, 48773, 57425, 56027, 38431, 12927, 54445, 12445, 27087, 33727, 51305, 48371, 7488, 32356, 59057, 10185, 57955, 46571, 326, 43692, 43661, 25990, 42979, 8957, 59425, 9205, 42414, 10752, 5573, 37965, 14726, 60329, 24708, 38900, 13804, 12531, 19400, 40437, 3102, 15384, 9922, 48890, 655, 58588, 55933, 56542, 20001, 11584, 62303, 19888, 38565, 19636, 21974, 26170, 61468, 27655, 30144, 38002, 59044, 33839, 58996, 7516, 41660, 26146, 20606, 9052, 41933, 43479, 45221, 37564, 60731, 9073, 5647, 25184, 21426, 47334, 48473, 57336, 38775, 56475, 55863, 33194, 59184, 17109, 10792, 35915, 37682, 18123, 56383, 55538, 26718, 29128, 5521, 51803, 22632, 19827, 32242, 38280, 51359, 10800, 22661, 63621, 58920, 22073, 59845, 56670, 24860, 21801, 22225, 45849, 35453, 38351, 58831, 63677, 49340, 58625, 59284, 8244, 22567, 42599, 39629, 44023, 55480, 23933, 54557, 36080, 18074, 53598, 26233, 46291, 10356, 982, 20899, 9791, 43246, 40308, 38630, 40376, 23805, 35194, 45957, 56662, 38493, 50650, 41811, 40225, 20212, 10975, 38947, 14443, 62213, 16366, 55641, 20063, 28304, 34336, 48695, 11196, 20382, 32670, 61020, 27154, 60750, 42124, 64065, 45687, 32335, 60310, 14344, 39059, 31190, 12119, 57101, 13774, 58824, 54012, 32689, 12347, 13368, 42262, 15453, 61631, 51804, 27658, 53000, 30414, 42427, 61957, 16811, 19230, 23527, 24728, 60773, 28925])

    @property
    def i32_1(self):
        return 898734
    @i32_1.setter
    def i32_1(self,value):
        if (value != -9837284): raise Exception()

    @property
    def i32_2(self):
        return [-461364931, -881174363, 1190512124, -652344200, -1904465790, 654215830, -8237446, 1554134258, -1171405181, -2097329372, -1168547037, 4964041, -162499187, -1566779923, 396658647, 1372847452, 1952977117, -2055030887, 1369558008, 1159869637, -151488968, -1230916956, -1662654082, -692556634, -2108882739, 1919783279, 86726599, -479175753, 368307099, 263085896, -1297854452, -475865862, -1052798892, -195216089, -1808717864, 1435851230, 213845163, -2014435943, 1958739019, 1950538379, 195043354, -2094251280, -552928187, 212026163, 1882789473, -1701156512, 700729029, 617009319, -51379635, 1437981860, 143582562, 1759700160, -1043283958, 790685144, 1053455552, 888961142, 1884764193, -574487120, 205387093, 1706716858, -1564706331, -1119162850, -320357115, -216356729, 1133115157, -1585595150, 1163420546, 2095530513, 959051309, 1266503031, -1940662617, -1207768369, 2071048923, -247500208, 729695364, 1732441574, 919515230, -1307758899, -1362232635, -985845056, 1183002178, -967666429, 61839483, -797969544, 1019207261, -2080745651, -1493399698, 448039065, -1006260032, 547484182, -433873666, -145482008, 1266128764, -374269118, -148627528, -481205875, 28560825, 1620567461, 160877005, -152736921, 566726869, 1690610724, 1551218429, 129384906, 1756514951, -1619123979, -1635458102, 461420293, -1025697720, 1074881682, -1342853402, -2024581138, -1021476707, -979756855, -2061951658, 495595484, 1072057242, -1075816975, 634930689, 1462757877, -355459145, 113806554, -1586994022, -1759236007, 1642313755, 1844726616, 263774839, 865591847, 1137711548, 568540382, 1697402204, 1287333602, -18557107, -543522023, -747044673, -894978937, -1633590316, 1469569043, -1916659051, -245350462, 558791729, -1069756095, -1671183103, -675709621, -1496240619, 1002596182, -1049603233, 1067628357, -320684962, -1756926613, -1978637534, 2115134917, 293851213, 188870457, -2033713174, 316694162, -1680926305, 1578104820, 2019431451, 1672278268, 518272185, -366138444, 1261822504, 1003789835, -595796762, -1764183978, -1066900678, 1415600408, -173332206, 341584118, 1836086928, -77555270, -1989963843, 428500682, -489840295, -1096671034, -1915424250, -1746745758, 473428620, 1155878488, 1534484342, 1866809635, 2125417205, -356683367, -724519561, 476765866, -509611460, 1067343485, -1663160103, -1973204454, 1891962125, -1486851183, 539703058, -78175960, -1038870474, 585234261, -1015599511, -1860840029, -1939494917, 2120890829, -1396051426, 442584714, -559475888, 1852553473, 1370937853, -189979498, -1942748392, 575014321, -206759426, -31154557, -2070305927, -1863241823, 976830155, 405210820, -1810403626, 1246769487, -1690543149, 1313271912, -351123144, -169833423, 329135592, 1471013659, 1018659812, -1227714342, -191860948, -1335651686, 883360682, 836140176, 533570354, -306737045, 503171813, 1574245195, 486740175, 2103577114, 1369514515, 631086314, -1519000748, -1651625120, 2072505877, 343400009, 1919137338, 1103988337, 2071554186, 150773570, 2097705645, -130202734, 327475069, -884235865, 52111222, -1080547500, 682409781, 1559839293, -1958998234, -668500619, 1652828958, 1898194722, 1411170984, 2027809940, 2057915321, 624976316, -1590230095, -39277437, -399063086, -199887533, 1695889089, -179411470, -814891514, 441001215, 228328910, 1969824685, 1673102538, -939256124, -2021849575, 1292458519, 1963232860, -701199322, 1898059105, -2045458245, -896773856, -465102206, -1132267068, 1715928377, -1576771507, -76241412, 1187144803, -1067322651, 570283207, 1328683328, 1679817753, 1351131251, 218112167, 1288274663, 1769551475, -1459879021, 907399627, -129113618, -816814174, -281922806, 1308242407, 959061391, -643658909, -1586885260, -731576338, 872407494, -1435528398, -978470065, 561011867, 2094464646, -1961457104, -370593344, 173444003, -1787659154, 1403917210, 1314481998, -2064760703, 627159779, -1209896425, 950681678, -1599356229, 1797678336, 1407713282, -1860763990, 1818135625, -797982794, 1766490463, 146950743, -573489171, 541336457, -786031692, -823206893, 472702619, 301835709, 903962039, 334036788, 1308489144, 1982571588, -1297489003, 1027291239, -1050223998, 1301065587, -131811840, 840706119, 151612697, -1514662009, 2045477247, -78244632, 1428738052, 999845946, 632205998, -2084777797, -1263080892, -1527740973, -1052672864, -1148385231, 2118437588, 64244951, 610247700, -192213951, -1677840790, 695619117, 194487568, -1064818224, 567953693, -556351633, -358984117, -543035561, 1299534234, -1814192015, -1987974286, -251589327, -1550216573, 1039391427, -648231381, 209808513, -1809205905, 425289643, -1478441699, -499830484, 895438284, 1388891777, -141187536, -1921173432, -2109700894, -629643543, -1992180854, 1262181466, -1000112113, 1891981448, -511356474, 678112000, 231308715, -845426086, 2065931343, -690231821, -2065441467, -497137258, -288817447, -272642500, -1778307241, -206926623, -1058833162, 1207480823, -577760388, 967667904, -747757357, 1515713516, 1901169583, -43384102, -1869097267, 698722931, 1723948263, 895747277, -963077288, 2007160291, -1139652897, -1941673179, 1182316407, -1504345279, -69517474, -1337091986, 1144745436, -295343637, -368530206, 423117467, -1160707313, 606107242, 973575490, 782358427, 1225701496, 1354180679, -1819084457, 210496900, -1607248517, -100403486, 357128435, -1211000784, -1699635523, -1995757335, -2041727997, 1639346630, -1140917407, -1428441321, 1391552530, 950439976, 1536850187, 1755763383, 349315024, -1716747422, 1788059719, -956787148, 435093165, -519717781, -1185043774, 1326150846, 666841562, 977518902, -1878116663, -1052216208, -159814671, 545626237, -1161390691, 172913262, -1143147285, -711220581, -2073758388, 1347605160, -274461216, -1138600943, 1812589913, 1321776791, -654185814, -514865093, 342576025, -1227661029, 2027182643, 499090278, -1057042386, -1200362684, 1633068952, 1127338030, 66338457, 1655244407, 1091076049, 1868857534, 1902975017, 427968982, -689633450, 1869590905, 828919724, 374348665, 291496172, 369492724, -1956000730, 149774736, -283502913, 542857976, 1810830261, 1711344293, -1158072113, -1788295198, -314318981, -1029216204, 1180472328, -769273193, -1884508206, -1558495607, 19086583, 2059341589, -1133755497, -2103950715, -353373479, -330597102, 146329926, 1139012057, -1595155154, 92242787, 1758776536, -2142059846, -1016391823, 572794885, -1164070685, 936895954, -530252487, -852015578, -1387262267, -610552571, 993685216, -2060482368, -54855358, -1368415548, 1727532083, -1998919251, 1004938093, -193604754, 402127614, 15533913, -822374248, 914869992, -398825428, -1951818825, 1024562104, -1513050369, -1086194365, -1602294388, 506250848, -450950473, -1107350963, 724811630, 1667267553, -1296578611, 1797492484, 1593191271, -797438732, -1327763127, 1815794923, 968830944, -1597687229, 453031735, -311267208, -1363949093, -680526092, 2111164100, 1874373703, -737231277, -1941054345, -1943683241, 299275156, -777764717, -1580845667, -1590831315, -706883071, 1006664100, -455650726, 405499155, -1557738572, 1434435376, -476662082, -390599384, -1023097080, -462139722, 1416922513, -1243778374, 1721356353, 2052478481, 1576465185, -1753145409, -1866886190, -709091910, 1188370346, -47903041, 833750418, -714362080, -1356224125, -1264932342, -2019192812, -1865286029, -872940604, -1103730145, 960420100, -1042876502, -1376735106, 652488617, 265536834, -727122450, -1304252301, 1452309463, -345462904, -1385578434, 1005791488, -1952157450, 1535232809, 1539175065, 1764693654, 370125766, -1202518768, -1045824063, -1277351352, -209760871, 745809202, -969253860, -263968717, -1987049520, -994220477, 1014895379, 767424874, -1455749768, -1031331847, 102844430, -1853475234, 1375464119, -36893052, 738438714, -2023227099, -766955665, 917641510, 2098209786, -1217824087, 1658975849, 519874226, -253260859, -1162718483, 1786747123, -1141951794, -2107503630, 454499128, -1967565552, -1023321135, -1996284503, -752431392, 472701630, -1632851902, 410108660, -1046454863, 1967316776, 855860213, -1312902400, 2040315518, -1117439624, 493239897, -1998091182, -2034474271, -1097999735, 1318127173, 606300235, 1842233668, 575662433, -2004034017, -453132858, 575442626, 312602259, -2052800210, 1864640938, -1558226144, 1723181891, 1563560258, 1335087794, 1484455993, 1617896015, -1725417335, 1319720221, -1761963217, -699139792, -1289651408, -1107156983, 1743906484, -4909723, -1308860494, -1458950358, -1346838156, 770842123, -2015270071, -24732450, 1317412484, 713576473, -367369916, 1304052776, 249082034, -1501300599, 440635569, -1918514505, 1703744454, 1979510875, -1459719502, 2080733946, 1591601168, -1279512428, 1050916259, 506633589, 985141457, -1785288990, -264273336, -929708322, -719186799, 821741784, -672362448, 552181928, -802373915, -390543422, -343050866, -1958288614, 898584575, -2009826787, 695541207, -490634204, 1677702760, -881113644, 949838036, -1754707531, 1625802700, -2116565724, 1986923158, 755539119, -1478875610, 266787239, 1794560040, 1005034935, 1558408357, 763790383, 677517420, 2072139195, -235728628, 1725705385, -1582053707, 1113461586, 1674642759, -1414719663, -608468252, -1873260761, -1401304493, -1029303396, 1873534265, 912963743, 645715337, 1132031991, 487696799, 1110621999, 1383752223, 1018103642, 536280867, 1764666589, 1624759145, -707782673, 1407012132, 1887436609, 568473975, -758524638, 1093808445, 330404853, 240981075, -250484760, 498674002, -1126343191, -1070540555, -17257403, -1302522037, -1500566183, -706742387, 1731391627, -121892623, 1944180, 697150366, 1175869801, -1081726694, -772936078, 300113930, -1519743318, 1011619084, 966435032, -271530967, 1478437384, -2000885569, -1625488897, -30409891, -577640443, -491669659, 1721990364, 464531779, -1035520457, 1234811766, 58268492, 761680308, 338102126, -1281454585, 1554633851, -2008859178, 55616722, -2039496630, -902950403, 673529549, 1020509295, 1518665847, -478044459, -296723364, -2075845731, 1809506854, -99500436, 883142933, 289332182, 738556337, 1501633470, 2058318873, -346819242]
    @i32_2.setter
    def i32_2(self,value):
        ca(value,[-966485083, 547919123, -1194190604, 1550099195, -86896479, -1346998266, -111775936, 1595883280, 95277373, -483593724, -1194231658, -1664247993, -1125879490, -774112094, -908971354, 1257430739, 278831106, 2146175077, 1216734947, 108534888, 712376825, 472415212, -413092215, -186896831, -983274891, -814159203, 491332674, -1080086896, 305863740, -588641755, -1173634854, 1500595228, -1011735210, 1396816521, -1843412764, -1174697157, -2042333138, 1720132956, 1179474025, -734588992, 1928960553, 653905969, -1152761709, 206317133, 1066603916, 1788908206, 1901091544, 1610435338, -1051581785, -1953636422, 1076388567, 1462395490, -237116033, 454691362, 1619801391, 1845599647, 1868321380, 1723200218, 766619638, 105371815, -877177590, -1885723170, 434710859, -1146593520, 209995917, -1047842747, 465673729, -2084508649, 1968279245, 587205365, 1583233886, -1752333729, -114021301, 59161723, 1580036234, 345745650, -468378351, 245003371, 1673787261, 1587452615, -1303597866, 822157520, 64527339, -4281296, -64380840, 37142322, 500059241, -1469346913, 11916922, -338760031, -2025817128, 83726551, -754215578, 368103720, -821582629, 717962460, 2144471201, 223671109, -199755353, -841621639, 1540857720, 1804628518, 2118963299, -1595232224, 400238135, 933224750, -215585205, -985264044, -988901458, 986847698, -1856650438, -651146661, -978168494, -532172509, 1691932093, 1876106029, 525396768, 1743090554, -162073951, 806798458, -1403694340, 559542160, 207806919, 590536881, -1650417281, 1858408059, 1983218923, -1543131382, 1706115652, 2119926306, 1424134413, 1205448675, 1811525641, 861875958, 2007619106, -845489490, -55633190, 1816674890, -614507920, 286578932, -1342898663, -1261324825, -1506404786, -1806499804, 1974771054, -98303714, -290587554, 1090231453, -985937256, -839357172, -1416681172, -1007624128, -1578990962, -1728169897, -844916635, 506302833, 667662716, -663874058, -1362455403, -2060230793, -1319792032, -2017894569, -1689519196, 479605380, -117340189, -1052087080, 1498560347, -870303564, 1098382715, -2086046098, -1642542296, -628648039, -719920250, -2060321401, 525438216, 281529006, -459505556, -1796557506, 1024549346, 1853853925, -312303325, -1579857332, -1269984071, 473304768, 721731410, -1737559733, -438494623, 1802127802, -1731233704, -1390726345, 485787940, 943002107, -187237495, 1869312126, 442020547, -87826467, -696183927, 616713843, 945472556, -972856985, 151686386, 1488133092, 175341883, -1180397098, 948926458, -503479659, -1267580010, -388943415, -1363469783, -1527776457, 268299441, 191219066, -1024035842, -1475980660, 1828759673, -1442955646, 1790351422, 574018056, 1803848768, -2095818881, 1210053959, 1551296999, -942626269, -1321443296, -1859662526, -2071020753, -1184904851, 988848078, -412054768, 1493935320, -196557049, -704875093, 134497249, -1224190928, -2068208534, -965095455, -564081208, -1156543555, 461090533, 701882132, 910649700, -1878641070, 1446533896, 1970740772, -204663013, -1698033554, 972688594, 1110078968, 810548960, -1509538061, 1958800693, -543420990, 217640235, 1880493927, -1671735529, 1137613142, 2072545208, -414851757, -1785997391, -364718164, 450315208, -993471993, 768175939, -1566579292, 85961510, -1827000830, -1893503205, 869202084, 713571555, 680257288, 1524440291, 1741022434, 561415328, 1990319608, 1142451744, 39401847, 1221297801, -2124038766, 1215377498, -2068455826, 560063055, 383922313, 7329552, -1417241590, 1973186515, 358937975, 1808732034, 894888594, -1620703934, -1409454021, -224706429, 631015427, -701827114, -1980442971, -1243431585, 1865483925, -1340041763, 259984294, -1443453841, -885229413, 973067512, 780961235, -282514052, -1110338800, -722213025, 1714985605, -1287879595, 1509400751, 324286798, 1011968175, 1774625427, -335835050, 1241953488, -485251005, -2023480468, -1498664236, -1676758135, -2078759270, 368391173, 1770332091, 602035732, -1157125163, -726848951, -296396612, -418101410, 1516209091, -433026570, 2065899179, 286245383, -1428168800, 310716072, -563791242, -1325785953, 1826452534, -23905747, 1034013849, -1085065618, 1611085765, -60799609, 1082236453, 561831452, -1827984069, -277941810, -2097393299, 1609593516, -1947366285, 2039786925, -2039232768, 986451997, 2119304777, 49748214, -1530450382, -588012225, -142349556, 1234615466, -1482467714, 728929313, 438851997, -424861037, -1835013005, -674124377, -1634348548, 1081331853, 2111035427, 143997944, -1158230701, 4815417, 2122369877, -77009634, 282329472, 2124624001, 1395262123, -602351149, 1496495731, -522090375, -1089014497, 1060099030, -514142834, 624755360, 101709947, -259648574, -1721466978, -1470128315, 1344990842, -2138737258, 101466176, 1692425055, -1157926775, 592741389, 1813083585, -769169250, 1770253928, 1208684737, -702112980, 1001273019, 1705993099, 1407346099, -2142523547, -1355363485, -267899641, 449328343, -987691219, 438101969, 572223309, 379113218, 1466899667, -623010689, 2125548615, -145443483, 631502783, 1728343290, 1277749965, 1997442958, -1429886186, -537022197, 763891225, -1238739363, -821719020, 940172257, 114964281, 2090254185, -966856290, 1594918376, -1912990965, 1325705675, 1909184548, 837435170, -590257590, 1748272543, 65934393, 2073600222, 170572472, -1901011521, 2133543824, -1551997487, 1825478098, -941111977, 2081346119, 1276024247, -1737235139, 1172151357, 1861822828, 2017860579, 2079359170, -712881259, 353483674, 1081877284, -310138121, -1387900910, 1509477224, 321767828, -334162604, -1426416668, 122601289, 900426562, -1974038173, -187934215, 1716122553, 536633084, 653559614, -106459236, 612788932, -426096009, -407044580, -231495552, -20598604, -1049988598, 1707164387, -907341708, 1018148334, 420273830, -717817139, 746522674, -1091234728, -769304365, -1783917863, -1773360712, 1421244394, -1489877988, -1400774353, 704671809, -523850319, 107160908, 2024605373, -799692707, -2092464355, -948361722, -1132761744, 429369122, -76789764, -1551036156, -1351725409, -11045966, -1316255914, 1121595316, 1364255025, 1812124631, -1134809617, -1230048918, -1823006270, 103013418, -1985924618, 1276352832, 1604221273, -237209206, -1822616069, -1899068745, 1297703890, -240045011, 810578223, -1422419765, -1418704599, 1034032605, 2085440174, 607645733, 716362365, 1235513555, -1211579413, -261155896, 2022908495, -146539076, 1167671484, -211945140, -268072629, 40741212, -317939085, 728869511, 1342184697, -522128634, -716993901, -885638830, -1889540956, -518758183, 194076888, -263047735, -53295197, -2039369321, -1402107402, -1232069700, -860885703, 667080371, 2003791013, -1792537425, 593890515, -302918528, -371191726, 915728277, 1775934623, -1884658077, 1983888460, 298800478, 1016157169, -1717781878, -1076292572, 1732073196, 542964773, -773239025, 1070547456, 1719362726, -1490080193, -1399780184, -58541011, -1591258, -1250990694, -443129975, 1822357515, -1774941626, -1423917059, -1324183435, 1247654078, -785941226, 208759350, 1371670412, 1903510098, 2128083745, 435649658, 1127890999, -1861063799, -188564302, 1199643492, 1891452416, -217657738, -67141750, -1266789415, 2131626424, 2098938511, 1874390421, -1698831352, 1922731129, 1143118810, -2026197630, 2086052126, 842500141, 287962959, 850955114, 2012362088, -817258418, -1072214227, 978057684, 992062798, -2041866817, -1611489850, 1663409654, 112766564, -1689406122, 1616786320, 556057860, -1680102493, 867719167, 453575899, -191805706, 1712061526, -744377824, -615870979, -1980362202, 1649307499, -613527529, -514007552, -354868527, 740361284, 1191787483, 1421727561, 1066283904, -452434665, 2020141000, -1987374530, 412400833, -621803967, 20900810, 559102704, -443346658, -768206607, 1402289809, -1479041896, 1359182666, 84692384, 1919671125, 1665432592, -1427511811, 1351138729, 714150331, 1584608034, 1063897075, -470363603, 1537682572, 760337828, 270984358, -1339485809, 467876006, 1515737109, -2141726672, 1046916347, 1259950801, -835983188, -2073384503, -697440699, 1343223043, -1288734811, 27645887, -1066885181, 2063044057, -56607701, 319902811, 960858771, -423030408, -812161836, -1112301146, 132484238, 1783289397, -2018957458, 450584409, 1012115988, -2101400823, 1667035362, 1107203875, -1865977929, -723361763, -1343871789, 1135679266, -1675492453, -140706303, 1364740541, -1551211173, -2009393394, 2000971427, -344052593, 462623413, 143090848, -1640955654, 1157518396, 659813664, -165571783, -761091080, 1439584252, -52830785, -1885945630, 1884406245, -555522218, 1323853722, 930747959, 137706091, 555548831, -1337759477, -1009674506, -1977870785, 1180081172, -687421630, 194151065, 1311924712, -866937125, -137781558, -698706859, -1895205467, -1848499551, 1896490516, -6509636, 1269553250, 186532024, -955818569, 1845517066, -400727025, 1078611153, 863814973, -1229137047, 1718754324, -216510561, 1988750453, 29465919, 1428890551, -62281515, -937668540, -1508270436, -927907488, -505451885, 1033857489, -389957828, -2065486196, -352295525, -2105963968, 1299134698, 816779483, 156423679, -1354381381, 1887465750, -2105822745, 642600242, 1123616314, 188710252, -1703216607, 1459661161, -1941560289, 601336479, 1863482085, -857985266, 794305967, -1660447453, 226783646, 241199673, 583367867, 849630317, 1914170489, 565711020, -1488638620, 609086194, 1720536967, -1694564352, 692492707, -1506800749, 730802235, -157471351, 242744029, -164780657, 554729192, 826406260, 2052603794, 1509424364, 880799424, -742089480, -1122708577, 1850636033, 1672099719, 1908731732, 1738334895, -2040611202, 1682998097, 1398609974, -1324949149, -975919403, -1450888087, 1833224637, -619514125, -990582005, 1412067944, 886169183, -391523199, 607372595, -1262130460, -1519841199, -1773159746, -1708684329, 1508540061, -445129927, -861216001, 449901651, 1557438209, -1188736704, -630147206, -679376511, 1198115538, -382787307, 697875997, -22939436, 239787497, 500731101, 195546534, 1392914720, -187209041, 455847608, -2049957759, 766204445, 1368826958, -2042625013, -180992444, -713812831, -114800611, -607409323, 162793232, 2138008530, -1531267188, 868044052, -1630059848, 1621859247, -1597211643, -1129166747, -1199701638, 1770783044, 36166445, 1439401965, -994866018, -960772827, 2001685784, 441293150, 408861924, 905891633, 1537313206, 400637893, 61265814, 1571963795, 838433145, 2065601099, 778646834, 316955585, -2087195141, -1175880744, -1556081321, 1057881099, 261925029, 1208410025, -1666750702, -1564870443, -1780046839, -921180273, 1249930686, 22741986, 1111587522, 1806539596, -2004101869, -1217186294, 1838807150, 1025186692, 1739799205, -970775152, 1248070355, -507661275, 1255915477, 227039459, -1806354804, -1933273622, -1702447540, 998405321, 1478470466, -1376315847, 30712562, -2027352328, -1528293401, -1983304959, 504320567, 1291680060, -1444744047, -1127727805, 1549237293, 1204875828, -290551371, 1890491263, -60192594, -338589164, 520299155, -1570639410, 1365342605, 717971876, 2100041137, 950014485, 2111827591, -1614588413, 1565446784, -711540009, -612602607, -1878381653, 759406734, -1354242425, 1036377793, 283764256, -147639272, -280351513, -314754805, -993828539, 998353033, -1202064568, -1057618001, -395391049, 1549721165, -598972723, -982907535, 1557165381, 1891640427, 654353458, 1775642645, 935383528, -1688413182, -419838142, -1817002350, 1500587707, 439484714, -671255505, -1446765092, 1379929086, 284924340, 322973021, 517663367, 1269409562, 1635098653, -456602725, 216521789, -390880857, 22702718, -141949792])

    @property
    def i32_huge(self):
        o=[0]*2621440
        for i in xrange(2621440):
            o[i]=i
        return o
    @i32_huge.setter
    def i32_huge(self,value):
        if(len(value)!=2621440): raise Exception()
        for i in xrange(2621440):
            if(value[i]!=-i): raise Exception()

    @property
    def u32_1(self):
        return 547919123
    @u32_1.setter
    def u32_1(self,value):
        if (value!=1550099195): raise Exception()

    @property
    def u32_2(self):
        return [4251946440, 3334867394, 1627635129, 2588419147, 4174027116, 3897125158, 80443814, 1389733726, 4117149812, 12542280, 1256007817, 1703348194, 4237384057, 1454512978, 2775061970, 3298540861, 3715621276, 2362002640, 3636980763, 3430743390, 1830381203, 1507092396, 4142499824, 4213673901, 1183960426, 1874370435, 4181283334, 2200901254, 3332790298, 3423644529, 2387935836, 952382132, 3924524172, 3719680299, 853249098, 4083610173, 2636543308, 657361882, 1525744446, 376298547, 2451684942, 3240929540, 2310416762, 730671377, 2937427586, 3563592349, 2472196520, 2147357762, 914655107, 1758244054, 3876886042, 12351564, 1679162795, 1489623257, 2455794558, 2538372341, 2057637059, 3508778762, 567682489, 283434754, 3167627543, 1915532592, 1232942381, 2754609078, 4150346060, 1663219004, 1231896519, 2755959635, 183820585, 1055352125, 2147188623, 1645909010, 1893712235, 1485051038, 870164520, 1966826561, 48501444, 2556720793, 3128066451, 790988700, 865202135, 4263049716, 2090861867, 1748977625, 2699841095, 113797990, 2481195137, 2574284167, 834141103, 476065944, 1480757910, 315080683, 350708905, 338916974, 709575589, 3077697353, 1231129412, 746021816, 2332229547, 1946675456, 583346238, 3135681244, 1842291655, 231618544, 104978643, 4086067348, 3174792638, 1543369889, 1101673653, 3023672083, 3205010661, 1536466390, 966572661, 3883854770, 3427219648, 2247096744, 4079126348, 776176295, 2599372279, 1888032134, 360725842, 3052443662, 865793013, 3084628677, 516162558, 1020425629, 2915535067, 4215116317, 2977464272, 1660722837, 3507058298, 864890045, 249379031, 3973345746, 2629825645, 771115239, 3526813236, 3106614042, 203525488, 2971666751, 2845337507, 1637317812, 1743782319, 3991795965, 3057486763, 2839184028, 2831552101, 2836007599, 14115933, 2147447119, 3904004068, 3346997713, 1322155226, 1049159718, 2520132354, 2765453431, 4205328777, 4063219623, 2238279021, 1619016803, 415896490, 3591765870, 3318597287, 1557289292, 2845067684, 89482247, 2114516871, 3464828768, 1114311788, 4215401081, 3458358731, 2736518275, 380431203, 3435888629, 4249714953, 1764633576, 1915821483, 1597234883, 111251916, 274107180, 2935452271, 4072034355, 357724805, 1550422867, 1378849275, 3264188640, 3028697235, 2805673388, 656257910, 1454961285, 188865944, 1924561757, 3184772136, 129725152, 1587697966, 106462817, 1587951867, 3192757556, 2829152265, 3270745049, 435873692, 3749929242, 2062096658, 4149869860, 2418404390, 3646774382, 343128996, 2496743364, 734565947, 3826051517, 2828517029, 962692901, 730853036, 1082602175, 298823790, 3231844899, 526460170, 2579457360, 1480606553, 1842946907, 2622701868, 3895551897, 2026981125, 3153668454, 3704749050, 1185971623, 2504477989, 1870109318, 1518600621, 14687749, 3846239097, 2613355571, 4011868731, 4273118207, 539188665, 2099254272, 1043640546, 2517454961, 4147146631, 3753370580, 3811721724, 989962603, 2211483632, 1480428764, 1954557704, 1112461942, 1569266181, 1678583802, 1646459706, 316406457, 3242999591, 3888012390, 2402113654, 746240298, 3662473135, 1260156363, 1203238376, 3061859356, 2032152659, 966717679, 2534194659, 3388402620, 3223059378, 3877902454, 2566178070, 4108564664, 2578614366, 2924743698, 3967226306, 1346866215, 4129141259, 2159606690, 237374413, 2311773278, 2936435723, 1669343609, 3835118141, 2474006294, 2312776854, 3991958455, 66050323, 2021998927, 3191454066, 2189188580, 2142686591, 262029985, 1334540897, 877178233, 322292574, 583880104, 994626866, 2643853709, 2746736170, 1819097952, 3500683162, 2717819610, 1979841756, 4158317627, 3768907483, 4144867490, 2428342768, 407254584, 3876466370, 2906963449, 2747730439, 2807429483, 390805623, 1347724002, 3708124771, 1996426487, 209852741, 3539291907, 1973958470, 930781564, 3333035683, 555854849, 540149787, 3214341438, 1165683130, 284698251, 3229514555, 1944044250, 676799831, 3415601775, 686883721, 2475380401, 2417075124, 1731220395, 2692854334, 2090593377, 2377595670, 3031508806, 24480902, 3556421449, 1940400454, 3751271557, 585927728, 2399018121, 1897248871, 4110307692, 1294121928, 2976700231, 2519149970, 2393660481, 1452332020, 1320620207, 2261085851, 2445477360, 3141380218, 1044718590, 50521930, 112491419, 4149332237, 1091423792, 1469962572, 3907732209, 3328879500, 4063642960, 3006889620, 425720040, 2842213341, 2094386140, 3171166176, 757382335, 2515418722, 2466505128, 4181749776, 3386253778, 1241141486, 3110299582, 599382492, 3361936057, 2904521896, 3463235864, 1686895148, 4096837571, 2649784396, 102145162, 4034413105, 1309891308, 1727749117, 4111125789, 3485689078, 1298526747, 3208723720, 1387080573, 3497204630, 2701756222, 866112144, 3332181807, 2824696606, 4019789661, 1393196838, 477838543, 3838343203, 2399752805, 1676970714, 2163423971, 3918831727, 2082667742, 687058482, 4132123776, 2944329588, 830337633, 3305684867, 1115400173, 1409924819, 4213431551, 101974285, 721035281, 418956469, 3537419424, 3058980494, 3735712173, 31898322, 812527641, 1412975070, 214035881, 3370497326, 275023508, 2188096928, 2698269714, 2338536560, 2217867267, 780724394, 168999967, 4028242661, 2057116599, 248770288, 142100118, 558526929, 367796080, 1613088719, 111252491, 569035372, 2444968023, 4163888313, 3008206018, 655301551, 1102089047, 2157711351, 1189565715, 1048858627, 3463105328, 1659606364, 2839652561, 311401265, 297227948, 2049718821, 1287086069, 2816817582, 753298510, 79123064, 2058422267, 1988231070, 1697021200, 3755875481, 2000787653, 372680790, 770642272, 3557979977, 3242763045, 3424268849, 2545039983, 3403101537, 804431778, 3022051943, 1799982329, 835187866, 1307679719, 795446639, 2865087004, 2503099400, 1097854687, 412079412, 2918593238, 4204336449, 3272876881, 3701287131, 215671154, 2729194459, 3828900376, 407889473, 2386020434, 1672155598, 1588439879, 2355888880, 2451706408, 2223568426, 4230924842, 1121564168, 3971399371, 2302823247, 1838239260, 4017581704, 197226193, 1773201901, 22730505, 599013585, 2360399780, 3459055993, 2359729316, 2534122212, 3338162386, 681551474, 804682591, 3684776026, 2611917837, 518924291, 3527933723, 2831363989, 2092857661, 3011292035, 2036768662, 1165948954, 3915111934, 3715091842, 3486642823, 2169348932, 2210412086, 2082504433, 218262071, 2666551070, 3844955859, 1885787522, 50919684, 30300958, 3237830009, 1004399278, 1420324202, 2995067867, 3343455201, 1341482320, 2707911315, 2322962795, 104691279, 433113543, 1673935915, 237192280, 3866873407, 3719846074, 504926120, 1585743054, 710382710, 2276436306, 2976938826, 1322735386, 1856969923, 311925360, 1497000075, 2852252785, 207694370, 3237126868, 126779936, 696212993, 3860732454, 2811018481, 3182218492, 2694262689, 954054185, 1145279765, 1827792779, 647535690, 2378645894, 1603060963, 1501639457, 967601596, 3979534574, 2129057469, 1503074666, 3455573355, 1277747107, 2364423785, 718418781, 2029920441, 3230465514, 3292224990, 796319542, 4143628522, 2357283776, 3321794845, 2371483975, 1136784117, 2757314460, 132067372, 294498845, 2989608361, 1147501898, 848670725, 3702484846, 3398317762, 274118355, 3486956662, 2414417547, 4165976855, 3707418163, 3614978249, 793009306, 4227283826, 2072607460, 2291123052, 1319566667, 3736885972, 1075733989, 2822123350, 883768237, 165340447, 2283477403, 3854687889, 2702364501, 261781101, 4253180939, 1904200988, 3670999235, 2081253795, 1013385256, 3393606543, 3915738401, 3677841368, 2222722431, 3582521284, 2184635962, 1379820344, 4132361812, 3076369748, 3111110095, 1060089765, 3951504597, 276119608, 4292130693, 1208342406, 2964718231, 1156835032, 1503506724, 17689181, 1253790050, 2052448727, 3951262449, 1045066741, 1212371757, 3864687390, 2781636814, 4164334487, 1434750495, 1015217609, 492107542, 4106176432, 4258301116, 52857279, 3601017578, 553436516, 1286022350, 2970181802, 1531473162, 615711544, 2770114226, 3807138554, 1254115612, 405024141, 2248962327, 3661682788, 3457720992, 2391719239, 3782958744, 3184983441, 1120404266, 1505151243, 2382314268, 4164517871, 782247452, 923774834, 3508260701, 2537984828, 2116287910, 3255992169, 2640296699, 614769200, 767427138, 3456406779, 1809700841, 2437468993, 642938299, 3155191374, 4074085350, 2642920857, 3189984175, 3169851773, 4086000673, 2490375684, 3948311217, 3105674217, 1698869289, 1311043867, 193634359, 3011562913, 4136987101, 3694637471, 3746665664, 984905715, 1842085529, 2014624560, 1012559384, 381626366, 3316965712, 3951018504, 1396133012, 2477956684, 3892489603, 2447107565, 1585934707, 2614794953, 4048636321, 697301886, 2382428822, 2964257243, 506994596, 1901393962, 3958702238, 930275666, 3970480891, 2137671677, 911161575, 3800494155, 278586712, 1193762952, 154795879, 3301269187, 1668521332, 444082092, 1753908500, 1687735396, 3236812133, 2861130228, 179908202, 1539423798, 1280312575, 1354412234, 890265444, 3698680851, 653081540, 3681719879, 838283359, 969405299, 1918696509, 651424255, 1081467498, 1369194422, 969636592, 1353343686, 1151142771, 622249210, 2324152022, 3419137792, 2402401643, 417315756, 2283635979, 2730135008, 945357607, 1421847419, 546033882, 3198842674, 3343416782, 1103542692, 4192435052, 2680753787, 1928123125, 1829821471, 3877076359, 2319958157, 1817991563, 3019027601, 3350099005, 122241996, 2220681659, 1867304134, 3903645175, 3926484316, 561272258, 2924762331, 1521681554, 4276247138, 4264605013, 3489960755, 90524145, 3924010437, 2159859802, 3931840385, 1622645822, 3614003481, 4142324969, 2557247602, 4114169094, 2832266442, 1338437964, 4072229872, 3375287658, 2231757313, 4020609455, 2396693058, 2794056809, 1622056246, 3798643807, 3419424563, 1469037362, 3368075234, 2696057690, 4239384736, 2499585821, 488059987, 2262538463, 1978623658, 294535630, 3609960885, 432048986, 2518665415, 576966143, 1577963777, 3672258101, 1737846056, 1033455641, 3049863102, 414818580, 2310833967, 3876593023, 1159401619, 512103557, 3929750248, 104744865, 2294284829, 700010847, 3919829947, 472148418, 2495096228, 1476352517, 3466719922, 1423170701, 1835216137, 3804324362, 3156638174, 218238460, 2122719443, 1475392811, 4191547266, 1660363531, 1752963086, 814996542, 1775564261, 2768667643, 1691944624, 2673873848, 3717015687, 4274924722, 4267842589, 3218843587, 4086630122, 2525920765, 2642512022, 2581476770, 1587395043, 2479647167, 2075617909, 2220378822, 1164751823, 1254817289, 3012514369, 535781325, 1155411560, 3470618493, 3736078399, 727696447, 3668735551, 2540239292, 1287246718, 1034530277, 3398095154, 2277784043, 1007465081, 2592218771, 2307100491, 2280001478, 3781351274, 517873620, 16783814, 376212454, 1269327062, 2190745862]
    @u32_2.setter
    def u32_2(self,value):
        ca(value,[237099665, 1725693514, 3671290215, 2838122575, 2174235839, 1926762547, 837710207, 2675306390, 3296759548, 3236712776, 1185582523, 3424554628, 2120088772, 3672727628, 1229489468, 299615394, 2391828662, 2161918065, 3215046430, 4090719326, 4046969338, 2837195073, 1814520605, 3281278603, 2366669618, 889646058, 2889818005, 582950935, 1660657214, 3304485267, 3017091402, 4182786222, 381383578, 468232037, 4264726246, 548129943, 228487325, 1626908942, 3843628003, 340032714, 896193553, 1589965383, 421647904, 1025804481, 37483739, 314532432, 2655347560, 117434633, 503953090, 3976906518, 1323855325, 538108471, 4161859424, 1912643799, 1352908924, 3415941572, 2123957567, 2125372546, 3660361032, 2093953170, 844556942, 350952258, 3712309630, 1671728833, 1515702177, 674196370, 1804290265, 2369213421, 659681625, 3007121556, 3629421992, 2355746396, 1887771, 1763854265, 3669589284, 3060951582, 2289752966, 2753656458, 453476287, 3858397040, 1755557022, 1056528532, 1074824037, 3392115327, 959387159, 4047339053, 4055444899, 2701521116, 3269246259, 1658313101, 1191016218, 2976266754, 4058115909, 3148745595, 2255966436, 1286833652, 3846605743, 332980236, 2987111809, 2863137443, 3589002629, 3634508729, 3050304267, 426166523, 38644952, 4120741158, 3779249472, 2247004208, 3887627978, 771737466, 327488668, 2413511241, 3742352323, 1800531129, 3093397506, 119855689, 1044449337, 1621589532, 2435672368, 2249934961, 2486385468, 2733265378, 2055466545, 3463839050, 1741434858, 1937180913, 53147295, 380685724, 2147133772, 3377145922, 1696161493, 986108230, 552797714, 1030805428, 3633258771, 724378483, 1453096552, 3633745301, 722493301, 3218821892, 3672842476, 3232339885, 2194639207, 3626117658, 160139022, 1220950174, 1499215195, 2900860877, 1105932921, 2513047638, 2975567394, 2688547895, 1701949245, 494851022, 3099438803, 2302405511, 3002890773, 3694596195, 1818301109, 2241585621, 3375937719, 2173718080, 3174769392, 2332849203, 1120354034, 3688107993, 3910547603, 475511452, 165704715, 2543590060, 4279301981, 308235882, 1816022030, 2611287885, 2638354900, 1603444131, 2625463614, 2748122332, 2695819720, 3508062749, 4213882116, 1456900955, 2527945808, 1021825166, 2050461441, 2014465404, 1165369542, 1735932899, 3460204932, 1482933068, 1853558960, 3796877889, 2819245867, 1495722807, 286085468, 1232127264, 1369041740, 1203310608, 4013214417, 3662137316, 3906425458, 1886277730, 3592347464, 4124894145, 1520615672, 2057935984, 2780423261, 3807868959, 1096708615, 1133308613, 2081283278, 3031731081, 777297905, 728628197, 1045968931, 2798986608, 1441163940, 425803298, 3425923673, 3174138272, 225290447, 2789342514, 1500710940, 2214009944, 2611052505, 1511169866, 3468976229, 887023337, 3301621653, 348051316, 3413528372, 688050819, 3270149113, 2721404891, 2790531383, 1307526009, 24196953, 3323021735, 1883300819, 827261292, 1024782357, 4200877565, 961985674, 166365221, 3011947146, 3773678739, 3122249899, 4236359826, 3567170538, 164427914, 3384429677, 3901604544, 3178054797, 1736839253, 2964545385, 891428101, 1944593339, 1989423560, 1361523913, 3168022842, 3512787479, 1890231449, 1593427930, 4149710413, 206469070, 1896704648, 1231454209, 4068940405, 3271655038, 2008435184, 2914967896, 2357818161, 1859278865, 3410094777, 1298228364, 222292372, 1055108733, 4040689906, 2210549194, 1948747, 2506100330, 962472296, 1968083925, 113875684, 1936131419, 1016307414, 1060859451, 1739828182, 3346648079, 1164081840, 2485888280, 3476085289, 585721471, 390929102, 517669802, 2653223889, 1174053498, 1569525180, 3310507972, 1002962122, 2262804195, 3220775546, 3182459697, 2156503148, 4131684371, 2813459977, 1117022498, 1997829290, 2683851565, 107074302, 1419327824, 3915955155, 3780878619, 610899511, 1901058671, 4050293718, 2053491262, 1391571066, 1177627511, 743398950, 3803305715, 194123827, 3621325995, 472267748, 3375152783, 2897163902, 3462255512, 4250233830, 3994919468, 2831376517, 246739001, 2563541164, 2158887230, 3637942716, 2966210109, 47815115, 521677298, 645694605, 3228944885, 737962495, 826169136, 3548976344, 4043510480, 495863083, 777697689, 805624668, 1263172222, 3510345575, 1056092728, 2969537722, 747239264, 3369168528, 1344872701, 3335255317, 4214479629, 3890217901, 212326383, 626667851, 4084223303, 2815290146, 3385778156, 1708926854, 295550151, 494270470, 3067952778, 1533064310, 2934900292, 1705387163, 1307922285, 2193031516, 2433387564, 439649015, 2639844157, 3899988054, 3512645808, 4082111285, 39460185, 2109679546, 2807623639, 872015072, 980218181, 3396910791, 3668142418, 1001890199, 3235923562, 3566499716, 363410876, 2673237222, 573356352, 1636136151, 2224553312, 3704628010, 1623877736, 2563570732, 1232767726, 2971775467, 4216718036, 3488020769, 257411122, 1168087703, 818565641, 900860168, 1947568647, 164818961, 3931611634, 3720231207, 2690894061, 1424779930, 90538671, 131364160, 616530415, 743044912, 129491467, 4041759658, 3433286148, 4169430938, 2922959631, 3821215730, 3097046213, 3611435200, 2326824436, 184884915, 2069988071, 3914342196, 106319212, 1325869172, 3906567559, 1758481342, 1277175140, 2754342337, 1294820705, 791996734, 41241012, 3345622322, 3718866993, 1255338839, 1391956142, 3839078475, 3457508262, 551513656, 1004850662, 3795985935, 298265118, 3742037297, 3355517467, 3601723593, 3585988041, 3063759488, 3171470181, 4259702765, 3239000394, 2708065681, 4092601030, 346908933, 849213263, 2851377667, 1796454246, 2735073999, 2777745491, 2294240001, 2121652435, 2706284022, 585848169, 1936702478, 2371114722, 1541583037, 116304242, 3676364969, 3879455349, 3833621771, 3701696564, 2780518089, 1479844512, 1789233460, 2165430981, 3709637684, 1215700310, 3383152932, 2134182167, 3267525810, 4142614062, 1913035686, 299460925, 2677124325, 2261142050, 2007429043, 515722793, 25703755, 3410497288, 1661381183, 1667524384, 530887788, 3517835794, 159256235, 3805603779, 2368397, 2999883232, 39771046, 49747199, 3734347231, 185140859, 2259304947, 3389847559, 3758478898, 1438981583, 1923428196, 4294696986, 1917080172, 3599354053, 813437110])

    @property
    def i64_1(self):
        return -1357833931563696072
    @i64_1.setter
    def i64_1(self,value):
        if (value!=8621740821050813024): raise Exception()

    @property
    def i64_2(self):
        return [8621740821050813024, -9092072209079113602, -3056007272962959794, 5895514005284775249, 4825857599917744482, 2093519537988072834, -4390907564722863586, 8598973384036716702, -1889020672280261540, -8273635663381002611, -1941314642980235766, 1812319066748738475, 4190176042918780749, -4555199367311683530, 5467393609117797644, 8359783806563259266, 3800668915803924955, -2655932873935461949, 3136675805239089308, -3633713411557631382, -672757299114219972, 3045962201700775993, -3026485644327632861, -3372272670687649520, 3387661134442604201, 3677140703283269642, 4482422720713908644, 1337692977628619063, 6948420747960198793, -2492903114419653680, -5938903035079054289, -7806446185001452553, 9040686595201532492, -2127381394247868345, 8655785215940696615, 6435851473422996010, -8509497626685383427, 1304836616586909040, -2675436555158709746, 7454381249933066408, 1631169664587044350, 6013206163109033855, -2269271257167747155, 362749191994199052, -2710425314932035541, -3130715904393787670, -4410494504975660198, 4957729582609338569, -8246870151259110017, 6845983371242614475, -2258617392930568184, -8252230642158077029, 2670510062513563636, -6653455225739816423, 3093107250382849352, 1150551445512420048, 1546949923942708166, 5021898317351658427, 3707867854662121111, -1206055501856481918, -1873593186785558123, 6775838224715797812, -1115046710372778769, 528633723916988990, -4174382295242439358, -5547557100483108777, 5731859982382023557, 2204054933203810496, 3007479017130878933, 6608694896063582073, 1503694568421070630, 1248413523206321552, -6401043893159800201, 1353202742204949340, 2304302719445899395, -1291964394378923514, -5522844881206564639, -1277367478728568636, 1849991021787670735, 478721890957105862, 7757247149420834244, -373709650675810738, -5057614129950301004, 6162983513491054102, 3145006736835504836, 5885317631158909353, -7602326138257639761, -4157450027384868646, -1360567824864190920, 229176854089967110, -2202711857284656499, -2946750387084440631, -7399092435233174868, -931278862032913506, 8725183201793225879, 4422438402418122694, 7390489870132742668, 5253764508555093227, 1198113859723757987, 7260998365611273804, 1540767319493735478, -5799740479458549922, 1136167730386243597, 1413668892541509388, -8362134679601352333, 3664237052291625965, -7059531260401496534, 244969021945500288, 7960640458120876383, -2144041369569582147, -8542531942333624037, -6912033525905196529, 7309130333167087960, -1428796488709117140, 7889412153530907816, -6519274351560620428, -7194011194445795971, -2253470711475766161, 2052913415378741465, 8349030699411536987, 2962275883196204755, -8896757719886490153, -3481651114681941922, 9178906373760388169, -2393681984948405823, -4722899724188292419, 2219571189613806132, -8736536710280581263, -6631663654879231430, 1213083601717174358, 351791283162447724, -2728467560827636562, 2174378918144416458, 748751282949822397, 4251372914295826830, -4967177568325109568, 3825916028954041329, 7303839053387841791, 8648996684183789510, -6188350610717327471, -9016026939100696370, 8366545235017906362, -4151061240351591634, -3308165752571595210, 5710967263762362072, -7116887066458274066, 6003026705335466483, -2788076296930402698, -696935785960712847, -3523035848103775545, -4808396779515182120, -4487243801299967856, -316555344628268867, 2148745648896444003, -7908465185551702581, 209478862744791304, 8329349262325078360, 2312897865550480622, 3534430375708664567, -4313813383770928446, 7798388933635693783, 423303070618897314, -6223899204612392666, -7997497118304435999, 1761514773996835425, -8886871075540730292]
    @i64_2.setter
    def i64_2(self,value):
        ca(value,[-1418708830105823852, -1357833931563696072, -8308127073437794904, 6203263204523798112, 7076661289157584762, -3645491092747259726, 2969229117250121621, -8403401867791621438, -5706351777107258259, 6979420050019736435, 1350986631885231652, -8626678967587677100, 8380704325304801386, 3423582193572197909, 8713973059069583959, -4562940403005824119, 9144900318464157853, -8717799056344934090, -8792498500921807539, -8345039878076898189, 5201358909840838683, -3398583150340629128, -5482869438456886726, 1644815108571813337, 7248497692538999361, -1178045319005427907, -7220532561583062381, -2882504460577706964, -3460274637164886125, 9053064536664375063, -8649931456492292885, 72282480921257410, 3058905063630457969, 8394362105178121659, 8263211448476405605, 8671703720724529690, 1117912130945798022, -7392161278301566795, 9070973456367872189, 5064083874137910433, -2216141782782730608, 6092600172408194906, -7328184273434559673, 7340896108422144895, 8041029351530593362, 3567042073657363684, 6634152186323571334, -939114094925119978, 3932918768588612631, 2223869457290740495, -1394521432769550065, -7708491921728269104, 2558409591077932690, 7323090212396920736, 4463226188281322565, -7684442752899854301, 3813932804031799733, -3061288894555894392, -8926314527654650550, -5483212417699975352, -5168152193234004511, -5252714907036148733, -8899682260331039592, -6945672564712903320, 1843836835216653982, 6265565553002088665, -9191803385169282118, 824381268893232707, -4195712559860724390, 3170122388521742267, 93238405484244323, -3808714570016938587, 7751370385159261162, -415651213975075366, -400640794129234242, -3632420176870277542, 2145224332581955327, 8408764257602201311, -5753925773175608181, 2442171188911603754, -718254550700219999, -5279112326876598860, 7731819115318618935, 7285784364016347384, 6648758251111712748, -4965048064766122366, 1799714525316551079, 5808264002475810898, -521447549589589148, 263148779791826658, -1256378489223837059, 3001523551318331984, -2133704098322946340, 9175731965505830169, -275510851941027307, -3450575930678805596, -4673869135690784872, -2779584507299050825, -6244919930307138446, 5663020090027727817, 3592337319079719462, -7699870730217589682, 3427192886285003578, -566635025493084181, 2780130284244381358, 3422425913941932991, -723427948584706426, -1731222455107826641, -3556462521989327042, -8514332474959779238, 3681987062303886320, 1266418540216073989, 4892980044242035752, -5243563662285950589, -8021867029688739836, -5712778566201121978, -2133887347488624783, -667985954315002704, 2350239843243973147, 5123432618264623922, -271741713269398666, 8726020244487579882, 3802883727236102212, 4050625489658817027, 6873081973971784099, -7507676454188557650, -675853520577120389, 4704868291861385417, 1767091830085798988, 1315143445596137295, -8400502078442130692, 4250620495159315861, 7743903342313618441, 8236285998949285411, 920705431865098656, -2187810178560173353, -5636947816335562469, -8869870121412151030])

    @property
    def u64_1(self):
        return 13389861970863644378
    @u64_1.setter
    def u64_1(self,value):
        if (value!=1465640522145789825): raise Exception()

    @property
    def u64_2(self):
        return [17812699909525330179, 13389861970863644378, 16257896157253761478, 14191477546208115816, 1387441194387183523, 8800889055657239662, 3787113061722336589, 2075067786453142295, 2302772129471114307, 16660993589300385169, 5227667125318999851, 17211198982499914739, 13967365476154884537, 6210802835678950626, 413837793611927178, 15016088479821729126, 14194309003275915218, 5521545037113246785, 9721585675207248367, 2487154057124779480, 4054392452442988950, 15742440468026600431, 8404041348136789525, 5704587169648799325, 8615894037736189999, 7555294940121326684, 166204857340424907, 10630415758080788319, 3699593146963368456, 15841753586674104403, 1425904355269403798, 6757749835782369274, 6484708862168533651, 14311810156028177789, 13305336491678304892, 9547219694933920657, 16939089102075290494, 13780222831094724753, 729578726262763066, 6741605646549400625, 860499368566843233, 4821657628681234936, 10629375059978179469, 12676697982045410789, 7965873501849669898, 6463814633396676710, 10304605129170106831, 17634109250944839532, 7874201956261190767, 2093432098376142516, 15162293521637815459, 14480915389905814968, 12246183009228206627, 9927056522845945393, 10708714764412026102, 12620101894595011829, 9720992984909508434, 1335165052342958298, 3842118717279685369, 5703296853718993513, 10169884007081888934, 2514628960699067131, 5254570865582417565, 9562135776312844762, 27891557900731192, 14886705471885923481, 3399688988254798568, 14640082747632735324, 12221809011211673821, 12865683977160344326, 12797396568995658538, 16277433856161229511, 5834216036130347946, 41836075316600799, 6171722505441450511, 8601242920007887523, 13624814788188880079, 7848598808818978240, 14273686016064474182, 9616131192223535887, 17907341921682029586, 10138262866472100954, 14661185914352643699, 18102813560908894003, 12307841218657619289, 14709882437025014177, 10238864911411793767, 4776457610936466600, 8782354639535937976, 18274481696525890320, 13992637006136445380, 11566349649437476293, 1209664843394078754, 14394522101288007152, 2915009092315033094, 182528511086129450, 15695741318843217573, 744918667092745933, 7146826536782008676, 13838640680680387773, 6708462726963541522, 7741352156378706754, 15062394166759350529, 10613549923461193838, 11002287295489384645, 11112868002985992483, 14972199425906445655, 15176061787056984512, 3369667758791907709, 10545737311162535909, 10549452773932875360, 977025607559254534, 8213649184128301518, 16026014660753415782, 16346803042848708719, 8641570190583236526, 10372374375551503871, 8475065376071450531, 9492316019190861724, 7258336917778003543, 7704933404615957344, 14492234026024540236]
    @u64_2.setter
    def u64_2(self,value):
        ca(value,[6515978873578326855, 1465640522145789825, 14139647178981527348, 17376225719361197745, 4827355217349405315, 5237172857588412536, 11185863429255124449, 11922950710462888186, 9723873762901963012, 2360891509504070464, 17595800616336901155, 4676383109049523121, 5519403084078587651, 15199794964642249670, 10725748072798711186, 11861452006494413908, 10866242934922922899, 15599520359228044898, 4022505103249338009, 15081262745932646374, 9978655822822015426, 1893338345735521355, 8335612627840221039, 13125076221780371251, 1843608744939432450, 1877855184169582147, 360237399108374165, 14133486497511175136, 6918428392028668980, 4207262405010786686, 11882372330517522341, 2660307236802524516, 16105897257753062921, 2353931053072926625, 10173424970756197713, 3742480367255311168, 1303431584704287527, 12527899890265500372, 32220987555692133, 17556513786877588779, 14599571048880016586, 2017220613051019209, 13580232873699969747, 3864855431338072766, 10522968089599101769, 445176367690966897, 7790111520686478868, 6394442284921113988, 16995884223523288612, 11216569412804039035, 4321418227933556664, 5409834497962741327, 690550291029646943, 16074599988808644612, 11236550486638087434, 6844569081007881849, 5869987636307743707, 7778211196101597376, 15853871901637280370, 18058575643888946512, 14027203060397441285, 12712062502708340258, 4041613882264720796, 11645048579559315688, 1246226537584125354, 3474795601576826029, 11513896830487717539, 1974322205737539934, 17242471345616954213, 8678121572397745114, 17527671945381764646, 5033231148296076497, 6411880965725185093, 174473638020748044, 8158678930583416018, 9507609436552652251, 16205993571484058929, 8035338227846555833, 8791374446603527925, 14595445946451526244, 5169961786923105799, 13397974474224235898, 2364042737119390982, 5321299597050057517, 1121024914655468441, 12207167839097364776, 12619831538472755181, 4864354177058320218, 17848460798228747459, 13261044407690283599, 10209900008497671979, 6862409070349488681, 1432310611369939292, 2092522766869471913, 15058223303172327711, 4178174561433201628, 12906394038648389198, 15191542062580018441, 16452252929507747318, 11201120125455394600, 6726163449083399053, 8426476024479275017, 7026246701397961488, 9033438331677737541, 5951673483825817230, 10638919135849238472, 3252342350133602871, 15766880131631627052, 12385842632184481382, 2748643971592610065, 6396730451340699978, 13659499533346384982, 4282043305472384300, 1711405441567413160, 17992713571449412921, 3556627233283536994, 4138074248161109398, 1622144212241737621, 18087263875532968938, 14104137172003718411, 7644309790031389842, 8816844725250613052, 11421439960737023984, 10454322951672789795, 2119200398037807197, 8384409476347314289, 2527068029837223073, 4862875043870995989, 17581079332542377528, 18385625565005546141, 5262116103886681622, 14174635193688816521, 3985859099523137999, 5526499814203466410, 1239704066545123753, 5917443538249299253, 878138865084935513, 10218107935864045533, 6547939038367120283, 7353731416371741667, 5504609912290331194, 17697030959073472945, 3134771705926671223, 1308908721146697947, 10579235124105673010, 17332984836700322102, 13722665407351335633, 18423215754649979094, 3171161736406578023, 4234709098044006158, 7347564326123203638, 8195365762234651673, 7781698260938130820, 1180819293191049424, 493531138123366511, 1365828412106184272, 10313217779396245974, 7602972172978537794, 6065626025778962290, 9672897350080504270])

    @property
    def str1(self):
        return "Hello Client!"
    @str1.setter
    def str1(self,value):
        if (value!="Hello Server!"): raise Exception()

    @property
    def struct1(self):
        s1=RobotRaconteurNode.s.NewStructure("com.robotraconteur.testing.TestService1.teststruct1")
        s1.dat1=[2.416507e+16, 4.573981e-21, 3.468194e+10, -2.393703e-06, 4.937973e-15, 4.706768e+14, 4.286830e-10, -1.090462e-14, 2.238670e+03, -1.254407e+14, -1.275776e-21, -4.124599e-10, -4.953108e+11, 2.808033e+03, 4.685151e+14, 3.710607e-08, 3.523588e-01, -5.585682e-20, -3.290719e+08, 1.600972e+17, 4.257210e+16, 1.114490e+04, 2.739939e-10, -4.332717e+16, 3.482223e+00, -2.162451e+10, -4.527774e-04, 8.558987e-19, 3.755463e-12, 3.863392e-08, -8.351348e-05, 4.774283e+02, -4.612524e-06, 2.206343e-06, -2.767520e-17, -4.183387e+08, -2.037466e-19, -1.780912e-18, 1.656909e-07, 4.799751e+07, -3.604348e-06, -3.146762e+08, -3.709450e+15, -2.379431e-09, -3.034066e+05, -3.072796e+01, -1.057111e-14, 4.753235e+07, -2.725014e+07, -4.895406e-20, 5.339502e-20, 9.375211e-11, 1.632454e-03, 1.051386e+01, 1.915580e+17, -1.999453e-09, -3.087190e-02, -3.222377e+15, 4.219576e+03, -1.401039e+05, 3.950473e-15, -1.620577e+10]
        s1.str2="Hello world!"
        s1.vec3={1 : "Hello Client!", 2 : "Hello Client, again", 4372 : "This is yet another test string"}
        s1.dict4={"teststring1" : "Hello Client!", "teststring2" : "Hello Client, again", "anotherstr" : "This is yet another test string"}
        s1.list5=["Hello Client!", "Hello Client, again", "This is yet another test string"]
        s1.struct1=RobotRaconteurNode.s.NewStructure("com.robotraconteur.testing.TestService1.teststruct2")
        s1.struct1.mydat=[-2.457273e-05, -3.349504e-13, 4.139542e-09, -3.944556e+04, 2.761296e+04, 8.570027e+16, -2.472613e-03, -2.096009e+03, -4.186716e+10, 4.584716e-20, 3.951344e-03, 4.557915e+05, -7.117988e+03, -4.605957e+11, 7.353630e-10, -3.303575e-19, 6.133982e+05, 4.528668e+01, -1.427778e-11, -3.509465e+15, 1.695706e-04, 1.732872e+14, -6.370107e+01, 3.269065e-06, 4.480613e+03, 2.058970e-06, -3.748223e+05, -1.507989e-09, 1.690251e+19, -2.177567e-08, -2.391641e+16, 3.617128e+03, 2.568296e+15, -3.009031e-07, -3.754976e-09, 2.458890e-06, -3.800108e-11, 1.555663e-11, -2.085887e+18, 8.574830e-22, -7.228491e-13, -3.987643e-10, -4.777544e-02, 3.908200e+04, 4.221779e+11, -7.528852e+06, -2.077042e-19, 4.478813e-02, 3.506975e-06, 1.011231e+12, -2.181961e+17, -5.098346e+16, -3.791130e+06, -2.734203e-14, 6.340994e-13, -4.582535e+07, 3.977645e-06, -3.785260e-07, -4.102542e+06, 4.751411e-16, 4.203566e-14, -3.894958e+00, -4.585783e-14, 2.432993e+15, -3.592680e+14, -1.560186e-12]
        s1_dstruct2_1=RobotRaconteurNode.s.NewStructure("com.robotraconteur.testing.TestService1.teststruct2")
        s1_dstruct2_1.mydat=[3.785355e-17, -2.518001e+17, 4.016500e+08, 6.566648e-04, 1.284318e+07, -2.674821e-13, -4.955749e-14, -1.699098e+00, 2.901400e+05, 1.499143e+13, -2.252822e-05, -2.653172e-14, -2.482811e+07, 2.353638e+18, -2.177258e+17, -4.715112e+06, 4.508858e-18, 1.205611e+17, -3.469181e+00, 2.383792e-13, 4.544766e+14, -3.029250e-05, -2.545049e+05, 3.149303e+19, -3.724982e-10, 4.066723e-02, 2.809941e-08, 1.279689e-20, -3.303471e-09, 1.846558e+08, 1.311495e-06, -1.185646e+04, -2.603100e-19, -3.519314e-17, -1.595996e+04, 9.735534e-20, 1.234003e-04, -9.697458e+08, -4.895883e-02, 4.770089e-16, 3.757918e-11, 5.253446e+18, 5.071614e-13, 3.793300e-08, -1.993536e+12, -1.846007e-11, -3.458666e+03, -3.995887e-10]
        s1_dstruct2_2=RobotRaconteurNode.s.NewStructure("com.robotraconteur.testing.TestService1.teststruct2")
        s1_dstruct2_2.mydat=[4.856615e+15, 5.981566e-22, 1.433616e+14, 1.747102e-09, 2.850376e+06, -3.748685e-08, -4.969544e-21, 2.530419e-01, 4.393913e-09, 3.837331e+04, -4.315065e-04, -1.073834e-17, 1.244057e-15, 3.901853e-10, -2.725237e+10, 2.896243e-18, 3.609897e-13, -1.937982e+02]
        s1.dstruct2={"test1" : s1_dstruct2_1, "anothertest" : s1_dstruct2_2}
        s1_lstruct3_1=RobotRaconteurNode.s.NewStructure("com.robotraconteur.testing.TestService1.teststruct2")
        s1_lstruct3_1.mydat=[3.785355e-17, -2.518001e+17, 4.016500e+08, 6.566648e-04, 1.284318e+07, -2.674821e-13, -4.955749e-14, -1.699098e+00, 2.901400e+05, 1.499143e+13, -2.252822e-05, -2.653172e-14, -2.482811e+07, 2.353638e+18, -2.177258e+17, -4.715112e+06, 4.508858e-18, 1.205611e+17, -3.469181e+00, 2.383792e-13, 4.544766e+14, -3.029250e-05, -2.545049e+05, 3.149303e+19, -3.724982e-10, 4.066723e-02, 2.809941e-08, 1.279689e-20, -3.303471e-09, 1.846558e+08, 1.311495e-06, -1.185646e+04, -2.603100e-19, -3.519314e-17, -1.595996e+04, 9.735534e-20, 1.234003e-04, -9.697458e+08, -4.895883e-02, 4.770089e-16, 3.757918e-11, 5.253446e+18, 5.071614e-13, 3.793300e-08, -1.993536e+12, -1.846007e-11, -3.458666e+03, -3.995887e-10]
        s1_lstruct3_2=RobotRaconteurNode.s.NewStructure("com.robotraconteur.testing.TestService1.teststruct2")
        s1_lstruct3_2.mydat=[4.856615e+15, 5.981566e-22, 1.433616e+14, 1.747102e-09, 2.850376e+06, -3.748685e-08, -4.969544e-21, 2.530419e-01, 4.393913e-09, 3.837331e+04, -4.315065e-04, -1.073834e-17, 1.244057e-15, 3.901853e-10, -2.725237e+10, 2.896243e-18, 3.609897e-13, -1.937982e+02]
        s1.lstruct3=[s1_dstruct2_1,  s1_dstruct2_2]
        s1.multidimarray=numpy.array([-3.949071e-09, 2.753555e+10, -2.724923e+07, -3.553170e+09, -3.674923e+08, -2.479267e-22, -4.898990e+18, -3.561455e+19, 3.890325e+13, -4.980286e+18, 1.142884e-15, 1.570587e-12, 1.398743e-14, 1.769117e+11, 2.086717e+05, 2.986916e+13, -1.204547e-17, -6.138080e-08, -1.468512e-12, 3.240537e+11, 7.476873e+15, 1.627340e+19, -2.421611e-13, 3.549785e-20, 1.469061e+05, 4.172556e-06, -3.369810e-17, -4.639587e+10, 3.776574e-13, 4.990526e-08, -1.321627e+07, 4.224942e+10, -4.515185e-03, 3.619167e-12, 3.046092e+19, 3.712879e+03, -4.019784e-13, 4.005048e+18, 2.988709e-07, -4.123078e-06, -1.064380e+09, -1.931617e-18, 4.223366e-22, 1.783661e-19, -4.153799e+16, 1.591527e-10, -3.649908e-15, 4.348772e+18, -1.470750e-14, 1.637311e+08, 3.982951e-05, -1.304963e-04, -3.522058e-06, 3.869385e+02, -4.640831e-15, 1.292954e+00, -9.474137e+13, -4.196137e-17, -1.540996e+02, -1.742881e+00, -1.597433e-02, 4.062517e-04, -2.724799e-13, -4.113398e+05, -4.704501e+02, 2.977726e+04, -2.662004e+14, -1.376497e+04, -5.993109e-22, -1.265974e-15, 6.387767e+11, -2.696841e+04, -1.983347e+11, 3.214742e-13, 1.906709e-06, -6.956937e+12, 3.637926e-07, 2.706666e-16, -9.795675e-19, 7.311871e-15, 2.343927e-09, 1.709674e+18, 2.961079e-05, 4.009574e+11, 6.468308e-18, -4.041410e+11, 2.991768e-15, 4.240906e+19, 2.260404e-12, 4.786043e-03, 2.439493e-09, 1.698043e-13, 8.655885e-18, -2.598418e-15, 6.685593e+05, 2.895287e+13, -3.098095e-05, -3.764497e-06, 3.192785e-12, 2.098857e-08]).reshape([10, 10], order="F")
        s1.var3=RobotRaconteurVarValue("This is a vartype string","string")
        return s1

    @struct1.setter
    def struct1(self,value):
        ca(value.dat1,[1.139065e-13, -1.909737e+06, 2.922498e+18, -1.566896e+15, 3.962168e+17, -3.165123e+17, -1.136212e+13, 3.041245e+16, -4.181809e-18, 3.605211e-18, -3.326815e-15, -4.686443e+05, -1.412792e+02, -3.823811e-14, -6.378268e-09, 1.260742e-14, -2.136740e-16, -4.074535e-10, 2.218924e+01, -3.400058e-08, 2.272064e+02, -2.982901e-21, 4.939616e-19, -4.745500e+03, -1.985464e+16, 3.374194e-04, -8.740159e-09, 1.470782e-06, -2.053287e+06, 4.007725e-13, -1.598806e-13, 2.693773e-06, -3.538743e-08, 4.854976e-16, -4.778583e-12, 3.069631e+06, -3.749499e+03, 3.995802e+05, -2.864014e+13, 1.276877e-13, -4.479297e-02, -9.546403e-13, 8.708525e+06, 3.800176e+04, 4.147260e+10, 2.252187e-20, 9.565646e-14, 4.177809e+13, 3.032250e+01, 3.508303e+10, -4.579380e-17, 1.128779e+05, -1.064335e+11, 1.795376e-06, -1.903884e+09, 2.699039e-03, 3.658452e+15, 4.534803e+15, 1.366079e-03, -3.557323e+07, -4.920382e+18, -3.358988e-07, -4.024967e-11, -4.784915e+16, 1.490340e-18, -4.343678e+08, -1.955643e+14])
        if (value.str2!="Hello world 2!"): raise Exception()
        if (len(value.vec3)!=4): raise Exception()
        if (value.vec3[10]!="Hello Server!"): raise Exception()
        if (value.vec3[11]!="Hello Server, again"): raise Exception()
        if (value.vec3[46372]!="Test string!"): raise Exception()
        if (value.vec3[46373]!="Test string again"): raise Exception()
        if (len(value.dict4)!=2): raise Exception()
        if (value.dict4["cteststring1"]!="Hello Server!"): raise Exception()
        if (value.dict4["cteststring2"]!="Hello Server, again"): raise Exception()
        ca(value.struct1.mydat,[1.783093e+12, -2.874045e-19, -2.311319e-19, -3.099234e-12, 1.000951e+16, 3.775247e-12, -5.853550e-18, 3.175537e-10, -3.112089e+08, -1.577799e-06, -1.379590e+00, 4.777044e+13, 4.811910e+18, 4.736088e-11, 1.770572e-08, 2.713978e-22, -1.649841e-12, -2.486590e+10, 4.092716e-18, 8.724120e-03, -1.183435e+18, -3.904438e+08, -1.251365e-11, -4.007750e+19, -2.206836e-16, 4.014728e-13, -3.960975e-12, 7.192824e+05, 1.981836e+04, 1.840814e+16, 1.488579e-16, -4.862226e-06, 1.612923e-17, -4.978203e-04, -2.305889e-02, 7.627221e+13, 4.014563e-03, 2.388221e-03, -1.129986e-02, 4.055276e+10, 3.842121e-10, -8.588514e-04, 1.299077e-12, -3.331850e-12, 4.863277e-01, -2.250328e-11, -2.261245e+04, -2.770899e+09, -4.710672e-15, -2.267765e+06, 1.582168e-09, 3.664505e-06, -1.507921e+12, 5.460120e+09, -3.256706e-15, 3.012178e-12, 2.274894e+15, -9.664342e-18, -2.770443e-15, -1.955281e-06, 4.768349e+01, -7.679375e-19, 2.774544e-17, -4.928044e-17, 7.602063e-15, 2.506718e-12, -2.794058e+11, 4.329292e+03, -4.041289e-02, 4.035282e-19, 8.577361e-04, 4.197333e-18, -3.509270e-01, -1.711871e-12, 4.578825e-02, -8.783497e-13, 3.862885e+17, 4.219735e+13, 4.281035e-21, 3.323068e-03, 4.931847e-11, 4.032955e-21, -4.373013e-03, 1.592633e-16, -4.484112e-16])
        if (len(value.dstruct2)!=2): raise Exception()
        ca (value.dstruct2["ctest1"].mydat,[4.122753e+13, -2.656829e-13, 1.813864e-04, -4.675181e-05, 1.759511e-19, 3.517805e+10, -7.912215e+01, 7.708557e-07, 2.434017e-21, -2.540544e+00, -9.412568e+15, -2.124215e-18, 2.797799e+13, -2.240464e-07, 2.780110e-12, -1.025574e-14, -3.762272e-09, -5.715981e-02, 1.839704e-21, -4.719538e-15, 3.148156e-06, 3.483886e-12, 3.484006e-02, -4.544817e-08, 3.200642e+00, 4.503141e+07, -4.077123e+04, -2.776985e+00, -2.900651e-18, -1.463711e+08, -3.460292e-03, 2.348911e-18, -3.704219e+08, -3.275364e+05, 4.613595e-01, 4.867108e+16, 4.114866e-10, 3.070767e+17, 4.662623e+01])
        ca(value.dstruct2["anothertest"].mydat,[-1.037656e+15, -3.782364e-06, 4.982303e+06, -5.510401e-07, 4.271118e-02, -1.718093e+11, -2.644457e+01, -2.374043e-08, 1.729038e-14, 3.370840e+10, 4.302550e-13, 2.643402e+14, 3.199649e+01, 4.620204e-08, 1.323645e+00, -4.337167e-07, -5.003428e+11, 4.176127e+13, 3.324907e-09, -4.207938e-09, -3.324360e-15, 3.317889e+00, 1.775668e+07, -1.295276e-15, -1.610388e-05, 3.417067e-02, -4.874588e+04, -2.109628e+12, 3.130648e+09, 1.898554e-13, 2.421724e-01, 4.227281e-08, 4.844407e+19, -4.490481e+10, 2.599780e+00, 4.039296e+06, -2.944167e-03, -7.388370e+08, -4.473409e-02])
        if (len(value.lstruct3)!=2): raise Exception()
        ca (value.lstruct3[0].mydat,[4.122753e+13, -2.656829e-13, 1.813864e-04, -4.675181e-05, 1.759511e-19, 3.517805e+10, -7.912215e+01, 7.708557e-07, 2.434017e-21, -2.540544e+00, -9.412568e+15, -2.124215e-18, 2.797799e+13, -2.240464e-07, 2.780110e-12, -1.025574e-14, -3.762272e-09, -5.715981e-02, 1.839704e-21, -4.719538e-15, 3.148156e-06, 3.483886e-12, 3.484006e-02, -4.544817e-08, 3.200642e+00, 4.503141e+07, -4.077123e+04, -2.776985e+00, -2.900651e-18, -1.463711e+08, -3.460292e-03, 2.348911e-18, -3.704219e+08, -3.275364e+05, 4.613595e-01, 4.867108e+16, 4.114866e-10, 3.070767e+17, 4.662623e+01])
        ca(value.lstruct3[1].mydat,[-1.037656e+15, -3.782364e-06, 4.982303e+06, -5.510401e-07, 4.271118e-02, -1.718093e+11, -2.644457e+01, -2.374043e-08, 1.729038e-14, 3.370840e+10, 4.302550e-13, 2.643402e+14, 3.199649e+01, 4.620204e-08, 1.323645e+00, -4.337167e-07, -5.003428e+11, 4.176127e+13, 3.324907e-09, -4.207938e-09, -3.324360e-15, 3.317889e+00, 1.775668e+07, -1.295276e-15, -1.610388e-05, 3.417067e-02, -4.874588e+04, -2.109628e+12, 3.130648e+09, 1.898554e-13, 2.421724e-01, 4.227281e-08, 4.844407e+19, -4.490481e+10, 2.599780e+00, 4.039296e+06, -2.944167e-03, -7.388370e+08, -4.473409e-02])
        
        numpy.testing.assert_allclose(value.multidimarray, numpy.array([2.430620e+07, -3.455593e-03, 3.902400e+12, -2.638755e-03, 3.850613e+07, 4.754008e-11, 4.661031e-06, -3.707214e-19, -7.073631e+02, 2.254953e-04, -1.575093e-16, 5.197798e-13, -9.801721e+03, -1.787872e+19, -3.366880e-19, -6.242096e-19, 4.750613e+12, 2.200462e-07, 2.175487e+10, -4.574155e+13, -2.009829e-18, 4.228100e-10, -3.002835e-06, -4.486729e+06, 5.433280e-05, -1.966891e-02, -3.934083e+11, 3.893263e-01, 2.139116e-13, 2.223028e+19, -9.567949e+17, -2.740272e+16, 1.099169e-03, -1.569567e+07, 1.960769e-10, 2.839805e-11, -4.907690e-21, 2.112493e-18, -4.618149e-10, 2.613307e+14, 2.590624e-17, 3.838474e+13, 3.249062e-08, -3.456972e-02, -5.653457e-19, -3.560782e-17, 4.205253e+10, -1.775030e-11, -2.490865e+04, -2.059649e-07, 1.126958e+00, 1.236458e+16, 4.050441e+17, 3.706921e+11, -5.893431e-13, -3.802021e-05, 4.939106e-17, -2.295579e+11, 2.784939e-18, 2.251843e+07, 4.187086e+13, -8.627249e-13, -1.636854e-09, 3.436699e+05, -1.494004e-06, 1.669621e-05, 4.224858e-11, -1.206711e-21, -4.717112e-12, 2.149234e+09, 4.829485e-12, -9.782035e-03, -4.809568e+11, -2.363817e-20, -1.774867e-19, 2.675132e-08, -3.796278e+06, 8.447614e-11, -2.926861e+01, -3.179427e+19, -2.686571e+01, 4.629595e-21, -4.785666e-19, 1.189135e+05, 3.103998e-16, 9.759246e-06, 1.974804e-15, -2.446973e-18, -2.116347e-10, 3.372892e+14, 3.756516e+18, 1.818836e-01, 5.930870e+08, -2.908608e+14, -4.900761e+01, -1.467246e+11, -2.431436e-08, -2.025905e-13, 6.246066e+01, 1.601360e+13]).reshape([10,10], order="F"))
        ca(value.var3.data,[6.404176e-12, 9.258110e-03, 8.657620e-03, -2.064381e+00, 5.182360e-16, 4.167658e-16, -4.533051e-19, 5.357520e+18, -4.990383e-13, 2.286982e+08, -4.727256e-18, 1.465299e-17, 3.000340e-10, -2.304453e-04])

    @property
    def struct2(self):
        out=RobotRaconteurNode.s.NewStructure("com.robotraconteur.testing.TestService1.teststruct2")
        out.mydat=[-4.415088e+16, -2.033093e-17, 3.634431e-17, 2.030794e-03, 4.464343e-14, -4.137056e+11, 3.609991e-16, 4.332970e-11, 1.327470e-06, -3.304680e+02, 3.184654e-08, 1.194960e-16, -2.958549e+05, -3.320274e+13, 3.486845e-05, 2.878185e-10, -2.982726e-12, -3.653410e-06, 2.059068e+00, 1.150498e+16, -3.647068e+18, -3.847760e+03, -4.333684e-21, -2.357376e-07, -2.560470e-09, 2.931250e-15, 4.966713e-21, 2.960478e-14, -1.959583e+03, 4.593629e-16, 4.193491e-07, 5.941674e+14, 2.198075e+05, 1.487817e-20, -4.643292e+06, 2.543864e-14, 9.478332e+04, 2.948237e+13, -3.144190e-17, -1.369134e+11, -4.908672e-18, -3.581399e-21, -1.682968e-14, -8.984437e-02, 3.067043e-19, -3.361220e+14, -2.591105e-10, -2.119291e-13, 7.649594e+03, -1.869427e-01, -3.403057e+11, -4.798229e-09, -4.120069e+04, 3.384741e-12, 4.697254e-10, -3.594572e-02, -1.973059e+12, -2.627069e-21, 4.096077e-20, 1.629242e-20, -1.561816e+11, 3.240449e+07, -3.967391e+08, 4.635131e-14, -3.436364e-17, 1.485817e-15, -2.145973e+18, 1.160688e+19, 3.266439e+11, 1.686854e+02, -4.048943e+00, -2.905109e+17, -3.953827e+15, -2.855712e+10, -1.197294e-02, -1.997014e+14, 3.951602e+08, 1.287972e+18, -4.228933e+08, 4.212816e-06, -1.252397e+15, 3.517842e+12, -3.315039e-17, -1.816738e+19, 3.595783e+14, -2.834015e-08, 3.436611e+04, -4.192603e+12, 1.152454e+11, -9.405739e-21, -1.862898e+17, -3.811397e-10, 4.486272e+00, 3.666408e+14, -2.681908e-10, -4.859125e+08, -3.593152e+04, -1.883343e-03, -2.445939e-08, 4.540371e+01]
        return out
    @struct2.setter
    def struct2(self,value):
        ca(value.mydat,[-1.451096e-09, -3.762302e-18, 2.016877e+04, -4.171245e+16, 1.500851e+09, -3.071385e-05, 1.329949e+09, 9.439580e-14, 8.652806e-06, -2.729712e-17, -1.664008e-09, 3.787440e-16, -4.281157e-20, -8.703642e-07, 7.130173e-13, 1.162347e-04, -2.485922e-01, 8.924836e+13, 2.150995e+18, -1.816269e-08, 3.572064e-06, -1.020374e+19, -2.467612e-05, 1.294111e-21, 3.030328e-11, 1.736324e+04, 4.221306e+17, -2.544109e+09, 1.047630e-04, 2.082666e+04, -4.120572e-04, -4.550228e-11, -4.959645e+00, 3.988634e-06, -2.901463e-06, 4.379435e+14, 3.697324e+17, -3.285280e+00, -4.491892e-21, 4.962405e-03, -4.143004e-05, 4.447309e+01, 3.196998e-04, -1.679927e+06, -1.859794e+19, -2.749978e-17, -9.042867e+14, 3.970588e+06, -2.359863e-19, 4.923781e-03, 3.689224e-03, 1.741368e-14, -4.943555e-15, -2.473041e-09, -1.687125e-12, 4.622096e+17, 2.456838e-17, -4.076597e+07, -4.082942e-21, -4.483141e+19, 2.463502e-01, -1.818087e+04, 1.094518e+14, 7.514618e+03, -1.175704e-07, -3.071050e+18, -8.006996e-20, 1.363550e-14, -6.753529e+08, -4.661760e+15, -2.475629e-01, -1.282411e+16, -6.328699e-04, 4.898115e+00, 6.921801e-14, 9.951973e+01, 1.669967e-08, -3.750408e-19, -3.363050e-10, -2.470083e-09, 1.544354e-05, -2.844838e-09, 4.426875e+02, 3.468203e-17, -2.376018e+07, -1.431106e+08, -6.900572e-18, -4.640801e+07, 9.947893e+14, -1.166791e+10, -3.478840e+19, -3.103020e-09, -3.256701e+00, 4.374203e-14, 4.655054e-04, -4.106246e-17, 2.373568e+15, -1.319790e-04, 1.485607e+02, -4.933523e-05])

    @property
    def struct3(self):
        out=RobotRaconteurNode.s.NewStructure("com.robotraconteur.testing.TestService2.ostruct2")
        out.a1=[-8.483090e-19, -4.401548e-08, 3.908118e+00, 2.063513e-18, 4.237047e+18, -1.124681e-16, 3.924541e-01, -2.184335e-10, -1.978950e+11, 1.586365e+18, 1.712393e+00, -6.314723e+00, 1.196777e-16, -2.748704e-08, -1.289967e+02, -4.051137e+17, -1.902860e+10, -2.070486e+08, 3.622651e+06, 1.315398e+17]
        return out
    @struct3.setter
    def struct3(self,value):
        ca(value.a1,[-2.426765e+05, -9.410735e+01, -1.667915e+12, -4.084240e-05, 3.199460e+03, 8.256717e-12, -4.772119e-11, -1.061407e-13, 2.759750e+02, -1.212549e+10, 7.012690e+15, 3.953354e+04, -2.617985e-07, 1.104408e-21, -3.889366e+00, 4.549493e+16, -1.376791e+15, -3.445205e-21, 2.137830e-14, 4.620179e+18])

    @property
    def is_d1(self):
        return {9285 : 1.643392e-01, 74822 : 1.537133e+09, 4 : 1.369505e-03}
    @is_d1.setter
    def is_d1(self,value):
        if (len(value)!=3): raise Exception()
        if (value[928]!=4.074501e-07): raise Exception()
        if (value[394820]!= -4.535303e+05): raise Exception()
        if (value[623]!=-2.956241e-20): raise Exception()

    @property
    def is_d2(self):
        return {"testval1" : -1.079664e+16, "testval2" : 2.224846e+00}
    @is_d2.setter
    def is_d2(self,value):
        if (len(value)!=2): raise Exception()
        if (value["testval3"]!=5.242474e+10): raise Exception()
        if (value["testval4"]!=2.208636e+08): raise Exception()

    @property
    def is_d3(self):
        out={}
        out[12]= [8.609080e-13, 3.946603e+03, 2.994203e-10, 3.200877e+14, 1.747361e-09, 2.827056e-16, -3.676613e-18, 1.886901e-14, -9.970511e-12, 1.932468e-18, -3.629253e-05, 4.903023e-12, -3.919949e-10, 4.982164e+07, 3.823096e-20, -4.044068e-13, 3.114078e+09, 7.572697e-12, -2.619929e+04, -3.882046e+01]
        out[832]= [4.750899e+00, 3.924377e+18, -2.735066e+17, 4.095362e-21, -2.407932e+09, 4.059499e+10, 1.376975e-10, -8.547220e-21, -1.344568e-20, 2.809398e+03, 2.118944e-06, 2.435328e-03, -1.410999e-12, 9.907226e-04, -9.745948e-20, 1.270118e+15, -2.833333e+05, 1.032636e-10, 5.312574e+13, -2.651512e+02]
        return out
    @is_d3.setter
    def is_d3(self,value):
        if (len(value)!=2): raise Exception()
        ca(value[47], [4.335907e-08, -3.270294e-03, 1.752801e-01, 1.235219e-20, -4.348647e+02, -4.503864e-21, -3.316231e+15, -2.080056e+17, 1.813854e+13, -3.380846e-05, 4.350998e+03, 4.539570e+11, 8.981827e+09, 3.326114e+01, 2.975688e+06, -1.017456e-12, 2.989498e-03, 2.842392e-03, -1.258677e-21, 1.068563e-15])
        ca(value[324], [3.239279e+12, 1.047689e+17, -1.236114e+17, -4.002822e-17, 2.657374e-03, 7.383907e-19, -5.067889e-13, -4.195122e-12, 3.642885e-01, -2.946040e+14, 5.522403e-08, 6.603132e+04, 1.464154e+05, -1.851534e-08, 2.808294e-13, -2.702278e-11, 3.850704e-06, -2.453957e+02, -3.015401e-02, 1.654070e+05])

    @property
    def is_d4(self):
        out={}
        out["testval1"]= [1.113851e-04, 3.830104e+07, 4.571169e-21, -4.064180e-05, 2.889736e+01, -1.790060e-06, 4.608538e+00, 4.687713e-04, 1.387717e-08, 3.914187e-18, -5.618118e-06, 1.530811e+05, -5.848922e-11, -3.397558e-20, -6.597368e-08, -3.779049e-06, 2.406033e-19, 2.507939e-10, 3.246113e-20, 1.341205e+16]
        out["testval2"]= [-3.088190e-13, -4.033334e-20, 4.150103e-21, -6.610855e+17, 3.688824e-13, -3.208025e+13, -5.034888e-11, -4.098363e-06, -1.272830e-03, 2.748392e-03, -2.644272e-06, -4.810065e-18, 4.629861e-19, -5.444015e-03, 4.046008e+17, -3.548079e+12, -3.455290e+16, -3.668946e-12, -3.522178e-01, -1.537583e+14]
        return out
    @is_d4.setter
    def is_d4(self,value):
        if (len(value)!=2): raise Exception()
        ca(value["testval3"], [1.771838e+06, 3.037284e-01, -1.739742e-02, 1.399508e-20, 3.605232e-21, 3.517522e+14, 4.887514e+14, 3.505442e-03, -3.968972e+18, 1.422037e-20, 2.596937e-21, 4.852833e-11, 6.852955e-17, 4.765526e-12, -3.445954e+16, 2.322531e-14, -1.755122e-12, 3.941875e+00, 8.877046e-13, 2.818923e-02])
        ca(value["testval4"], [4.146439e+16, 2.923439e-07, 3.549608e+16, -1.664891e-01, -4.192309e-15, 3.857317e+05, -1.101076e+00, 1.213105e+19, 3.237584e-14, -2.421219e-06, -4.603196e-05, -3.719535e-10, 1.124961e+06, 2.032849e+10, 4.639704e-22, 3.946835e+01, -9.267263e+01, -4.456188e+11, 3.470487e+08, 7.918764e+10])

    @property
    def is_d5(self):
        out={}
        out1=numpy.array([-2.240130e+14, 1.609980e+16, -1.794755e+07, 8.108785e+17, -2.296286e+08, -2.689029e+13, 2.036672e+07, -4.822871e-02, 4.070748e-05, -2.894952e-04, -1.728526e+17, 4.077694e-19, -2.977734e+13, -9.428667e+03, 2.672315e-08, -1.844359e+19, 4.243010e+09, 4.592716e-01, -3.792531e+10, 3.117892e+04, -1.830821e-16, -3.702984e-18, -1.957300e+12, 9.017553e+12, -2.184986e-17, 1.436890e-02, 4.008279e-12, -2.407568e+10, -3.170667e-07, -2.315539e+16, 6.646599e+09, 2.443847e-01, 1.928730e-21, 3.089540e+00, 2.813232e-02, 1.352336e-21, -3.562256e+05, 3.778036e+08, -3.726478e-13, 3.112159e+15, 3.573414e+17, 3.607559e+09, -2.923247e-19, -2.079346e+14, -4.611547e-16, 2.200040e+00, 3.670772e+07, -4.176987e-20, 2.086575e+06, -2.388241e+01, -3.759717e-19, -2.232760e-01, 9.066157e-21, 2.797633e+07, 3.455296e+00, -3.306761e-08, -2.062866e-22, -4.653724e+07, -3.694312e-17, 2.254095e-06, 3.519767e-16, 1.292737e-06, -3.840896e-08, -1.946825e-20, 2.639141e+18, 3.021503e+07, -1.834066e+18, 4.474920e-02, 3.005033e-20, -1.233782e-10, -3.260111e-08, 2.326419e-09, -2.298222e-19, 7.554873e+15, 2.378479e+19, -5.092127e-03, -4.724838e-07, 3.204184e+06, 2.713748e-12, 1.574309e-05, 6.622323e-01, -4.944461e-01, -1.559672e+19, -3.350494e+15, 2.467451e-14, -4.881873e+13, 1.031263e+15, -4.051814e+12, 1.418548e+07, 1.204368e+17, -4.113152e-02, -4.472069e+16, 4.896886e-14, 2.371633e+05, 3.543019e+04, -3.083516e-22, 1.041761e-09, -2.579812e-06, -2.937567e+09, -4.775349e-16]).reshape([10, 10], order="F")
        out[564]=out1
        return out

    @is_d5.setter
    def is_d5(self,value):
        if (len(value)!=1): raise Exception()
        in1=value[328]       
        numpy.testing.assert_allclose(in1,numpy.array([2.792909e-01, 6.554477e+16, 4.240073e-13, -4.490109e+19, 5.410527e-22, -2.244599e+17, -2.656142e-02, -3.819500e+13, -7.086082e-02, 7.790729e-13, 3.375900e-12, -6.915692e+09, -2.900437e-18, 1.257280e+05, -3.810852e+15, -4.589554e-12, 2.670612e-14, 4.725686e+06, -3.018046e+07, 2.439452e+07, 2.726039e-07, -2.805143e+02, -1.870376e+03, 4.573047e-06, 1.904868e+19, -1.966383e+00, 3.426469e-11, -1.400396e+13, -1.724273e+09, -7.347198e+10, -4.081057e-12, -3.868203e+10, -2.686071e+13, -5.289107e+01, -5.574151e-09, -2.580185e-06, -8.222097e-21, -4.957833e-12, -2.491984e+03, -7.900042e+16, -4.809370e-11, -2.048332e-19, 4.984852e-21, 1.350023e+13, -4.492022e-11, -3.255594e+10, 1.495149e-09, -7.272628e+02, -4.236196e-04, 4.736990e-02, -4.030173e-11, 1.017371e+11, 1.124559e-09, 4.177431e-21, 1.026706e+06, -4.702729e-04, -2.633498e+18, -4.689724e+08, -2.593657e+05, 3.433194e-18, -1.977738e-13, -1.163773e+03, 3.424738e-20, 7.391132e-06, 1.364867e+12, -7.155727e+16, 3.078093e-21, -3.151787e-04, -4.715633e+06, 1.017894e+19, -1.121778e+14, -3.529769e-10, 4.530606e+19, 3.988296e-17, -3.469818e+06, 1.204304e+03, -1.404314e+15, -1.369871e+04, -2.796125e-03, -4.842068e-06, -2.639632e-03, 1.324740e+08, 1.440651e+07, -4.778885e+03, -4.643859e+06, 1.726955e-09, -8.160334e+05, 3.763238e+13, 1.391028e+02, -4.269393e+04, -2.698233e+02, -3.677556e+14, 1.070699e-17, 3.949376e+19, 4.503080e-06, 4.344496e-07, 1.714091e-19, -3.436426e+01, 4.914505e+15, -1.101617e+09, -1.899511e-04, 2.195951e-06, 2.402701e-12, 1.783431e-09, -7.329137e-08, 4.423889e+16, 2.812547e-19, -7.848554e+05, -3.635151e+13, 3.128605e-09, -2.858963e+08, 2.086065e-11, -2.544450e+12, 1.450579e+19, -1.508905e+13, 4.307174e+00, 1.038108e-05, 4.313281e-05, 3.647351e+05, 1.309105e-16, 4.180469e+13, -2.701332e-07, -4.033566e+14, -3.116748e-06, 2.342296e-07, 1.870335e-19, 2.312273e+01, -4.478923e+08, -4.854324e+09, 2.681828e+03, -4.280128e-01, -4.690703e-21, 3.853815e+16, 1.366639e+02, -2.944985e-11, -4.486958e-13, 3.017750e-11, 3.551437e-13, 2.263828e-12, -6.545014e-18, -7.552023e+12, 7.595238e+14, 2.810247e+12, 6.516008e+15, -3.035786e+14, 2.523040e+11, -3.766603e+09, 7.316287e+18, -2.147132e+17, 1.972210e+10, 2.906768e-13, 4.226577e-14, -2.640568e+17, 2.181408e+10, -1.043256e-08, -3.649181e+06, -2.776638e+18, 3.660147e-07, -1.415433e-17, -4.945127e-17, 2.655050e+01, -2.269828e+04, -2.585499e-01, -3.299965e+05, 3.707494e-18, -1.257923e-19, -1.321880e+14, -1.815888e-12, 9.366926e-09, 1.024923e-14, 4.494907e+04, -2.596971e-20, -3.403446e-12, 1.537084e+17, -3.850430e-17, -4.821759e+05, 4.255435e-20, -1.016978e-16, 1.430658e-09, -3.696861e-14, -4.427905e-19, -1.999724e-09, -3.489402e-06, -4.677864e-03, 1.246884e+13, -4.458271e-19, 3.551905e-04, -4.458221e-20, -3.472033e+01, -1.745714e+08, 4.396891e+03, 4.345767e+02, -1.800116e+05, -1.217318e+00, 3.605072e-08, 1.306109e-09, -2.798295e+16, 4.387728e-13, -3.284039e+11, 3.424124e+17]).reshape((10,20), order="F"))

    @property
    def is_d6(self):
        out={}
        out1=numpy.array([4.229153e+02, 3.406523e+03, -2.158208e+15, -7.464845e+07, -4.763504e+18, 6.777497e-20, -1.265130e+18, 2.145141e+12, -8.473642e-18, -3.780104e+17, -4.356069e+06, 1.199990e+04, -2.413259e+07, -2.609077e-12, -2.121030e-16, -1.224176e+09, -2.836294e-15, -1.975701e-18, 4.311314e-04, -4.932020e-20, -1.307735e-18, -4.000536e+02, -1.718325e+15, -3.493595e+05, 1.707089e+00, 4.416780e+01, -1.152954e-13, 8.396437e-02, -4.304750e+16, 1.154166e+02, -2.331328e-02, 4.821737e-04, 5.831989e-20, -6.887913e+06, -1.592772e+11, 4.730754e-19, 2.543760e-17, -5.864767e+14, 2.077122e-13, 2.801695e-12, -1.171678e+12, -8.854966e+18, -1.555508e-08, 3.589410e+11, -1.495443e-21, 2.876586e-06, -2.265460e-03, 2.544109e-03, 2.019117e-06, -6.458547e-21]).reshape([5, 10], order="F")
        out["testval1"]=out1
        return out
    @is_d6.setter
    def is_d6(self,value):
        if (len(value)!=1): return Exception()
        in1=value["testval2"]        
        numpy.testing.assert_allclose(in1,numpy.array([2.080438e+03, -2.901444e-01, 2.561452e+12, 6.760682e+14, -2.461568e-10, -4.811907e-20, 6.299564e+11, -2.660066e-19, 4.643316e+13, 3.292265e-13, 1.187460e+19, 3.054313e-07, 3.503026e-20, -1.465147e-08, 3.993039e-17, 2.469296e-10, -4.014504e+07, 1.810733e+17, -3.976509e-19, -9.166607e+15, 1.854678e+02, 2.884879e-12, -4.382521e+14, 3.064407e-05, -9.542195e+07, -3.938411e-13, -2.850416e-03, 3.042038e+14, 1.464437e-12, -1.550126e-06, 4.938341e+11, -3.517527e+19, 3.135793e+19, 1.380313e-14, -1.060961e+18, 2.833127e-10, -1.862230e+02, -2.232851e-05, 4.773548e-05, 3.746071e+13, -4.972451e+09, 4.553754e-14, -8.183438e+10, 3.739120e+18, -1.619189e+19, 4.644394e+08, -8.327578e-11, 4.080876e-02, -2.806082e-03, -1.595033e-06, 1.973067e+16, 2.989575e-07, -8.974247e+15, -4.204211e-03, 1.513025e-02, -4.604953e+03, 4.107290e+16, -3.631920e+12, -1.902472e+13, -4.186326e-14, 2.465135e+13, 5.060414e+12, 7.508582e+11, 3.233186e-14, -6.750005e+14, -9.467336e-16, 2.101440e+03, -1.162425e+08, 7.808216e+04, 4.356208e-19, -3.316834e+14, 3.299774e-19, -3.746431e-16, -3.971172e-07, 2.423744e+10, 1.542747e+17, 2.358704e-05, 4.201668e+17, -3.736856e+07, 3.585645e-07]).reshape([8, 10], order="F"))

    @property
    def is_str1(self):
        return {23 : "Hello server"}
    @is_str1.setter
    def is_str1(self,value):
        if (len(value)!=1): raise Exception()
        if (value[24]!="Hello client"): raise Exception()

    @property
    def is_str2(self):
        return {"testval1": "Hello server"}
    @is_str2.setter
    def is_str2(self,value):
        if (len(value)!=1): raise Exception()
        if (value["testval2"]!="Hello client"): raise Exception()

    @property
    def is_struct1(self):
        out={}
        out1=RobotRaconteurNode.s.NewStructure("com.robotraconteur.testing.TestService1.teststruct2")
        out1.mydat=[-9.692618e+00, -1.944240e+03, -2.456327e+16, 4.673405e-20, 5.147581e-14, -3.773975e+15, 2.336430e-21, 1.597144e-18, -2.609059e-03, 3.557639e-21, -1.666575e-16, -4.242788e-07, 2.686206e+07, -3.200902e-05, -1.549754e-06, -3.010796e-12, 4.638418e+01, 2.664397e-14, -2.689174e+01, 4.564584e-21]
        out[748]=out1
        return out
    @is_struct1.setter
    def is_struct1(self,value):
        if (len(value)!=1): raise Exception()
        ca(value[372].mydat,[-2.101948e-07, -2.594836e-08, 2.515710e+01, -3.834127e-14, -3.088095e+06, -3.256612e-02, -1.855481e-19, 3.801916e+07, 2.145894e+09, 4.487676e+12, 1.351202e-02, -1.125124e-16, 1.369826e-20, -2.290673e+00, 1.786029e-20, -4.991515e+08, 4.006107e-10, -4.947871e-11, -2.737020e-08, 4.123759e-20])

    @property
    def is_struct2(self):
        out={}
        out1= RobotRaconteurNode.s.NewStructure("com.robotraconteur.testing.TestService1.teststruct2")
        out1.mydat=[-4.489570e+13, 9.574895e-05, 4.081711e+06, 5.612839e-18, -1.078604e+05, 3.658139e+08, -4.748975e+05, -2.606481e+01, 3.016739e+15, 3.174709e+19, -4.572549e+17, 1.980389e-04, -3.551911e-10, 3.598401e-07, 2.659416e-12, -3.606157e+06, 2.059674e+17, -9.362336e-20, -3.299256e+17, -2.245745e+16]
        out["testval1"]=out1
        return out
    @is_struct2.setter
    def is_struct2(self,value):
        if (len(value)!=1): raise Exception()
        ca(value["testval2"].mydat,[6.931327e-21, 4.527137e-02, 1.260822e-18, 3.592805e-12, 1.088317e-05, 3.305865e+03, -9.798828e-20, 1.497504e+18, -3.653592e+01, 1.473952e+10, -1.003612e-20, 1.302159e+18, -8.544326e+05, 1.038521e+16, -2.845746e-18, -3.899909e-04, 4.785560e-02, -7.203365e-12, -1.500022e-14, -1.892753e-17])

    @property
    def list_d1(self):
        return [1.643392e-01, 1.537133e+09, 1.369505e-03]
    @list_d1.setter
    def list_d1(self,value):
        if (len(value)!=3): raise Exception()
        if (value[0]!=4.074501e-07): raise Exception()
        if (value[1]!= -4.535303e+05): raise Exception()
        if (value[2]!=-2.956241e-20): raise Exception()

    @property
    def list_d3(self):
        out=[]
        out.append( [8.609080e-13, 3.946603e+03, 2.994203e-10, 3.200877e+14, 1.747361e-09, 2.827056e-16, -3.676613e-18, 1.886901e-14, -9.970511e-12, 1.932468e-18, -3.629253e-05, 4.903023e-12, -3.919949e-10, 4.982164e+07, 3.823096e-20, -4.044068e-13, 3.114078e+09, 7.572697e-12, -2.619929e+04, -3.882046e+01])
        out.append( [4.750899e+00, 3.924377e+18, -2.735066e+17, 4.095362e-21, -2.407932e+09, 4.059499e+10, 1.376975e-10, -8.547220e-21, -1.344568e-20, 2.809398e+03, 2.118944e-06, 2.435328e-03, -1.410999e-12, 9.907226e-04, -9.745948e-20, 1.270118e+15, -2.833333e+05, 1.032636e-10, 5.312574e+13, -2.651512e+02])
        return out
    @list_d3.setter
    def list_d3(self,value):
        if (len(value)!=2): raise Exception()
        ca(value[0], [4.335907e-08, -3.270294e-03, 1.752801e-01, 1.235219e-20, -4.348647e+02, -4.503864e-21, -3.316231e+15, -2.080056e+17, 1.813854e+13, -3.380846e-05, 4.350998e+03, 4.539570e+11, 8.981827e+09, 3.326114e+01, 2.975688e+06, -1.017456e-12, 2.989498e-03, 2.842392e-03, -1.258677e-21, 1.068563e-15])
        ca(value[1], [3.239279e+12, 1.047689e+17, -1.236114e+17, -4.002822e-17, 2.657374e-03, 7.383907e-19, -5.067889e-13, -4.195122e-12, 3.642885e-01, -2.946040e+14, 5.522403e-08, 6.603132e+04, 1.464154e+05, -1.851534e-08, 2.808294e-13, -2.702278e-11, 3.850704e-06, -2.453957e+02, -3.015401e-02, 1.654070e+05])

    @property
    def list_d5(self):
        out=[]
        out1=numpy.array([-2.240130e+14, 1.609980e+16, -1.794755e+07, 8.108785e+17, -2.296286e+08, -2.689029e+13, 2.036672e+07, -4.822871e-02, 4.070748e-05, -2.894952e-04, -1.728526e+17, 4.077694e-19, -2.977734e+13, -9.428667e+03, 2.672315e-08, -1.844359e+19, 4.243010e+09, 4.592716e-01, -3.792531e+10, 3.117892e+04, -1.830821e-16, -3.702984e-18, -1.957300e+12, 9.017553e+12, -2.184986e-17, 1.436890e-02, 4.008279e-12, -2.407568e+10, -3.170667e-07, -2.315539e+16, 6.646599e+09, 2.443847e-01, 1.928730e-21, 3.089540e+00, 2.813232e-02, 1.352336e-21, -3.562256e+05, 3.778036e+08, -3.726478e-13, 3.112159e+15, 3.573414e+17, 3.607559e+09, -2.923247e-19, -2.079346e+14, -4.611547e-16, 2.200040e+00, 3.670772e+07, -4.176987e-20, 2.086575e+06, -2.388241e+01, -3.759717e-19, -2.232760e-01, 9.066157e-21, 2.797633e+07, 3.455296e+00, -3.306761e-08, -2.062866e-22, -4.653724e+07, -3.694312e-17, 2.254095e-06, 3.519767e-16, 1.292737e-06, -3.840896e-08, -1.946825e-20, 2.639141e+18, 3.021503e+07, -1.834066e+18, 4.474920e-02, 3.005033e-20, -1.233782e-10, -3.260111e-08, 2.326419e-09, -2.298222e-19, 7.554873e+15, 2.378479e+19, -5.092127e-03, -4.724838e-07, 3.204184e+06, 2.713748e-12, 1.574309e-05, 6.622323e-01, -4.944461e-01, -1.559672e+19, -3.350494e+15, 2.467451e-14, -4.881873e+13, 1.031263e+15, -4.051814e+12, 1.418548e+07, 1.204368e+17, -4.113152e-02, -4.472069e+16, 4.896886e-14, 2.371633e+05, 3.543019e+04, -3.083516e-22, 1.041761e-09, -2.579812e-06, -2.937567e+09, -4.775349e-16]).reshape([10, 10], order="F")
        out.append(out1)
        return out

    @list_d5.setter
    def list_d5(self,value):
        if (len(value)!=1): raise Exception()
        in1=value[0]
        numpy.testing.assert_allclose(in1,numpy.array([2.792909e-01, 6.554477e+16, 4.240073e-13, -4.490109e+19, 5.410527e-22, -2.244599e+17, -2.656142e-02, -3.819500e+13, -7.086082e-02, 7.790729e-13, 3.375900e-12, -6.915692e+09, -2.900437e-18, 1.257280e+05, -3.810852e+15, -4.589554e-12, 2.670612e-14, 4.725686e+06, -3.018046e+07, 2.439452e+07, 2.726039e-07, -2.805143e+02, -1.870376e+03, 4.573047e-06, 1.904868e+19, -1.966383e+00, 3.426469e-11, -1.400396e+13, -1.724273e+09, -7.347198e+10, -4.081057e-12, -3.868203e+10, -2.686071e+13, -5.289107e+01, -5.574151e-09, -2.580185e-06, -8.222097e-21, -4.957833e-12, -2.491984e+03, -7.900042e+16, -4.809370e-11, -2.048332e-19, 4.984852e-21, 1.350023e+13, -4.492022e-11, -3.255594e+10, 1.495149e-09, -7.272628e+02, -4.236196e-04, 4.736990e-02, -4.030173e-11, 1.017371e+11, 1.124559e-09, 4.177431e-21, 1.026706e+06, -4.702729e-04, -2.633498e+18, -4.689724e+08, -2.593657e+05, 3.433194e-18, -1.977738e-13, -1.163773e+03, 3.424738e-20, 7.391132e-06, 1.364867e+12, -7.155727e+16, 3.078093e-21, -3.151787e-04, -4.715633e+06, 1.017894e+19, -1.121778e+14, -3.529769e-10, 4.530606e+19, 3.988296e-17, -3.469818e+06, 1.204304e+03, -1.404314e+15, -1.369871e+04, -2.796125e-03, -4.842068e-06, -2.639632e-03, 1.324740e+08, 1.440651e+07, -4.778885e+03, -4.643859e+06, 1.726955e-09, -8.160334e+05, 3.763238e+13, 1.391028e+02, -4.269393e+04, -2.698233e+02, -3.677556e+14, 1.070699e-17, 3.949376e+19, 4.503080e-06, 4.344496e-07, 1.714091e-19, -3.436426e+01, 4.914505e+15, -1.101617e+09, -1.899511e-04, 2.195951e-06, 2.402701e-12, 1.783431e-09, -7.329137e-08, 4.423889e+16, 2.812547e-19, -7.848554e+05, -3.635151e+13, 3.128605e-09, -2.858963e+08, 2.086065e-11, -2.544450e+12, 1.450579e+19, -1.508905e+13, 4.307174e+00, 1.038108e-05, 4.313281e-05, 3.647351e+05, 1.309105e-16, 4.180469e+13, -2.701332e-07, -4.033566e+14, -3.116748e-06, 2.342296e-07, 1.870335e-19, 2.312273e+01, -4.478923e+08, -4.854324e+09, 2.681828e+03, -4.280128e-01, -4.690703e-21, 3.853815e+16, 1.366639e+02, -2.944985e-11, -4.486958e-13, 3.017750e-11, 3.551437e-13, 2.263828e-12, -6.545014e-18, -7.552023e+12, 7.595238e+14, 2.810247e+12, 6.516008e+15, -3.035786e+14, 2.523040e+11, -3.766603e+09, 7.316287e+18, -2.147132e+17, 1.972210e+10, 2.906768e-13, 4.226577e-14, -2.640568e+17, 2.181408e+10, -1.043256e-08, -3.649181e+06, -2.776638e+18, 3.660147e-07, -1.415433e-17, -4.945127e-17, 2.655050e+01, -2.269828e+04, -2.585499e-01, -3.299965e+05, 3.707494e-18, -1.257923e-19, -1.321880e+14, -1.815888e-12, 9.366926e-09, 1.024923e-14, 4.494907e+04, -2.596971e-20, -3.403446e-12, 1.537084e+17, -3.850430e-17, -4.821759e+05, 4.255435e-20, -1.016978e-16, 1.430658e-09, -3.696861e-14, -4.427905e-19, -1.999724e-09, -3.489402e-06, -4.677864e-03, 1.246884e+13, -4.458271e-19, 3.551905e-04, -4.458221e-20, -3.472033e+01, -1.745714e+08, 4.396891e+03, 4.345767e+02, -1.800116e+05, -1.217318e+00, 3.605072e-08, 1.306109e-09, -2.798295e+16, 4.387728e-13, -3.284039e+11, 3.424124e+17]).reshape([10,20],order="F"))

    @property
    def list_str1(self):
        return ["Hello server"]
    @list_str1.setter
    def list_str1(self,value):
        if (len(value)!=1): raise Exception()
        if (value[0]!="Hello client"): raise Exception()

    @property
    def list_struct1(self):
        out=[]
        out1=RobotRaconteurNode.s.NewStructure("com.robotraconteur.testing.TestService1.teststruct2")
        out1.mydat=[-9.692618e+00, -1.944240e+03, -2.456327e+16, 4.673405e-20, 5.147581e-14, -3.773975e+15, 2.336430e-21, 1.597144e-18, -2.609059e-03, 3.557639e-21, -1.666575e-16, -4.242788e-07, 2.686206e+07, -3.200902e-05, -1.549754e-06, -3.010796e-12, 4.638418e+01, 2.664397e-14, -2.689174e+01, 4.564584e-21]
        out.append(out1)
        return out
    @list_struct1.setter
    def list_struct1(self,value):
        if (len(value)!=1): raise Exception()
        ca(value[0].mydat,[-2.101948e-07, -2.594836e-08, 2.515710e+01, -3.834127e-14, -3.088095e+06, -3.256612e-02, -1.855481e-19, 3.801916e+07, 2.145894e+09, 4.487676e+12, 1.351202e-02, -1.125124e-16, 1.369826e-20, -2.290673e+00, 1.786029e-20, -4.991515e+08, 4.006107e-10, -4.947871e-11, -2.737020e-08, 4.123759e-20])



    @property
    def is_struct3(self):
        out=RobotRaconteurNode.s.NewStructure("com.robotraconteur.testing.TestService2.ostruct2")
        out.a1=[-8.483090e-19, -4.401548e-08, 3.908118e+00, 2.063513e-18, 4.237047e+18, -1.124681e-16, 3.924541e-01, -2.184335e-10, -1.978950e+11, 1.586365e+18, 1.712393e+00, -6.314723e+00, 1.196777e-16, -2.748704e-08, -1.289967e+02, -4.051137e+17, -1.902860e+10, -2.070486e+08, 3.622651e+06, 1.315398e+17]
        return out
    @is_struct3.setter
    def is_struct3(self,value):
        ca(value.a1,[-2.426765e+05, -9.410735e+01, -1.667915e+12, -4.084240e-05, 3.199460e+03, 8.256717e-12, -4.772119e-11, -1.061407e-13, 2.759750e+02, -1.212549e+10, 7.012690e+15, 3.953354e+04, -2.617985e-07, 1.104408e-21, -3.889366e+00, 4.549493e+16, -1.376791e+15, -3.445205e-21, 2.137830e-14, 4.620179e+18])

    @property
    def var_num(self):
        return RobotRaconteurVarValue([-1680284833, -54562307, 732107275, 1470526962, -1389452949, 256801409, 261288152, 1728150828, 1322531658, -1640628174, 1036878614, 511108054, 2057847386, 288780916, 996595759],"int32[]")
    @var_num.setter
    def var_num(self,value):
        ca(value.data,[-1046369769, 1950632347, 1140727074, -1277424443, 163999900, 970815027, 545593183, 514305170, 1896372264, 1385916382])

    @property
    def var_str(self):
        return RobotRaconteurVarValue("Hello Client!","string")
    @var_str.setter
    def var_str(self,value):
        if(value.data!="Hello Server!"): raise Exception()

    @property
    def var_struct(self):
        out=RobotRaconteurNode.s.NewStructure("com.robotraconteur.testing.TestService1.teststruct2")
        out.mydat=[-9.052731e+13, 4.151705e-17, -4.004463e+19, -2.838274e+03, 9.983314e+12, 2.764122e+10, -1.131486e+03, 2.418899e+12, 1.323675e-05, -4.602174e+13, 2.717530e+01, 1.193887e-10, -4.137578e+16, -1.246990e-19, 4.244315e-18, -2.833005e-08, 1.956266e-04, 4.130129e-21, 1.641708e-11, -4.488158e-19]
        return RobotRaconteurVarValue(out,"com.robotraconteur.testing.TestService1.teststruct2")
    @var_struct.setter
    def var_struct(self,value):
        ca(value.data.mydat,[-4.945426e-20, 1.763386e+13, 3.431578e-04, 4.411409e+17, -2.690201e+03, 3.025939e-10, -3.659846e+11, -4.780435e-10, -3.246816e+14, -1.815578e+04, 2.236455e+10, -4.639041e+14, 1.767930e+10, -1.636094e+05, -4.392462e-01, 2.225260e+04, -5.250245e+18, 8.755282e-12, 2.005819e-10, 2.702210e+04])

    @property
    def var_vector(self):
        out={}
        out[10]="Hello Client!"
        return RobotRaconteurVarValue(out,"string{int32}")
    @var_vector.setter
    def var_vector(self,value):
        if (len(value.data)!=1): raise Exception()
        if (value.data[11]!="Hello Server!"): raise Exception()

    @property
    def var_dictionary(self):
        out={}
        out["test1"]="Hello Client!"
        return RobotRaconteurVarValue(out,"string{string}")
    @var_dictionary.setter
    def var_dictionary(self,value):
        if (len(value.data)!=1): raise Exception()
        if (value.data["test2"]!="Hello Server!"): raise Exception()

    @property
    def var_list(self):
        out=["Hello Client!"]
        return RobotRaconteurVarValue(out,"string{list}")
    @var_list.setter
    def var_list(self,value):
        if (len(value.data)!=1): raise Exception()
        if (value.data[0]!="Hello Server!"): raise Exception()

    @property
    def var_multidimarray(self):
        return RobotRaconteurVarValue(numpy.array([-4.915597e-01, 3.892823e+00, 2.622325e+08, -7.150935e+04, 9.418756e+00, 3.633879e+18, 3.522383e-03, -4.989811e+05, 2.027383e-03, -3.153241e+12, -6.948245e-21, -3.198577e+14, 6.172905e+09, 3.849430e+15, 8.600383e+13, 4.079437e-17, 3.194775e+06, 4.222550e-18, 1.758122e+17, -1.018308e+03]).reshape([5, 4], order="F"),"double[*]")
    @var_multidimarray.setter
    def var_multidimarray(self,value):        
        numpy.testing.assert_allclose(value.data,numpy.array([3.792953e+00, 2.968121e-17, -3.976413e-15, 4.392986e+19, 2.197463e+10, -2.627743e-14, -2.184665e+17, 1.972257e-17, 9.929684e-03, -3.096821e+17, 3.598051e+11, -6.266015e-18, 1.811985e-11, 2.815232e-07, 7.469467e-06, 6.141798e+13, 3.105763e+09, -1.697809e-10, -4.141707e-17, 4.391634e+13]).reshape([5, 4],order="F"))

    @property
    def errtest(self):
        raise Exception()
    @errtest.setter
    def errtest(self,value):
        raise Exception()

    @property
    def nulltest(self):
        return None
    @nulltest.setter
    def nulltest(self,value):
        if (not value is None): raise Exception()

    #functions
    def func1(self):
        def timer_handler(ev):
            try:
                self.ev1.fire()
            except:
                traceback.print_exc()
        t = RobotRaconteurNode.s.CreateTimer(1,timer_handler,True)
        t.Start()
        

    def func2(self, d1, d2):
        def timer_handler(ev):
            try:                
                s=RobotRaconteurNode.s.NewStructure("com.robotraconteur.testing.TestService1.teststruct2")
                s.mydat=[d2]
                self.ev2.fire(d1,s)
            except:
                traceback.print_exc()
        t = RobotRaconteurNode.s.CreateTimer(1,timer_handler,True)
        t.Start()

    def func3(self, d1, d2):
        try:
            user=ServerEndpoint.GetCurrentAuthenticatedUser()
            if (user is None):
                print ("No user")
            else:
                print ("User is: " + user.Username)
                print ("Login time is " + str(user.LoginTime))
                print ("Last access time is " + str(user.LastAccessTime))
                print ("Privileges " + str(user.Privileges))
        except:
            #traceback.print_exc()
            print ("No user")
        print (str(RobotRaconteurNode.s.NowUTC()))



        try:

            isconnectionsecure=self.tcptransport.IsTransportConnectionSecure(ServerEndpoint.GetCurrentEndpoint())
            if (isconnectionsecure):
                ispeerverified=self.tcptransport.IsSecurePeerIdentityVerified(ServerEndpoint.GetCurrentEndpoint())
                if (not ispeerverified):
                    print ("Peer identity is not verified")
                else:
                    print ("Peer identity is: " + self.tcptransport.GetSecurePeerIdentity(ServerEndpoint.GetCurrentEndpoint()))
        except:
            traceback.print_exc()
            raise

        return d1+d2

    def meaning_of_life(self):
        return 42

    def func_errtest(self):
        raise Exception("This is a test")

    def func_errtest1(self):
        raise DataTypeException("This is a test 1")

    def func_errtest2(self):
        e=RobotRaconteurNode.s.GetExceptionType("com.robotraconteur.testing.TestService1.testexception1")
        raise e("This is a test 2")

    def func_errtest3(self):
        e=RobotRaconteurNode.s.GetExceptionType("com.robotraconteur.testing.TestService2.testexception3")
        raise e("This is a test 3")

    #objrefs
    def get_o1(self):
        return self._o1, "com.robotraconteur.testing.TestService1.sub1"

    def get_o2(self,ind):
        iind=int(ind)
        with self._o2_lock:
            if (not iind in self._o2):
                self._o2[iind]=sub1_impl()
                self._o2[iind].i_ind=iind
            return self._o2[iind],  "com.robotraconteur.testing.TestService1.sub1"

    def get_o3(self,ind):
        iind=int(ind)
        with self._o3_lock:
            if (not iind in self._o3):
                self._o3[iind]=sub1_impl()
                self._o3[iind].i_ind=iind
            return self._o3[iind], "com.robotraconteur.testing.TestService1.sub1"

    def get_o4(self,ind):
        iind=str(ind)
        with self._o4_lock:
            if (not iind in self._o4):
                self._o4[iind]=sub1_impl()
                self._o4[iind].s_ind=iind
            return self._o4[iind],  "com.robotraconteur.testing.TestService1.sub1"

    def get_o5(self,ind):
        return self._o5,  "com.robotraconteur.testing.TestService1.sub1"

    def get_o6(self):
        if (isinstance(self._o6,sub1_impl)):
            return self._o6,  "com.robotraconteur.testing.TestService1.sub1"
        if (isinstance(self._o6,sub2_impl)):
            return self._o6, "com.robotraconteur.testing.TestService1.sub2"
        if (isinstance(self._o6,subobj_impl)):
            return self._o6, "com.robotraconteur.testing.TestService2.subobj"

    def o6_op(self, op):
        try:
            #print "op " + ServerContext.GetCurrentServicePath() + ".o6"
            ServerContext.GetCurrentServerContext().ReleaseServicePath(ServerContext.GetCurrentServicePath() + ".o6")
        except:
            traceback.print_exc()

        if (op==0):
            self._o6=sub1_impl()
        elif (op==1):
            self._o6=sub2_impl()
        elif (op==2):
            self._o6=subobj_impl()
        else:
            raise Exception()

    #pipes
    @property
    def p1(self):
        return self._p1
    @p1.setter
    def p1(self,value):
        self._p1=value
        value.PipeConnectCallback=(self.p1_connect_callback)

    def p1_connect_callback(self,p):
        p.RequestPacketAck=True
        p.PacketReceivedEvent+=self.p1_packet_received
        p.PacketAckReceivedEvent+=self.p1_packet_ack_received

    def p1_packet_received(self,p):
        def p1_pr():
            try:
                time.sleep(.5)
                with self._p1_lock:
                    while p.Available:
                        dat=p.ReceivePacket()
                        pnum=p.SendPacket(dat)
                        if (not self._packet_sent):
                            self._packetnum=pnum
                            self._packet_sent=True
            except:
                pass
        RobotRaconteurNode.s.PostToThreadPool(p1_pr)
        

    def p1_packet_ack_received(self,p,packetnum):
        if (packetnum == self._packetnum):
            self._ack_recv=True


    @property
    def p2(self):
        return self._p2
    @p2.setter
    def p2(self,value):
        self._p2=value
        value.PipeConnectCallback=self.p2_connect_callback

    def p2_connect_callback(self,p):
        p.PacketReceivedEvent+=self.p2_packet_received

    def p2_packet_received(self,p):
        try:
            time.sleep(.5)
            with self._p2_lock:
                while p.Available > 0:
                    dat=p.ReceivePacket()
                    p.SendPacket(dat)
        except:
            pass


    def pipe_check_error(self):
        if (not self._ack_recv): raise Exception()




    #callbacks
    def test_callbacks(self):
        ep=ServerEndpoint.GetCurrentEndpoint()
        self.cb1.GetClientFunction(ep)()
        self.cb2.GetClientFunction(ep)(739.2,0.392)
        res=self.cb3.GetClientFunction(ep)(34,45)
        if (res != (34 + 45 + 3.14)): raise Exception()
        if (self.cb_meaning_of_life.GetClientFunction(ep)()!=42): raise Exception()

        errthrown=False
        try:
            self.cb_errtest.GetClientFunction(ep)()
        except:
            #traceback.print_exc()
            errthrown=True

        if (not errthrown):
            raise Exception()

    @property
    def broadcastpipe(self):
        return self._broadcastpipe

    @broadcastpipe.setter
    def broadcastpipe(self,value):
        if (self._broadcastpipe is not None): raise Exception("Pipe already set")
        self._broadcastpipe=PipeBroadcaster(value,3)        
        assert self._broadcastpipe.MaxBacklog == 3
        self._broadcastpipe.MaxBacklog = 3
        
        def timer_func(ev):
            try:
                
                for i in xrange(100):
                    self._broadcastpipe.AsyncSendPacket(i, lambda: None)
                    
            except:
                pass

        t = RobotRaconteurNode.s.CreateTimer(.025,timer_func,oneshot=False)
        t.Start()

    #wires
    @property
    def w1(self):
        return self._w1
    @w1.setter
    def w1(self,value):
        self._w1=value
        value.WireConnectCallback=self.w1_connect_callback

    def w1_connect_callback(self,w):
        #print "connect"
        w.WireValueChanged+=self.w1_value_changed

    def w1_value_changed(self,w,value,time):
        #print "change"
        w.OutValue=w.InValue

    @property
    def w2(self):
        return self._w2
    @w2.setter
    def w2(self,value):
        self._w2=value
        value.WireConnectCallback=self.w2_connect_callback

    def w2_connect_callback(self,w):
        w.WireValueChanged+=self.w2_value_changed

    def w2_value_changed(self,w,value,time):
        w.OutValue=w.InValue

    @property
    def w3(self):
        return self._w1
    @w3.setter
    def w3(self,value):
        self._w3=value
        value.WireConnectCallback=self.w3_connect_callback

    def w3_connect_callback(self,w):
        w.WireValueChanged+=self.w3_value_changed

    def w3_value_changed(self,w,value,time):
        w.OutValue=w.InValue

    @property
    def broadcastwire(self):
        return self._broadcastwire

    @broadcastwire.setter
    def broadcastwire(self,value):

        if (self._broadcastwire is not None): raise Exception("Value already set")
        self._broadcastwire=value

        b=WireBroadcaster(value)

        def timer_func(ev):
            try:                
                for i in xrange(100):
                    b.OutValue=i                    
            except:
                pass

        t = RobotRaconteurNode.s.CreateTimer(.025,timer_func,oneshot=False)
        t.Start()

class sub1_impl(object):
    def __init__(self):
        self.d1=None
        self.d2=None
        self.s_ind=""
        self.i_ind=0

        self._o2_1=sub2_impl()
        self._o2_2={}
        self._o2_2_lock=threading.RLock()
        self._o2_3={}
        self._o2_3_lock=threading.RLock()

        self._lock=threading.RLock()

    def RobotRaconteurMonitorEnter(self,timeout):
        print ("Monitor enter")
        self._lock.acquire()

    def RobotRaconteurMonitorExit(self):
        print ("Monitor exit")
        self._lock.release()

    def get_o2_1(self):
        return self._o2_1,  "com.robotraconteur.testing.TestService1.sub2"

    def get_o2_2(self,ind):
        iind=int(ind)
        with self._o2_2_lock:
            if (not iind in self._o2_2):
                self._o2_2[iind]=sub2_impl()
                self._o2_2[iind].i_ind=iind
            return self._o2_2[iind],  "com.robotraconteur.testing.TestService1.sub2"

    def get_o2_3(self,ind):
        iind=str(ind)
        with self._o2_3_lock:
            if (not iind in self._o2_3):
                self._o2_3[iind]=sub2_impl()
                self._o2_3[iind].s_ind=iind
            return self._o2_3[iind],  "com.robotraconteur.testing.TestService1.sub2"

class sub2_impl(object):
    def __init__(self):
        self.s_ind=""
        self.i_ind=0
        self.data=""

        self._o3_1={}
        self._o3_1_lock=threading.RLock()

    def get_o3_1(self,ind):
        iind=str(ind)
        with self._o3_1_lock:
            if (not iind in self._o3_1):
                self._o3_1[iind]=sub3_impl()
                self._o3_1[iind].ind=iind
            return self._o3_1[iind],  "com.robotraconteur.testing.TestService1.sub3"

    def RRServiceObjectInit(self, context, service_path):
        print("Got RRServiceObjectInit: " + str(context) + " service_path: " + service_path)        

class sub3_impl(object):
    def __init__(self):
        self.ind=""
        self.data2=""
        self.data3=0

    def add(self,d):
        return d+42

class subobj_impl(object):
    def add_val(self,v):
        return v+1

class ServiceTestClient2:
    def __init__(self):
        pass
    
    def RunFullTest(self, url):
        self.ConnectService(url);
                
        self.TestWirePeekPoke()
        self.AsyncTestWirePeekPoke()
        self.TestEnums()
        self.TestPod()
        self.TestGenerators()
        self.TestMemories()
        
        self.TestNamedArrays()
        self.TestNamedArrayMemories()
        
        self.TestComplex()
        self.TestComplexMemories()
        
        self.TestNoLock()

        self.TestBool()
        self.TestBoolMemories()

        self.TestExceptionParams()
        
        self.DisconnectService()
    
    def ConnectService(self, url):
        self._r = RobotRaconteurNode.s.ConnectService(url)        

    def DisconnectService(self):
        RobotRaconteurNode.s.DisconnectService(self._r)

    def TestWirePeekPoke(self):
        (v, ts) = self._r.peekwire.PeekInValue()
        if v != 56295674: raise Exception()
        
        self._r.pokewire.PokeOutValue(75738265)
        (v2, ts2) = self._r.pokewire.PeekOutValue()
        if (v2 != 75738265): raise Exception()
        
        w = self._r.pokewire.Connect()
        for i in xrange(3):
            w.OutValue=8638356
        
        time.sleep(.1)
        (v3, ts3) = self._r.pokewire.PeekOutValue()
        if (v3 != 8638356): raise Exception()
        
    def AsyncTestWirePeekPoke(self):
        async_wait=threading.Event()
        async_err=[None]

        def TestAsync_err(err):
            async_err[0]=err
            async_wait.set()
            print (err)
            traceback.print_stack()
        
        def TestAsync1(val, ts, err):
            try:
                if (err is not None):
                    TestAsync_err(err)
                    return
                if val != 56295674:
                    TestAsync_err(Exception())
                    return
                
                self._r.pokewire.AsyncPokeOutValue(75738261, TestAsync2)
            except:
                traceback.print_exc()
            
        def TestAsync2(err):
            if (err is not None):
                TestAsync_err(err)
                return
            
            self._r.pokewire.AsyncPeekOutValue(TestAsync3)
            
        def TestAsync3(val, ts, err):
            if (err is not None):
                TestAsync_err(err)
                return
            if val != 75738261:
                TestAsync_err(Exception())
                return
            
            async_wait.set()
            
        self._r.peekwire.AsyncPeekInValue(TestAsync1)
        
        """if not async_wait.wait(1):
            raise Exception()

        if (async_err[0]):
            raise async_err[0]"""

    def TestEnums(self):
        
        c=RobotRaconteurNode.s.GetConstants("com.robotraconteur.testing.TestService3", self._r)
        
        if(self._r.testenum1_prop != c['testenum1']['anothervalue']):
            raise Exception()
        self._r.testenum1_prop=c['testenum1']['hexval1']
        
    def TestPod(self):

        if sys.platform == "darwin" and sys.version_info[0] < 3:
            return

        s1 = ServiceTest2_fill_testpod1(563921043,self._r)        
        ServiceTest2_verify_testpod1(s1[0],563921043)
        
        s1_m = RobotRaconteurPythonUtil.PackMessageElement(s1, 'com.robotraconteur.testing.TestService3.testpod1', self._r)
        s1_m.UpdateData()
        s1_1 = RobotRaconteurPythonUtil.UnpackMessageElement(s1_m, 'com.robotraconteur.testing.TestService3.testpod1', self._r)
        ServiceTest2_verify_testpod1(s1_1[0],563921043)
        
        s3 = ServiceTest2_fill_teststruct3(858362,self._r)
        ServiceTest2_verify_teststruct3(s3,858362)
        s3_m = RobotRaconteurPythonUtil.PackMessageElement(s3, 'com.robotraconteur.testing.TestService3.teststruct3', self._r)
        s3_m.UpdateData()
        s3_1 = RobotRaconteurPythonUtil.UnpackMessageElement(s3_m, 'com.robotraconteur.testing.TestService3.teststruct3', self._r)
        ServiceTest2_verify_teststruct3(s3_1,858362)
        
        p1 = self._r.testpod1_prop
        ServiceTest2_verify_testpod1(p1[0], 563921043);
        
        p2=ServiceTest2_fill_testpod1(85932659, self._r)
        self._r.testpod1_prop = p2;
        
        f1 = self._r.testpod1_func2()
        ServiceTest2_verify_testpod1(f1[0], 95836295);
        
        f2=ServiceTest2_fill_testpod1(29546592, self._r)
        self._r.testpod1_func1(f2);
        
        ServiceTest2_verify_teststruct3(self._r.teststruct3_prop, 16483675);
        self._r.teststruct3_prop = (ServiceTest2_fill_teststruct3(858362, self._r));
        
    def TestGenerators(self):
        assert cmp(self._r.gen_func1().NextAll(), list(xrange(16))) == 0
        assert cmp(list(self._r.gen_func1()), list(xrange(16))) == 0
                
        g = self._r.gen_func4()
        for _ in xrange(3):
            g.Next([])
        b = g.Next([2,3,4])
        print (list(b))
        g.Abort()
        try:
            g.Next([])
        except OperationAbortedException: pass
        
        g2 = self._r.gen_func4()
        g2.Next([2,3,4])        
        g2.Close()
        try:
            g2.Next([])
        except StopIterationException: pass        
        assert cmp(list(self._r.gen_func2("gen_func2_a_param").NextAll()), [bytearray([i]) for i in xrange(16)]) == 0
        
                
    def TestMemories(self):

        if sys.platform == "darwin" and sys.version_info[0] < 3:
            return

        self.test_m1()
        self.test_m2()
        
    def test_m1(self):
        pod_dtype=RobotRaconteurNode.s.GetPodDType('com.robotraconteur.testing.TestService3.testpod2', self._r)
        o1 = numpy.zeros((32,), dtype=pod_dtype)
        for i in xrange(32):
            o1[i] = ServiceTest2_fill_testpod2(59174 + i, self._r)
        assert self._r.pod_m1.Length == 1024
        self._r.pod_m1.Write(52, o1, 3, 17)
        o2 = numpy.zeros((32,), dtype=pod_dtype)
        self._r.pod_m1.Read(53, o2, 2, 16)
        
        for i in xrange(2,16):
            ServiceTest2_verify_testpod2(o2[i], 59174 + i + 2)
    
    def test_m2(self):
        pod_dtype=RobotRaconteurNode.s.GetPodDType('com.robotraconteur.testing.TestService3.testpod2', self._r)
        s1_1 = numpy.zeros((9,), dtype=pod_dtype)
        for i in xrange(9):             
            s1_1[i] = ServiceTest2_fill_testpod2(75721 + i, self._r)
        
        s = s1_1.reshape((3,3), order="F")
        self._r.pod_m2.Write([0,0], s, [0,0], [3,3])
        
        s2 = numpy.zeros((3,3), dtype=pod_dtype)
        self._r.pod_m2.Read([0,0], s2, [0,0], [3,3])
        
        s2_1 = s2.reshape((9,), order="F")
        
        for i in xrange(9):
            ServiceTest2_verify_testpod2(s2_1[i], 75721 + i)
        
    def TestNamedArrays(self):
        
        self._r.testnamedarray1 = ServiceTest2_fill_transform(3956378, self._r)['translation']
        a1_2 = ServiceTest2_fill_transform(74637, self._r);
        a1_2['translation'] = self._r.testnamedarray1
        ServiceTest2_verify_transform(a1_2, 74637);
        
        self._r.testnamedarray2 = ServiceTest2_fill_transform(827635, self._r)
        ServiceTest2_verify_transform((self._r.testnamedarray2)[0], 1294)
        
        self._r.testnamedarray3 = ServiceTest2_create_transform_array(6, 19274, self._r)
        ServiceTest2_verify_transform_array((self._r.testnamedarray3), 8, 837512)
        
        self._r.testnamedarray4=(ServiceTest2_create_transform_multidimarray(5, 2, 6385,self._r));
        ServiceTest2_verify_transform_multidimarray(self._r.testnamedarray4, 7, 2, 66134);

        self._r.testnamedarray5 = (ServiceTest2_create_transform_multidimarray(3, 2, 7732, self._r));
        ServiceTest2_verify_transform_multidimarray(self._r.testnamedarray5, 3, 2, 773142);
        
        a1 = ServiceTest2_create_transform_array(6, 174, self._r)
        a2 = RobotRaconteurNode.s.NamedArrayToArray(a1)
        a3 = RobotRaconteurNode.s.ArrayToNamedArray(a2,a1.dtype)
        numpy.testing.assert_equal(a1,a3)
        
    def TestNamedArrayMemories(self):
        self.test_named_array_m1()
        self.test_named_array_m2()
    
    def test_named_array_m1(self):
        n_dtype=RobotRaconteurNode.s.GetNamedArrayDType('com.robotraconteur.testing.TestService3.transform', self._r)
        
        s = numpy.zeros((32,),dtype=n_dtype)
        for i in xrange(32):
            s[i] = ServiceTest2_fill_transform(79174 + i, self._r);
        assert self._r.namedarray_m1.Length == 512
        self._r.namedarray_m1.Write(23,s,3,21)
        
        s2 = numpy.zeros((32,),dtype=n_dtype)
        self._r.namedarray_m1.Read(24,s2,2,18)
        
        for i in xrange(2,16):
            ServiceTest2_verify_transform(s2[i], 79174 + i + 2)        
    
    def test_named_array_m2(self):
        n_dtype=RobotRaconteurNode.s.GetNamedArrayDType('com.robotraconteur.testing.TestService3.transform', self._r)
        
        s = numpy.zeros((9,),dtype=n_dtype)
        for i in xrange(9):
            s[i] = ServiceTest2_fill_transform(15721 + i, self._r);
        s=s.reshape((3,3),order="F")
        self._r.namedarray_m2.Write([0,0],s,[0,0],[3,3])
        
        s2 = numpy.zeros((3,3),dtype=n_dtype)
        self._r.namedarray_m2.Read([0,0],s2,[0,0],[3,3])
        s2_1=s2.reshape((9,),order="F")
        for i in xrange(9):
            ServiceTest2_verify_transform(s2_1[i], 15721 + i);

    def TestComplex(self):
        if (self._r.c1 != complex(5.708705e+01, -2.328294e-03)):
            raise Exception()
        self._r.c1 = complex(5.708705e+01, -2.328294e-03)
        
        c2_1_1 = numpy.array([1.968551e+07, 2.380643e+18, 3.107374e-16, 7.249542e-16, -4.701135e-19, -6.092764e-17, 2.285854e+14, 2.776180e+05, -1.436152e-12, 3.626609e+11, 3.600952e-02, -3.118123e-16, -1.312210e-10, -1.738940e-07, -1.476586e-12, -2.899781e-20, 4.806642e+03, 4.476869e-05, -2.935084e-16, 3.114019e-20, -3.675955e+01, 3.779796e-21, 2.190594e-11, 4.251420e-06, -9.715221e+11, -3.483924e-01, 7.606428e+05, 5.418088e+15, 4.786378e+16, -1.202581e+08, -1.662061e+02, -2.392954e+03]).view(numpy.complex128)
        numpy.testing.assert_allclose(self._r.c2, c2_1_1)
        c2_2_1 = numpy.array([4.925965e-03, 5.695254e+13, -4.576890e-14, -6.056342e-07, -4.918571e-08, -1.940684e-10, 1.549104e-02, -1.954145e+04, -2.499019e-16, 4.010614e+09, -1.906811e-08, 3.297924e-10, 2.742399e-02, -4.372839e-01, -3.093171e-10, 4.311755e-01, -2.218220e-14, 5.399758e+10, 3.360304e+17, 1.340681e-18, -4.441140e+11, -1.845055e-09, -3.074586e-10, -1.754926e+01, -2.766799e+04, -2.307577e+10, 2.754875e+14, 1.179639e+15, 6.976204e-10, 1.901856e+08, -3.824351e-02, -1.414167e+08]).view(numpy.complex128)
        self._r.c2 = c2_2_1
        
        c3_1_2 = numpy.array([5.524802e+18, -2.443857e-05, 3.737932e-02, -4.883553e-03, -1.184347e+12, 4.537366e-08, -4.567913e-01, -1.683542e+15, -1.676517e+00, -8.911085e+12, -2.537376e-17, 1.835687e-10, -9.366069e-22, -5.426323e-12, -7.820969e-10, -1.061541e+12, -3.660854e-12, -4.969930e-03, 1.988428e+07, 1.860782e-16]).view(numpy.complex128).reshape((2,5),order="F")
        numpy.testing.assert_allclose(c3_1_2,self._r.c3)
        c3_2_2 = numpy.array([4.435180e+04, 5.198060e-18, -1.316737e-13, -4.821771e-03, -4.077550e-19, -1.659105e-09, -6.332363e-11, -1.128999e+16, 4.869912e+16, 2.680490e-04, -8.880119e-04, 3.960452e+11, 4.427784e-09, -2.813742e-18, 7.397516e+18, 1.196394e+13, 3.236906e-14, -4.219297e-17, 1.316282e-06, -2.771084e-18, -1.239118e-09, 2.887453e-08, -1.746515e+08, -2.312264e-11]).view(numpy.complex128).reshape((3,4),order="F")
        self._r.c3 = c3_2_2
        
        c5_1_1 = numpy.array([1.104801e+00, 4.871266e-10, -2.392938e-03, 4.210339e-07, 1.474114e-19, -1.147137e-01, -2.026434e+06, 4.450447e-19, 3.702953e-21, 9.722025e+12, 3.464073e-14, 4.628110e+15, 2.345453e-19, 3.730012e-04, 4.116650e+16, 4.380220e+08]).view(numpy.complex128)
        numpy.testing.assert_allclose(c5_1_1,(self._r.c5)[0])
        c5_2_1 = numpy.array([2.720831e-20, 2.853037e-16, -7.982497e+16, -2.684318e-09, -2.505796e+17, -4.743970e-12, -3.657056e+11, 2.718388e+15, 1.597672e+03, 2.611859e+14, 2.224926e+06, -1.431096e-09, 3.699894e+19, -5.936706e-01, -1.385395e-09, -4.248415e-13]).view(numpy.complex128)
        self._r.c5=[c5_2_1]
        
        numpy.testing.assert_allclose(self._r.c7,complex( -5.527021e-18, -9.848457e+03))            
        self._r.c7 = complex(9.303345e-12, -3.865684e-05)
    
        c8_1_1 = numpy.array([-3.153395e-09, 3.829492e-02, -2.665239e+12, 1.592927e-03, 3.188444e+06, -3.595015e-11, 2.973887e-18, -2.189921e+17, 1.651567e+10, 1.095838e+05, 3.865249e-02, 4.725510e+10, -2.334376e+03, 3.744977e-05, -1.050821e+02, 1.122660e-22, 3.501520e-18, -2.991601e-17, 6.039622e-17, 4.778095e-07, -4.793136e-05, 3.096513e+19, 2.476004e+18, 1.296297e-03, 2.165336e-13, 4.834427e+06, 4.675370e-01, -2.942290e-12, -2.090883e-19, 6.674942e+07, -4.809047e-10, -4.911772e-13],numpy.float32).view(numpy.complex64)
        numpy.testing.assert_allclose(c8_1_1, self._r.c8)
        c8_2_1 = numpy.array([1.324498e+06, 1.341746e-04, 4.292993e-04, -3.844509e+15, -3.804802e+10, 3.785305e-12, 2.628285e-19, -1.664089e+15, -4.246472e-10, -3.334943e+03, -3.305796e-01, 1.878648e-03, 1.420880e-05, -3.024657e+14, 2.227031e-21, 2.044653e+17, 9.753609e-20, -6.581817e-03, 3.271063e-03, -1.726081e+06, -1.614502e-06, -2.641638e-19, -2.977317e+07, -1.278224e+03, -1.760207e-05, -4.877944e-07, -2.171524e+02, 1.620645e+01, -4.334168e-02, 1.871011e-09, -3.066163e+06, -3.533662e+07],numpy.float32).view(numpy.complex64)
        self._r.c8 = c8_2_1
        
        c9_1_1 = numpy.array([1.397743e+15, 3.933042e+10, -3.812329e+07, 1.508109e+16, -2.091397e-20, 3.207851e+12, -3.640702e+02, 3.903769e+02, -2.879727e+17, -4.589604e-06, 2.202769e-06, 2.892523e+04, -3.306489e-14, 4.522308e-06, 1.665807e+15, 2.340476e+10],numpy.float32).view(numpy.complex64).reshape((2,4),order="F")
        numpy.testing.assert_allclose(c9_1_1,self._r.c9)
        c9_2_1 = numpy.array([2.138322e-03, 4.036979e-21, 1.345236e+10, -1.348460e-12, -3.615340e+12, -2.911340e-21, 3.220362e+09, 3.459909e-04, 4.276259e-08, -3.199451e+18, 3.468308e+07, -2.928506e-09, -3.154288e+17, -2.352920e-02, 6.976385e-21, 2.435472e+12],numpy.float32).view(numpy.complex64).reshape((2,2,2),order="F")
        self._r.c9 = c9_2_1
        
    def TestComplexMemories(self):
        c_m1_1 = numpy.array([8.952764e-05, 4.348213e-04, -1.051215e+08, 1.458626e-09, -2.575954e+10, 2.118740e+03, -2.555026e-02, 2.192576e-18, -2.035082e+18, 2.951834e-09, -1.760731e+15, 4.620903e-11, -3.098798e+05, -8.883556e-07, 2.472289e+17, 7.059075e-12]).view(numpy.complex128)
        self._r.c_m1.Write(10,c_m1_1,0,8)
        c_m1_3 = numpy.zeros((8,),numpy.complex128)
        self._r.c_m1.Read(10, c_m1_3, 0, 8)
        numpy.testing.assert_allclose(c_m1_1[0:8],c_m1_3)
        
        c_m2_3 = numpy.array([-4.850043e-03, 3.545429e-07, 2.169430e+12, 1.175943e-09, 2.622300e+08, -4.439823e-11, -1.520489e+17, 8.250078e-14, 3.835439e-07, -1.424709e-02, 3.703099e+08, -1.971111e-08, -2.805354e+01, -2.093850e-17, -4.476148e+19, 9.914350e+11, 2.753067e+08, -1.745041e+14]).view(numpy.complex128).reshape((3,3),order="F")
        self._r.c_m2.Write([0,0],c_m2_3,[0,0],[3,3])
        c_m2_4 = numpy.zeros((3,3),numpy.complex128)
        self._r.c_m2.Read([0,0],c_m2_4,[0,0],[3,3])
        numpy.testing.assert_allclose(c_m2_3,c_m2_4)
        
    def TestNoLock(self):
        o5=self._r.get_nolock_test()
        
        errthrown=False
        try:
            a = o5.p1
        except ObjectLockedException:
            errthrown=True
        if not errthrown:
            raise Exception()
        
        a = o5.p2
        o5.p2 = 0
        a = o5.p3
        errthrown=False
        try:
            o5.p3 = 0
        except ObjectLockedException:
            errthrown=True
        if not errthrown:
            raise Exception()
        
        errthrown=False
        try:
            a = o5.f1()
        except ObjectLockedException:
            errthrown=True
        if not errthrown:
            raise Exception()

        o5.f2()
        
        errthrown=False
        try:
            o5.q1.Connect(-1).Close()
        except ObjectLockedException:
            errthrown=True
        if not errthrown:
            raise Exception()
        o5.q2.Connect(-1).Close()
        
        errthrown=False
        try:
            o5.w1.Connect().Close()
        except ObjectLockedException:
            errthrown=True
        if not errthrown:
            raise Exception()
        o5.w2.Connect().Close()
        
        errthrown=False
        try:
            o5.m1.Length
        except ObjectLockedException:
            errthrown=True
        if not errthrown:
            raise Exception()
                
        b1 = numpy.zeros((100,),numpy.int32)
        
        a = o5.m2.Length
        o5.m2.Read(0, b1, 0, 10)
        o5.m2.Write(0,b1,0,10)
        
        a=o5.m3.Length
        o5.m3.Read(0,b1,0,10)
        errthrown=False
        try:
            o5.m3.Write(0,b1,0,10)
        except ObjectLockedException:
            errthrown=True
        if not errthrown:
            raise Exception()
        
    def TestBool(self):
        
        self._r.b1=True
        if not self._r.b1:
            raise Exception()

        self._r.b2 = [True, False, False, True, True, True, False, True]
        if not numpy.array_equal(self._r.b2, [True, False, True, True, False, True, False]):
            raise Exception()

        self._r.b3 = numpy.array([True,False]).reshape(2,1)
        if not numpy.array_equal(self._r.b3, numpy.array([False, True, True, False]).reshape(2,2,order='F')):
            raise Exception()

        self._r.b4 = [True]
        if not self._r.b4[0]:
            raise Exception()

        self._r.b5 = [numpy.array([True, False])]
        if not numpy.array_equal(self._r.b5[0],numpy.array([False, True, False, False])):
            raise Exception()

        self._r.b6 = [numpy.array([True, False]).reshape(2,1)]
        if not numpy.array_equal(self._r.b6[0], numpy.array([False,True,True,False]).reshape(2,2,order='F')):
            raise Exception()

    def TestBoolMemories(self):
        v1_1 = numpy.array([True, False, False, True, True, False, False, False, True, True])
        self._r.c_m5.Write(100, v1_1, 1, 8)
        v1_2 = numpy.zeros((10,),numpy.bool_)
        self._r.c_m5.Read(99, v1_2, 0, 10)
        if not numpy.array_equal(v1_1[1:9], v1_2[1:9]):
            raise Exception()

        v2_1 = v1_1.reshape(2,5,order='F')
        self._r.c_m6.Write([0,0],v2_1,[0,0],[2,5])
        v2_2 = numpy.zeros((2,5),numpy.bool_)
        self._r.c_m6.Read([0,0],v2_2,[0,0],[2,5])
        if not numpy.array_equal(v2_1, v2_2):
            raise Exception()

    def TestExceptionParams(self):

        exp1_caught = False
        try:
            self._r.test_exception_params1()
        except Exception as e:
            exp1_caught = True
            assert e.errorname == "RobotRaconteur.InvalidOperation"
            assert e.message == "test error"
            assert e.errorsubname == "my_error"
            assert len(e.errorparam.data) == 2
            assert e.errorparam.data["param1"][0] == 10
            assert e.errorparam.data["param2"] == "20"
        
        assert exp1_caught == True

        exp2_caught = False
        try:
            self._r.test_exception_params2()
        except Exception as e:
            exp2_caught = True
            assert e.errorname == "com.robotraconteur.testing.TestService3.test_exception4"
            assert e.message == "test error2"
            assert e.errorsubname == "my_error2"
            assert len(e.errorparam.data) == 2
            assert e.errorparam.data["param1"][0] == 30
            assert e.errorparam.data["param2"] == "40"
        
        assert exp2_caught == True

class testroot3_impl(object):
    def __init__(self):
        self._peekwire=None
        self._pokewire=None
        self._peekwire_b=None
        self._pokewire_r=None
        
        self._timer=None
        
        self._const=RobotRaconteurNode.s.GetConstants("com.robotraconteur.testing.TestService3")
        pod_dtype=RobotRaconteurNode.s.GetPodDType('com.robotraconteur.testing.TestService3.testpod2')
        self._pod_m1=ArrayMemory(numpy.zeros((1024,),dtype=pod_dtype))
        self._pod_m2=MultiDimArrayMemory(numpy.zeros((3,3),dtype=pod_dtype))
        transform_dtype=RobotRaconteurNode.s.GetNamedArrayDType('com.robotraconteur.testing.TestService3.transform')
        self._namedarray_m1=ArrayMemory(numpy.zeros((512,),dtype=transform_dtype))
        self._namedarray_m2=MultiDimArrayMemory(numpy.zeros((10,10),dtype=transform_dtype))
        self._o5 = obj5_impl()
        
        self.c_m1=ArrayMemory(numpy.zeros((100,),numpy.complex128))
        self.c_m2=MultiDimArrayMemory(numpy.zeros((3,3),numpy.complex128))

        self.c_m5=ArrayMemory(numpy.zeros((512,),numpy.bool_))
        self.c_m6=MultiDimArrayMemory(numpy.zeros((10,10),numpy.bool_))
        
    @property
    def peekwire(self):
        return self._peekwire
    @peekwire.setter
    def peekwire(self, v):
        self._peekwire=v
        self._peekwire_b=WireBroadcaster(v)
        self._peekwire_b.OutValue=56295674
        self._timer=RobotRaconteurNode.s.CreateTimer(.1, self._timer_handler)
        self._timer.Start()
    
    def _timer_handler(self,evt):
        self._peekwire_b.OutValue=56295674
        
    @property
    def pokewire(self):
        return self._pokewire
    
    @pokewire.setter
    def pokewire(self,v):
        self._pokewire=v
        self._pokewire_r=WireUnicastReceiver(v)
        
        def in_value_changed(val, ts, ep):
            print ("In value changed: " + str(val) + " ep: " + str(ep))
            print(self._pokewire_r.InValue)
            print(self._pokewire_r.TryGetInValue())
            
        self._pokewire_r.InValueChanged+=in_value_changed
    
    @property
    def testenum1_prop(self):
        return self._const['testenum1']['anothervalue']
    
    @testenum1_prop.setter
    def testenum1_prop(self,value):        
        if (value != self._const['testenum1']['hexval1']):
            raise Exception()

    @property
    def testpod1_prop(self):
        return ServiceTest2_fill_testpod1(563921043, None)

    @testpod1_prop.setter
    def testpod1_prop(self,value):
        ServiceTest2_verify_testpod1(value[0], 85932659)
    
    def testpod1_func1(self, s):
        ServiceTest2_verify_testpod1(s[0], 29546592)
        
    def testpod1_func2(self):
        return ServiceTest2_fill_testpod1(95836295,None);
    
    @property
    def teststruct3_prop(self):
        return ServiceTest2_fill_teststruct3(16483675, None)

    @teststruct3_prop.setter
    def teststruct3_prop(self,value):
        ServiceTest2_verify_teststruct3(value, 858362)
        
    def gen_func1(self):
        return xrange(16)
        
    def gen_func2(self, name):
        assert name == "gen_func2_a_param"
        return [[i] for i in xrange(16)]
                
    def gen_func4(self):
        return func4_gen()
    
    def get_o4(self):
        return obj4_impl(), "com.robotraconteur.testing.TestService3.obj4"
    
    @property
    def pod_m1(self):
        return self._pod_m1
    
    @property
    def pod_m2(self):
        return self._pod_m2
    
    @property
    def testnamedarray1(self):
        return ServiceTest2_fill_transform(74637,None)['translation'];
    
    @testnamedarray1.setter
    def testnamedarray1(self,value):
        a1=ServiceTest2_fill_transform(3956378,None);
        a1['translation'] = value;
        ServiceTest2_verify_transform(a1, 3956378);
        
    @property
    def testnamedarray2(self):
        return ServiceTest2_fill_transform(1294,None);
    
    @testnamedarray2.setter
    def testnamedarray2(self,value):
        ServiceTest2_verify_transform(value, 827635)
        
    @property
    def testnamedarray3(self):
        return ServiceTest2_create_transform_array(8, 837512,None)
    
    @testnamedarray3.setter
    def testnamedarray3(self,value):
        ServiceTest2_verify_transform_array(value, 6, 19274);
        
    @property
    def testnamedarray4(self):
        return ServiceTest2_create_transform_multidimarray(7, 2, 66134,None)
    
    @testnamedarray4.setter
    def testnamedarray4(self,value):
        ServiceTest2_verify_transform_multidimarray(value, 5, 2, 6385);
        
    @property
    def testnamedarray5(self):
        return ServiceTest2_create_transform_multidimarray(3, 2, 773142,None);
    
    @testnamedarray5.setter
    def testnamedarray5(self,value):
        ServiceTest2_verify_transform_multidimarray(value, 3, 2, 7732);
    
    @property
    def namedarray_m1(self):
        return self._namedarray_m1
    
    @property
    def namedarray_m2(self):
        return self._namedarray_m2
    
    @property
    def c1(self):
        return complex(5.708705e+01, -2.328294e-03)
    
    @c1.setter
    def c1(self,value):
        numpy.testing.assert_allclose(complex(5.708705e+01, -2.328294e-03),value)
        
    @property
    def c2(self):
        return numpy.array([1.968551e+07, 2.380643e+18, 3.107374e-16, 7.249542e-16, -4.701135e-19, -6.092764e-17, 2.285854e+14, 2.776180e+05, -1.436152e-12, 3.626609e+11, 3.600952e-02, -3.118123e-16, -1.312210e-10, -1.738940e-07, -1.476586e-12, -2.899781e-20, 4.806642e+03, 4.476869e-05, -2.935084e-16, 3.114019e-20, -3.675955e+01, 3.779796e-21, 2.190594e-11, 4.251420e-06, -9.715221e+11, -3.483924e-01, 7.606428e+05, 5.418088e+15, 4.786378e+16, -1.202581e+08, -1.662061e+02, -2.392954e+03]).view(numpy.complex128)
    
    @c2.setter
    def c2(self,value):
        numpy.testing.assert_allclose(numpy.array([4.925965e-03, 5.695254e+13, -4.576890e-14, -6.056342e-07, -4.918571e-08, -1.940684e-10, 1.549104e-02, -1.954145e+04, -2.499019e-16, 4.010614e+09, -1.906811e-08, 3.297924e-10, 2.742399e-02, -4.372839e-01, -3.093171e-10, 4.311755e-01, -2.218220e-14, 5.399758e+10, 3.360304e+17, 1.340681e-18, -4.441140e+11, -1.845055e-09, -3.074586e-10, -1.754926e+01, -2.766799e+04, -2.307577e+10, 2.754875e+14, 1.179639e+15, 6.976204e-10, 1.901856e+08, -3.824351e-02, -1.414167e+08]).view(numpy.complex128),value)
    
    @property
    def c3(self):
        return numpy.array([5.524802e+18, -2.443857e-05, 3.737932e-02, -4.883553e-03, -1.184347e+12, 4.537366e-08, -4.567913e-01, -1.683542e+15, -1.676517e+00, -8.911085e+12, -2.537376e-17, 1.835687e-10, -9.366069e-22, -5.426323e-12, -7.820969e-10, -1.061541e+12, -3.660854e-12, -4.969930e-03, 1.988428e+07, 1.860782e-16]).view(numpy.complex128).reshape((2,5),order="F")
    
    @c3.setter
    def c3(self, value):
        numpy.testing.assert_allclose(numpy.array([4.435180e+04, 5.198060e-18, -1.316737e-13, -4.821771e-03, -4.077550e-19, -1.659105e-09, -6.332363e-11, -1.128999e+16, 4.869912e+16, 2.680490e-04, -8.880119e-04, 3.960452e+11, 4.427784e-09, -2.813742e-18, 7.397516e+18, 1.196394e+13, 3.236906e-14, -4.219297e-17, 1.316282e-06, -2.771084e-18, -1.239118e-09, 2.887453e-08, -1.746515e+08, -2.312264e-11]).view(numpy.complex128).reshape((3,4),order="F"), value)
        
    @property
    def c5(self):
        return [numpy.array([1.104801e+00, 4.871266e-10, -2.392938e-03, 4.210339e-07, 1.474114e-19, -1.147137e-01, -2.026434e+06, 4.450447e-19, 3.702953e-21, 9.722025e+12, 3.464073e-14, 4.628110e+15, 2.345453e-19, 3.730012e-04, 4.116650e+16, 4.380220e+08]).view(numpy.complex128)]
    
    @c5.setter
    def c5(self,value):
        numpy.testing.assert_allclose(numpy.array([2.720831e-20, 2.853037e-16, -7.982497e+16, -2.684318e-09, -2.505796e+17, -4.743970e-12, -3.657056e+11, 2.718388e+15, 1.597672e+03, 2.611859e+14, 2.224926e+06, -1.431096e-09, 3.699894e+19, -5.936706e-01, -1.385395e-09, -4.248415e-13]).view(numpy.complex128),value[0])
        
    @property
    def c7(self):
        return complex( -5.527021e-18, -9.848457e+03)
    
    @c7.setter
    def c7(self,value):
        numpy.testing.assert_allclose(complex(9.303345e-12, -3.865684e-05),value)
        
    @property
    def c8(self):
        return numpy.array([-3.153395e-09, 3.829492e-02, -2.665239e+12, 1.592927e-03, 3.188444e+06, -3.595015e-11, 2.973887e-18, -2.189921e+17, 1.651567e+10, 1.095838e+05, 3.865249e-02, 4.725510e+10, -2.334376e+03, 3.744977e-05, -1.050821e+02, 1.122660e-22, 3.501520e-18, -2.991601e-17, 6.039622e-17, 4.778095e-07, -4.793136e-05, 3.096513e+19, 2.476004e+18, 1.296297e-03, 2.165336e-13, 4.834427e+06, 4.675370e-01, -2.942290e-12, -2.090883e-19, 6.674942e+07, -4.809047e-10, -4.911772e-13],numpy.float32).view(numpy.complex64)
    
    @c8.setter
    def c8(self,value):
        numpy.testing.assert_allclose(numpy.array([1.324498e+06, 1.341746e-04, 4.292993e-04, -3.844509e+15, -3.804802e+10, 3.785305e-12, 2.628285e-19, -1.664089e+15, -4.246472e-10, -3.334943e+03, -3.305796e-01, 1.878648e-03, 1.420880e-05, -3.024657e+14, 2.227031e-21, 2.044653e+17, 9.753609e-20, -6.581817e-03, 3.271063e-03, -1.726081e+06, -1.614502e-06, -2.641638e-19, -2.977317e+07, -1.278224e+03, -1.760207e-05, -4.877944e-07, -2.171524e+02, 1.620645e+01, -4.334168e-02, 1.871011e-09, -3.066163e+06, -3.533662e+07],numpy.float32).view(numpy.complex64),value) 
    
    @property
    def c9(self):
        return numpy.array([1.397743e+15, 3.933042e+10, -3.812329e+07, 1.508109e+16, -2.091397e-20, 3.207851e+12, -3.640702e+02, 3.903769e+02, -2.879727e+17, -4.589604e-06, 2.202769e-06, 2.892523e+04, -3.306489e-14, 4.522308e-06, 1.665807e+15, 2.340476e+10],numpy.float32).view(numpy.complex64).reshape((2,4),order="F")
    
    @c9.setter
    def c9(self,value):
        numpy.testing.assert_allclose(numpy.array([2.138322e-03, 4.036979e-21, 1.345236e+10, -1.348460e-12, -3.615340e+12, -2.911340e-21, 3.220362e+09, 3.459909e-04, 4.276259e-08, -3.199451e+18, 3.468308e+07, -2.928506e-09, -3.154288e+17, -2.352920e-02, 6.976385e-21, 2.435472e+12],numpy.float32).view(numpy.complex64).reshape((2,2,2),order="F"),value)
    
    def get_nolock_test(self):
        return self._o5, "com.robotraconteur.testing.TestService3.obj5"

    @property
    def b1(self):
        return True
    @b1.setter
    def b1(self,value):
        if value != True:
            raise Exception()

    @property
    def b2(self):
        return numpy.array([True, False, True, True, False, True, False])
    @b2.setter
    def b2(self,value):
        if not numpy.array_equal(value, [True, False, False, True, True, True, False, True]):
            raise Exception()

    @property
    def b3(self):
        return numpy.array([False, True, True, False]).reshape(2,2,order='F')
    @b3.setter
    def b3(self,value):
        if not numpy.array_equal(value, numpy.array([True,False]).reshape(2,1)):
            raise Exception()

    @property
    def b4(self):
        return [True]
    @b4.setter
    def b4(self,value):
        if value[0] != True:
            raise Exception()

    @property
    def b5(self):
        return [numpy.array([False, True, False, False])]
    @b5.setter
    def b5(self,value):
        if not numpy.array_equal(value[0], numpy.array([True, False])):
            raise Exception()

    @property
    def b6(self):
        return [numpy.array([False,True,True,False]).reshape(2,2,order='F')]
    @b6.setter
    def b6(self,value):
        if not numpy.array_equal(value[0], numpy.array([True, False]).reshape(2,1)):
            raise Exception()

    def test_exception_params1(self):
        params_dict = {}
        params_dict["param1"] = RobotRaconteurVarValue(10,"int32")
        params_dict["param2"] = RobotRaconteurVarValue("20","string")
        params_ = RobotRaconteurVarValue(params_dict,"varvalue{string}")
        err = InvalidOperationException("test error","my_error",params_)
        raise err

    def test_exception_params2(self):
        params_dict = {}
        params_dict["param1"] = RobotRaconteurVarValue(30,"int32")
        params_dict["param2"] = RobotRaconteurVarValue("40","string")
        params_ = RobotRaconteurVarValue(params_dict,"varvalue{string}")
        e4=RobotRaconteurNode.s.GetExceptionType("com.robotraconteur.testing.TestService3.test_exception4")
        err = e4("test error2","my_error2",params_)
        raise err
    
class func4_gen(object):
    def __init__(self):
        self._j=0
        self._aborted=False

    def Next(self, v):
        if self._aborted:
            raise OperationAbortedException()
        
        if (self._j>=8):
            raise StopIterationException()
        
        a = copy.copy(v)
        for i in xrange(len(a)):
            a[i]+=self._j
            
        self._j+=1
        
        return a
    
    def Abort(self):
        self._aborted=True
        
    def Close(self):
        self._j=1000
            

class obj4_impl(object):
    def __init__(self):
        self.s_ind = ""
        self.i_ind=0
        self.data=""

class obj5_impl(object):
    def __init__(self):
        self.m1 = ArrayMemory(numpy.zeros((100,),numpy.int32))
        self.m2 = ArrayMemory(numpy.zeros((100,),numpy.int32))
        self.m3 = ArrayMemory(numpy.zeros((100,),numpy.int32))
        self.p1 = 0
        self.p2 = 0
        self.p3 = 0
        self.q1 = None
        self.q2 = None
        self.w1 = None
        self.w2 = None
        
    def f1(self):
        return 10
    
    def f2(self):
        return 11
    
class ServiceTest2_test_sequence_gen(object):
    
    double_constants = [0.11808806176314335, 0.39707350606301617, 0.27114383032566935, 0.1816549980743133, 0.9745821790407598, 0.3871963990399544, 0.23019466875895944, 0.9750733084525263, 0.9082211077758257, 0.3458578243892674, 0.2145223031819451, 0.050577890701211214, 0.6859014835404248, 0.13346491631693647, 0.31130161297472747, 0.4427049020013023, 0.6668933913989237, 0.27386895592679106, 0.7935266595399671, 0.1801039408397278, 0.24687809555578377, 0.14371795298956047, 0.6919432557030775, 0.26342660961205466, 0.8297390075495092, 0.590707127717445, 0.31363110564252494, 0.9347078770102211, 0.9092858094676379, 0.05007361982869851, 0.6839993121920985, 0.04537519346436425, 0.9596513618649168, 0.014192218318528238, 0.3461518994899867, 0.2892061109297216, 0.7852209512734595, 0.5512898498515767, 0.23876171449479588, 0.18603170199864816, 0.9332549148364775, 0.7196381585823254, 0.11328783534529274, 0.28718907679131567, 0.8943265682808665, 0.09528306977661194, 0.12076041011075966, 0.9093613227704904, 0.6159424378241243, 0.46040246050201283, 0.10114403603396294, 0.3256022559352807, 0.4345689432015529, 0.16526053043685363, 0.921377210764023, 0.047316086921034506, 0.8124471820976614, 0.5549322662743057, 0.6372044012956544, 0.7384490314500013, 0.08785073630126417, 0.34009451753816633, 0.1128188235298141, 0.7570689642925523, 0.8888240249867422, 0.4793558825392765, 0.2873446224140068, 0.5812977408955284, 0.12115017049089272, 0.027781953854400854, 0.2261478033219121, 0.5215829399443781, 0.6689715427971396, 0.037255766439576954, 0.027369544851444938, 0.0012655162592882796, 0.057718580810741105, 0.768571577589763, 0.40663466239871804, 0.37132551049394413, 0.35689602073641835, 0.999288862894407, 0.45921716865448736, 0.8858162825940926, 0.5256617928380493, 0.10987414986308519, 0.2282318164593513, 0.9447877860501251, 0.3916195407188612, 0.3162722195101684, 0.6022681762024559, 0.8968606183295518, 0.9660981389203961, 0.8259051566799759, 0.9567596329789867, 0.10899477146391134, 0.8686975579744052, 0.6460925454900462, 0.014139153158731599, 0.8236465472145591, 0.14070749413750772, 0.45029851995863457, 0.49760400143002703, 0.4269219371696674, 0.6497722752581501, 0.18891142683143125, 0.7842553099501023, 0.4567336175118104, 0.41557010767259617, 0.5409386156760537, 0.8569918583692724, 0.6404373935353948, 0.3979570017461407, 0.7638872113303937, 0.3143786258820297, 0.4124363084260697, 0.7511608198176333, 0.9309621020613599, 0.3510817626656133, 0.4129906358226556, 0.160132289651869, 0.9034249772852133, 0.29307932554939686, 0.6648217626783984, 0.57370441847376, 0.25866833134255185, 0.9868393298504949, 0.7519952534740356, 0.9125793884741256, 0.09414441028013487, 0.3698912686054433, 0.7697425935080573, 0.818433838006258, 0.45387442546859913, 0.9540623871808379, 0.6546622392518656, 0.33175597948205304, 0.3650812315404032, 0.2204262671755911, 0.2896249886230644, 0.4359348975163234, 0.6874635995532687, 0.9898862923022991, 0.8447030875007443, 0.556631665555674, 0.22535633122318266, 0.2962015363488314, 0.40919811529893524, 0.35277813955676585, 0.9135649109049062, 0.1362136204679547, 0.014832030307457944, 0.9786997284639897, 0.8831443107570999, 0.18693034847662915, 0.6306544158593178, 0.7195346571103611, 0.12280632826845916, 0.09598120028079893, 0.41628580769894785, 0.4563945117320106, 0.5453569722070474, 0.5409708243628841, 0.9548826130433853, 0.73826674029996, 0.7606706691331442, 0.7451510370045543, 0.46905357694223615, 0.38604069300230726, 0.24227549467990406, 0.36888260743435897, 0.7736266009784566, 0.5599726292985049, 0.1638200476964048, 0.5231363926268443, 0.46476816047428493, 0.7354540829476179, 0.7592160523397236, 0.904926665320885, 0.13659567661634864, 0.3605347480789368, 0.8559898787924197, 0.05806361089284218, 0.3514516073731695, 0.3200035963730826, 0.8130816300220727, 0.2441806071247825, 0.5094333382670222, 0.3085154105289487, 0.8016697912649855, 0.489223980669399, 0.1271196388708592, 0.45361959574589095, 0.4076021039211315, 0.21008200776692043, 0.6492824809428919, 0.36355899831102345, 0.3700493597456158, 0.8804732140356909, 0.6838347468524664, 0.6251817013921166, 0.8129669218885914, 0.5802559767397518, 0.7612778764685251, 0.7743182342054986, 0.8813454629585609, 0.13901937602535086, 0.6441396609146538, 0.0669814086333228, 0.7988834918175571, 0.21342150853610775, 0.48912606983409, 0.6268962979617757, 0.3420705951554025, 0.644355248574381, 0.02474027233115894, 0.9629261752485292, 0.32756595461616556, 0.6234896183759103, 0.8694620695988075, 0.5339106063143038, 0.8138209300770278, 0.4605248816782116, 0.22035927729293459, 0.46230821418688905, 0.040888157819212734, 0.9342201664439329, 0.49451931633162305, 0.7828481989036491, 0.6308540812254672, 0.787338250006729, 0.8242296298141132, 0.37842153129646017, 0.4037533058169085, 0.29363853429695086, 0.2616333890346294, 0.021747079536094893, 0.07159932403819824, 0.0836252556663275, 0.6508931436148896, 0.4696851495094455, 0.7780320192599322, 0.9056810238799952, 0.16581571523410876, 0.07477643334310968, 0.08918832273632304, 0.3510030518197498, 0.8208879098716282, 0.6730030327410184, 0.2056228302092813, 0.8589526402816096, 0.7661103309406245, 0.10410779894694244, 0.2980240916305603, 0.08309278020221389, 0.16892923264993776, 0.1673649190856814, 0.9902665970726163, 0.3958281017993982, 0.6357761365697472, 0.0004985278107018098, 0.8934719592462411, 0.4433264015781644, 0.3060269838972648, 0.5961031105262977, 0.19337740613989174, 0.6601304530774094, 0.3188815478943351, 0.9591385952061902, 0.7487404392909567, 0.021452192187004893, 0.09677090814242906, 0.9443022122893349, 0.06906514980446588, 0.47150949773110995, 0.5254661986191255, 0.35885196872594927, 0.6149642641579985, 0.43424327780540106, 0.22788025977293125, 0.49038872275875656, 0.7629112500519988, 0.39008097446204415, 0.6305574278747439, 0.8660069529571268, 0.09187729927486732, 0.10263894893766723, 0.9867782984008415, 0.6162178104927842, 0.5865318376745987, 0.7492617148781313, 0.3109228268448453, 0.4066052601781911, 0.8077848008927694, 0.2339009135047284, 0.8946378393181584, 0.46618372347474724, 0.8228301884287071, 0.4963502528255559, 0.10742931804428801, 0.3790151347468922, 0.3556483613732718, 0.7454368606830942, 0.29581192451899996, 0.23435803066694416, 0.5567984286403972, 0.9944409203657257, 0.40931036913420094, 0.6117874287675803, 0.6747592372520032, 0.5883710356352353, 0.5879986008137923, 0.9894877844299926, 0.24498970716199964, 0.43472097669493615, 0.5658599957342948, 0.6785955276344691, 0.32468469937473055, 0.8120952606970443, 0.9665109134432694, 0.3633211690155298, 0.8776842975299799, 0.6166943967353135, 0.5264436393190735, 0.43461378380896143, 0.31963622439415607, 0.5661547056518071, 0.2799550324270562, 0.5225294051645226, 0.21965894465606783, 0.8745496251589806, 0.355155931673077, 0.9785028143409555, 0.549180958773751, 0.04728436109850853, 0.4408505961142082, 0.14266589754619374, 0.12806936439311334, 0.8422508564579877, 0.30560080277060553, 0.28786165870961034, 0.5910301159521268, 0.04620033959431569, 0.26425608337438955, 0.7018316541730308, 0.5339492648974965, 0.6430291468345456, 0.6907932037900721, 0.6245286197249267, 0.37094536018183155, 0.2396910270788618, 0.39124245712771666, 0.5541688454847093, 0.8713377215893969, 0.05938742665581742, 0.01241460136353345, 0.879517562854424, 0.37477715983213533, 0.07192681026285175, 0.9241059349680454, 0.9385300558643621, 0.4421320115952644, 0.7237581457744204, 0.5911461221297237, 0.5052348293128005, 0.768573703207428, 0.5428363230360528, 0.8136325092440324, 0.08178473157166011, 0.08127441625255183, 0.16118756878439533, 0.5324614938478965, 0.7504733592403365, 0.8395312059157386, 0.006502769647036333, 0.681805185167828, 0.55062774394151, 0.7720599468655934, 0.7108274856720785, 0.5029284824736332, 0.7296136311360604, 0.18611079483260184, 0.3214894555659986, 0.5497521448934527, 0.612312546478986, 0.2567665793415739, 0.18063694335767433, 0.6529415469066755, 0.428220857347304, 0.27033865701859017, 0.6301539033537722, 0.8954399656398911, 0.8620791238652082, 0.358883885983992, 0.6565637660364451, 0.03899031230829075, 0.5992254226976144, 0.676891025853718, 0.2762482994500366, 0.7702445697240418, 0.7883253815379588, 0.20393956323595241, 0.9626316053331848, 0.6335084312247247, 0.2576140594017752, 0.05256518359732176, 0.9159962132008892, 0.2513156443590282, 0.582613297989311, 0.09486499892714495, 0.5089995503110107, 0.023105697168018247, 0.6934221576913613, 0.6447280482700932, 0.9222950845931368, 0.4908271777816723, 0.4012739483720401, 0.5949023418177657, 0.40571994486797613, 0.6467215135683724, 0.09603587913633727, 0.5880987073700991, 0.9475098122497913, 0.17017882359144798, 0.7611288126744469, 0.7800004705344918, 0.9805157090633413, 0.49239767506511134, 0.525621028628471, 0.5955097911630189, 0.8382565015317662, 0.8521067587896233, 0.016174722075197212, 0.9622504576974049, 0.41305828807482736, 0.9696375267344141, 0.9570049439265458, 0.3725469311180356, 0.7217083924350551, 0.13550047029202483, 0.048554001245699197, 0.611121478355831, 0.11699009554859885, 0.2549105305320696, 0.8353167504742361, 0.00855534601782959, 0.7420952212399781, 0.9306301641377172, 0.2582575255846541, 0.40373052563148093, 0.4724456211978053, 0.48473950091287354, 0.13641662775945151, 0.892900261781099, 0.9134971038444577, 0.8124550194246825, 0.021377019307288747, 0.5371219453187059, 0.06616515667907086, 0.8392982081481858, 0.7878164775264851, 0.6038019826468104, 0.5407279567805809, 0.8334685679598667, 0.8828200130301792, 0.2892161433059288, 0.6363827534826434, 0.9111080426139715, 0.2216791093450039, 0.8706828446080086, 0.058320171542013854, 0.0017885147201338603, 0.5374100491309518, 0.9191921406673188, 0.9004840238169437, 0.21546548822697664, 0.21521643757150222, 0.4135650192826279, 0.41735904098918497, 0.3680566475553957, 0.5361010291026598, 0.2060745133027586, 0.6466786414844194, 0.2555059150169803, 0.3042398408694681, 0.13599973293246204, 0.5643396250890071, 0.49022960983678765, 0.886775268876995, 0.6808574378306889, 0.34886912190621966, 0.05910306999475168, 0.2644985648004752, 0.43248727337474, 0.4338321881250695, 0.3379412208548226, 0.7314920530536205, 0.38747717497997813, 0.43788062299958863, 0.6252405062326328, 0.4228607506564407, 0.11043479369103382, 0.8600310571909089, 0.3238100345473882, 0.6118121488628919, 0.5136309395371775, 0.7134454351295275, 0.36297050974034517, 0.7863582181437382, 0.9394021060565931, 0.19272040719334027, 0.8892728719954666, 0.3739539578009009, 0.40828732660228084, 0.7710108251456727, 0.3139143928322433, 0.5231143486040469, 0.5884727079237009, 0.40292448955304494, 0.31229128739915457, 0.008103390161475987, 0.5951526889855415, 0.08913610806878203, 0.9945373885500453, 0.9252330715818449, 0.02261280756297268, 0.7055952792909543, 0.011887107429877974, 0.06471394323665669, 0.3073821113611167, 0.7209790243952364, 0.9890927427895614, 0.2829090159211163, 0.38987754724421464, 0.4054688299855227, 0.020066476289379187, 0.2626615925901822, 0.5590002234109553, 0.9498023765681355, 0.5973420301849269, 0.8980548256172753, 0.5616962292771038, 0.04230268859383657, 0.30308051212676623, 0.35930920515841924, 0.6036950051401851, 0.384968274852718, 0.312308774242101, 0.3692273904078601, 0.3172006270594643, 0.7226276523499817, 0.20439047525077614, 0.6357508706809525, 0.3577069534295817, 0.9492404541407644, 0.3735290617972227, 0.5119756913679082, 0.9664339494183619, 0.6364328990394912, 0.2846721192618006, 0.010964760898709014, 0.49772356258980777, 0.46988334199167014, 0.4279494746262865, 0.22623302281987934, 0.3187704225374557, 0.2093231719134918, 0.7593963353959611, 0.4625524803450076, 0.8468487813319907, 0.30206910755651506, 0.3380613633549854, 0.39455415467782573, 0.7019645750419382, 0.947065639026993, 0.605333850442553, 0.11292456377093496, 0.4721597294029506, 0.6477029655985921, 0.011172089213592806, 0.44983047519810904, 0.38910305768154374, 0.18975209868914733, 0.8165156644762526, 0.16011293264660797, 0.8835426554822109, 0.5429230439593155, 0.8489041844295836, 0.12524355886296823, 0.3400126851146301, 0.5384281394899175, 0.4771459907557558, 0.06033129106902324, 0.38125744632632086, 0.7131492958924768, 0.8136329955769709, 0.16376611177446598, 0.0022631081640877015, 0.18366496166829394, 0.11032363663544142, 0.6709984131227905, 0.591537150789633, 0.3965894462978884, 0.4462240652526217, 0.6489369153602685, 0.15627792060804246, 0.5828561460304416, 0.8021362221478929, 0.46969278894375666, 0.9270688928839373, 0.48232595220072527, 0.3030139868257481, 0.26417159530156886, 0.4771428897714962, 0.03133356850609259, 0.8009407727149894, 0.9277491659668051, 0.532200504678513, 0.6829142967963835, 0.09841692883850661, 0.26374551811487834, 0.9018313727579701, 0.11942764786327098, 0.7166639736889414, 0.5132679723575806, 0.5338325173566333, 0.7805635679525501, 0.7656351819693812, 0.6204226093833011, 0.1850875995156398, 0.9073688196259678, 0.8233469506736163, 0.2658230025797421, 0.13501660774180047, 0.026158102821365548, 0.7538369816313552, 0.4373271076245152, 0.2559079732442736, 0.44318061196793557, 0.18874478556217944, 0.9001217870246204, 0.02510911772630009, 0.629531681380815, 0.27491250373270626, 0.7652802588216262, 0.2342039700077978, 0.1905300339535071, 0.9241302782770972, 0.04821274718469781, 0.2788030830433196, 0.7247337501517115, 0.6850118669022752, 0.9866938645400655, 0.1446727020334575, 0.2597335525496386, 0.7915445798552591, 0.863576504277694, 0.3511934296903042, 0.7049169116788868, 0.6914137749844148, 0.92883026483981, 0.11672137780963687, 0.048423681326212, 0.18739398181964795, 0.3717443471715435, 0.3289046003213417, 0.9558190128626967, 0.20714383936144587, 0.3714676810861953, 0.4392060538337378, 0.984907109132837, 0.9751413322207008, 0.015264435061731918, 0.8991052688073077, 0.7580255717541848, 0.28082798296481626, 0.6179452769767477, 0.9311574279329193, 0.5114546595067491, 0.25643598931795397, 0.38961615906891567, 0.8845533119972361, 0.4662208803328106, 0.8969664884345281, 0.2010493976166119, 0.32510086587086084, 0.4860247268592096, 0.18103893281063999, 0.8318100859577969, 0.7508416834751045, 0.44478094716908256, 0.49254435499316973, 0.8482475369094777, 0.7819299413149919, 0.5624486431318817, 0.8643988258521559, 0.7397756253502105, 0.415206714651393, 0.6352217336497741, 0.933368986711593, 0.7749550979908477, 0.36235331034037, 0.5998729853921307, 0.20554147883025997, 0.4796964376513627, 0.5430472244564134, 0.6611784861824505, 0.649118006557437, 0.0894991374510038, 0.9332151757938915, 0.8518028707789924, 0.6875168603250106, 0.40224345420985697, 0.43613323910022517, 0.5764611501317158, 0.5110203090553879, 0.11778146782866938, 0.2750499555771603, 0.9204412228511986, 0.5982084604806762, 0.49465927285377154, 0.23843873632115298, 0.14799321572142765, 0.5249347049449488, 0.676157317555957, 0.07035946204215415, 0.7955851364803835, 0.31302775703764785, 0.8603218104066013, 0.5653696525722016, 0.045118422639226274, 0.22217852731666943, 0.04206878707044237, 0.9267416745378635, 0.4484419159416485, 0.772649961781817, 0.04313723247025614, 0.5833126281497195, 0.8920846214147803, 0.32629738035933775, 0.834026700320939, 0.8515113953422444, 0.34647394864933556, 0.9312457566253319, 0.9288110303011535, 0.911460819066421, 0.5061654217295981, 0.22126802227839937, 0.11011894041989267, 0.07982945058915258, 0.6014129884740537, 0.21137697706366954, 0.5050947780080455, 0.9368090455974944, 0.8095629063653647, 0.41897458881848004, 0.18376286120576935, 0.3746585886118071, 0.0514557303230222, 0.6149285340353486, 0.7175000558317168, 0.24323239233243676, 0.8995782262049171, 0.4382141996921126, 0.9689105908967175, 0.5567083081333106, 0.21824050358884228, 0.3041010071253871, 0.8578257860572073, 0.6874809725039885, 0.2567360177759136, 0.09289556655791065, 0.601394757441654, 0.3905707847343465, 0.6269622665451811, 0.18548477615937786, 0.9831751317670202, 0.9293763674710948, 0.2883425128582334, 0.9447685757268528, 0.6668718639718363, 0.08860781220164293, 0.27866294123711366, 0.018152249861373426, 0.7769442305211107, 0.22290755311883403, 0.7110899525064801, 0.29545667903194384, 0.21042804961990236, 0.6696809283826698, 0.9429756296173233, 0.9858086538513796, 0.3365876016010937, 0.09820421262945267, 0.9721375652021342, 0.14524893899638558, 0.32051082913121176, 0.3790811793383936, 0.8081682727177745, 0.9041790482728926, 0.9072273155669196, 0.7361854451937497, 0.01700535777444878, 0.3462198523221117, 0.20133171171444586, 0.6552903602781011, 0.9849045806546715, 0.10300029387803, 0.0343363381484898, 0.29587874639823764, 0.27247339500700607, 0.8122815814942925, 0.697282148600555, 0.8019014337248156, 0.32110392002997645, 0.5435989135525243, 0.25336273564042755, 0.07511506630216169, 0.5771842509539693, 0.9494621082892432, 0.05181408451256031, 0.2255346787482062, 0.4052327551356675, 0.07002191149959391, 0.7497381003217017, 0.5287801105987655, 0.08701267341844254, 0.05728977368575816, 0.8453833084072174, 0.7370291032527608, 0.1974931159403368, 0.4410433468592112, 0.6561633530650004, 0.961638637866387, 0.400232474605695, 0.7881918099093638, 0.971989792765586, 0.3421476666378508, 0.21695082711274027, 0.9662372712701265, 0.5587525738781545, 0.23411049934669048, 0.21927272214165738, 0.25875228093183666, 0.39125949901194423, 0.3722976464384721, 0.5799971412857879, 0.7924928130616936, 0.34733016920823634, 0.39825231686321305, 0.47353011301205017, 0.8665153254160903, 0.8170832171132127, 0.7186757014161756, 0.36797525340135495, 0.7202421373604678, 0.22742374060848236, 0.05237345131925608, 0.7815250696637724, 0.537865375063918, 0.05877508249063901, 0.3388461477231621, 0.010378113246003129, 0.7635891851459585, 0.26189296267345497, 0.8921563062382811, 0.5704929121896244, 0.8921102439856884, 0.8631244998126665, 0.21437254249809667, 0.17325378430506577, 0.4413631319356942, 0.16723067628477095, 0.05844671650583211, 0.40713674036451775, 0.5478318535374214, 0.7507637054462191, 0.5518810990780751, 0.3531061208308618, 0.18367405870536502, 0.2128763730880997, 0.5545834436303758, 0.05712173937328735, 0.9396878932616111, 0.8429071406736056, 0.4799604112179615, 0.19740273089087257, 0.9598896492166362, 0.5385708537121373, 0.3020694526890365, 0.5970228839519559, 0.03311460687787404, 0.21582178251860484, 0.2723664867630228, 0.73377974515052, 0.8759617868844667, 0.8232976308651004, 0.03700306133178122, 0.38716654259545924, 0.771694669657325, 0.7642610346956655, 0.8731197874627835, 0.4189921573136275, 0.7403621716160607, 0.591107629855735, 0.4963269450394223, 0.9929002976618904, 0.5051598559514098, 0.8762214154952497, 0.26345798260901243, 0.8734010724298948, 0.33930779461274674, 0.20455454107155213, 0.27202864323058396, 0.8379340605826956, 0.1577136422613713, 0.3497420070274553, 0.6047774698098963, 0.1346439907993906, 0.032487045996263286, 0.42192915900170036, 0.5819629347562012, 0.5583299171311906, 0.9465277347015835, 0.16478091262264427, 0.5694667944642635, 0.30707535620818993, 0.49819159245955047, 0.792023510165612, 0.13850939867398881, 0.7765136993634244, 0.7757240424754629, 0.7027089483498431, 0.7576024695597564, 0.6780908097829627, 0.8115402968381701, 0.04230081680416986, 0.598117466699103, 0.25247094709709106, 0.21789026412046208, 0.5596450902785303, 0.27924138534471954, 0.5836857352686641, 0.3101052990547787, 0.8082219755862983, 0.4002538473011129, 0.4418030617217851, 0.3355220622939905, 0.6418736967123997, 0.04002086572356123, 0.2697100442778948, 0.05219412234533882, 0.9682244357590644, 0.7524399392871339, 0.3150178009344061, 0.6841813700641486, 0.16121920066904383, 0.7166309590400565, 0.8239736649769723, 0.13056426951089095, 0.5382711196638462, 0.2918655247296591, 0.06361986731678793, 0.4997101653793863, 0.7160735980905536, 0.6883210348229364, 0.29028961949956644, 0.32840692839408236, 0.9867303846619755, 0.682667858295624, 0.9999344111044323, 0.9093754505051961, 0.13987442946833872, 0.6717610673233682, 0.870856346750566, 0.789550023057975, 0.8912727758158918, 0.8620626807962146, 0.6647804690817651, 0.7203747981083668, 0.9445149767375695, 0.3485298532125519, 0.7475414127294949, 0.35630027486927696, 0.45177948270215307, 0.40537211735323664, 0.289655671324311, 0.3523591255345878, 0.658299152446759, 0.5723421077235467, 0.32340677976336263, 0.608024402599978, 0.15065571536169664, 0.9454653804613852, 0.6639779299499051, 0.9448532211731823, 0.16446005174859324, 0.8134121698691537, 0.5902108167131438, 0.17269140068719557, 0.47092834327354394, 0.8024210549243069, 0.1835032794252719, 0.22855832354810224, 0.2956629333405023, 0.11277119125261792, 0.3708014084241472, 0.1771214316910451, 0.0613256329734867, 0.15535562508038425, 0.14643768124284207, 0.7113786632051002, 0.6816121941010977, 0.25427440589044625, 0.9105039942575283, 0.2626275949650906, 0.8743248467589826, 0.17775109798408306, 0.8233144213044139, 0.4493045862148761, 0.9289574215563192, 0.41246605757394894, 0.46305006898485435, 0.09465486382456179, 0.14138710454789294, 0.5995265742175495, 0.1895915026442926, 0.7703539240047068, 0.39460296525219274, 0.09298348697370684, 0.05572666816234695, 0.5768972850553533, 0.12143304436502067, 0.22177355070763383, 0.8456161476367566, 0.9950862202917009, 0.8762989615513064, 0.12973237372807023, 0.5096093345704372, 0.29856204365830596, 0.13405184341373155, 0.3508844672598084, 0.2715606876631014, 0.5920439335131269, 0.5203008049176737, 0.2645334446296833, 0.9961756572030332, 0.6947528615717281, 0.2656923389499519, 0.800219418664097, 0.5253090362395398, 0.9331940049262183, 0.20702393231987304, 0.5133355601340401, 0.30525838587897336, 0.12777611264004018, 0.5699751271320035, 0.2552404635084413, 0.07162322795740794, 0.7647529845336876, 0.672224159186855, 0.7739403827398212, 0.1595963822742964, 0.16503380393425038, 0.2341066103208712, 0.25413513980031965, 0.3201946129772437, 0.7886082407666994, 0.30279949786360616, 0.5458688386567395, 0.27593536647410677, 0.6199644196256926, 0.9769056462226836, 0.0690346955004767, 0.7356449880772845, 0.5680675438627516, 0.7885194500613456, 0.5745253694880936, 0.09516979118464852, 0.41095363718596567, 0.5247806528166639, 0.06889327257344358, 0.10220677524749744, 0.46156592611062375, 0.9941755888582899, 0.6575323541511688, 0.8903014197576481, 0.021566699717169846, 0.5854098813021632, 0.024849866692510547, 0.7321832185208413, 0.9398908189062314, 0.161605146097898, 0.2923692981350924, 0.29683177201663824, 0.888225972664728, 0.4952168768403802, 0.9347639362844131, 0.8957212359907937, 0.33057629726945703, 0.6980354931964999, 0.4623267600384875, 0.4295381149626404, 0.763010526632678, 0.603341430953062, 0.7821487281285144, 0.9834613693375158, 0.12016505491050056, 0.9589619378542033, 0.4665205603498396, 0.2331460897326887, 0.5503369340809909, 0.32026322926348005, 0.1281583012900599, 0.24177065071469128, 0.8703669385484409, 0.014422433798426337, 0.793121808695591, 0.9887371052863829, 0.27674894683934126, 0.3601826273412466, 0.6612945952139901, 0.7978130570800702, 0.7680528221246946, 0.9683709178140776, 0.48495751622276795, 0.03602089758790905, 0.6294163266719937, 0.9471301945981717, 0.710097092302267, 0.12870016302295506, 0.023377190448314322, 0.10137820933379493, 0.8781540719257389, 0.8141122873538388, 0.11184975599118285, 0.08318427795620031, 0.28165385046275526, 0.8517555579123011, 0.8221724831015889, 0.45468896351717525, 0.613370628079813, 0.7416285770432711, 0.6578158745550554, 0.9242826184836967, 0.19823000884358288, 0.1946117703636946, 0.15748670161390943, 0.041554014102250125, 0.17467695217063406, 0.536890983485062, 0.6051092503685662, 0.22638709958870196, 0.2577118066365772, 0.47789381671870235, 0.40216971144124936, 0.9081173281300887, 0.4323062424734797, 0.33331616108164186, 0.6387841843184672, 0.34771928976438904, 0.25238005084111514, 0.0673507596143672, 0.7827784228217279, 0.5486749171461384, 0.2686786993773266, 0.7216673320831933, 0.8521385622030841, 0.4036556213101784, 0.05389955361271492, 0.8605727495121023, 0.2620183453126005, 0.7428276631488362, 0.7499868891698707, 0.4751417615162302, 0.08078468464713362, 0.4833549981351992, 0.29646612965330355, 0.7230809728254035, 0.0013587526739268219, 0.6485697032808296, 0.8236726896984554, 0.48605546526841714, 0.5886948874045671, 0.039866344675153154, 0.8772918848628517, 0.9278577278780504, 0.3533904891796865, 0.526476660178618, 0.9840169017457732, 0.3914102913105054, 0.09552078871295433, 0.4263214500389727, 0.4160116237030925, 0.4775880417453596, 0.7728455635232607, 0.13485017351503592, 0.39924559821712424, 0.9352737505809616, 0.4797889211413007, 0.34357765474066104, 0.8648071336289281, 0.813513159951602, 0.37306270264629016, 0.4990443401952108, 0.9014805016325693, 0.32956878239317655, 0.2053848292855347, 0.3525575775160579, 0.5176633807445933, 0.7516770606798547, 0.04562244478478217, 0.1697806508231906, 0.593943897397884, 0.7363436395713012, 0.594900843719289, 0.6911625891709269, 0.6526154357662239, 0.05973222546491319, 0.4538110117378529, 0.9660242907014512, 0.38756108341096485, 0.43861132953360515, 0.06521149107238222, 0.639911222345425, 0.7110133731361981, 0.33737462182563505, 0.920827379705587, 0.4289816371072974, 0.07185369345591985, 0.06472721805646531, 0.9524089639989497, 0.44624432954810545, 0.4963945823468069, 0.8395184978194854, 0.45481361137329523, 0.23145947579975878, 0.3836691793079763, 0.041253631016087144, 0.7689487771662921, 0.7843263106396721, 0.5921029375626075, 0.178462024863297, 0.38195102635650247, 0.18393464903080758, 0.853978220418008, 0.16226466739788248, 0.6028903173288414, 0.9144495364343216, 0.8495834813249012, 0.9989565942210943, 0.3982606756919106, 0.49710529158564365, 0.8058155133515219, 0.6995545318333856, 0.8046146561850005, 0.21531481161005384, 0.2660918678310139, 0.4963448864050486, 0.011219916681143527, 0.7814034093507488, 0.9698350708617531, 0.8206367554151386, 0.0811353783080675, 0.3048635443295752, 0.34035895649236947, 0.4741623827096034, 0.4755925001741895, 0.23599971348225468, 0.5972830659522512, 0.44446389036036027, 0.18781147593917435, 0.2852150593091246, 0.9247682052276058, 0.39022873535731395, 0.29999547645337565, 0.23261722839790344, 0.4726943541336024, 0.32999969901504733, 0.4106989605368676, 0.25987594226771926, 0.5733237991090476, 0.46743347859059914, 0.20734017822547657, 0.8250933905245337, 0.8950083703449331, 0.9826330335178797, 0.2588455973558593, 0.8848482397545162, 0.22425334548902476, 0.007114102341946094, 0.6178306237171123, 0.2882679935056218, 0.004110606721978272, 0.3578514370324011, 0.937117502373018, 0.8191362478327489, 0.5264503774680637, 0.7126310314599116, 0.725033035599427, 0.6836460833678726, 0.9489555706663746, 0.24217381582170605, 0.9981285947519442, 0.6885491304249269, 0.4083676847227724, 0.41476349129012857, 0.19828809994981234, 0.08554267342931854, 0.2724756424933251, 0.6938317918015329, 0.14644679680150752, 0.9188312971572159, 0.49378911499433087, 0.582784427728424, 0.8372117508389326, 0.24040536728651163, 0.294899190156918, 0.7600285165968004, 0.1306238194294148, 0.0475468072376124, 0.2974487598308012, 0.29112882855008715, 0.42002893918675976, 0.2857520673654842, 0.47201924256805516, 0.2203772263861664, 0.5649892518642434, 0.41960301968761426, 0.021473881707026243, 0.8267686083066739, 0.10934400430896418, 0.2688685389783312, 0.27425166388781275, 0.5020029909044462, 0.2474929645284265, 0.09668173589614204, 0.48362150833826734, 0.5214144537225854, 0.05779557946888281, 0.34711514861747206, 0.44103471585161436, 0.19257946498362577, 0.06857816020547614, 0.7895372691077953, 0.04804763170078852, 0.7658751154176736, 0.74824490448168, 0.6560107291125247, 0.6299841841489916, 0.12680992071631447, 0.8980663961263227, 0.13756442813749192, 0.6043579779445404, 0.15684452277827166, 0.06156868078255817, 0.7600416796273484, 0.0041341338186680066, 0.46616097834364856, 0.353338545534724, 0.5360763505364982, 0.23993508958618148, 0.46383924606953497, 0.43949438112491745, 0.11406731638782297, 0.045103838284834885, 0.7981253345694256, 0.6012632962924179, 0.23569683055647783, 0.13351735962171918, 0.6005229376866086, 0.86711390221398, 0.5268355039292378, 0.16525694371415878, 0.6182720043990849, 0.5888447353429345, 0.2615255713038652, 0.7149559980228649, 0.7500650589278361, 0.732435553882271, 0.8498340899577493, 0.4323993025519053, 0.7524203478625255, 0.00926228750802971, 0.43384304529061035, 0.466847231825109, 0.46020945246307177, 0.44590941202823486, 0.7852062253288729, 0.06713230092025946, 0.7689787442422019, 0.031521215638755984, 0.6856683373579755, 0.11715023177116335, 0.9477129117060692, 0.6103592592393331, 0.9726436692624316, 0.8719805409274874, 0.9600124902875928, 0.7633157640954337, 0.9031194006984042, 0.4117097655798424, 0.5917728902647283, 0.880696780078381, 0.10076849583773773, 0.6440486856072943, 0.5578275563873039, 0.19923344200809012, 0.729868957904753, 0.022465466357680097, 0.555717066085314, 0.04111507661864633, 0.03990711913222722, 0.04232565979515879, 0.9913994787497808, 0.4237501411829311, 0.472725602110709, 0.6500451579043571, 0.7974431296125448, 0.7921010448281448, 0.75532316597476, 0.443662947185513, 0.868632168915875, 0.637953815996993, 0.27687102768226457, 0.4844189010822929, 0.7619495590109543, 0.4988385920081573, 0.5733691945233387, 0.594937884768482, 0.9796855921456933, 0.8707838701595241, 0.13988820411508085, 0.8029451472278305, 0.836685754190935, 0.021052858917557704, 0.2992704689336185, 0.3022074571287551, 0.7572899905699652, 0.4300839916838026, 0.7707864486268577, 0.8673409467843307, 0.9434105103438207, 0.6326363671871539, 0.6667845795407594, 0.34096992156059946, 0.707632243060371, 0.950964921015516, 0.5800677495952639, 0.7511405441957287, 0.6516326902418639, 0.6007137599408454, 0.4490037841618797, 0.8685940002941004, 0.23347001254834931, 0.2786319207646102, 0.07699077865421378, 0.9058912618889178, 0.8019059430515363, 0.0221649395179927, 0.7342096818030527, 0.10661336410019429, 0.6833093656955919, 0.323633706564883, 0.821913546511289, 0.4876412538229209, 0.8663555957631257, 0.9784109123396604, 0.494848107427869, 0.9485381134044084, 0.23466042866463965, 0.26879330230348275, 0.40924541255648617, 0.024547492477307475, 0.8684653423970778, 0.40061932541866885, 0.1331811266667069, 0.030309176671732496, 0.07872555954011373, 0.4144064580934682, 0.13511750669157718, 0.17107649830858374, 0.7071731489900208, 0.7625363329695407, 0.5164087569034105, 0.5158360046777561, 0.28535790612195233, 0.9879664343944952, 0.67280256912603, 0.8890291546480457, 0.9160230021859649, 0.3870806889253373, 0.856090460117206, 0.5768102059551495, 0.9223337174375985, 0.23721869407349916, 0.4069096715991599, 0.7796022542728966, 0.5193936684525793, 0.1748902593527093, 0.09086477172395413, 0.054490239252921735, 0.1881730383889063, 0.7110632070770782, 0.8303308295384368, 0.8334735451402168, 0.5379791047283308, 0.16302925152042347, 0.7727351062557225, 0.3388189644788434, 0.6973041144352392, 0.4733588987442421, 0.8402609835393424, 0.49625970826659327, 0.6378136894404014, 0.2856951819363074, 0.4413238986227448, 0.6525680894378554, 0.9983963327111249, 0.48752627131731285, 0.906506038704346, 0.01932347244522925, 0.8121950275380121, 0.9255041756709821, 0.5995564672674958, 0.4205531648080212, 0.033335219953896544, 0.5912868361012278, 0.3196128167231035, 0.221903568953581, 0.6908879786020649, 0.3787754104609753, 0.8522534041955377, 0.03873285724146169, 0.43482947815592, 0.919129126644546, 0.667354082627777, 0.31783226395103603, 0.8001375957424187, 0.17310362640226762, 0.5233480284832298, 0.2913233109609661, 0.8792650757288446, 0.07868718804987207, 0.9509021711701667, 0.4108003288622233, 0.5934766628579128, 0.34995291077153867, 0.41854717950418097, 0.6941658891238749, 0.12557733400099758, 0.3281062412202753, 0.05141635826312552, 0.7419427766883007, 0.5974167460502979, 0.11843824474324205, 0.41624570357145785, 0.5241978143519431, 0.6088797415457056, 0.07468968176757884, 0.5023265176344017, 0.9090329039918261, 0.4732874239558371, 0.0873343552445005, 0.6764967429865865, 0.2685285522329034, 0.17987348708361062, 0.21794025543419937, 0.04506667459049274, 0.5018862569659501, 0.5078747135732997, 0.43021565967376363, 0.6523140326710496, 0.28274802785807285, 0.07106725904517608, 0.28412045938179287, 0.9880686559758622, 0.15413418168040405, 0.6816532780414968, 0.10817525221350599, 0.24761260716111821, 0.8649020852886178, 0.411873463400273, 0.17058153589762415, 0.9163691971503306, 0.007196092301011703, 0.1936665602549229, 0.46466627431828744, 0.44295911943086863, 0.1172971321827675, 0.4400844880916466, 0.5368268361835457, 0.8684164555968115, 0.2812307653966326, 0.06851445918914023, 0.7132782777678082, 0.09576820129809371, 0.8995898428580046, 0.10543798768004409, 0.4614566156221068, 0.6331937101571287, 0.4807961686524217, 0.4609565296429643, 0.5836532376147622, 0.5807543463780841, 0.8162136284856114, 0.8132769016139306, 0.16919281057255597, 0.6922889722501279, 0.6638165028617848, 0.44427877700540563, 0.24612130969874924, 0.2288978442462356, 0.4196732099844862, 0.6068876369911855, 0.8538412466282072, 0.5377958438136206, 0.0001820101730740653, 0.06012719703223002, 0.7839390339179111, 0.8661168961580733, 0.7862900458227231, 0.775939700793733, 0.04398179954449821, 0.35386997226032924, 0.38318008423155825, 0.8753253311427119, 0.5387594663326629, 0.11380706765344151, 0.379221151136929, 0.3369951011284258, 0.3586380278000254, 0.24562341723876546, 0.7498769304062437, 0.24873804182437853, 0.05127831463752808, 0.998994870524362, 0.775559809580817, 0.6384471957165043, 0.012789066888993506, 0.20010407278711184, 0.18521892179341282, 0.21464298369620527, 0.34693695168648864, 0.4316773585977651, 0.7126073849598474, 0.7548406602482975, 0.9296337158718612, 0.12077500898366889, 0.6245571106285978, 0.583836571235023, 0.9160327609345381, 0.922492499533602, 0.9420495998387024, 0.20225159488872646, 0.33422669541135364, 0.739250921818253, 0.1884582293852114, 0.8695566511000842, 0.7363479454729783, 0.23805479899600146, 0.7407899518410447, 0.2755179071645256, 0.6912781729057249, 0.04029952914467361, 0.9398317582837065, 0.9261184105857462, 0.6223123077462753, 0.2650908892091116, 0.3408005108816735, 0.9965574809953514, 0.46445559413888493, 0.418762462623965, 0.24059957173932311, 0.5364698219203713, 0.17213550136081102, 0.41049021521591167, 0.5401304007079931, 0.7357920834555868, 0.11236329476922269, 0.6067416559966118, 0.30045453801629995, 0.5362729073390462, 0.6126397865724198, 0.8408852964127183, 0.9395203879546513, 0.8029151136285452, 0.43569243314527684, 0.31820688821012033, 0.247134880790028, 0.8186121927712436, 0.32669531958500064, 0.667774009341066, 0.1425393689196467, 0.3150549477793537, 0.006931651342571454, 0.37126719317107526, 0.7684911017700815, 0.12496740176870935, 0.29317902632472626, 0.20034287744146184, 0.5340688691066464, 0.6159440609913173, 0.04264050938256159, 0.28411421975240747, 0.16536872596589292, 0.37402454445497735, 0.27979702387612193, 0.29424633772813824, 0.1341630729328499, 0.07763118770442157, 0.8294037178312093, 0.6445986349739792, 0.3573744028172974, 0.3359609212464857, 0.3662960055336121, 0.7267007076504431, 0.5282700898845214, 0.23177774254702455, 0.470034327964415, 0.42530540953223683, 0.1855509777931731, 0.26908806206556557, 0.1058875659598546, 0.2918959111214987, 0.5545413381101905, 0.567650111225151, 0.6251358005929395, 0.5933163913435103, 0.4060824049027698, 0.3563463664492532, 0.35579322788767087, 0.6731741839779117, 0.6030411395318556, 0.539902239255278, 0.41469875627509156, 0.8169267616188663, 0.7481953395321682, 0.04745545889242653, 0.9136849896008767, 0.23983362418774523, 0.36534185129051266, 0.8244963402964302, 0.2655065350921111, 0.08034038945972422, 0.39861362533490385, 0.2103281730057336, 0.5606626584279822, 0.3761745209390953, 0.3521432404037028, 0.7230344739471675, 0.24479933799615217, 0.130564383077452, 0.23182891228666191, 0.13456639528662862, 0.14881261821245917, 0.5215527736126426, 0.6059596476399376, 0.5008135126734993, 0.5073085084774656, 0.16221552331119804, 0.6569892805853472, 0.023823951884095362, 0.24088471492098207, 0.9147818962823043, 0.8693736909602656, 0.3294903103332074, 0.4000389448166144, 0.8559660814456523, 0.20719352722991435, 0.20586435039089146, 0.4929536358123232, 0.0284778463489761, 0.30467746930710504, 0.6328536928316043, 0.7691416172430684, 0.9637769150111929, 0.3767251645700964, 0.5119265629781609, 0.5462630373901048, 0.8288551022692897, 0.4005909943239402, 0.20637488276832783, 0.6035790621789057, 0.6395792658562701, 0.42420700165424496, 0.0022867360860429065, 0.17061920599563474, 0.09465517020546466, 0.9655750476934547, 0.06734395045139452, 0.43144153648859573, 0.8167948544785013, 0.2868153926147301, 0.7381193628197686, 0.908682969271311, 0.17655464918497465, 0.7443308117004017, 0.3300566213058971, 0.21146004717299705, 0.29257045439475937, 0.661600674725096, 0.5293186076596803, 0.3855758051123559, 0.32653997627207876, 0.9399809592108904, 0.6717696795741708, 0.8890848140281892, 0.8892205579650635, 0.42105114843140046, 0.5967477733647794, 0.24103976527527382, 0.10398362871060707, 0.0590543439899619, 0.5312719269231081, 0.16846601546263862, 0.2721027330357856, 0.9269754095126502, 0.2457055747937893, 0.48265466231188936, 0.4668849041781735, 0.5141109693686958, 0.6234964068512966, 0.28330092949879404, 0.5762229615596921, 0.8515478253312639, 0.6834088928467109, 0.708220890090973, 0.3269988295645756, 0.7524749744744885, 0.13811343367924422, 0.5801666070348239, 0.9957700676641733, 0.8831522987220461, 0.40343267550789286, 0.5205365089412439, 0.9539164251395428, 0.754499986986482, 0.4467291942830106, 0.5936160462266381, 0.5710205352468797, 0.5270047257938951, 0.45164915195739164, 0.2691168623386204, 0.6750068715192817, 0.11957620398471724, 0.6199395121547603, 0.9313905823070637, 0.26675434276491106, 0.09100085646490552, 0.09246017788786476, 0.5948023039352007, 0.1701221210699292, 0.6842521824606033, 0.30698034058199875, 0.19742432338007554, 0.6024877191469418, 0.8902628719182986, 0.06047871106563152, 0.8631127790901112, 0.5077809457414237, 0.7728702230516774, 0.5028895064850561, 0.7750250102673119, 0.8957417305842154, 0.10733555728450861, 0.7478021739851379, 0.0899010730440053, 0.44660696413342926, 0.15137624315723375, 0.5913262760232515, 0.9560738958091881, 0.7874244726408918, 0.8253902953367841, 0.9418138202926816, 0.007836847312340023, 0.4839496639431803, 0.024038625585567686, 0.1851074871157825, 0.12281028550110629, 0.8064402324522449, 0.15612839722975447, 0.7060641037996749, 0.4673448736786716, 0.011894829080457359, 0.39272168726970946, 0.7161259792323178, 0.6290052734397343, 0.7772797803099432, 0.1574463433421165, 0.8030899813503648, 0.7363431400338964, 0.45879823345308324, 0.0037917753764487028, 0.28447976376466977, 0.5921853608258534, 0.7245782648400525, 0.8096837273927996, 0.7932210447765462, 0.15080502500483772, 0.9259156010110698, 0.15669259858340023, 0.05376718762761912, 0.17555446073882497, 0.556873070039762, 0.88559663950969, 0.18637987027397696, 0.7700255428942459, 0.8164845822377289, 0.9138337355820165, 0.14901577192750448, 0.34358497671230726, 0.7940872150147961, 0.6041870780033277, 0.9520589780511517, 0.4337068157339632, 0.9677477722371496, 0.5392420826655399, 0.07939819567247197, 0.22847717117027255, 0.7655723588101238, 0.041164715874710156, 0.8285532626279466, 0.21536398847890037, 0.583061000667976, 0.0062261609347386004, 0.03221266681545243, 0.0861970443208151, 0.8763050548197815, 0.09103933223536842, 0.6737024438959067, 0.7405594875601649, 0.8125159677470202, 0.9658410265388896, 0.38767817859684217, 0.24770028846362457, 0.8356555369302041, 0.14644493140939052, 0.1400698032811769, 0.11292835074344476, 0.8292038135029747, 0.8195253443641697, 0.4305707875447039, 0.008768925103462055, 0.9418116386213089, 0.3700537696460441, 0.7281458705441715, 0.3525597878986072, 0.4706622356938852, 0.07597023166061723, 0.7263845942968795, 0.7926957856529625, 0.20708854189893933, 0.8550994281361883, 0.4921826901475681, 0.731291818473225, 0.7581965712856973, 0.9847295665065082, 0.35840503352716013, 0.8036214506614977, 0.6721274753851932, 0.8500341541503577, 0.05622160200809767, 0.9192843691149019, 0.027933283911725004, 0.9280325658207272, 0.5617424927797804, 0.5642222892605603, 0.9011999782137274, 0.3167170964934296, 0.5419148325336923, 0.3651261427058342, 0.0159896116887146, 0.7018674495198965, 0.8360808351884182, 0.7375427821032601, 0.7412603958012424, 0.5150371220928276, 0.7748984109571144, 0.6296323711967572, 0.6234499015258101, 0.024127763826156445, 0.989420995145785, 0.5510541799966217, 0.016152307255765885, 0.9004863713616409, 0.901535273772316, 0.5337852001885921, 0.8199119894702028, 0.9602062266495569, 0.02635737140901462, 0.5152671357593348, 0.11413472626947263, 0.7271220524232084, 0.04669851962449345, 0.973215206797113, 0.06783606544762733, 0.5844296822524406, 0.42134165886829256, 0.825224107446682, 0.21615617130344023, 0.4605835313838086, 0.7152292017218791, 0.39286153037332894, 0.2539815252546994, 0.22192389250490863, 0.8671251111429498, 0.9326793274770836, 0.4985496220390869, 0.2884633592216248, 0.2583217015191792, 0.940757553166467, 0.1604329513170739, 0.6821676702342997, 0.5233404828416436, 0.0775679753161076, 0.7760026334993639, 0.9614881246947393, 0.6950328669480749, 0.8515268490542989, 0.09479128969214268, 0.39494728277981694, 0.4891769476639597, 0.41815752427950004, 0.002589580520870216, 0.3521693755960913, 0.6173911460923495, 0.8436265316336606, 0.4357535838448764, 0.6043833408130997, 0.948749730572852, 0.5456556522329518, 0.7662402976927806, 0.053064650631492793, 0.3742569671467624, 0.5827552867093838, 0.4889867387806579, 0.3820360142557956, 0.041034126282015415, 0.03371107995460243, 0.17335834127993832, 0.5371189738919894, 0.29752399365933646, 0.9286286264166171, 0.10053376819026816, 0.9519555140547626, 0.5380222669463706, 0.5360900152115715, 0.6896312366373103, 0.23960618855662463, 0.5001524977804008, 0.9410407030719887, 0.5546259450199411, 0.7384377027597124, 0.8867532014071955, 0.5532096254824155, 0.3888227482273181, 0.9584850375383954, 0.22411777454756432, 0.06716569034802933, 0.03624978672089152, 0.2449932378264459, 0.8147438662205808, 0.8235595013273971, 0.2893755968545869, 0.6549066969067938, 0.5884037291461175, 0.6833479121086908, 0.3258673953587694, 0.14899594581568953, 0.722285317207751, 0.9387781974451291, 0.5956209233022104, 0.32995424803264606, 0.513543699170583, 0.6856517421406892, 0.3484620158608389, 0.08591173217023884, 0.7216905568962927, 0.572228776676013, 0.13500720071578665, 0.0050531610163068175, 0.6305800108483972, 0.27613953256055224, 0.3113362409469934, 0.9481644323543554, 0.09548186749721632, 0.19042100198379142, 0.6501161284002616, 0.32604043008100503, 0.45583282030161676, 0.3092296984805829, 0.5981846050269867, 0.8786203326873409, 0.4211951023483903, 0.25893027667094404, 0.5820861663660312, 0.16588048611517814, 0.9909001330674879, 0.5146467776521106, 0.6890849695525968, 0.24123070427349003, 0.1645764521259283, 0.08324399422537854, 0.22221536783269424, 0.7318393486409069, 0.5270003280355477, 0.03360274379553796, 0.6139566592431733, 0.8015177461520704, 0.7291459651181122, 0.04219298921856329, 0.7812088799573482, 0.038004761877105664, 0.15169045145630933, 0.7336080796610778, 0.4321421952876542, 0.24856079593973557, 0.6081573338404965, 0.8733286351828925, 0.7890779557070375, 0.04189005311550542, 0.27637014102896573, 0.6204954038575486, 0.5653786728700275, 0.3732710478564275, 0.849386101873059, 0.9653013944564804, 0.0807368816315579, 0.04608995311394204, 0.15113810120034965, 0.990384502134036, 0.7495425194796209, 0.07615960014862666, 0.3820918759585902, 0.757002544984481, 0.37983058080434107, 0.6084548349806261, 0.7592175264980374, 0.6377560264624994, 0.014791085098256329, 0.5036562051824344, 0.9543143183435266, 0.2604842540819292, 0.6173257441758949, 0.8261649801252334, 0.8013303320945281, 0.14527962650796356, 0.22448127924488914, 0.32509376978289195, 0.5098732051987036, 0.19046104219183801, 0.6392980519244734, 0.21859424523447457, 0.26278855474731755, 0.18072378418074853, 0.9591595406028821, 0.9190787106943422, 0.48302761425224616, 0.7422902417466823, 0.24995642067620194, 0.12466455199951032, 0.8272258519851345, 0.4114210682179176, 0.32062426361257945, 0.30458700001408, 0.25667551160023694, 0.8900286474799964, 0.42455454617674293, 0.45666880150266953, 0.0693183413941536, 0.9454989347857441, 0.35165264478129843, 0.3498666628649668, 0.01456774626142987, 0.31515040663895133, 0.10346516575790154, 0.7578485962534294, 0.3309948092820333, 0.534297688397666, 0.2857557785794663, 0.4193694879451202, 0.08756225558562658, 0.19137192615143683, 0.8954386627589025, 0.9591420819176131, 0.993492948252887, 0.36936988473957844, 0.17461262186922533, 0.7392188932477525, 0.752907274396299, 0.9291615441767478, 0.5512000308603481, 0.381139811279397, 0.5865361829032815, 0.611593134511888, 0.22338528282159997, 0.1605048387912127, 0.9035349998127344, 0.10685187281330522, 0.04950599766051966, 0.7713245856983733, 0.40065711193552667, 0.9119457079044073, 0.7262105842833073, 0.6553078510892713, 0.15560506127053697, 0.1551553551941499, 0.03542722557158384, 0.39459663453385474, 0.17302792860073513, 0.04743024311252164, 0.45222697483459573, 0.09727342383121718, 0.37070121288662183, 0.7717157479636357, 0.6526827338596336, 0.9597813263941959, 0.3506004159048033, 0.4120935734358421, 0.28746676879539, 0.40846442705034247, 0.34042521125650027, 0.9998776398159358, 0.3199212645260523, 0.3787052054488068, 0.7954085859068571, 0.24121975389211103, 0.5007010982589831, 0.5557316216194076, 0.7120093450390624, 0.7757483338262458, 0.15679902985768457, 0.5115840422955561, 0.4683384901513723, 0.9710901626736105, 0.531114877023973, 0.11944046760628668, 0.28810598823138733, 0.49737931173820227, 0.7630338973591214, 0.6297796776608683, 0.982918177966818, 0.9754048510738085, 0.30894769342950446, 0.1408139794098764, 0.1421447645088545, 0.7805266338360533, 0.24009724933284315, 0.11350093545615292, 0.17353948867266333, 0.19109267959865261, 0.7667167687284862, 0.09969916744372154, 0.7189765042250021, 0.9386198919957126, 0.1794141209968937, 0.17547456761587, 0.5300011606306563, 0.0942936592224356, 0.043386635042763966, 0.9714582340334335, 0.9914623205017665, 0.06662655613515922, 0.15741300969346605, 0.5879464987497366, 0.042086381233854, 0.3562158512248824, 0.443417272397133, 0.07566634837683883, 0.89634056982892, 0.022100208338563188, 0.6361340178435013, 0.9620599959216278, 0.2713322161356465, 0.8488416767279183, 0.1498237166844839, 0.37875305290250194, 0.4773676271281221, 0.8938920543568624, 0.3843629822974356, 0.09950524502221147, 0.20396081180396708, 0.3077922050083325, 0.5615088176538799, 0.918773298750677, 0.40293770414876373, 0.918592120395035, 0.019895001735154794, 0.43764829173947684, 0.6887578842986972, 0.8228543176726193, 0.5226371799728504, 0.4682092578022833, 0.6446047763275783, 0.27680698885994237, 0.5935186026217055, 0.45485018935797084, 0.8418826034312816, 0.9767222143976066, 0.5117145979721889, 0.566149567436225, 0.8763309511866845, 0.499923718246694, 0.7161767899432988, 0.9099114594312094, 0.29641050214914477, 0.0954943857066205, 0.5936248330113836, 0.11020524057556624, 0.5175859520520134, 0.42662706190829447, 0.13726487467797988, 0.8011462974433778, 0.7703060716926005, 0.30144372606039793, 0.7224483265482576, 0.21876759896010178, 0.9199722993473572, 0.17055163283414543, 0.2815264904912502, 0.5830296466816132, 0.07820325563111274, 0.8343410830887459, 0.6098400806799412, 0.1139511840093036, 0.8982717680510702, 0.27792006001022285, 0.07470992041645985, 0.29259309942416034, 0.46252455578479323, 0.009096850030739678, 0.9456742603747124, 0.582154355738705, 0.49120756461815784, 0.4281452027122896, 0.9144348881913614, 0.6908781650908771, 0.16718051131447043, 0.5368850490327784, 0.05347617173396779, 0.04521314971280177, 0.8961707730083248, 0.9798855033702991, 0.16480904255871043, 0.37301216634895107, 0.2524925851605131, 0.5232767842087098, 0.7691593448330488, 0.9536964916877203, 0.9848775214497036, 0.546559794412735, 0.6406298013606235, 0.9114179316381104, 0.41169760443203196, 0.050971120079208565, 0.9613464804886003, 0.9356312388442105, 0.9517782951791955, 0.4062152467312564, 0.4296848295237362, 0.6626379387038296, 0.15413405458482943, 0.9391679348537739, 0.63801076840913, 0.19770649294628073, 0.14329257523214267, 0.24694895980913123, 0.7753486540336143, 0.7404694927364381, 0.20774376083936952, 0.5578868313750754, 0.47477915987055463, 0.6596469680927798, 0.1963596193492394, 0.6051300750975935, 0.7234991160038934, 0.04905759995353154, 0.7773179075013043, 0.49347551827551184, 0.6188762345745582, 0.14319769591362674, 0.5058206446025271, 0.214621999730513, 0.8030536961046402, 0.5097326026525754, 0.573781625100325, 0.23586093188786506, 0.01756712760874246, 0.028441160053459424, 0.17403124536830727, 0.6463542000447045, 0.3276111952616175, 0.07432614797139292, 0.10385318009891331, 0.3167305499719085, 0.06311345757646147, 0.18962033979741688, 0.8814844946531515, 0.15491351069263926, 0.10852109814295696, 0.3240637235044723, 0.36559071047741976, 0.2564973944069866, 0.6826292614794567, 0.24747784083097324, 0.5746978029366447, 0.06891287393783507, 0.600125175206528, 0.38191339337927643, 0.8627395667345134, 0.6230874782216934, 0.9210343883110211, 0.9724284063784515, 0.7431049195537048, 0.9696098011907885, 0.04618012856063358, 0.13673976409545696, 0.2281827149464647, 0.07016593291139372, 0.9389972369382291, 0.38973125312917256, 0.0013417138651293792, 0.049013252619224734, 0.3435698928387867, 0.3842870570793231, 0.43269632772394195, 0.8522927514527636, 0.755969298158086, 0.9339258507139604, 0.9136241944280807, 0.11522556842570664, 0.78335990296543, 0.611482297547138, 0.5162057004111185, 0.5143283856491905, 0.5482974399405539, 0.5897777047423666, 0.45219424036166156, 0.5758191701388371, 0.6984615264093182, 0.598111605345339, 0.7432743938310424, 0.20560371186312243, 0.3402964803568025, 0.17336099556730689, 0.8669935435193754, 0.8967247415048393, 0.11265689079018526, 0.10030682162467541, 0.4108619107229994, 0.24060839367580422, 0.9393915493941769, 0.9457855092079419, 0.17875232120634932, 0.42578326188448756, 0.6698869198498638, 0.5824992597630952, 0.25467239643420037, 0.3049903314837056, 0.048010554652256454, 0.3861953542566655, 0.5345273410223993, 0.02624265892337896, 0.6848512549823775, 0.002514097826813111, 0.9396724066630506, 0.6219813242597629, 0.9995311930688077, 0.23698645667834384, 0.1705093220131445, 0.3017230951321942, 0.4143836311475525, 0.1767556976050806, 0.7084464121933092, 0.07801558589512991, 0.40284553390334454, 0.519412074409634, 0.15793171509248938, 0.18495561278166328, 0.8193602367999603, 0.49194064014969774, 0.6200423767761295, 0.9162033188748976, 0.8289827810984656, 0.9673295648421363, 0.6512193643108418, 0.16411888147926568, 0.23383804059763114, 0.11964701561830104, 0.6290278355052964, 0.9950103755953448, 0.29995291760004783, 0.2983580309672912, 0.4568280505317853, 0.12036860501427671, 0.7655538601568828, 0.20217928748091718, 0.22390669334174584, 0.7018462032438008, 0.8951049333769487, 0.6408536578064189, 0.11923325800797147, 0.5788651270556688, 0.28746660158034365, 0.33777613814759233, 0.6113074414616786, 0.7337042150149125, 0.41170069084718797, 0.6939031555748576, 0.6775056563440938, 0.8529427257187413, 0.3652924229440403, 0.048099343782390114, 0.21789259382300408, 0.7367935457485177, 0.23088031866698078, 0.9133046070597758, 0.642658696321858, 0.06871831747188573, 0.3511510958290064, 0.24886822958384247, 0.36759300858275834, 0.5355212813587565, 0.6234508362469428, 0.5433610213100648, 0.7909494857889581, 0.44185026695052365, 0.7152703888002844, 0.9788794367484707, 0.3384594262355374, 0.51451618182596, 0.7942183252400027, 0.08613796561292286, 0.2294362673417849, 0.05194408733084144, 0.1721897358594271, 0.7832719681111163, 0.48639651559051134, 0.39585135910388103, 0.7521834990319302, 0.07072008710945821, 0.17760798159525137, 0.23718053105526427, 0.6331239258299188, 0.6347519205097168, 0.8765830782746383, 0.9565809403047149, 0.9998768782909935, 0.4709686054539567, 0.7073010926730097, 0.3052706870648968, 0.5197766682135851, 0.5565881174458365, 0.17969173133250826, 0.3681515934629004, 0.3980140261931231, 0.023802569996914102, 0.21145440202098342, 0.9195942258593471, 0.24079018878434544, 0.9733819174048696, 0.9692146455721969, 0.09854074135406643, 0.26894464767709325, 0.8179284951769817, 0.7160063133938216, 0.4510908896392407, 0.276610298188953, 0.21322624706619175, 0.16941021800105205, 0.48736035905853936, 0.7687449190483973, 0.7557739944253864, 0.8610213881987214, 0.22032491479003957, 0.24606133861881097, 0.41051472856216564, 0.5899261917913632, 0.7244586739830227, 0.08690816631651976, 0.8850744546274172, 0.5602508931288084, 0.013340055963316555, 0.4230390048200161, 0.3204265511001234, 0.004092006956385674, 0.9109879206252187, 0.8366373131822703, 0.4215902658572529, 0.8532773718403144, 0.02693733574196866, 0.4360766069594092, 0.16348845075398621, 0.028887159524982553, 0.5416161679445444, 0.7700477093487886, 0.43007659807676757, 0.04542086297836534, 0.7804761916975351, 0.4305110191806777, 0.0015512806231195997, 0.5234473013503755, 0.7017270620543213, 0.49084484702102116, 0.2111339130003579, 0.8174819372777837, 0.3029583706565877, 0.6699701589858571, 0.47389629250119514, 0.5251702701872705, 0.8440908253660291, 0.5001314273320203, 0.196807061896765, 0.15564503929895857, 0.4480700445464203, 0.5760380254928401, 0.034729318595858594, 0.3215007866362165, 0.4623789796270176, 0.1018846860259609, 0.03628207673368378, 0.7568326501476224, 0.2615733574631275, 0.9982413707898519, 0.37311324212027275, 0.8561193908808279, 0.6985262701519291, 0.0899219195496902, 0.4837180436167945, 0.40931109524891485, 0.22793212592605983, 0.35985242580268006, 0.7354309456205813, 0.3522648755390645, 0.5684831309986088, 0.21578915801626508, 0.2653202226551683, 0.3823056920719937, 0.7055507309431205, 0.00039283548935353796, 0.17579774816140614, 0.2750680916869609, 0.5254263808147814, 0.9378144255303508, 0.9285071576418966, 0.8385333568244282, 0.4518907236845362, 0.5640029082059482, 0.7814762954988036, 0.36085253207849677, 0.8035042172458713, 0.5768605741417565, 0.21313087796513386, 0.1816584887933913, 0.3036087738755773, 0.5815654004960356, 0.610553741473695, 0.9004794621544634, 0.11064083867461294, 0.32881077186069474, 0.8766984853201764, 0.8094416939313411, 0.8924390241659413, 0.3537515191885554, 0.8970451960201312, 0.9565357069340682, 0.64131042963527, 0.18620896307163504, 0.6391350610059358, 0.08947240905703113, 0.621455764104525, 0.0063786285874778414, 0.927569073578716, 0.5687799650578784, 0.046313305070152855, 0.6693345003244959, 0.22991393995842757, 0.45084180336885504, 0.6899796672357308, 0.47256239674648803, 0.598402725605706, 0.3047883124484012, 0.25850166399116825, 0.47737494279846127, 0.12132526694305201, 0.36962074720142946, 0.4111950813186772, 0.4896215731020557, 0.8113048965602441, 0.2500256691452587, 0.5264701251062012, 0.5818177209128076, 0.1478592444256308, 0.5695929357243108, 0.18625808885589867, 0.8757877582595698, 0.7724253817374587, 0.4302265969464366, 0.36062457071904863, 0.9940435342813795, 0.4518495055766967, 0.26069230903720797, 0.8348720887403068, 0.1852421456711113, 0.40954356501913003, 0.009846208686320135, 0.2013446314375591, 0.7531626998398254, 0.3337308808689585, 0.0424075241452927, 0.37285349750255437, 0.32485676082432047, 0.27313119313295675, 0.2331322656040885, 0.6968003623423193, 0.04536761461418082, 0.9013468463257183, 0.8552763171110279, 0.8595261054382751, 0.5316549983947071, 0.36718507477339213, 0.9606463362954432, 0.8456418045085219, 0.2857828637319778, 0.6003060048777412, 0.08463009106018893, 0.7806141379032902, 0.830984058287618, 0.231469481698801, 0.10423487162408762, 0.8050470791979834, 0.7877431848646022, 0.2517284831416057, 0.3548574157225389, 0.8550966698736117, 0.5453006595029133, 0.2858451187055142, 0.7660226750736991, 0.8015646354579128, 0.7487255142692215, 0.9847635880922488, 0.06803864911442081, 0.08273172290801212, 0.9210635594984841, 0.037878372508300395, 0.060072689142463886, 0.37543033638679746, 0.6106956528487804, 0.9916753250349124, 0.23549258351538327, 0.2564632229388758, 0.5990116249314974, 0.812927923318155, 0.2825451472016566, 0.5413038847070728, 0.3877899579242009, 0.5302479062841088, 0.5424864033544462, 0.9713521856885804, 0.5840132545453635, 0.547258891069285, 0.3835380680486892, 0.7120721435359034, 0.3033880848614229, 0.13641415536155488, 0.016011872494738122, 0.578320115952207, 0.04023854116224801, 0.3940698935357704, 0.38274045520347344, 0.7332539866978104, 0.971344368425348, 0.9187412911009326, 0.5047603892165965, 0.3226403207371059, 0.9423276074358952, 0.2290268121416097, 0.34985762876172233, 0.07874494740012916, 0.5052065343777334, 0.18287239440963776, 0.12318171253294807, 0.7287573239278213, 0.14142599434308634, 0.24927807660319856, 0.9158551192749332, 0.28919157438641874, 0.2348996035031694, 0.40855557787810026, 0.45504893094125265, 0.767227224797335, 0.5818291926517437, 0.014308915042779868, 0.37488754824549486, 0.32294853493992004, 0.05928427192516994, 0.35428716996761545, 0.41220527003171226, 0.26859108957429334, 0.8741139833814935, 0.6075051236790235, 0.2890899467490916, 0.5491615886776077, 0.7537100073947047, 0.5694917927351275, 0.6055449214915447, 0.8735338219121755, 0.4852041915381974, 0.06509190534510179, 0.9009886788572773, 0.3858912408829892, 0.12176496350515043, 0.08075775573754607, 0.16755746300805785, 0.8917133036370205, 0.9139204928860818, 0.09911876876935721, 0.720950732430429, 0.7715181263698246, 0.9573423658626958, 0.6627741999275679, 0.2029475297654838, 0.3083553828720149, 0.1294632871304532, 0.1678302617661922, 0.8270122819468562, 0.4578102194378917, 0.7581038461490538, 0.7675286876755522, 0.9733562569635608, 0.8270275598678809, 0.0878258390387785, 0.6482514031181247, 0.4379031753221688, 0.5157032142600425, 0.36618388156620674, 0.9160852349555045, 0.7067118789314688, 0.8624931676681007, 0.9792074096394295, 0.8133448211736258, 0.24650987150070136, 0.4457553787815328, 0.47544500486312746, 0.44439692115601104, 0.31194349248963427, 0.8257979887535002, 0.30855857157905464, 0.3717779619342073, 0.21800748653944135, 0.5647449378235687, 0.6104580210586518, 0.45906609083541106, 0.529641511186618, 0.4738460026771928, 0.6810308827738719, 0.8306726087078727, 0.345711611576077, 0.1844146733812414, 0.2000148908942101, 0.06727263359783153, 0.7631349960207461, 0.03566717580710854, 0.7098769233442549, 0.6325189026776282, 0.24888346983992704, 0.7180223025854079, 0.7234712353519344, 0.8246172456954701, 0.0989113139270189, 0.5841537473068414, 0.3868411059954022, 0.9393851576693042, 0.7853045760049937, 0.2662147804636781, 0.7069128842662119, 0.22583763183563044, 0.7035861420911306, 0.2465858641670633, 0.4636881220638156, 0.2330311819885833, 0.3154514405521681, 0.2924539172877595, 0.9857373546877803, 0.9598018735808685, 0.13575284561748824, 0.2999720153998805, 0.21735079598214113, 0.22394402103279887, 0.9530454820173864, 0.1596308591719282, 0.6290995579405391, 0.07577595411215055, 0.8616695446195058, 0.23481776802675658, 0.3928044534951387, 0.9104582959167222, 0.434877976301968, 0.6542473849483609, 0.9026424568777447, 0.7007405674255236, 0.7655756914680999, 0.437146275113413, 0.7273488271126418, 0.8149340957450891, 0.3869619231869017, 0.03089143649103754, 0.48785308907695957, 0.7830515366972868, 0.13273672388515678, 0.9444151761360882, 0.06805854212477513, 0.35796647799735115, 0.6498833838548614, 0.8021894946359983, 0.8472836493166831, 0.8058989848143164, 0.465086451404091, 0.12637369648776653, 0.5195536848373707, 0.5266373161514829, 0.977873650203974, 0.9707535092294907, 0.9772362872539798, 0.6275848301347967, 0.9785159662583963, 0.5538975175363018, 0.7951489306186488, 0.3767326540285659, 0.729647946582455, 0.3875675644198022, 0.827688228015073, 0.7788524079235603, 0.8736410066062794, 0.8081380737419247, 0.6208526669675403, 0.6760280928312599, 0.33165825327337195, 0.0014318939145854248, 0.13220524685383483, 0.8679297767642343, 0.890392909646724, 0.1955180196691393, 0.1201456634007011, 0.6106218094686656, 0.010727331788318528, 0.1909361435623047, 0.5999608041139243, 0.17542741083855917, 0.8041087864392908, 0.49464454554882287, 0.13612500781123194, 0.23992200980645306, 0.7655912936873249, 0.9057723681028971, 0.13177587254865497, 0.5983906669744957, 0.43185843805809676, 0.9826855163007238, 0.08986826076477294, 0.13329998689043498, 0.5877846423757153, 0.5556100147280302, 0.22137440681223297, 0.21165741625821122, 0.36387706409732024, 0.23563285844210113, 0.05511754106973754, 0.7371865362386334, 0.2793195336031903, 0.9703697925632194, 0.8796548179271865, 0.9039982362710011, 0.17160405246806798, 0.32270715806353223, 0.4796812565347358, 0.16333637340573715, 0.8893759794711299, 0.8411216732320622, 0.8828990404514035, 0.6371220283370423, 0.4651488463104875, 0.7010907054828708, 0.6920317041886856, 0.7927734617239862, 0.758488560267538, 0.6812219957974719, 0.8478475443388092, 0.5038845583805129, 0.23931042595547192, 0.45262291951936995, 0.10511934336609974, 0.43597758587988633, 0.258454359749239, 0.6770128487513555, 0.9006769542665601, 0.021667224418262077, 0.1417136002554985, 0.8606306849960799, 0.20725345597806932, 0.34173699239732214, 0.08410784422357265, 0.46759375514271095, 0.040022592625419295, 0.6776843564696649, 0.3668475339363545, 0.583494086741944, 0.10728872676544443, 0.5701126281443447, 0.9389818415318578, 0.183733763847036, 0.6815518661810608, 0.614932533487753, 0.7362828058663401, 0.09492427229668066, 0.3848274650306498, 0.6503859515045798, 0.25197801778951934, 0.06673369641552629, 0.24957362684278928, 0.2537500351950823, 0.1385896740620981, 0.7295932916950076, 0.7210174245341036, 0.8502610746350925, 0.16497072803320123, 0.9267158528222813, 0.2804173352164233, 0.4583101844652592, 0.4915607873900022, 0.7340181110445808, 0.7433386672138056, 0.8422317638570351, 0.3286462336352586, 0.8127611537764468, 0.12458201524224322, 0.5692742568470338, 0.29395757955104473, 0.42746217504695994, 0.25865985479099796, 0.04720807062660748, 0.9192320711250647, 0.2993476340142658, 0.007142688301701505, 0.2204812062903747, 0.5200916330793901, 0.6489104946179726, 0.8204106149844391, 0.06264511065207623, 0.8671491396485991, 0.6074139071984634, 0.5262128963098944, 0.2958716745812183, 0.7813396873303533, 0.873180571690271, 0.18225790991450785, 0.6462921511388142, 0.06376474836533608, 0.7248020594800143, 0.7079579906584446, 0.9052977895485574, 0.25984885646868994, 0.15606958485531963, 0.8988677091539751, 0.6473901414847865, 0.6600509898475924, 0.40518297286617166, 0.41929155257565276, 0.02064144996989603, 0.7022142710202426, 0.3838894818057821, 0.10985220181206967, 0.868250184425854, 0.09582341656945681, 0.48401269391839885, 0.4832365079598986, 0.020781892250526623, 0.15001142546445267, 0.24067638111054324, 0.440607801813774, 0.9127505302223127, 0.21817491658350352, 0.2465725054507102, 0.2812381104777337, 0.6557124107282353, 0.38928447419289036, 0.6181616723806028, 0.7995073278614203, 0.7401888309791503, 0.13117463757275383, 0.7774046984010252, 0.26245372666065214, 0.9568290244531503, 0.1277554271028044, 0.29653963508741477, 0.9611149520591701, 0.5160454663488208, 0.9250601226273969, 0.8726247639115782, 0.5518053231768054, 0.6914251582344108, 0.4912397711655774, 0.8115252415332865, 0.5218342197537854, 0.18236587918458325, 0.039501655165854355, 0.7294998023946525, 0.20660520422254613, 0.8313271371854392, 0.13069804480624958, 0.6217335884413676, 0.633157092642952, 0.7359265096602418, 0.5453449544360572, 0.5631001652584222, 0.14963075714136687, 0.5268886128924611, 0.2836812243221698, 0.7357656090263957, 0.5775445817868133, 0.5184293412962692, 0.6486845474479586, 0.6882335261966438, 0.25025640400915705, 0.8952458349480324, 0.9452513468635373, 0.9633228320603805, 0.10916311314862048, 0.9751227719466589, 0.30153449696639734, 0.8600021987263843, 0.551623508554851, 0.1216755688977923, 0.9454378111712867, 0.8648640640746488, 0.75460226001643, 0.8021674699568363, 0.2885961154639236, 0.5892655389175749, 0.5820366047050023, 0.6638692140695065, 0.6698557569948149, 0.04500805503346872, 0.5069740877616361, 0.8957017090827417, 0.8163075654907458, 0.009484964441270227, 0.20799557699400784, 0.6248598099190438, 0.8268831433609406, 0.24495511131665426, 0.9093102929274715, 0.6827487190995692, 0.6517748250094413, 0.685101378687588, 0.8420522932839575, 0.7830650199365697, 0.46864696841639675, 0.37773773598466365, 0.22103976661591662, 0.30948427037099635, 0.47974246876395077, 0.7898209564122577, 0.03500981065136166, 0.7668498769620313, 0.07081464978841678, 0.5410053019324684, 0.056809041781473835, 0.24741769991887064, 0.3246980719811503, 0.788445509784719, 0.7048449564252207, 0.5979729680175447, 0.021114046175444212, 0.3738050064348668, 0.34621015754869533, 0.048927153500845755, 0.523225995711705, 0.7220186048562133, 0.3580536686832083, 0.8451572964908878, 0.857427487948765, 0.23169407068989867, 0.38110578222122216, 0.8631619157574336, 0.8549071089253937, 0.5280198234883616, 0.727625447794741, 0.11514883793606923, 0.8139348606835712, 0.6860375793755535, 0.05294966937366408, 0.6589654624144575, 0.6021982750753707, 0.04476535837224083, 0.24343046777977528, 0.02005167285774956, 0.7850595228766827, 0.4059349951718122, 0.8944737192082901, 0.7788062086981887, 0.056590431798021035, 0.7523798021122023, 0.8977746111332048, 0.22788861502085933, 0.3657699507278147, 0.412687120947112, 0.056209988661683696, 0.17489934962869214, 0.3312024131975225, 0.356841273518706, 0.07745506210333619, 0.35883944910388454, 0.842713949632148, 0.5593598406439976, 0.995450779975233, 0.6607821288236504, 0.971357812661321, 0.23452596217137522, 0.6763995783187896, 0.20370294212333973, 0.7681986976304094, 0.34286632198852907, 0.649486023788997, 0.6958658790972774, 0.5324032657247066, 0.4423497942246497, 0.5244757693923124, 0.7259592672527376, 0.06328671709877087, 0.13796135768879303, 0.11627599126708488, 0.5602872813311196, 0.7724463171596005, 0.7402127274369983, 0.23173760273237543, 0.5014054340296494, 0.35581301026952705, 0.8016535823378489, 0.0765808508471093, 0.4705669442118541, 0.08987757030370458, 0.8765624968703016, 0.5096554481647972, 0.12861693235155358, 0.5033152272569512, 0.2869821112917659, 0.06276434146725585, 0.5460019010715733, 0.6804293325861408, 0.17077149115777335, 0.6252185561757618, 0.6847202326458784, 0.6340822911234761, 0.37992469307660226, 0.1310546588488768, 0.7529301677887328, 0.05818395888784089, 0.8005648840817398, 0.1450150422854155, 0.05344185972836257, 0.7682453440171657, 0.8984348507737858, 0.3994383796935356, 0.4670588072276147, 0.49027935151702107, 0.9881796187507176, 0.16810131075029355, 0.8455214645571316, 0.5361018503554209, 0.5190000373950252, 0.6624626931972518, 0.3017037390070031, 0.44069031856867, 0.9167781154821643, 0.04841865655290367, 0.6356951423655655, 0.4654591632635602, 0.05771375662133971, 0.8119703246206331, 0.8420305348811182, 0.9704548574825884, 0.1841781286534374, 0.4492837745761632, 0.07560534339333358, 0.43253538903013855, 0.13803103485403212, 0.35224203954420175, 0.8757658631262869, 0.15661733251981524, 0.2628912691386208, 0.6093001302585389, 0.6214514660998613, 0.34215896727147865, 0.850358073124269, 0.15742953063415577, 0.8326910081198957, 0.8036572985553427, 0.559250266099208, 0.5463677058033787, 0.3733665986030992, 0.4445747091705091, 0.14575674092864044, 0.9524490846759229, 0.3035830756814668, 0.8907864492893807, 0.8014531860175, 0.6606793575692113, 0.1258716435479723, 0.48217387047038396, 0.4774172734020168, 0.77099502057293, 0.04185936348086905, 0.37296062225255944, 0.9942133728554116, 0.8773592061759301, 0.5739843160124485, 0.05913781114276451, 0.2116335763409588, 0.48448498360275316, 0.18725617569109765, 0.660722171397489, 0.4790176750874734, 0.6789972124194318, 0.2759917826852536, 0.9854712951586065, 0.2750656661149097, 0.6957795047177117, 0.4056926043217185, 0.6048068813711487, 0.7413544514939397, 0.16212174676373936, 0.37050416942316233, 0.22621699933466966, 0.7400033811583572, 0.42686525547687015, 0.9697221280268933, 0.847976796655453, 0.5027407065016054, 0.7016645203192741, 0.6762263378589377, 0.07782895800404754, 0.4973343605855627, 0.5024993403149735, 0.9709257689357993, 0.7501038834155871, 0.7121992877599042, 0.35367386196162354, 0.3391267771165555, 0.28014695716341564, 0.24087553553881347, 0.5615797695981954, 0.9698559572852622, 0.5972661355434566, 0.19294176804827368, 0.9646521485234241, 0.14557982515515344, 0.34009276038258884, 0.3022193822174213, 0.1512788334569477, 0.9610585413236644, 0.21532147428744064, 0.019987991894313106, 0.43938670104992994, 0.14721788841742778, 0.058690849548663326, 0.4346965278714716, 0.35251851946336676, 0.7835813536122155, 0.6760653479386179, 0.6220431311477301, 0.2528196140742368, 0.000533959017523622, 0.894535870484847, 0.8492038880576421, 0.38584082932288033, 0.2884756729814787, 0.5492959390611992, 0.8017052722645179, 0.9698341074093364, 0.17679641372360777, 0.37850671471819664, 0.18521024429108068, 0.29242504625332066, 0.9902179706093583, 0.6009030722364157, 0.9543115655949146, 0.8052138837075908, 0.35885131314543905, 0.826698813731397, 0.23472943644304167, 0.7239904300116352, 0.2528411756865797, 0.9907365576775006, 0.6431339519213621, 0.7098248144745495, 0.017563394381231223, 0.2815643451598231, 0.17719456011547463, 0.8793359589476787, 0.16890251517331234, 0.03165094546018765, 0.6128364948691476, 0.048317563465782976, 0.1457891705597023, 0.958321841621704, 0.6416285373723682, 0.49774456764256825, 0.6727845817695177, 0.15352816461969254, 0.4439653279218745, 0.39448707551900963, 0.13456503199038383, 0.40250212649214834, 0.5164340130185989, 0.15652878620929878, 0.6051693965603501, 0.8639195616874488, 0.8639096596071155, 0.17127823137236653, 0.510855518917277, 0.4924797093273501, 0.33840311400076073, 0.5326024559457917, 0.1553291294271849, 0.6294304337632686, 0.9477040569348971, 0.40627235659717664, 0.9285678971514644, 0.31334293951594727, 0.31362824231638153, 0.4502801268279887, 0.43859159594574626, 0.09937237324211612, 0.7054532175727435, 0.7753889535366468, 0.5861858956790452, 0.9500288997523375, 0.49494136036292513, 0.08551923672392192, 0.2953832128564374, 0.358815848412364, 0.7999766996401263, 0.2535075252881923, 0.709208934072963, 0.9986422801896068, 0.5341064948385097, 0.06873813351617386, 0.32494143314782553, 0.5612590070724911, 0.38135270121565146, 0.3578925062065128, 0.9690429417434706, 0.4795512500636956, 0.07870280725666035, 0.9082116049561345, 0.18747127227801885, 0.7984100268726031, 0.20306850164878976, 0.23033397499655872, 0.3496075587760975, 0.9050194173979551, 0.5993050147422377, 0.08476893729639334, 0.39451639252751014, 0.12818913647973307, 0.05214553641964548, 0.7771611533497547, 0.9029496034331609, 0.37999809354136216, 0.893461277271767, 0.5612955556042161, 0.5010305335932177, 0.47018791099901425, 0.7502993429119359, 0.48090654094183216, 0.3130844076383874, 0.1449483159538807, 0.9732559879302132, 0.7024840598455233, 0.5653970243727656, 0.7152470131738804, 0.343701874839517, 0.8320915198545262, 0.5002502568983627, 0.03307604441020673, 0.8126455203432832, 0.8229732106738592, 0.03136039392274759, 0.2720364109029123, 0.7301508107518284, 0.3299319102803394, 0.9554750560532498, 0.017237000276937642, 0.42919080385716035, 0.78005512031634, 0.5634771660930555, 0.7626499454832276, 0.20983575343207828, 0.3353795873079396, 0.8460419427766125, 0.23459411670206154, 0.10143977413056626, 0.2540198303338761, 0.16254531179501208, 0.8510877229282166, 0.8603900589754762, 0.5863417808980522, 0.3651375649331312, 0.29219396354616056, 0.6399725148968649, 0.6166369188684203, 0.7025055322259772, 0.945320677587678, 0.5709421494658934, 0.6491879389472301, 0.22438970496628063, 0.9992061457403759, 0.5991961295332436, 0.4713474695799226, 0.3451558324576989, 0.06977221898922714, 0.6925857873300553, 0.31114840203074745, 0.5895698797598925, 0.5651384740091681, 0.4810231124728358, 0.23811355814026414, 0.2881941328093329, 0.7059334242709647, 0.3862342747127788, 0.6160680349594981, 0.8745689838607825, 0.7249998063143809, 0.8260889976654063, 0.9461138156932158, 0.9232592676394705, 0.7002892904118151, 0.32710601094386527, 0.7609746143683473, 0.9078564121681063, 0.5631487611378525, 0.9337899770870097, 0.48063525918471484, 0.446305670815657, 0.3212179171227414, 0.28954292649182123, 0.2989083340288635, 0.9076999853287178, 0.44323555788606805, 0.6137570359274979, 0.05957581469620821, 0.3366000856124568, 0.08626338501753195, 0.1981234472921627, 0.015468607014190394, 0.711428938259771, 0.6272950291743647, 0.7586996610501318, 0.03538306347582876, 0.9175646846602493, 0.050266955519039924, 0.4899910602560694, 0.9320885678788006, 0.15126804440615194, 0.48185592111675335, 0.8867781217033445, 0.7613221003785055, 0.47895124104726594, 0.9694583855463286, 0.4380567917172483, 0.5515965411048586, 0.7090355605932342, 0.020082172176081325, 0.4664782083319404, 0.37255000056190546, 0.6390226487338151, 0.7741287103550385, 0.6713249469103847, 0.46180421099794466, 0.9369123295076744, 0.8930325889057228, 0.06830040711617325, 0.10450093318836706, 0.8511348984748487, 0.36857198720172757, 0.46841500673112524, 0.7763205487419618, 0.41672253011437543, 0.49546416733663057, 0.23408803714483795, 0.18046233402362, 0.9647707995970993, 0.2510883664168052, 0.4268286869585586, 0.48451540528216774, 0.4106897791256524, 0.4748865054377208, 0.9434726709393102, 0.6729252617229817, 0.20310850702267869, 0.15682597663649578, 0.62938621985971, 0.15725016939867842, 0.09316966247617287, 0.549807658252104, 0.5684581247127587, 0.20500962025762381, 0.9915916240040688, 0.5531838019327445, 0.3852681875538304, 0.6775374708647425, 0.7392698286551905, 0.7561965802565661, 0.7567310776187554, 0.04107195111209694, 0.3445470410752436, 0.6832570305869778, 0.48694540992900726, 0.15771988453181485, 0.6835160196635619, 0.0036545237159456567, 0.7687750587858643, 0.9093054397902908, 0.9000873869222972, 0.04612756479018432, 0.12024135939338387, 0.38355819135720626, 0.5236485737785965, 0.46217373634580383, 0.6609297018983059, 0.8472810383305002, 0.5699403920894351, 0.11094595650523131, 0.06599277825960193, 0.6945660078349536, 0.08000264493762377, 0.9827103790893303, 0.28084947143076155, 0.6886879834680154, 0.9375709894211569, 0.37119994684545343, 0.5597294497456566, 0.18023997510214618, 0.688570379150127, 0.4639876785472594, 0.5926089871510987, 0.9232878153550489, 0.5725783530978408, 0.6253201890717913, 0.014828846321437661, 0.7737956195988298, 0.2256510137083334, 0.4048140687087728, 0.6107685042002363, 0.8479585538864394, 0.8459368003615639, 0.5526429704526007, 0.07981021620041762, 0.3838978361979044, 0.7380890240924678, 0.030016701710504856, 0.8231132870279131, 0.5552248637279988, 0.5783449981540453, 0.583719140387268, 0.9547676329852879, 0.23881420993413582, 0.778512530403879, 0.05354384989684169, 0.8847758901423215, 0.0934244491960089, 0.774238663844377, 0.5374889578637255, 0.48204633511148753, 0.8210247286258077, 0.38115910359161664, 0.4930872626732372, 0.7373114125949569, 0.749071600404724, 0.9525310601901555, 0.17239367171790387, 0.6524983150843158, 0.1883390016394142, 0.7664796972533965, 0.5886059333461698, 0.3726485840482904, 0.1982230480138164, 0.053283265509501354, 0.5398565851751425, 0.920321661414938, 0.6735057064793921, 0.7910033010070866, 0.8034306781765964, 0.34277323016501215, 0.2392219276306432, 0.7395680154657107, 0.2831464084076808, 0.51880802069894, 0.4433954778399597, 0.875451260554618, 0.9818288893780782, 0.04268041015526758, 0.8377873472053925, 0.3428193910756936, 0.909474114340329, 0.42493221730642494, 0.21916978989867908, 0.20703643858326093, 0.8649183337398252, 0.5239684532528621, 0.9620475523921062, 0.19871651067512663, 0.245484795900776, 0.5030573450324527, 0.8917145830169195, 0.5435086448826065, 0.38073496719614963, 0.30738859751223413, 0.5737258816002603, 0.5838885804555886, 0.6644898987869697, 0.03517234746272013, 0.0779590648010553, 0.6367520271705688, 0.023808817988623887, 0.5318755407449008, 0.4501402644966118, 0.6380617707736033, 0.5195017737746633, 0.3697355227912761, 0.06308657862797962, 0.5437725978434391, 0.14348257182809443, 0.06706542038454377, 0.6040834989081485, 0.7237275679084376, 0.8271277268879631, 0.9728583952899327, 0.19911747044977235, 0.34662098268578245, 0.7896168550923706, 0.6435219209311089, 0.22885469139976344, 0.27319066103448, 0.8583138529676103, 0.6530818991518622, 0.9677679679696225, 0.6340184685096437, 0.34358485217302726, 0.6642884973031035, 0.23606262960647395, 0.752463719835488, 0.5554193759757942, 0.6280018159939361, 0.636714735330071, 0.10232072322268781, 0.8031954240245469, 0.3247671057065975, 0.16757767946973934, 0.6131604919342938, 0.3545136595911871, 0.6423854308054646, 0.09010831777383399, 0.7379472997811976, 0.9831156431921086, 0.09468959884560968, 0.9250640861884252, 0.18821854382262215, 0.18658511981815096, 0.3031526078882073, 0.2599814779348334, 0.7679035779418721, 0.7811510947555005, 0.07002568323764746, 0.5057485754046723, 0.6455864546558661, 0.5639153676344986, 0.9598886242996483, 0.6590570558986457, 0.4720045565622838, 0.3979933888060523, 0.6354128243382362, 0.853369168406155, 0.13883221109673105, 0.6012323448672612, 0.2692879179933705, 0.015932180529431128, 0.2799709394365537, 0.41923148783036557, 0.761373284300726, 0.4438616719837132, 0.47117551223596643, 0.2134267740572383, 0.019986438589841726, 0.946450191651161, 0.6493837671450003, 0.5890143809234979, 0.23465768525359387, 0.8882229211011063, 0.9636191409761834, 0.11640288549105582, 0.946324727090255, 0.7832061418598538, 0.6639112603372258, 0.7029478771989037, 0.741496242989764, 0.1934853793228457, 0.9204462630770868, 0.3817481222895054, 0.4325391502898268, 0.966715327641235, 0.3413768474439476, 0.7590968313541181, 0.6302446925592264, 0.12668193372517922, 0.8366680209877133, 0.06383146344003943, 0.9345727159916446, 0.5317987385390454, 0.42603907321225354, 0.2697751953341604, 0.8513654833620978, 0.2256362970349669, 0.12039615374778923, 0.8441887167171969, 0.15540089962213055, 0.4748619138165948, 0.33477728403164086, 0.660091990030405, 0.3522092487374039, 0.9605347549769048, 0.891399753960918, 0.2667574128603796, 0.3847356369384093, 0.2662946342494672, 0.06700601468860212, 0.461432738334131, 0.34271726924061674, 0.1228510557956567, 0.4760640520035494, 0.9034353000751758, 0.13489956166553319, 0.3102163593063858, 0.3935082851993792, 0.158884209120577, 0.3297299781212023, 0.08195531804747669, 0.2845637361857394, 0.04061419519436171, 0.8251679044404158, 0.610107184515523, 0.6904074215497966, 0.14416008859316432, 0.9752875326476546, 0.7870931714812182, 0.2857860169524743, 0.0033525203769441125, 0.21291862412918294, 0.8326500906680618, 0.09167280498858721, 0.4970430300918708, 0.3296522732465922, 0.41693139177961525, 0.2870831433408576, 0.03441309187131092, 0.727453316826077, 0.8703418572628424, 0.11777039524549027, 0.5395813068325068, 0.02091846823133625, 0.04047698387022891, 0.6807515712419521, 0.9479338946535115, 0.9524131443818261, 0.2890352880519952, 0.07238105417765683, 0.43137329060552376, 0.6717730313796278, 0.33044131834912516, 0.9236197373166113, 0.4070099273863388, 0.5037609532692949, 0.5248114317054952, 0.5545078754405889, 0.7920784213773897, 0.36187902535390026, 0.7080061896039107, 0.76656569470362, 0.9562497687315548, 0.6156124430633811, 0.7816804933201404, 0.5776656571950493, 0.39959490625487715, 0.7196095213653716, 0.8118950018803841, 0.2649043135306659, 0.8019486090309614, 0.6722921313994507, 0.33993547182519346, 0.23104529434742094, 0.35958716954675896, 0.24459953664727552, 0.4908977644337984, 0.16909537785775464, 0.04424793368768476, 0.4885499036923432, 0.30915635275400666, 0.4537333984846085, 0.5333048616667747, 0.9514913923577094, 0.5439305964434474, 0.036786459912506286, 0.9884859311579072, 0.5218434362636359, 0.019965015556903443, 0.20086310447687517, 0.6296270725895466, 0.9842048731080741, 0.40286398653342537, 0.3830961321320234, 0.7719466396744851, 0.047165606537411975, 0.789320231199929, 0.5052885078366918, 0.9129221129500353, 0.3319239897534646, 0.8236419951534456, 0.9403590884242866, 0.6158362098139302, 0.7584830889199611, 0.8522707703972959, 0.0906376785865346, 0.8140780830136866, 0.5054216376335434, 0.6800525887899218, 0.6888351575201161, 0.4272965708307387, 0.35309087474123146, 0.7630276443193669, 0.1585598683870718, 0.7491552790187822, 0.4932155468413121, 0.9257005501844843, 0.2741664603809407, 0.4506298584279679, 0.8335201848903918, 0.5465767490059674, 0.5602912735981056, 0.49190857235443075, 0.45622390698234816, 0.7802158188871214, 0.499155492580064, 0.09103123865265628, 0.8805914898774542, 0.9098787481207782, 0.9765332208976073, 0.7821948171762165, 0.13224731365814824, 0.38179226430430935, 0.19624872266741666, 0.7348156848191983, 0.7505367338615669, 0.9173916431437428, 0.38373456776660575, 0.21730126096712377, 0.7084627514531115, 0.8226960992168382, 0.11244309088575566, 0.24980703036524965, 0.3833871399394828, 0.1107681331784337, 0.28990869260993357, 0.23023324059529593, 0.0824186734981005, 0.40069946794407274, 0.004836216027325313, 0.860694215568036, 0.1967855834010267, 0.8540660880593619, 0.09488824279522046, 0.9316356273318933, 0.24002919622213992, 0.23694014325207413, 0.07660790438716625, 0.7346414333313286, 0.8166020264437737, 0.5322892269551114, 0.8167017330574166, 0.9071014451653882, 0.9403203305035448, 0.2911236155631133, 0.6740891711622454, 0.7381132217125792, 0.20559227776763078, 0.14708226828706616, 0.12494659941696551, 0.4910773994830627, 0.09984819286125579, 0.19328817936099052, 0.01978829113749081, 0.41301529103022916, 0.7854914635679247, 0.9991389409218714, 0.908953964758846, 0.5225819662845984, 0.32782875443955517, 0.7517635620466835, 0.2662017485341044, 0.25924197193203635, 0.4945575810550099, 0.06597070182866505, 0.676940856183024, 0.7789758123751029, 0.9695066811579602, 0.2914529432070131, 0.19217873712155265, 0.3570129706073306, 0.7723774765477364, 0.5805704352706412, 0.7953107782357461, 0.057878873393940045, 0.7403069874803593, 0.37911141227174894, 0.8931220427257193, 0.023619975552459538, 0.5398322405277811, 0.7698849312170793, 0.8447166821910701, 0.7485756073717695, 0.5099173191007011, 0.5229212989954363, 0.5810602605117828, 0.7282652506332697, 0.18842457574228533, 0.15250920093124964, 0.9543321216637011, 0.6858381185157816, 0.9182655334384784, 0.8450976592784886, 0.12368686118131222, 0.6888867123142767, 0.3062447694584498, 0.2991486576902811, 0.1884960737501532, 0.010203016875596438, 0.53974930460702, 0.08590045224740495, 0.4530392360955344, 0.32656556864336506, 0.4673861133086109, 0.713838543006717, 0.43352356016341, 0.7607461135837655, 0.1507712055834748, 0.5388510625547493, 0.4912068297341492, 0.1693003550119253, 0.2705396304911616, 0.9355586536795282, 0.3260608590055567, 0.04816464436091039, 0.7047534238822833, 0.6421228811682665, 0.5225194021575739, 0.8313096205048437, 0.3181132630854606, 0.31579401277335073, 0.500740442377846, 0.446340062394746, 0.12883963860120773, 0.7960679424504243, 0.3293462959898794, 0.6827864548119956, 0.5450114666824731, 0.7810496036770709, 0.903025450466452, 0.4446943992479814, 0.27543489167922697, 0.7225159421831087, 0.8184770722851453, 0.2619256419896915, 0.48501725546838426, 0.09625144295563248, 0.9377218936533477, 0.6269704806135408, 0.25251367520544277, 0.5379050294431125, 0.9777390088992477, 0.8922712611535861, 0.43061620953887836, 0.18220002948565273, 0.5871470819511885, 0.3906010318573543, 0.7562445920564482, 0.4632623124636699, 0.6441053388678187, 0.7786547704763063, 0.3639719457921242, 0.03227375544695266, 0.6522258538744792, 0.9355362919340011, 0.2068183301780403, 0.21000894169481688, 0.8749400902645131, 0.25256883320256773, 0.4356078850766878, 0.09750260363736296, 0.550752586854734, 0.70355992438061, 0.7512486339369331, 0.1845058005228739, 0.13945887954954372, 0.6093130377717191, 0.46420353569880046, 0.6835199564235261, 0.30738452590033893, 0.8742105783565188, 0.21457207406794732, 0.018167347462280214, 0.31261461146762204, 0.6315950660091322, 0.5729616651969766, 0.8629945496969306, 0.3017522992670638, 0.18821416638211375, 0.8528020237511038, 0.06370803555111781, 0.6660838032458873, 0.6378639794749231, 0.3334419280741796, 0.8322912189829458, 0.280026944926816, 0.9520300354363374, 0.12791030845510665, 0.2534077505432255, 0.15194280729939358, 0.13421816561244282, 0.38613124073213934, 0.18651141998270038, 0.010402589079757885, 0.16171435952712698, 0.9368518641763011, 0.7839659530504567, 0.1755627210158469, 0.055370312290232815, 0.74607682373267, 0.21566443454913187, 0.7733302254016793, 0.28713023864838905, 0.34537634496983916, 0.11867444635225599, 0.24422446758200433, 0.6058777545966703, 0.7375392464212742, 0.6298138841112356, 0.4320743309455569, 0.5245113168857385, 0.5073628481028901, 0.10090946852275928, 0.682776976496594, 0.9179055782451095, 0.25439855333827033, 0.4096257747680766, 0.4727131165157603, 0.9115103389793892, 0.15292489841876844, 0.15081671692177911, 0.27285129646047157, 0.13746358292333571, 0.28096820730540806, 0.6235755869311604, 0.5133999369107294, 0.9954347732150087, 0.13902084460160313, 0.8492414381091979, 0.9092769614503873, 0.7321501874604914, 0.8703118390759484, 0.009828954589244265, 0.7127149585835475, 0.12254833940961174, 0.6841838706090675, 0.6797898678564891, 0.7617711949099634, 0.8867391934944756, 0.7510802090879748, 0.2182687354342141, 0.5996413031330944, 0.2495219488317163, 0.5074304285500727, 0.9630305833717229, 0.5003879980597904, 0.3660156716704823, 0.7373757695789731, 0.6122959717204958, 0.35009501397735077, 0.5348681087680487, 0.10878172778354811, 0.9722622130233555, 0.6475127320547724, 0.4843536830262407, 0.3829121220739766, 0.694985640799419, 0.4943348703751752, 0.44104112402752393, 0.8112753520850255, 0.015051745929245297, 0.23464567779627732, 0.5998022090031062, 0.939770680156893, 0.533962078997285, 0.39823394015738334, 0.4224836445078354, 0.3355259195981163, 0.04567579881080175, 0.17664618939821342, 0.4124880459451128, 0.99019933361313, 0.4086955523216489, 0.4953086452271196, 0.3101415459625855, 0.7353574057188267, 0.5057581829754964, 0.9067631351878555, 0.857896372901816, 0.5259515699425463, 0.7907037623687696, 0.24633864983957798, 0.958613383922992, 0.9536652702291899, 0.12375162740685253, 0.897529159644056, 0.7522813231613783, 0.1815177520813216, 0.519955178358722, 0.5652852399637138, 0.8131506573398954, 0.2997147074588975, 0.9028274140651887, 0.3077460655698906, 0.9707223948908753, 0.2508338100704173, 0.7942044110543858, 0.7331530249159441, 0.4136871809355265, 0.08242300808783987, 0.4398627661500544, 0.9039317408982772, 0.9366343786349624, 0.5587802596227949, 0.5153129805648125, 0.6462556860488188, 0.5775456450004183, 0.4707109021904742, 0.6270548880780359, 0.9350700949289592, 0.7715195681069944, 0.6619214085798729, 0.5369652107270392, 0.4585399444105942, 0.9331567039223996, 0.8997969906972278, 0.8013872239286973, 0.7991632835150955, 0.751574676725665, 0.850128778616071, 0.013911508478306245, 0.9827400167059904, 0.9089085891503617, 0.09058671152964304, 0.3661973962815184, 0.244121820766233, 0.8997529619424489, 0.3693548470994905, 0.594102047657788, 0.09752157303401265, 0.02117650643721969, 0.18986970609553888, 0.07777350856700349, 0.01904573908337026, 0.9604118276595635, 0.38843712631739946, 0.08297596525163997, 0.04035755694223486, 0.3145819492442985, 0.1055976227385077, 0.054878105918033215, 0.3956323792204476, 0.8004877339674538, 0.03238620302347428, 0.35131899136962963, 0.7795753260195983, 0.7572307446991025, 0.49778067799816084, 0.05733556369949788, 0.8395814334948822, 0.8136871182676774, 0.7117252857825732, 0.09569503688724135, 0.5123443211159915, 0.7671663718210584, 0.9455302466271156, 0.7403784074209128, 0.5241201235386309, 0.6487635799916047, 0.987967924849385, 0.7756042452359231, 0.5374466568988294, 0.17642898129508988, 0.08897407119910983, 0.8312141647459399, 0.019699242017796048, 0.0627663071534148, 0.09886805827280087, 0.8948561515283756, 0.6166313182506137, 0.7007348882992398, 0.13157354849063208, 0.400328020714128, 0.38279627065271804, 0.5063261002940321, 0.26141926300809104, 0.22626615071790923, 0.9566182719807035, 0.18824446159319685, 0.37836467510653504, 0.7556814884088183, 0.9131855356489142, 0.49645662437786187, 0.6455061132934143, 0.07170009230196261, 0.05016726960451312, 0.246136844714963, 0.7801616234699119, 0.06621854362724056, 0.299192622229307, 0.47863674955616087, 0.054847732663966364, 0.668997577900571, 0.938737489502215, 0.862391187970208, 0.15444142171095632, 0.03558629581172246, 0.3233858264378089, 0.06603821928005082, 0.4650165793341101, 0.5600925753097075, 0.11632169846131202, 0.035942986952755884, 0.7086663205896244, 0.4051267040626767, 0.3336461399304169, 0.11062929889736461, 0.6073381096757693, 0.9481483793877753, 0.549008197552151, 0.23057468652252244, 0.37727255424179507, 0.6168165812004855, 0.9771588132605955, 0.5855561243613178, 0.17422574674814018, 0.5521098006724932, 0.45393061629285436, 0.3442053516329908, 0.7113666247274623, 0.22069255640809038, 0.9293921496134889, 0.7251512337662525, 0.19528833682522828, 0.5925868613854349, 0.9224096624894336, 0.7930540132486785, 0.053977556374531166, 0.6173659424238513, 0.3166615457215467, 0.2760120664306902, 0.651412265932223, 0.2954147698615751, 0.7279642492491684, 0.9500540310842736, 0.19541987549040896, 0.030315060545994976, 0.10381241789090656, 0.26109155712713694, 0.16743343918145503, 0.3660054619794624, 0.5086532783785686, 0.3031691182421813, 0.9559312010085553, 0.745857449017812, 0.2917449824444206, 0.8577683453452225, 0.8954180812193946, 0.32416973847955133, 0.9091882509712734, 0.10389000119727343, 0.2084147111817648, 0.7251843233807603, 0.8872829326542705, 0.9416226842452367, 0.47454810889606125, 0.03708508106659658, 0.5612807944860695, 0.9207934982448776, 0.3690793914944117, 0.9353759280516082, 0.5535798540475436, 0.2980243748243394, 0.39153791581624053, 0.5924366962050152, 0.7452724291560255, 0.8942833573498825, 0.6237508355554183, 0.9160079480828767, 0.20860605914559727, 0.7962194634630373, 0.2964313431680926, 0.08225388546525936, 0.02404126472138579, 0.027414830160852, 0.701091972176009, 0.845402897055724, 0.9623105696795856, 0.7221929001820542, 0.07694316931802314, 0.6148512833513421, 0.6242010634659172, 0.14108133081161, 0.6739770687966241, 0.7434124504626559, 0.17692730499742315, 0.35054310800005617, 0.25598689434626665, 0.840436004348755, 0.32811108039111647, 0.5335790001265612, 0.0367023334215697, 0.11434700924632879, 0.02830433776542396, 0.8786642491666433, 0.7415723930220833, 0.7029743248725108, 0.6885049939678209, 0.47410612766607174, 0.451332581907825, 0.2471246483800431, 0.705495973341043, 0.5595049075229553, 0.5428842741209942, 0.27563765922292094, 0.5121487865852304, 0.2038375556652976, 0.6086603900392263, 0.8678569402224703, 0.3322341570669234, 0.8860578777712762, 0.15032365906523515, 0.5220672022410702, 0.6721320659029598, 0.7179995563835297, 0.9863298822247657, 0.14611327394893148, 0.636158167795051, 0.15016790490419085, 0.9293195820487136, 0.20823760292228488, 0.39118356255561604, 0.8478325466306105, 0.6238665869776472, 0.38892477643691836, 0.1947909169703793, 0.8193140109470651, 0.5916604624684888, 0.6617957218101335, 0.9523344606762081, 0.13791785859478323, 0.42166564581206156, 0.06395650815946285, 0.8547168218029992, 0.811467471942253, 0.956662340109981, 0.21135025812700725, 0.22776355710904816, 0.32873639923759523, 0.8225828581220365, 0.8074366260503684, 0.9253702522252192, 0.2870783243664534, 0.7482535627860125, 0.7419726164577817, 0.6800647655401266, 0.9306967856660886, 0.8828274999806435, 0.04603333283775202, 0.3976081728051163, 0.15712718412831284, 0.38232962704820084, 0.0014683820835882377, 0.24999329698617978, 0.09341463590013122, 0.44004159788156194, 0.8826032379171254, 0.2595692013354478, 0.9323031954938713, 0.9222566995715802, 0.8263635903912544, 0.19333393658373543, 0.7785983346877806, 0.2135325812843324, 0.8868077223754203, 0.491788787841855, 0.5116456034509074, 0.5159231461833037, 0.10975820478379894, 0.20576944288946197, 0.10877963016060477, 0.33408070142868684, 0.8855755648422882, 0.05980323401628351, 0.8637078748398969, 0.5638198307471801, 0.21125906686561158, 0.9930186890004368, 0.36552484848753086, 0.6227989212622395, 0.6409356312529642, 0.7715939125793486, 0.49335270791885677, 0.30916962880672894, 0.9558466760608072, 0.7157582382317161, 0.8479859401297832, 0.7436472908268735, 0.8374501847853362, 0.2687173784642233, 0.3719318154071177, 0.16145721576903904, 0.4786753717548976, 0.17658818617987182, 0.7253782046989563, 0.645246128489611, 0.9466051206847397, 0.640137228021984, 0.5722841875990824, 0.20389663712145034, 0.8545298024337249, 0.7380793932715825, 0.8215149966764985, 0.6104461557670458, 0.23442940460882034, 0.6123691691031152, 0.7437144857118246, 0.17825602719378109, 0.9357111995980801, 0.5216438852971895, 0.9326346419795244, 0.7769113405672327, 0.8671915782708538, 0.7101426036117587, 0.20192446126559493, 0.667684595450286, 0.7561302989575927, 0.5299678589610611, 0.4740460810184325, 0.6678976506603213, 0.18982740325987535, 0.7754815258209162, 0.8912418547340085, 0.8582391712715519, 0.5234959384184952, 0.5356656573964478, 0.08824207817225227, 0.2546587872233984, 0.06400271843996796, 0.14795991786070883, 0.7223041061317048, 0.45461459835409834, 0.23739663595483806, 0.46533302061863, 0.8797590379500149, 0.9679415151155805, 0.4950826473640618, 0.6364019081732267, 0.030230016743837962, 0.8385725904223664, 0.5684519872302574, 0.8072602201092485, 0.5248618191856367, 0.8852925311548213, 0.7482260141785877, 0.9713616877171397, 0.1420937958034003, 0.8017407154294148, 0.5106911663782366, 0.6098164389053784, 0.23115798242299546, 0.8509385790786431, 0.7665772983399602, 0.9393098407465904, 0.04209603234663706, 0.9771297635499196, 0.15358359790476628, 0.39352418017453883, 0.6202102266129389, 0.1335429286194626, 0.63193489864132, 0.5831564534087365, 0.8776136257771191, 0.9039207390994624, 0.8464470187024711, 0.22015445409166434, 0.8758007877722682, 0.5851239989684559, 0.5898595680926785, 0.04071547690235877, 0.8253457187844906, 0.24325808257077552, 0.9996262268885948, 0.3691614600340126, 0.5643614269762219, 0.1630823145336715, 0.9588420377385642, 0.4804879795691205, 0.8226960511587661, 0.956060073252254, 0.01659088473297099, 0.22739377608187905, 0.6706579158019068, 0.6063368383867996, 0.11763113616922216, 0.12242279151794855, 0.9985661462571744, 0.36903342899318914, 0.39869687250042274, 0.7187090588440607, 0.8475847475235313, 0.6553391141005228, 0.12863123150038558, 0.5836869686536438, 0.3522864599361549, 0.40955837698338127, 0.30611366257419803, 0.08414039290708708, 0.8336975233383931, 0.6738773074893865, 0.6428385059166033, 0.8907033084159207, 0.22959797284571337, 0.7369959079185738, 0.764559332056781, 0.8460897600611726, 0.9342745878169123, 0.6797930366609867, 0.2590611993749421, 0.18200367952682905, 0.5398052073548281, 0.6135052126501889, 0.9629087642347781, 0.3502142894623047, 0.8565328095187749, 0.30366728820722133, 0.8649565171904231, 0.30627643129486304, 0.5097112506135479, 0.5395615475838216, 0.30123127472496636, 0.3152643339579706, 0.623404055585028, 0.9681245535183327, 0.6878256269558346, 0.7011734214993312, 0.5586441073144988, 0.0379074017111003, 0.41196503601278955, 0.17326048618444756, 0.08967405677495122, 0.16327890416213398, 0.6067354530243341, 0.05574386708342938, 0.30702773695791663, 0.3591315779204586, 0.8485003205103784, 0.7595345211816413, 0.4856754427037272, 0.8172224268993479, 0.9877879242491928, 0.5924825579327764, 0.3618245110082776, 0.3548864109202763, 0.9762786876976958, 0.36117544164029625, 0.9384918355587047, 0.44482421907262093, 0.4512444243209993, 0.2942412676670435, 0.3520183660479801, 0.59524292074513, 0.060313488971640905, 0.5664757004758704, 0.8004140890203537, 0.049739496565150754, 0.8326238008556021, 0.5231451049952724, 0.9589558280589826, 0.4688736120635163, 0.6457270091130933, 0.2743253316453027, 0.9817226612551712, 0.19214408906157499, 0.5365377233133565, 0.21937798392084207, 0.4474268422020008, 0.21332809147586096, 0.45152629216338536, 0.3954384470090013, 0.08389248957965645, 0.9456696894285853, 0.5455269272443676, 0.7162977033121736, 0.9921059770406268, 0.009140458313235733, 0.3068422204833988, 0.979535754019835, 0.39829763785135963, 0.9535422055318536, 0.5234518862510418, 0.45524982399842284, 0.20405093144406117, 0.07696699410493557, 0.9804917453968658, 0.7825096762276561, 0.6844391970560416, 0.06298248031832787, 0.7065637824445677, 0.8624628480867429, 0.39673398563242634, 0.8039480405258369, 0.11194534090382247, 0.3383757894318189, 0.4474095215262046, 0.45858194942102426, 0.614589845977242, 0.4245550119524921, 0.8932963158388915, 0.018992805669430957, 0.273897431447773, 0.9056057865446592, 0.13748729687735983, 0.703547358197167, 0.4175471719258016, 0.0891231092090986, 0.521908149470029, 0.6181832510616906, 0.5162935080620106, 0.006874159381718203, 0.17212747826130959, 0.9220698879129372, 0.3572613445519437, 0.013537004339399195, 0.00332288167478878, 0.9250367428697359, 0.5502732509918479, 0.4397655101560085, 0.976601928543793, 0.06587254795860342, 0.9967676011516247, 0.6905977258713558, 0.26360736296776377, 0.7377790501676503, 0.58949493561779, 0.6804985950100816, 0.5981458303119022, 0.7703354565435662, 0.6627016653960298, 0.17224546603828572, 0.7082205562153289, 0.9359161836117396, 0.19886404832129612, 0.29836885703887706, 0.6473082353319027, 0.19284360062511752, 0.24025878824616786, 0.4614850648177867, 0.11502873683838533, 0.7526668882653277, 0.22760724539997257, 0.9202846102044087, 0.25550938435415715, 0.35544012534438074, 0.6126980217670746, 0.7890785075351323, 0.43009962728385065, 0.3086886946583104, 0.893588207570993, 0.17696739805360007, 0.05815134452806059, 0.4915140236220875, 0.1964501214583112, 0.39365076296370527, 0.9805756394782623, 0.04868204736327009, 0.7852713192874631, 0.5662294612024402, 0.1438711221710759, 0.30549087894587446, 0.83700883167725, 0.7583273991302517, 0.8360132064134883, 0.5700849208188266, 0.5481702973600299, 0.7511787034407322, 0.36120915262371334, 0.132261472961134, 0.6686710290333494, 0.43826121820220365, 0.27632276417904833, 0.9008174856418658, 0.3132578975392324, 0.13788308650145287, 0.33012548777667416, 0.06369117167103067, 0.5615609397503767, 0.8469336604603973, 0.07515128644039626, 0.7282956188244899, 0.6062687977350211, 0.19154058595916068, 0.051760414269677146, 0.9321707816408611, 0.6388059391959006, 0.16067973027254356, 0.49671002197682934, 0.810464225248854, 0.6242380199031319, 0.05822510543252912, 0.5859719405339411, 0.5369842479928887, 0.619865713972886, 0.9469581122505808, 0.4840236543656491, 0.2446590918317264, 0.3734040462532573, 0.41153241114773353, 0.6722644245654192, 0.9438265055904, 0.6151662338440665, 0.3197496864519831, 0.6445709776773069, 0.056224428769436674, 0.10088475920050821, 0.24889628578565504, 0.7738240305795522, 0.03380264814176548, 0.36631771582407024, 0.5995615466962256, 0.7315869652859625, 0.012710303153376956, 0.08364010672389866, 0.3706441905455059, 0.9373563883673417, 0.9875599034399782, 0.7509701583207454, 0.02864431810531165, 0.3335893834931921, 0.053975729619853974, 0.7492542388599975, 0.4236636780056169, 0.6489993496635825, 0.4757128477406488, 0.8501970384373653, 0.1268046479893734, 0.11640206411035037, 0.1802986721722314, 0.8453208273446001, 0.8275576269506577, 0.6147153087971005, 0.1175291803443439, 0.41477625112760397, 0.7704409147534934, 0.3533472246534449, 0.7043999684517056, 0.775247294967955, 0.9680923381195076, 0.07249110207318155, 0.7134446243960051, 0.2112924294650559, 0.5601033124031858, 0.8351535085778684, 0.6651260922739445, 0.849093636443096, 0.20523992884744047, 0.6985207565901812, 0.07930679838337618, 0.43241274678741615, 0.21381459398456937, 0.0519328953800301, 0.05624972539580908, 0.05839395149548465, 0.4433522299538598, 0.3895892892400896, 0.6261753770716189, 0.892302431029592, 0.13970306225988627, 0.1456114428839015, 0.4950650258719298, 0.545653270903222, 0.006004480737930917, 0.4208035646201753, 0.3573139364844512, 0.7434131064312294, 0.06236410776831858, 0.6221567609082567, 0.9748682253215738, 0.07931212068682203, 0.3545797843007681, 0.014486999616720397, 0.952942242408267, 0.702288586815865, 0.9409255416841286, 0.24827063949386452, 0.8583481708963405, 0.8646466524926354, 0.9449436184654777, 0.1379156671442492, 0.39301636473189094, 0.6940708441909698, 0.05064455415602809, 0.30932198343863126, 0.12439893551457126, 0.9725969293678293, 0.22981000064090706, 0.42793450167504743, 0.6240132929133849, 0.41274173218145593, 0.10829569501663205, 0.07595924640852625, 0.7891772556987178, 0.2029382856735208, 0.9504847151745953, 0.25946997333986954, 0.1848810682149351, 0.6815257687996995, 0.2822698882235799, 0.6119945853180316, 0.032081347455592435, 0.740984443711812, 0.38272402393289806, 0.21738260099766638, 0.8275875488973528, 0.8553262745989765, 0.5822720377847401, 0.5554500638376147, 0.7136089747266824, 0.8617301311847095, 0.11174941727880727, 0.10998531598519001, 0.11579210053669431, 0.5112942412426882, 0.40233180692142756, 0.48360045805782803, 0.28324739831875256, 0.590023394006501, 0.6283584737073288, 0.6101317601514166, 0.6823463906868024, 0.6878986835866159, 0.055622664124902355, 0.5721668333725881, 0.8310677523242348, 0.2354956414595888, 0.3921367771656503, 0.301710577021835, 0.07982569798898997, 0.5844595931256942, 0.010606427673007457, 0.6792236211085227, 0.48711598100376485, 0.4186848389719604, 0.1520205731322931, 0.7038373585767068, 0.5786547828151765, 0.4501356701602913, 0.5940159476490812, 0.054130408441241396, 0.5340508484006485, 0.14563077352160447, 0.3467809498492218, 0.015245119191614198, 0.11916804616842058, 0.6442054337019893, 0.22110456957047342, 0.45760836940150784, 0.40035833791514097, 0.39736125725439, 0.8406222554440334, 0.7480051824691096, 0.39607450326184934, 0.6169601784227084, 0.9147752952196849, 0.528942392721163, 0.19671595910585504, 0.7689629632964102, 0.5857627989010331, 0.7281758790847451, 0.47549678474268886, 0.9771515487528412, 0.774362181908109, 0.5792613657580393, 0.2915181063192954, 0.48129611722341215, 0.16842684750387993, 0.4322435813410115, 0.37706028162465177, 0.5275190748603705, 0.19388516254113952, 0.898894215990235, 0.4105507981093036, 0.10183344441151243, 0.207244497511354, 0.9936018501009102, 0.6822066970703475, 0.6097103669992625, 0.8596785426464303, 0.9737261311085316, 0.23384606795789475, 0.469228370203129, 0.3150856919691406, 0.45325584290765897, 0.3021481446971995, 0.7359263296519397, 0.1041928137278838, 0.5392024266393926, 0.06796476537924911, 0.7553123488967057, 0.2747219889480731, 0.7448023725235665, 0.7267290806878393, 0.154584743104079, 0.1426717670246317, 0.8522167288462654, 0.23101453763592739, 0.5324589078725956, 0.6001934763867139, 0.2841668620399004, 0.020418692597819477, 0.4722662627404567, 0.036155325406367345, 0.9978720177345408, 0.9098451173551634, 0.5419285071156141, 0.11797572280199964, 0.048379473113458804, 0.4672711193136607, 0.9976039161475324, 0.9060066652367704, 0.11916027567553478, 0.35622097880083825, 0.5837853249886084, 0.8673768649987554, 0.032129972124176565, 0.3178381599419763, 0.031188770237290275, 0.6740117489211176, 0.3874682439750927, 0.6034438219410512, 0.6976344752830447, 0.7235262307756359, 0.04479657754166555, 0.911151772773858, 0.15080123773789078, 0.589525284901, 0.17840564644069878, 0.9373110675973576, 0.21559324070959918, 0.10706404774727907, 0.5898301805791695, 0.71684443995085, 0.3955748642340061, 0.7195496822110167, 0.012350906723061605, 0.9904757588978808, 0.6105136929764267, 0.01682024403986948, 0.42501736700329673, 0.21419171941390525, 0.5487351165612928, 0.0023875126283702253, 0.6827750954806542, 0.10490738049003712, 0.18497201371089644, 0.670811504068588, 0.2927928640755091, 0.4998383395178182, 0.22808468769155055, 0.33078188807354403, 0.12880091194857413, 0.02885265498228462, 0.47935276328861187, 0.0273501250248277, 0.6184719965891724, 0.4484981019599926, 0.16317110109496624, 0.20872944653302772, 0.95201336175559, 0.7963354270919263, 0.7715986969599571, 0.403482508281638, 0.9297256200098162, 0.29986859030807567, 0.45218289423576097, 0.9159675492849336, 0.7797312318801557, 0.3292487117573706, 0.8932268863243941, 0.5440300092785846, 0.09194090420757495, 0.07879232640967515, 0.040625433564198565, 0.9503034730149118, 0.15328940647971256, 0.968374806319513, 0.9130639483136002, 0.8305563280949961, 0.7430223959392527, 0.8468642149605811, 0.9441514991775032, 0.059431005272214454, 0.9445956362139237, 0.8470158973052053, 0.41664160482788337, 0.8994160293188886, 0.6070162264314966, 0.36164423155689573, 0.31625664936558784, 0.6799843043260322, 0.6136959611617626, 0.1301268735001968, 0.02377007352486482, 0.7932053225469253, 0.2836196329545091, 0.0033773633064905217, 0.9345825605764154, 0.19414282257909432, 0.9248060469917657, 0.7165778920127337, 0.8753653449773379, 0.643516949277003, 0.7382024233299749, 0.7680237323978785, 0.9901440256760623, 0.6226630404604593, 0.8449432524291013, 0.6923742172151705, 0.2781587066872502, 0.4957407497415651, 0.4855832772459078, 0.31708832143366916, 0.058436697318391184, 0.0683478293038251, 0.5750520306533216, 0.28948034703034453, 0.5765627757815632, 0.4715704872547748, 0.22788663761967987, 0.7080665572063077, 0.2794882968516803, 0.20370161645442797, 0.03021991812820024, 0.4876444400214619, 0.9468853854088918, 0.8320045949627904, 0.7745298637300877, 0.2703193784452338, 0.19852261953924477, 0.6410566228896608, 0.4778123457137041, 0.545476392499247, 0.06642829785014648, 0.22189436858071054, 0.138348616122402, 0.1992553717660479, 0.6675765820845962, 0.7938402926354475, 0.1845485694491109, 0.5220038702812361, 0.9156628087827617, 0.5171059903078549, 0.7682320826737409, 0.5353184044875635, 0.2753276155492411, 0.8536998274382601, 0.9574612439879333, 0.8443201396244076, 0.452736414538202, 0.09814834076597412, 0.7831688382370738, 0.23053173360813417, 0.2872843483053551, 0.5464667272055969, 0.8339728010161706, 0.8737974051832735, 0.5791460745041196, 0.035061872524816406, 0.15330405242539535, 0.8833427264594675, 0.019455499177527202, 0.7765179596489821, 0.4246213814504972, 0.6018063770500839, 0.47550462640023883, 0.25401536848013795, 0.5276980323620261, 0.9761363781187026, 0.1067498076808111, 0.9685086403819209, 0.8698169765639949, 0.08316789304990158, 0.7638977882293679, 0.5973581096783714, 0.6938183139100992, 0.4195666743717207, 0.06693056686596344, 0.9028690484818521, 0.9702734767918807, 0.6764342486984665, 0.45625768583112336, 0.9648986798783104, 0.9396506860051668, 0.9538360653045057, 0.25325193102193755, 0.36031844206186947, 0.3977997550597844, 0.5572149144626898, 0.9415146703812277, 0.6501691840398597, 0.0810482876250247, 0.46703641936801854, 0.04871768527153719, 0.9957216498980977, 0.6893381973344791, 0.8880136437107692, 0.5497225509802108, 0.7422844449685458, 0.6941851504106487, 0.9593676896692689, 0.5606399742300912, 0.6421050338498311, 0.6233991086362393, 0.012802969408392428, 0.5121379506441427, 0.6445479385963687, 0.2808629709144951, 0.9134059284125124, 0.241129912522295, 0.394455873040213, 0.6446088672758098, 0.5904555718899333, 0.10540634673485016, 0.25908661804810684, 0.7728241403998817, 0.6358154054664722, 0.04101646728837749, 0.8516622868856863, 0.7702489121694064, 0.5358501365373546, 0.5980355452050076, 0.6381225444135599, 0.0005730689961515045, 0.970167631347459, 0.4139198325451804, 0.31278243934984296, 0.47495283600091587, 0.1506419275618026, 0.606656160038374, 0.7674287071193997, 0.24208578546375847, 0.05657336308366978, 0.7296473273305218, 0.2800903221949176, 0.3737098785122176, 0.5816524263942958, 0.7398790543278544, 0.8939526932421885, 0.5351544556658304, 0.563915725881967, 0.13263723512796788, 0.07480840017856882, 0.888439574882212, 0.26115699832587147, 0.08869035589692076, 0.31212028688447613, 0.656403249920012, 0.17757508468680894, 0.1818755206457191, 0.14906764949964846, 0.8318883046189531, 0.8662107933319225, 0.3764187147705156, 0.6696546881748311, 0.8458197048945892, 0.3110623979033247, 0.7437629057558237, 0.9027797770544782, 0.8209307165929335, 0.23092644666423678, 0.8242236924078323, 0.1056270838541351, 0.22714477549988266, 0.20030944013001561, 0.22947690294329104, 0.696107896913141, 0.1283109954762095, 0.44283684026157966, 0.9870057925549655, 0.38010663867098504, 0.4995866716824585, 0.05815074830759892, 0.830644135939699, 0.901107268640793, 0.6674748299363391, 0.8742574761980677, 0.5410088553711261, 0.41808675211638335, 0.3026323472134641, 0.6228425912179886, 0.8813533904099847, 0.2014708147991391, 0.18056524943067742, 0.27298410151262853, 0.5845715257984936, 0.1427309327353672, 0.19563483007643578, 0.6604895077724356, 0.4328040134627058, 0.5535861275702852, 0.43729116466734064, 0.5785703891701747, 0.8584977951034565, 0.9287300149661745, 0.3181366808854369, 0.018292526012644306, 0.8952263154294313, 0.44756393222725244, 0.8828372510820739, 0.7920190417259078, 0.6316487285191849, 0.47214678451975034, 0.1217236120656986, 0.06956671644049939, 0.8685768661626136, 0.6366666715394657, 0.7665535561264174, 0.2942000153076372, 0.0021384733335659822, 0.2705189531723111, 0.14852579879255556, 0.0031594701312605, 0.8020540104483613, 0.23825907633485832, 0.058572212572497784, 0.7212883579835159, 0.5100074611405732, 0.722192976008997, 0.819647715163588, 0.7612228919413981, 0.6876784548058867, 0.753905786906214, 0.39282539072319744, 0.004182904604925652, 0.48721894979930347, 0.5580422170120712, 0.8774420726435828, 0.8975977440531511, 0.9451131350702355, 0.41383061060177884, 0.817770323637275, 0.6039487832761105, 0.987517253890432, 0.05015786167681868, 0.04723660246617467, 0.12377526334074984, 0.21124698750240423, 0.1322116018152607, 0.7817994842033689, 0.03028219241051744, 0.3428835864849662, 0.03199451074338855, 0.2973095452202774, 0.49511220520603216, 0.9018201769429584, 0.0006354099343498509, 0.19421708019059825, 0.6450231697732115, 0.5296240807773047, 0.5105340545040825, 0.9386296804923623, 0.3161713115563347, 0.14028515886916293, 0.5387406003641704, 0.9110577932539954, 0.06657870021944057, 0.5912929046820949, 0.5179400632837544, 0.609261071478327, 0.9117110959165275, 0.8703690153188935, 0.5497902950456989, 0.9350579496703919, 0.5974582803716901, 0.13403848834280496, 0.6629294252295096, 0.47010691696034035, 0.9761243559009092, 0.34289882813318207, 0.8930139064505231, 0.19040777260393993, 0.051124774360734704, 0.5294072929890149, 0.19410419502989018, 0.9440421479442738, 0.4166782766470989, 0.3160191740816636, 0.5422214465437505, 0.949524592828134, 0.7619764670221031, 0.19813663447896934, 0.9358447108348422, 0.2258479781524465, 0.8369816032225623, 0.42371677122009965, 0.4927493002445543, 0.6460682076138372, 0.39918844597280256, 0.18909188427557178, 0.3883802426788604, 0.532017099455421, 0.7441909286934728, 0.23403353559202356, 0.061046748830294706, 0.5961221506465061, 0.8395904615929172, 0.6457084544821122, 0.15311372620329644, 0.4373881068440266, 0.1663769055446913, 0.7126706591764523, 0.4388229790700475, 0.6019044757231076, 0.3174900094703226, 0.7373903377263857, 0.3696894074493522, 0.8631994093593957, 0.10456056343761588, 0.5682302022515529, 0.11036687014440916, 0.1853534915477586, 0.4714290617030107, 0.021146922089727016, 0.4992025281859396, 0.853745244650295, 0.029389637234443766, 0.2376360327147291, 0.8675121158430259, 0.518866279317268, 0.9581510765966711, 0.3061391874518814, 0.7178121131464243, 0.42959687668058044, 0.8030624178476544, 0.1779311926645154, 0.9406148630475923, 0.5988386283208718, 0.21336034177209195, 0.8458220171084456, 0.6518563580968002, 0.8151656534406012, 0.11530676312167254, 0.8549342316974974, 0.12026560805600395, 0.8825419742135456, 0.25306197060654323, 0.6246537536440278, 0.9810507533303324, 0.08198675254978616, 0.18356708081737294, 0.840212309029986, 0.34978738639472473, 0.5811133514977767, 0.12108801074379638, 0.29279170621473194, 0.6211657218385176, 0.26614473502557867, 0.5215857463382015, 0.8374212992213292, 0.4503314494895746, 0.41182033387137573, 0.5294716972687585, 0.4490763273822429, 0.715512372665164, 0.7547233919025684, 0.5787696411606202, 0.9161390478144067, 0.04321560667689239, 0.5935981448998804, 0.3513088380775903, 0.1999436890474422, 0.7441935839647646, 0.9007133644535372, 0.8835327361660775, 0.6168277965883692, 0.5728661998859953, 0.29383979076085, 0.67588620149184, 0.780627164900737, 0.22948824232609555, 0.8087087491200404, 0.9517699074642698, 0.4837326541710554, 0.2649569323583517, 0.3893779848611677, 0.38993205745783954, 0.9995700115351378, 0.6854742123212844, 0.5223064599310434, 0.5965334844686394, 0.026911927555466453, 0.5564166288938609, 0.36077705590427533, 0.7389534773751507, 0.13404086412429939, 0.11630315014743342, 0.9315752021049897, 0.9403315245386192, 0.49533689452191676, 0.525325058494812, 0.47127611656533197, 0.0011261634158155065, 0.40116422984841105, 0.7810839083387513, 0.14908600010120387, 0.5835900308371406, 0.08424615664036961, 0.08954714530749353, 0.0042306551068308496, 0.3549308104413461, 0.9688357347342783, 0.805803674781628, 0.06464464059894703, 0.6492576322174521, 0.4603415023926454, 0.809980000381188, 0.4467787853548748, 0.8250527789304927, 0.5015847298091055, 0.3217176870635923, 0.6815068170860141, 0.9307020801316691, 0.5108938178855553, 0.22472536844261826, 0.3205189185569852, 0.8123237301607058, 0.7853530489145921, 0.17261391570358375, 0.20618152457728678, 0.07489774899267887, 0.6841235958896653, 0.8245657783242767, 0.6127687578195344, 0.21417887046334738, 0.5898995482446496, 0.43214776039847524, 0.287685658904389, 0.966668910907153, 0.6265879362570596, 0.5567067585752324, 0.9255099245349717, 0.15251016852114685, 0.07504678340158943, 0.6602504093047964, 0.037377946354966496, 0.30314961993664213, 0.028654271478108395, 0.13360344298379012, 0.24946821435783817, 0.36605019991506693, 0.9666551630999553, 0.2929026084461347, 0.7007829308242938, 0.3984103488422228, 0.7077815244254492, 0.20457366847316405, 0.3591135250823603, 0.782302855146139, 0.43044850338352525, 0.3279348118907016, 0.942806426429796, 0.5487491735780083, 0.8070770045965476, 0.8850820557086818, 0.4686457261050633, 0.9386256214555576, 0.04981444788221934, 0.45119441894347345, 0.3755329696980041, 0.6072001020632831, 0.04685556555031334, 0.36463888950011303, 0.1292736722422273, 0.5559461390331101, 0.448137606634192, 0.04307902521305429, 0.9915888468749282, 0.9937972790160576, 0.12683585302018174, 0.9190781144931423, 0.005173955568690269, 0.3789608860441951, 0.23225393791227356, 0.5197235209850033, 0.06068506165754006, 0.3328722232602167, 0.7144951467890664, 0.011772266936242448, 0.8089600890513293, 0.5584621751241723, 0.48685441469910484, 0.30140044336456673, 0.7384330273534823, 0.8838860911433283, 0.7655045666830963, 0.9655461107163853, 0.048934334553572434, 0.8638767051770332, 0.5627714547285853, 0.931310644602255, 0.41220090849492275, 0.7082542696207274, 0.6084347576669571, 0.20456104258164465, 0.477029268698448, 0.44844127675336487, 0.5787990745548962, 0.3770735574900834, 0.3735618947148749, 0.6876613663958867, 0.9064909516707507, 0.8821015134749218, 0.7932978766680677, 0.5459485896276415, 0.723823901752216, 0.7328258589747866, 0.19605109852844538, 0.024165035352742503, 0.7454203375687221, 0.18652268736533506, 0.02456337606947112, 0.5545478651158708, 0.7791745915654774, 0.22338557964806327, 0.6161725047861623, 0.4841106710643994, 0.5203647330718995, 0.9735371638682989, 0.6220421470403724, 0.936698459323376, 0.6061502892210182, 0.9335847299440825, 0.6633445705503808, 0.96514758068251, 0.6861018984601583, 0.3406344779441254, 0.6134172702116162, 0.8437599560787655, 0.13903574485505588, 0.15598235134828065, 0.5996357044099047, 0.7778885314496502, 0.845182037284684, 0.5644977593981221, 0.22574113472727053, 0.14143922421302713, 0.3459062599595004, 0.5467997698965403, 0.27877753281044704, 0.7719785301145675, 0.6558884344576283, 0.9484641184766361, 0.05356603962708251, 0.31347229890306105, 0.1927929374287186, 0.04700060806397721, 0.7777934067068457, 0.9428170789075296, 0.13788884083324016, 0.09225740257930115, 0.39538186666138386, 0.6426671597558447, 0.6645101669603284, 0.8516079960750027, 0.46352144150671604, 0.6821217471212255, 0.3166835374075665, 0.7565640234568531, 0.4572110580211288, 0.7091424258819078, 0.8284542114051713, 0.5954578784783009, 0.600818862321135, 0.20454027752451676, 0.8088374839902512, 0.7958778621997168, 0.7235778614070212, 0.12146761738117173, 0.9856505515985629, 0.12806218368711997, 0.6468565460652339, 0.9365945292512512, 0.11868796418600469, 0.22659383990738313, 0.3355705057867203, 0.8305069446356678, 0.9886186136039321, 0.8832738087870601, 0.8717170289090703, 0.6548832673263553, 0.3417799358955971, 0.8756836631678206, 0.9343578065576121, 0.6226707188188723, 0.2795650148316504, 0.15666076112472216, 0.3604682262499933, 0.6016462277742775, 0.011908818549332678, 0.8244967331339306, 0.5492979740004873, 0.08471502647339568, 0.9649886680574392, 0.4739467634309569, 0.9142314938199682, 0.9738370904225634, 0.6821333536605566, 0.40104361871173344, 0.6025757666988332, 0.29934741193327663, 0.36008701386172837, 0.9097456482328089, 0.5581538052997621, 0.735148341625817, 0.3118239423743223, 0.40755094388626223, 0.09849728258789037, 0.7571048153460735, 0.8181732279684203, 0.10281710395431065, 0.661738919058682, 0.6743533320839143, 0.33257752896774206, 0.5254200625539256, 0.16188812739496083, 0.5760914997424635, 0.39048671844780003, 0.6046862323244631, 0.21539773760842906, 0.45228997288386763, 0.7598499476723125, 0.25906168590022816, 0.13171301366244959, 0.9380895129310859, 0.24464236000193362, 0.6756528896294898, 0.8010293651258765, 0.11112497287813083, 0.15889180461314412, 0.6426914329245296, 0.08012933742817208, 0.7024438475025708, 0.7800406052437331, 0.6976349048033528, 0.2655752601089888, 0.11894263185853304, 0.9726891905476274, 0.958686883069459, 0.4614238216532637, 0.825206961294047, 0.00899802724395804, 0.10557162167042611, 0.2862468587516397, 0.4007705146493502, 0.36788320071433955, 0.6256519985464207, 0.6547717170923529, 0.01619095080673516, 0.6428985375774177, 0.37440334217310656, 0.9510114809838487, 0.7423930113498056, 0.3748510089200686, 0.3021426742837763, 0.27677748421735315, 0.4726216365748753, 0.35347246406955923, 0.47263562317504193, 0.8904053126100108, 0.993414980906022, 0.2108959975549224, 0.40179737370660873, 0.5413856702618038, 0.9837722202857723, 0.8392864405093642, 0.7804332664011326, 0.7599170086552804, 0.6616335657364181, 0.5060321394194944, 0.2645028217449016, 0.9021606622505445, 0.5011482781203392, 0.9161768880475764, 0.3521801941971522, 0.3645557372854108, 0.9212675626530059, 0.2481742895188387, 0.2597225757078925, 0.29922477348662346, 0.5555225525115886, 0.15510385590994913, 0.3917931411067034, 0.21419293874028134, 0.2123210702681928, 0.5423422640669667, 0.6022056003123867, 0.9852082112019599, 0.9408668231380903, 0.007452175377153258, 0.9918775989786723, 0.11968267433412427, 0.4171504253040472, 0.8990178806960634, 0.8204545641663439, 0.12737421210472932, 0.7767068637762939, 0.9543759938976861, 0.6539866469075626, 0.15083598527341247, 0.9105997857285306, 0.6899109893566384, 0.9330765131081907, 0.11471514165595975, 0.9830417643736598, 0.7915550882449488, 0.9792404144480158, 0.4427754250187914, 0.218546800472755, 0.38907061080875616, 0.08417536584888896, 0.4386027967603151, 0.15799180331449725, 0.768316164567885, 0.15825409957639613, 0.20959162724058022, 0.28239526818846694, 0.5805957186323695, 0.2990751101856757, 0.4261014875801308, 0.04983369279912864, 0.9740752200682488, 0.00032215374705446553, 0.6303506391626595, 0.10090378299958092, 0.5324431397683922, 0.10118549166252622, 0.9330794162946814, 0.28224380396207993, 0.26764062330390836, 0.11600917673683364, 0.177114301538137, 0.5889084764708228, 0.49035737310134797, 0.4193138969522666, 0.5482991153071438, 0.061978536212031976, 0.03648561086635893, 0.9595424045917216, 0.016561138083179938, 0.40419553893731397, 0.16071238740942773, 0.9053023052530427, 0.6611494893690456, 0.09368948959019074, 0.7537397509437487, 0.10984720438672857, 0.07435475772148714, 0.4363308394820318, 0.9783724151057756, 0.6842537483403482, 0.16593259214075062, 0.4283230180626766, 0.9656437260267741, 0.993918048460032, 0.7504252748810978, 0.3171313513657953, 0.6899439690944335, 0.19673981360546244, 0.7933607547701728, 0.6568330264840634, 0.0366604850596034, 0.586676094667199, 0.9002159750320393, 0.974587691501134, 0.39708846807912035, 0.018230579141917058, 0.8390032397927519, 0.7250606025155855, 0.707740834187484, 0.5897591282841996, 0.03204849377328489, 0.6249782190680675, 0.6121534063205292, 0.941684997455199, 0.40933037433017183, 0.7331045194725069, 0.9616559451212776, 0.05484791845088777, 0.14215545738865076, 0.7218411192012832, 0.7245761149461467, 0.11267407940931673, 0.7167815870902152, 0.7718592073731969, 0.1708343093299829, 0.006134529546718226, 0.3285773804069311, 0.8234402522217823, 0.20131489118473334, 0.9571295273757158, 0.9029364686662202, 0.7337951081119427, 0.6193750746550172, 0.5697903555297493, 0.04187276374112481, 0.05116979980185532, 0.8314816091403153, 0.13646266833628506, 0.1827819361273202, 0.08251065658619616, 0.22930002967559882, 0.9847498288427354, 0.4854014665012084, 0.9371163726291158, 0.43948179218112915, 0.7696563960696302, 0.9406734438198084, 0.0014140890580686127, 0.5828788152389587, 0.8115742064972556, 0.5336101774408298, 0.09703523482800858, 0.8857790891852446, 0.019260078528706148, 0.9288314028688027, 0.9860862022233942, 0.5219878989947618, 0.6919798726880586, 0.487644912548607, 0.1274325393669612, 0.2810803217475317, 0.5021660332039558, 0.13843448921554957, 0.5669820000670358, 0.9826325525752924, 0.040725980460798894, 0.41312061048452786, 0.7517449158380617, 0.8441372415542526, 0.5406017150189717, 0.5517473795646475, 0.5117995027340629, 0.21912236023425102, 0.15633221887458293, 0.8013934472183825, 0.7030608868768208, 0.3387838519224313, 0.06439131494485617, 0.6072484045014047, 0.7009052268738848, 0.4718957498453151, 0.7900346277920608, 0.44921073510498977, 0.25851607859383297, 0.6474009514787405, 0.45306798039003426, 0.2554132582319184, 0.10960580060874014, 0.47912881940191787, 0.027868363893438164, 0.006106173386905778, 0.7259626007588088, 0.016583008867730453, 0.8601740028990159, 0.20970860724401075, 0.4377378927082777, 0.34745035016919745, 0.7402309045176597, 0.09126785161894224, 0.9419552432406452, 0.36258247608941263, 0.8444264198665146, 0.9694907666031837, 0.33240556983912317, 0.2841548142222666, 0.9293360021847514, 0.17737241967651574, 0.8129789767923287, 0.43838646638112655, 0.044352029260083414, 0.42032070140515854, 0.9457038930907485, 0.8937664574663913, 0.9807780739109321, 0.86940403023997, 0.7985926255993681, 0.767649657289681, 0.2715392010357749, 0.5638233592226446, 0.5429260016497375, 0.6281534110495334, 0.6941281957059903, 0.2625504404760831, 0.574385438188128, 0.8166393028206065, 0.20953862956384983, 0.07813020231811607, 0.6591245871100481, 0.33077748352026937, 0.14595567132572362, 0.8024891767383944, 0.8909560685053818, 0.7373554637900283, 0.8388269948540654, 0.399190349529548, 0.6305751690917523, 0.5477434981710652, 0.42082606303815506, 0.9284524943968359, 0.07846200614647458, 0.08768393732336088, 0.9835584157484129, 0.22458938497257142, 0.7234381686683174, 0.8071042934264052, 0.38373858729637356, 0.6314764300376291, 0.17037297131760476, 0.26354482931810785, 0.30605507789000386, 0.7371997188797301, 0.9776135934677442, 0.008512820063818594, 0.10869869608049121, 0.9179058490408968, 0.10325024249521753, 0.8658809504227689, 0.4338200486094673, 0.4482240224907943, 0.32665629882468983, 0.11785058947074212, 0.8801195994988438, 0.21399401198667523, 0.8853200395578502, 0.3511490525481342, 0.9802061324552901, 0.5655375342681864, 0.7948142734645098, 0.5675696058794935, 0.6383856420960282, 0.8478230332215296, 0.9703696830313749, 0.4671297543772188, 0.06983129704605762, 0.6525838929635193, 0.04457626977989637, 0.46527766222973477, 0.869884077385513, 0.8713504397191266, 0.48174019199406026, 0.8786871247661204, 0.8444848915406978, 0.7909268831186177, 0.22938936649959962, 0.5111027984669417, 0.748651170513814, 0.37737539989049185, 0.8840334371857501, 0.5510733006826646, 0.10648063450738887, 0.21886789617142666, 0.16317662717280335, 0.7629352833426475, 0.12909066834194638, 0.8555171416585637, 0.8129929404099899, 0.16597345469807878, 0.2630470053173972, 0.12001620008038238, 0.2980015357381648, 0.8899244737630556, 0.44787156559219266, 0.4196703118908268, 0.5759109349541586, 0.4164581898027886, 0.6546265571009381, 0.684724154575046, 0.5590946252074627, 0.49168621314215666, 0.3058928221458628, 0.9544390401499846, 0.853658458874726, 0.21275808841632982, 0.4666348536818804, 0.7129036867018201, 0.6768287504098665, 0.4649588379702999, 0.5147326818148316, 0.03674789057197436, 0.4019630892602475, 0.6712487501813974, 0.6542485793652907, 0.6440612497487972, 0.8590372219447355, 0.008495614336447743, 0.08473985821507257, 0.6480516205261334, 0.07597894893155033, 0.05090009686790542, 0.26354064580002734, 0.6071189359327064, 0.8981093334339811, 0.9873705826957054, 0.2346938414790437, 0.5744909069047073, 0.13320613456206354, 0.2829557721335417, 0.6303316606235478, 0.10323905458911298, 0.05980034324224026, 0.6276329029724647, 0.7567814781709326, 0.8740605964980697, 0.7840824582989661, 0.2233471473003188, 0.05855824778786234, 0.2381236129766915, 0.1836136989133872, 0.7653580622360917, 0.9339037006205303, 0.5816951874334918, 0.7088541970400036, 0.4782210621723998, 0.6320182406635941, 0.8379102189796891, 0.4753302203434747, 0.5729176996679675, 0.5268155431449816, 0.11026388398003484, 0.13171219495346664, 0.9704246054166432, 0.6200459243536022, 0.8145628229831698, 0.23223366662359457, 0.5196496780277942, 0.4767948586098145, 0.8312713734556832, 0.5662305287300955, 0.7593409467477318, 0.004558678330644272, 0.298406011857943, 0.48730116497590836, 0.7239704676587752, 0.35959323344515326, 0.05126451485350014, 0.9064886768048788, 0.2692384607413335, 0.5589198081882547, 0.12912482259957514, 0.5147901213332146, 0.33145842966242545, 0.20871738123377692, 0.03541979678253637, 0.4098084717305672, 0.8554333210416315, 0.9267536963629067, 0.6083276773134011, 0.7916088354402241, 0.7813625572896977, 0.9170870928262315, 0.6282698742151044, 0.9343836859351446, 0.8886709101828077, 0.23626366539220522, 0.004105794434200116, 0.2879082699350165, 0.36567169973679237, 0.955256193504928, 0.6294458713305562, 0.09103900758001693, 0.8469312473693905, 0.0014838724188969143, 0.0730702896986335, 0.8364985398778184, 0.004808171586357379, 0.9302304023298917, 0.3793888885770289, 0.47793120630931707, 0.6178484131341514, 0.04348012623334574, 0.16919156084524, 0.1580940570587458, 0.33432653785086464, 0.446070816449764, 0.7456699751042108, 0.027248434098246066, 0.5130379707852901, 0.9124654482672971, 0.20776673925643374, 0.2636170738421506, 0.15322000146224457, 0.1241009866844297, 0.35578720492164695, 0.5211235421346518, 0.3164195130719253, 0.5299069809663779, 0.0030222633286991485, 0.29299764689615815, 0.34169217165685095, 0.09619199583064919, 0.7201185155794164, 0.523836365618791, 0.09422538430473615, 0.6894251441859315, 0.8109289188418026, 0.5507676267128784, 0.7875889700149205, 0.7460708818443026, 0.2674186102862097, 0.8880648493901172, 0.858649134282793, 0.6731546082956901, 0.358301666422131, 0.8638837182160444, 0.07775697534964099, 0.24497582154927666, 0.9593068764206688, 0.925761948926003, 0.32034453042173405, 0.6603319911009783, 0.4150325675390295, 0.778364300975389, 0.2636234943309784, 0.33923950173924644, 0.9218773376248665, 0.2889111478583931, 0.8770656737277066, 0.8621685222181902, 0.6723311758022619, 0.2605153243045394, 0.6097867896803811, 0.0009594047833868524, 0.4519505521431685, 0.6497667064297269, 0.453976342469788, 0.3993842862978997, 0.323114244725039, 0.8996004342586513, 0.9610662041067752, 0.5154665171363502, 0.6884889037472333, 0.2969198384398505, 0.6490400491756882, 0.05853874728565345, 0.7739308349734073, 0.3293458724575423, 0.9570197495433028, 0.17283147059396897, 0.28930996504732176, 0.3863223570947747, 0.15320749006711865, 0.23779080369512873, 0.8912304760868286, 0.47631078090237944, 0.7554738886093284, 0.90041004023757, 0.684442709249358, 0.3724315620337597, 0.25537990805579114, 0.9390953782390274, 0.6881598059238712, 0.41060365643565144, 0.8113060334062302, 0.5822406615965725, 0.6950494704883114, 0.8685724471069483, 0.6869400639375701, 0.7868680256982854, 0.8636048049648265, 0.044671237035904476, 0.3854928304185423, 0.992016344242109, 0.6607963854423865, 0.10006921197913154, 0.21217674304853384, 0.733714216367171, 0.5122882249286589, 0.25262671684003757, 0.7458952631238392, 0.4896060518251806, 0.06524300210801981, 0.15996823719534792, 0.9572921921652023, 0.21153701149568171, 0.3631876671228319, 0.10763292539292857, 0.3968451986744491, 0.009028588125270076, 0.5040465952864235, 0.18862980100115, 0.0009805060182767056, 0.20572530379515364, 0.5194566405462543, 0.17603804090113906, 0.7852113384431475, 0.3455382401713297, 0.6669634483788133, 0.038659822124262555, 0.9724654513697798, 0.6518917785234513, 0.6451266337602618, 0.5165842668692634, 0.6854582863536932, 0.36662112881860465, 0.19783858055409853, 0.05209320862630096, 0.06848818232131315, 0.5620488897349047, 0.7814340593863996, 0.0015579886364495144, 0.06801034182744226, 0.35691965425128225, 0.4090556670508517, 0.5950249280592846, 0.17296012453967602, 0.9808186822058274, 0.6436863887760205, 0.17719172988316012, 0.3122834597142039, 0.18286887466427793, 0.46885879849994994, 0.8897053245055813, 0.21141486050979375, 0.8499188869077299, 0.3847450841790877, 0.5133694204353769, 0.05265969096711354, 0.3455522195496137, 0.7217475042024573, 0.3424069753314998, 0.703047185039163, 0.7138267365136245, 0.8309582196073724, 0.48830636927457494, 0.2977454794617652, 0.8147915021967428, 0.9546752875251681, 0.47394632155077965, 0.9187583027266814, 0.5199272297544021, 0.7351357157352518, 0.24241224252407434, 0.8882538524878565, 0.5091420004969103, 0.6013326660222763, 0.3883364996654842, 0.33419583928849395, 0.6088957250977964, 0.2512737647019182, 0.1440776830337569, 0.13152661362709495, 0.027209246542848398, 0.01531794977564005, 0.240542598102776, 0.7596825260658513, 0.6914039379483994, 0.7173036065320775, 0.5317048926357799, 0.7900798940346032, 0.47558250705400873, 0.43140919042029446, 0.006624543162651486, 0.10685220449336275, 0.02099659947815813, 0.5417995639525759, 0.8131460186438586, 0.10122039633826663, 0.47316976394079624, 0.08650257713109899, 0.5785365363729024, 0.8921250150145295, 0.03926862909827877, 0.5963595868324929, 0.5525448237680127, 0.32775234214947824, 0.5580311564883518, 0.5647264840758505, 0.9637602690673241, 0.5004588681439911, 0.008233208197315878, 0.9131174631834843, 0.7228242118599889, 0.46011176280499877, 0.6832861096429752, 0.36761886948973943, 0.9888457755905448, 0.32008849008322426, 0.12964271829216167, 0.834250831696058, 0.7921133763199811, 0.7088284502442913, 0.6445253845709896, 0.9757803908793508, 0.5958956780884561, 0.8517141963333277, 0.3867321041619475, 0.933646823188871, 0.5517153496071622, 0.6064114202369612, 0.05381169728787194, 0.1665464501399011, 0.7188102443965307, 0.03341989673273382, 0.49499423099274154, 0.24257111116569807, 0.6835386035994174, 0.2538157229731184, 0.15753291274024483, 0.34072935511982405, 0.3195146633356625, 0.8511823281209047, 0.4461198295997485, 0.9259272250881303, 0.4691039267989945, 0.2408756672628607, 0.9411203555036771, 0.5540495686734663, 0.9088247039656665, 0.24239076588000175, 0.5785070541835289, 0.3334163393503512, 0.8976127973908765, 0.8397523142250739, 0.3761085760990982, 0.05313095725491579, 0.2607452849893952, 0.9392688961636607, 0.5013323863257974, 0.9046928310275727, 0.44188844270745653, 0.8359912018845598, 0.0822785264788175, 0.8737461017188949, 0.5461114455167173, 0.23458332243804225, 0.354598828580427, 0.17074144352596876, 0.652880039149025, 0.08674833780617708, 0.9433128679469707, 0.688610349741941, 0.29791472890076676, 0.05702280238702284, 0.6504621333364767, 0.6272505494004752, 0.6025390029659357, 0.40241964671223396, 0.9457134788906609, 0.8499828828747102, 0.18874303465998554, 0.38265519286797, 0.3839713919094293, 0.39623883311327335, 0.507783171844135, 0.2159221921031832, 0.3383099360285574, 0.009235637470865199, 0.4350184977393765, 0.2827485430683232, 0.21949116903208565, 0.5887193767478403, 0.3235558510240778, 0.137034251626184, 0.4324954521609413, 0.5063480657717252, 0.7087781196894043, 0.9695436451232501, 0.6244514168327856, 0.534911067305013, 0.11123425487237404, 0.4874933865585298, 0.5869751368421979, 0.9886124565976541, 0.895544757837733, 0.8736215098206865, 0.8338167978213771, 0.7889393112040557, 0.38017432689403385, 0.38589852409526315, 0.5050591878790863, 0.25109960441872625, 0.3513171415203168, 0.8613864643311907, 0.24625770971407268, 0.20160456083689404, 0.41129704655919896, 0.019888400775907922, 0.875684711714011, 0.26178602387477823, 0.27146811211289, 0.20894847792573257, 0.9532003942984517, 0.6971137063522846, 0.9059634199855195, 0.4401591098507093, 0.01795931575255738, 0.3156566676032445, 0.020849147083099928, 0.5324972298270672, 0.9825763272511439, 0.29102036181761004, 0.03851503672095169, 0.9700768884098047, 0.2928766518767334, 0.7396726161195039, 0.11705518788264502, 0.2064290881156181, 0.885448570732786, 0.3608795153631795, 0.926213206265405, 0.8005651607912058, 0.7468219392837232, 0.4745352229453357, 0.4295922286919248, 0.3918061341334991, 0.21617368663594672, 0.10724936361729775, 0.7703147080282404, 0.22351682233434744, 0.6641192981124071, 0.0414143720617377, 0.9640355474055853, 0.5963444792374569, 0.00032576302701692317, 0.05759281353769996, 0.1348350085635298, 0.9377182381070673, 0.3509626613109743, 0.611345075498055, 0.19680647255566963, 0.884740330637731, 0.09306291499684138, 0.3184543304085907, 0.22669912803822467, 0.2313644701578511, 0.5166488952792366, 0.8436555064781269, 0.621279780741898, 0.6363668512929629, 0.8783271403907555, 0.8514132706625926, 0.827000147149191, 0.8190674600844177, 0.4174407512821495, 0.47732917335211555, 0.34164224909308405, 0.11176172250866745, 0.5619264977667451, 0.2998048892748941, 0.8782580113637876, 0.028709689237371938, 0.5737998865292607, 0.29895815732751985, 0.5210463785967583, 0.2629070567007913, 0.4034693081517102, 0.08692303941134549, 0.6775110833178721, 0.9728437083447087, 0.3315476186337849, 0.29365418449414804, 0.08257032324159874, 0.9839761032407703, 0.964596905069, 0.6352606890928622, 0.0779268074873748, 0.4804084418422565, 0.2859898228427621, 0.6882206128169568, 0.06794141790154729, 0.5459718775781492, 0.684403524954966, 0.8977701651948777, 0.23049289195691436, 0.3121148858081436, 0.7013666863671739, 0.09449449022911982, 0.173557023555454, 0.7612665270325496, 0.5007091800644236, 0.19048201710756119, 0.1369013382062383, 0.542581138677758, 0.5473320075870957, 0.7355024033867158, 0.8952954213484605, 0.4290925298134547, 0.08528902496775348, 0.5151435907985005, 0.2515577179564804, 0.6380966397994302, 0.1539732886463263, 0.1857156364463718, 0.4475982103370326, 0.703556244196847, 0.7668627495264866, 0.7771115684144717, 0.19842515945648576, 0.8524290693121767, 0.6032880069677579, 0.6096275954768208, 0.7817415707442399, 0.3641611905873149, 0.8906932714831536, 0.8124175227970734, 0.7164991708784773, 0.9581985445955595, 0.60220506974975, 0.6970748647959257, 0.29345481682203756, 0.032845128302094295, 0.14508293497014635, 0.23059118521943367, 0.996903368983305, 0.7140268534044998, 0.5464022577479941, 0.6075985633909603, 0.5243844313750604, 0.22751203875198844, 0.9875323576741843, 0.4764127368024498, 0.0815070809410211, 0.07516088937063392, 0.08436110819767584, 0.4069514509177412, 0.14827279891330147, 0.4554411973237368, 0.5026695518808091, 0.36792917904223554, 0.6206544293634522, 0.015440128666228126, 0.10269067329161896, 0.015163468995910256, 0.2969412928298417, 0.6085918034852696, 0.08025312949222818, 0.15179257293992798, 0.04315776888042311, 0.7677755031904019, 0.9381448304518312, 0.5140876763299803, 0.9514443011555282, 0.6407757657079132, 0.0765698599268878, 0.8476496982444982, 0.29742023288486263, 0.4278682864122032, 0.9807213380432217, 0.07911917475472163, 0.8512230995302364, 0.10464574549303729, 0.29640579653429244, 0.5330302554416567, 0.26513319106603617, 0.5904796810764913, 0.8045767818618806, 0.8366111498182954, 0.5803132778233024, 0.33546911180316286, 0.19755405967272732, 0.7739232168523782, 0.3431428162209841, 0.06943880657672563, 0.8424212560717366, 0.1792541652464148, 0.23923891139115705, 0.2695174630337248, 0.5983688408671621, 0.2166853566314202, 0.9555002941610525, 0.3733927328005682, 0.06773668612539918, 0.5897664723661606, 0.16220980649511318, 0.8217097211780661, 0.013322815612317407, 0.19994234068611894, 0.23980826687700363, 0.16567772272135473, 0.9225760341307798, 0.8495754373962656, 0.3747780614528954, 0.6370432578151596, 0.9768984204125892, 0.4204515151680184, 0.7005843204770014, 0.6892847660959509, 0.9545148748016049, 0.6143830077940992, 0.2094946748069053, 0.6137540635212229, 0.7907730339684662, 0.43928047555035843, 0.2404702909941716, 0.03525245664088905, 0.9468549780596774, 0.7018444589043075, 0.4233097335254806, 0.17055600084252887, 0.21479511489577663, 0.015803981578659143, 0.8413223905651063, 0.519348093484841, 0.677328794875255, 0.04102853537158957, 0.5973099425200125, 0.1961516047773859, 0.0062697185169774405, 0.12995538953415364, 0.5024906873648372, 0.9366413539188541, 0.2005732471901741, 0.2845429314469091, 0.7420525443666908, 0.32663474803099335, 0.41817090842663707, 0.34679822715136543, 0.6254450782613655, 0.5617918392055117, 0.8493672841886342, 0.5678823903181036, 0.5414854471001395, 0.07595259068167515, 0.05992393753186531, 0.43950385738819386, 0.22426024207450634, 0.3440795103112836, 0.543614736931006, 0.39840127677842285, 0.8380022094986134, 0.42735989849616896, 0.21116213301339326, 0.10688135855039405, 0.8122754674795016, 0.24349142326505413, 0.7548582735244727, 0.32867610838513206, 0.9288904160700249, 0.9209177539290534, 0.8842602740791992, 0.8279493007772021, 0.30075977066974824, 0.07280702774796677, 0.11864651501493295, 0.6688470229861069, 0.03724364818799586, 0.48612155851759253, 0.6309638611431445, 0.4942769924580389, 0.7984005800249495, 0.6556850452872549, 0.6973321309187377, 0.8105546372590183, 0.5271401700450064, 0.31988416310121603, 0.11292485612467362, 0.6897767445279341, 0.18083999759778802, 0.10577005826134867, 0.02511931159870806, 0.6547138599790717, 0.8680967675529965, 0.5719830697041671, 0.7644132002714386, 0.7696055721073414, 0.4588595172180936, 0.03628478642533983, 0.8715479674408582, 0.5279191738220554, 0.7464273424343992, 0.34195259909108366, 0.47625196882372234, 0.9063949033141615, 0.6451078418202955, 0.010016678965625081, 0.5633772179641451, 0.3040492111100356, 0.04602006615957521, 0.3639265456872167, 0.13654018444855898, 0.6480557055009035, 0.4445476879765782, 0.17204731875768708, 0.7040595552109383, 0.3198017362250478, 0.82812696432128, 0.7595605039974195, 0.218581275194754, 0.9964171235689756, 0.5783764464966217, 0.7050543348500834, 0.12082311647408495, 0.1617173102063515, 0.21358993038707508, 0.3094097996762023, 0.7661823190831037, 0.8518447945034651, 0.2964770449576728, 0.09779437868900487, 0.3815727848325584, 0.6554275411064775, 0.29164952428811597, 0.6161379450466672, 0.35509282781577445, 0.22558271275348163, 0.7371844681372586, 0.5944039305145205, 0.5003711575045766, 0.47049432476265973, 0.730610739466964, 0.0988134281342925, 0.16190754148570252, 0.8531650549659385, 0.7910486502112972, 0.7654902688364232, 0.7264305760700777, 0.8622773323691552, 0.6651306024752726, 0.38696232353989524, 0.6380258212742878, 0.31873156785888435, 0.4903899038977766, 0.17016070510187253, 0.08357688777509897, 0.2898204855944452, 0.39949727107717015, 0.18313485335274593, 0.3894034077267524, 0.18318318558418012, 0.6009342776632394, 0.34872036976469056, 0.6581115690298905, 0.33150890354645746, 0.0496414017443747, 0.6261616029903583, 0.9412282007497498, 0.9354433265928807, 0.3343757259527984, 0.17110105275028809, 0.5743773228256834, 0.631282326851356, 0.1265223154947448, 0.05956666006745148, 0.29275659742335025, 0.9638479862044448, 0.8835168473733069, 0.44233475395862565, 0.776302788765977, 0.960790521074214, 0.6418119681054083, 0.5297743900364406, 0.20908914378335974, 0.2112387646466073, 0.2409200625286152, 0.9658210624840681, 0.7194427745114023, 0.8961510058897204, 0.7158726271323808, 0.9709478427129915, 0.71641934291295, 0.6978598889198826, 0.562433685892602, 0.7584211186028187, 0.5285173957402748, 0.5281476200616488, 0.2433402131975656, 0.6416443509917007, 0.9919156121101268, 0.08325553077154091, 0.844919711577578, 0.21736855876623884, 0.5134126025348843, 0.649945492330081, 0.507371406922281, 0.9612080916546023, 0.799559489036482, 0.38784886231871973, 0.2514257805169353, 0.5147929132519722, 0.7359179457042792, 0.393962295971405, 0.7215352480207046, 0.04692795757302448, 0.5262940246059401, 0.965670867852144, 0.5821420648305368, 0.6541083154130035, 0.28200537946886706, 0.8515727218320565, 0.23394206114530003, 0.8440952963960885, 0.3420720114566579, 0.8598142741233008, 0.06844682464594498, 0.7764638527281771, 0.6891653983619935, 0.5906360377441091, 0.693767863223038, 0.501631277360539, 0.1259357782951196, 0.8811637311755608, 0.9296187432293417, 0.03430909767154722, 0.5885428138086796, 0.3523586217223946, 0.5141633202186399, 0.01478331280322187, 0.07374690088781022, 0.6008897850962397, 0.45508763695770293, 0.366143275617999, 0.4007635264016053, 0.6256287424398075, 0.3876117061535449, 0.12617695049817323, 0.32648577285849867, 0.2393650854928122, 0.14525875946788858, 0.9304786362838342, 0.22634427890693198, 0.5872569341864483, 0.49786461824300887, 0.809109922707037, 0.4908787429728545, 0.2971558348741945, 0.9202443725906043, 0.4708581261693834, 0.05047996039399072, 0.8085789561361016, 0.0033775962984968766, 0.8378561958865722, 0.8831252690408297, 0.8832717731022176, 0.7446755804075358, 0.33093560300141756, 0.20094491008482307, 0.3588281454786427, 0.32285719792862544, 0.7451138552440213, 0.14248586173611089, 0.7926058404533078, 0.8841408961254881, 0.43399243441758395, 0.050645097031216224, 0.1338309253389658, 0.3166573015111728, 0.6844013834047146, 0.5582398424106365, 0.19639199836219712, 0.8806278774744208, 0.04775053841211363, 0.6207222172034218, 0.2126533800165451, 0.6985288696086546, 0.4872620844632072, 0.38223701361720486, 0.609888972221702, 0.7026030762052993, 0.8950892592987694, 0.9686700539177381, 0.42344736369788927, 0.995783156210629, 0.5751781192031303, 0.44121798802045287, 0.7205876863304265, 0.9391234975151154, 0.2102330928534104, 0.5232897972052771, 0.3526268668321072, 0.9424589210795762, 0.4684433770462869, 0.2938901162459294, 0.5546783052046197, 0.17987847012488312, 0.9458445471073877, 0.7989491359988972, 0.5850240381583725, 0.48744171318427953, 0.6221944870992951, 0.46489192369226817, 0.4185053947197217, 0.13874959872689918, 0.9837782839018144, 0.15547885847650267, 0.031368698829014496, 0.14915857339116922, 0.1264875125442777, 0.6197256944016849, 0.8282624133666818, 0.7391256673104295, 0.7740924967553946, 0.2641937528674697, 0.3215436705782915, 0.5341497193875369, 0.0040252106313000136, 0.7983273280819632, 0.42029374880025616, 0.8780664298021492, 0.3402349161445176, 0.1898755944354369, 0.6001491642575865, 0.6778463508273469, 0.8305032695240993, 0.7387814919440702, 0.7190797644683271, 0.8835005631864289, 0.8054966845612681, 0.8854776989211987, 0.49612141649228214, 0.35216950999292207, 0.23621763753759806, 0.35939180325653164, 0.836430640027048, 0.2685592614020714, 0.8500592818896662, 0.5519154210321693, 0.1281922490422176, 0.06626489412482861, 0.4943884264671894, 0.9340699457518234, 0.8799353758955039, 0.22460624607326451, 0.8937286575037703, 0.23008378783339944, 0.7386036495961216, 0.40421863803923963, 0.795152586222173, 0.055833935043233085, 0.5845715858837066, 0.9897177031962151, 0.9905302982165827, 0.9596811901141332, 0.6979122440459229, 0.29108276423325186, 0.6682494989534188, 0.5499315391981521, 0.6224334711333187, 0.11226274018948956, 0.48733213291776956, 0.887085706303916, 0.7056629698221989, 0.5655546768425956, 0.4105407543749683, 0.12895505212239988, 0.5890961544353817, 0.5778132175626944, 0.4409406759190033, 0.75867006830884, 0.7523397188233624, 0.527472315336094, 0.969672806413678, 0.2394692485901424, 0.41812898416021005, 0.8677863194061313, 0.15590500040576416, 0.831963739937221, 0.8896851243689841, 0.48713367625648896, 0.8130921353370143, 0.20963918051728903, 0.9244678891191762, 0.46966604449107063, 0.579149925671282, 0.6743628448529819, 0.23451845746220412, 0.7466847660417775, 0.391001983821309, 0.6538754715696976, 0.4615012769017248, 0.9377676181245355, 0.9491675354663268, 0.05052363368814217, 0.28390908597093845, 0.8183874505567702, 0.38543395956917315, 0.26858281977863985, 0.6392153388365647, 0.22887880767960878, 0.13644806044088376, 0.167587051612752, 0.8718839872689222, 0.6559717724307271, 0.9251067684415579, 0.06990914454920516, 0.5034640312497337, 0.5013076850206055, 0.7717294275008427, 0.3306092938951103, 0.9986186396878293, 0.2035067252166245, 0.4857108461400149, 0.7301867962151891, 0.8603827869142012, 0.41607976024504234, 0.14543979623993353, 0.24986808624527845, 0.8518435288618611, 0.16583027167137498, 0.26630399296914486, 0.2094887667292088, 0.2698471225304603, 0.4294969362240938, 0.12421028850091864, 0.5172828650569337, 0.2792594547636793, 0.8039707526453396, 0.8027059302843155, 0.39949250067778885, 0.04208102326762064, 0.6493345143904136, 0.15722527973254075, 0.8840554396535564, 0.3728498153822032, 0.9729287610957722, 0.7359173630256405, 0.48074366583962336, 0.6422662945681412, 0.04312589553324786, 0.20546291298784636, 0.22943639894890788, 0.7244921625489029, 0.7032849770842924, 0.9865104182765432, 0.9103658416923569, 0.7639586222414887, 0.19371354249069217, 0.8874634147020038, 0.519538039677244, 0.10538261162636964, 0.5398822865493209, 0.6241623772444894, 0.7589325100642482, 0.48214847884172085, 0.4724791737229119, 0.48800175782053024, 0.5833304396342864, 0.7006271893758288, 0.7605323272374044, 0.806455429269515, 0.9493614975208688, 0.1413773857944206, 0.07714424812896614, 0.6638952078911184, 0.3857321163325369, 0.08046988083065976, 0.991204058533467, 0.9374056560421572, 0.556728157190655, 0.9771817120283296, 0.27541630326710465, 0.005146815194777221, 0.16841371636410674, 0.2503051083358384, 0.023120626516520915, 0.449515835483693, 0.1455111998190729, 0.9237147951376047, 0.7549402473173545, 0.8910507255063151, 0.2181033764675262, 0.6695649417369641, 0.39023252436127176, 0.3056219734968382, 0.7830062743808217, 0.2211189480527077, 0.5275464326323508, 0.6825488169507075, 0.5540142155206008, 0.9676159603279827, 0.2588339382028777, 0.3415262264678389, 0.8268978189146996, 0.739718656690241, 0.6186378232095143, 0.23993343238269738, 0.46240402745559617, 0.131666449657584, 0.5515999590910257, 0.4954134937877559, 0.10504577970245632, 0.22783547119025505, 0.07603704088554908, 0.13459028458226674, 0.41422163791855326, 0.15114803866664073, 0.34779088953069504, 0.5497424103806892, 0.6299660213595425, 0.3945009204561891, 0.6218681857283719, 0.49805165210862345, 0.5483917613969087, 0.563114391006557, 0.214282079860027, 0.3257468566357794, 0.6687235569951967, 0.6567727844592294, 0.8655073384906574, 0.45553984700746053, 0.8484727547627134, 0.12745038797870378, 0.7570133137494108, 0.7866880419140133, 0.6561719210467561, 0.6115834726324461, 0.19268027491263107, 0.21949169943589864, 0.0021835569105005392, 0.4836238089724795, 0.3132379788030558, 0.2755510112780075, 0.5367570544631642, 0.37898054086881505, 0.25231798687035223, 0.7356090701612248, 0.3855546751882303, 0.05419937161400601, 0.5771402420930211, 0.06901883372463047, 0.7389251498611187, 0.2354254979231436, 0.12715140226240396, 0.597647547746675, 0.9257713493525752, 0.014222004234462626, 0.18027176272878798, 0.17750742865196356, 0.48847818687235345, 0.89605781077376, 0.9674192283326282, 0.8702891571510301, 0.17140908918377384, 0.3489816474812989, 0.21634035020867626, 0.6526093819618123, 0.23974249012825755, 0.6645119754125621, 0.6158025842993531, 0.34728413784387224, 0.614104079623674, 0.9223348436311207, 0.1691604750813117, 0.4644488648277778, 0.5433276173770782, 0.5774792042703888, 0.37503896462277264, 0.6698841424708741, 0.1655345874062174, 0.20064189172088998, 0.8787630592009681, 0.740963351191044, 0.18738418238312793, 0.30674530123907895, 0.5493610555830722, 0.8973843163827346, 0.617142252785327, 0.8940984297603277, 0.7516765245950261, 0.06261524901748194, 0.8811387950890462, 0.205881158051069, 0.5166067992948751, 0.5796213990184897, 0.012784999546325837, 0.6103794639880136, 0.005096072042229283, 0.16360686065783658, 0.21291828903343213, 0.8278661975212714, 0.668681077497476, 0.8837657933192906, 0.37153073497376876, 0.8321645486333105, 0.13638622192474203, 0.25566130756854, 0.6473606209411075, 0.7377522715023068, 0.7541021968364529, 0.8357749535235386, 0.7456231642603187, 0.3338486673371397, 0.8862421825817257, 0.7583987760311064, 0.19064969356828676, 0.242924315508393, 0.3534597682176439, 0.0918961543561223, 0.5954630160842695, 0.39985144716215026, 0.0985583146578195, 0.29166877468564134, 0.7652616441449321, 0.0959772267667961, 0.7546602672158454, 0.2636849154411278, 0.06956636809013739, 0.4095461896828313, 0.3822624480902461, 0.28907049079939007, 0.4424939406510091, 0.8412601179142394, 0.29166021210179627, 0.5405706157448056, 0.8873811396705715, 0.7076703541511937, 0.8959490233081647, 0.7804495718442109, 0.9209043193280484, 0.19566557446183153, 0.8085961911859586, 0.32057679670364725, 0.12189096673230837, 0.26473675989398004, 0.996629730927226, 0.652548786334173, 0.9075290277802945, 0.4802252392747707, 0.10779965292920712, 0.4054066761800629, 0.17330367182750972, 0.6096458664729524, 0.5798044779596909, 0.872703786037611, 0.17769553180704267, 0.6712507817496286, 0.5816981470279134, 0.07448701842743422, 0.7742141516056278, 0.5609798783301355, 0.9212181017004285, 0.27354334468042285, 0.060049799538552606, 0.5807922937993397, 0.9027411453522435, 0.7936661335019406, 0.09273493131472499, 0.6200412702613728, 0.35529556980971366, 0.0933884829245043, 0.8011910925342979, 0.8856129084246106, 0.5982123576259409, 0.028053739675490408, 0.36801177677912855, 0.15324761311259505, 0.19625512528600997, 0.3490375679764771, 0.8954704199061206, 0.4992270415928295, 0.3855763822318714, 0.8701777267092509, 0.8957514762731625, 0.8260499455480201, 0.5787364801339311, 0.9455651034940513, 0.4236325954612683, 0.7885191319871936, 0.11265470628235752, 0.9373392045772332, 0.7522189865280404, 0.5814389968184337, 0.33740972281117654, 0.3898500726198344, 0.8187579391512357, 0.464228690644809, 0.7386098231187797, 0.7870214398333207, 0.6096311176459468, 0.38708134964679464, 0.07205113130750673, 0.6338669142030066, 0.5699560960020534, 0.689485551532759, 0.2823074432983642, 0.6364356587618056, 0.16526808895445344, 0.08565142875036769, 0.645794132217499, 0.22340577154801444, 0.6703925461586239, 0.8368333338080013, 0.6443011912694613, 0.6697007632746084, 0.9476557015003222, 0.4444850665642158, 0.5241759847527117, 0.1561431110825181, 0.07550122041145502, 0.3570740774708877, 0.9655642633584276, 0.7768888645136565, 0.9542591993094416, 0.06537037259879463, 0.6244902707110851, 0.619335704927162, 0.9024727399270388, 0.3363927692719417, 0.8340553635826755, 0.39458753751179954, 0.29280597218899285, 0.29280151563985113, 0.0023619134490885374, 0.036164389869845937, 0.6338880628939046, 0.08180223658834529, 0.8097360023824277, 0.2948129029100992, 0.6745822965184326, 0.00668946935004, 0.2141593341913347, 0.10834281616655295, 0.20028147367340476, 0.02919486252302861, 0.8275058057243686, 0.14220912348912718, 0.6494289915814013, 0.16866692031776653, 0.8467359167534151, 0.00953142527471984, 0.649615243939638, 0.8111062048998361, 0.0041109823210867535, 0.2766170683786505, 0.9425521933946843, 0.45022914524978563, 0.6439886356559811, 0.9359720802259758, 0.8091212583918839, 0.2394861050549778, 0.19216059728221646, 0.08833106056260387, 0.3967525844210681, 0.660530811057208, 0.9028932778584909, 0.038576696949704226, 0.2881754330313526, 0.377862615838773, 0.34666458169725156, 0.9384985944515373, 0.01674451817158873, 0.4730875502376053, 0.9736795684317692, 0.9615005865111602, 0.18419355085875677, 0.1015017264929916, 0.729049027418257, 0.7912470031735453, 0.9732974539737105, 0.3024315499162922, 0.3047123131178312, 0.07167484786396039, 0.08329515475062188, 0.012203199038870904, 0.5608236383142611, 0.6920618822140845, 0.8095692585838979, 0.6456886089041037, 0.8956088161237685, 0.3710937215887009, 0.6404408266676882, 0.5390560861940349, 0.840548664985671, 0.5393434220055948, 0.8483093847917064, 0.6964580612142962, 0.2787613190958763, 0.07836622434053908, 0.5527624513089565, 0.4511954710934898, 0.6322303115731569, 0.5293147692553649, 0.4797456112485896, 0.022772621439471563, 0.4315028392758812, 0.8131063302519922, 0.835499462708823, 0.5954735929903859, 0.6499520035504176, 0.05338546770130992, 0.25987643775558844, 0.7854030318948674, 0.0453186845636645, 0.37732247264323415, 0.24730619642092388, 0.9832938258449161, 0.9595452798656801, 0.9670633194992989, 0.04985201664670402, 0.49379417267049563, 0.32464719033751355, 0.05908443060987556, 0.8605731642912389, 0.7588451327435463, 0.13682080278644893, 0.9238049022655254, 0.36103458382292253, 0.5691471759361028, 0.07679617119683702, 0.22554866316988564, 0.09019253585688614, 0.6829468282654838, 0.5322399347649318, 0.7855180040164972, 0.551441074662128, 0.37267763228484374, 0.2614767444463608, 0.9845275285642371, 0.4809313904914674, 0.9735731762954789, 0.17294585753831992, 0.24838795395334812, 0.023193114474997056, 0.1677125151942439, 0.5980536563961926, 0.5094414515754091, 0.5848334887699315, 0.8434228252082491, 0.5081123729304549, 0.8334310703822422, 0.576281011375385, 0.727398688422103, 0.24250344784585076, 0.26248952658702684, 0.7857180015568903, 0.9586489749249053, 0.6242176521314566, 0.3125571475935296, 0.904140994234653, 0.0248786103272427, 0.5120182640408835, 0.29296668216215205, 0.018175546421433597, 0.5830810683650586, 0.31239383484399397, 0.5133045603102073, 0.8239687413547585, 0.46903947330926243, 0.3068865751767762, 0.8957272222664127, 0.82794151092707, 0.921864906207686, 0.6147469688809836, 0.6070393815969863, 0.9125018173596807, 0.7180590457979998, 0.5221858544982311, 0.7340443908857213, 0.6038863399482572, 0.8610766999390486, 0.061324527421735886, 0.341826990505229, 0.9005398881117763, 0.7230753909523456, 0.14739802123142443, 0.14209125041580228, 0.5358758818702276, 0.7189664771481943, 0.9300285770261746, 0.7693915123560771, 0.019251287073499546, 0.9248839830120014, 0.12621894400507894, 0.6867737288479482, 0.032680230880641314, 0.4069136584337537, 0.6253620375462905, 0.484710004813795, 0.8819106166842692, 0.20096370427907773, 0.8767716072491476, 0.15960265132057694, 0.4072239661601368, 0.18500455513199598, 0.9876394034684657, 0.7732073919080598, 0.9691301348452812, 0.8316759940377845, 0.3390482084822115, 0.3068363628806766, 0.89429028538344, 0.3507965907102011, 0.8025229912756378, 0.32891518374725437, 0.1995050643077776, 0.11345689929296021, 0.17715025247364635, 0.6137519414216935, 0.7505328581926496, 0.6206097253399693, 0.5581998354828086, 0.3890985099875842, 0.6041862610103657, 0.6887317822347351, 0.23649827137390378, 0.4035361076165067, 0.907810064530496, 0.5512149530609041, 0.6006771364583976, 0.5364266948952668, 0.18812340634434443, 0.24008019293269933, 0.12330343847850334, 0.7923882639552893, 0.788794433348703, 0.09001757626753426, 0.963776828369856, 0.38997933298417775, 0.06913317435072419, 0.46540111757705316, 0.0672872355426023, 0.11970712197334388, 0.4837497438343644, 0.716006175723687, 0.9196124482785273, 0.2806521491767219, 0.4924204469842667, 0.575221183532452, 0.7082377001353426, 0.3893620091624832, 0.768575683521727, 0.1666110102015781, 0.8217487545712984, 0.6846048419441862, 0.6484204249873066, 0.2887921814417467, 0.8074589850504662, 0.5721180734009176, 0.4948531394053586, 0.8266828036249912, 0.6002156077046021, 0.8701953052395094, 0.35966990082375916, 0.1391258762896067, 0.16570526960164822, 0.28651830362544173, 0.4209468159672606, 0.8635118930924496, 0.002105787324557462, 0.2986969731657273, 0.6324681441508591, 0.5144504246929688, 0.9839651495710753, 0.925487354312196, 0.38684611218736664, 0.8108566785379234, 0.12860817956540105, 0.35021553632084623, 0.22879031476930356, 0.9327602696109594, 0.1171975798340954, 0.3749003812688314, 0.5585917445219102, 0.47648012276778173, 0.14792193396090836, 0.5579323016162466, 0.9257747733243183, 0.6454751055754582, 0.08902832364082969, 0.41407476566965784, 0.5030668155257981, 0.22392580321263844, 0.7043137117556717, 0.5889609256421384, 0.07784725750424648, 0.21837353609550036, 0.9775765306028937, 0.7514452960820399, 0.21500455747244895, 0.03290953413354536, 0.7309979480137581, 0.6631765136220552, 0.11501792606472094, 0.0638901299986917, 0.09142430319850059, 0.04663221593976219, 0.4325415576671975, 0.20250946390595048, 0.7764686233338783, 0.4323002886695487, 0.30075383252854215, 0.4316586449563681, 0.059885683881701346, 0.044153467557825454, 0.8935041504972123, 0.0621708142544537, 0.6732993069806318, 0.2774134661046056, 0.8541275762303439, 0.8216988069874015, 0.11339178565233443, 0.004412879002477221, 0.8318428611376332, 0.8123648883815588, 0.6370638647189433, 0.10654390706417594, 0.08015229654888001, 0.3788005682981507, 0.8812993715788957, 0.5619597016662584, 0.21920900354534312, 0.6483033859144742, 0.10851351594888248, 0.2679636649610744, 0.7775006389844328, 0.10223863685007828, 0.8233178820297202, 0.9015206721860061, 0.7421818127428116, 0.89120891843561, 0.8662696959482991, 0.5238487920744104, 0.13031015249773115, 0.8122146489924141, 0.519649573401864, 0.6062902919061554, 0.9289469874268724, 0.9154548321372453, 0.34181309802928206, 0.22391040221784797, 0.07534484858417001, 0.6439959087282352, 0.9557479018614742, 0.6948757339995211, 0.049963193467885914, 0.60894336917863, 0.8375203024627258, 0.6308213194733441, 0.7411289925447127, 0.48738162529546436, 0.4487463792772949, 0.09463960166913454, 0.4917098078464722, 0.084679545424733, 0.8981172106185014, 0.5643407456087915, 0.10280956965060795, 0.8446685996472796, 0.005672569156133678, 0.19430454370552486, 0.41542539803568546, 0.16139040859770426, 0.8148232444632695, 0.00219476245394179, 0.558126251727518, 0.025490801311942368, 0.6243556794150557, 0.15263981875604826, 0.46113324845654036, 0.09439774163074055, 0.43338363177681083, 0.8735631903092378, 0.548737972500742, 0.356577731866747, 0.2216284515060788, 0.35808441524217993, 0.19946198866894305, 0.7972599484010688, 0.3969494681372636, 0.41303112591424085, 0.3629446841370786, 0.43815260135519096, 0.6081897376303848, 0.06061842189676503, 0.45448279770904665, 0.8651442426808169, 0.875784558896079, 0.26619078665105345, 0.6687528123676825, 0.5293380989606575, 0.3606973326886752, 0.644668779378844, 0.5283358938106392, 0.3761013949497658, 0.1444075025269388, 0.2964504848233692, 0.8260597276896579, 0.0010408844952033425, 0.6327646232036179, 0.25519377871235494, 0.7334459062910789, 0.8352962334396864, 0.3712143547332777, 0.3857487965639541, 0.8908591275975474, 0.1632486684334511, 0.05585055487883728, 0.29876702859262105, 0.9212755251623836, 0.4877536995687354, 0.16312621646167935, 0.06198923668777623, 0.3408401771661087, 0.3437149336859253, 0.965569472171775, 0.4071605953291859, 0.1319173782542049, 0.9210643219714407, 0.33341408227859104, 0.26794225996066756, 0.7271841327337942, 0.500512280771342, 0.532695588261878, 0.5315885920567364, 0.04016188132390264, 0.6567369668594921, 0.6876916189734837, 0.04370932251268134, 0.6237993092787643, 0.10145884299695607, 0.7961359183941386, 0.6987872082606429, 0.35586250958042254, 0.035145325217329826, 0.060568669216712334, 0.5468054342866828, 0.7393761292911065, 0.15670465181461124, 0.8885322749284394, 0.6505310431462754, 0.08900138402539315, 0.517909975243018, 0.510026910570548, 0.9996659700671005, 0.6598015799757174, 0.26010373975449186, 0.6553309858599665, 0.7059001111288336, 0.03451288281714926, 0.564822482703087, 0.7950942413110569, 0.9718398887831793, 0.38896727150691845, 0.9549654767605698, 0.7610265087207583, 0.2466482848656565, 0.9826401165829733, 0.6724416529809022, 0.8553310159247016, 0.59012229030453, 0.7893202985537364, 0.3880540541277854, 0.5397899758006192, 0.44891113982799047, 0.7940119733291549, 0.335713647962803, 0.1255635719357745, 0.2993241079455562, 0.8339833103857486, 0.8587951659765223, 0.5168356364606572, 0.76857854596841, 0.13921789802027074, 0.8792955541141682, 0.3147070194056061, 0.16839495249502945, 0.9833910146930196, 0.5527135313737833, 0.7535831659267808, 0.1206764827757475, 0.5817707669612704, 0.75484924910893, 0.8564088753374455, 0.10027374478199413, 0.21901293916668552, 0.21372659786785808, 0.2610308811511607, 0.2077100158056363, 0.6808735502500124, 0.9364906709807392, 0.3994579834368802, 0.7920285370885659, 0.8767103114330838, 0.6662238298581796, 0.7754728851504256, 0.9800903040300273, 0.7277460129131508, 0.3832250915755193, 0.15417868149594816, 0.19094404961675926, 0.5087669646008749, 0.7602254425791766 ]
    uint32_constants = [2158666988, 41566169, 2242813059, 1713905491, 2606451716, 3868193376, 953481666, 598543991, 1620112842, 1783380745, 702486269, 3481835270, 886505658, 3711857897, 1912586610, 279198896, 2990750274, 2293739987, 3457210255, 4018112145, 2763371318, 3726406775, 1096023021, 1186046627, 1116027162, 3883451390, 1413212609, 1922870598, 2144350207, 2531522485, 3583052253, 297082084, 1346016468, 1498830614, 2975560587, 3864573242, 2513414439, 1926180840, 1507012395, 3810784083, 2219900517, 2630495414, 3443916083, 1257987869, 1455772753, 3493511787, 3565932205, 3654154348, 713252439, 1231100340, 2507469338, 1255110123, 1473099086, 2898961517, 3329252557, 3210151383, 4101284308, 1045422807, 3689845597, 3559599122, 762352229, 992604139, 3516511433, 310565989, 2350549856, 1787529558, 191559108, 2969207420, 1959453500, 2869200955, 253142935, 83104345, 1326000413, 3127635973, 916430015, 502338120, 1279770172, 2684782390, 6410385, 301927079, 672926313, 1327095627, 30026292, 4272216602, 713858743, 1020363043, 357184972, 1066014934, 2467663112, 2391201341, 3047502643, 3754235121, 3028204666, 863098688, 504881819, 4257903901, 3936895409, 3484823576, 2920531816, 913607873, 1851335489, 2729323520, 430812535, 454713344, 3606777711, 323269189, 228087775, 3715774926, 87304774, 2724174865, 2741710073, 2363411441, 2984351010, 3122302154, 3761742840, 2637795393, 1498606255, 365444637, 4018582963, 616621843, 536217682, 3526534505, 2151710982, 4288448152, 321129786, 3618224247, 1760120453, 1319764869, 923677380, 1980023747, 4142526672, 1171973909, 80415349, 1504514183, 1815926859, 1098670025, 4286748890, 4199827595, 1735659228, 1598829280, 2720631255, 1366940606, 2727212117, 3766845735, 527239947, 3493602309, 625302532, 39812166, 870083950, 1786903320, 1880636901, 4093266999, 3282335302, 357434705, 1328655766, 1547886936, 318515014, 2314429322, 2141252918, 2976923311, 369989193, 3283646902, 287922603, 3777945103, 300919787, 3584241478, 131942094, 1934539312, 1935955185, 2520746479, 1019305967, 1793998806, 2609753108, 436646368, 240056312, 2228855878, 4038353379, 3584669790, 1651887006, 2404125598, 3157825810, 3221667529, 868172354, 66146997, 4022808626, 475819631, 4125130933, 1469148787, 904808754, 2163561042, 2071071076, 2424735571, 3309468947, 2563037901, 15047719, 4225844177, 85031320, 3153777246, 977619786, 3283632453, 578076009, 2853928610, 1041016160, 3196664503, 1496700517, 3311367586, 3675589745, 396535749, 2068790523, 394454707, 1187963860, 2943363568, 3636043126, 140250703, 2835280382, 3545386937, 2517461116, 2351103394, 2218750624, 638891508, 1510935278, 4238333939, 481858224, 123947157, 1193350485, 90689506, 3308396371, 1966200518, 947655450, 731953131, 4123495735, 2598767721, 380288531, 775781230, 3325334231, 3831585271, 934900884, 722596038, 2743507613, 986030440, 4056516429, 1473215144, 4256082289, 3320633226, 3152690777, 2340508503, 1592677695, 1294814188, 2248830908, 2165980709, 1115104845, 4065450736, 2887934294, 1599817958, 3283096764, 426517169, 1909580759, 944023695, 3547361356, 970009285, 376807911, 2201401838, 3057162944, 1180624372, 1893697363, 3011229047, 3926971963, 3741420086, 3789566068, 2069995971, 447946484, 1708268297, 2571646232, 1320924626, 2420220487, 273213642, 63841886, 854214527, 1419911288, 2643013425, 1021217668, 3769479382, 1421863155, 2086393539, 1903914849, 305952136, 3620996500, 1730535425, 3041968399, 2543371796, 2427288063, 2474673125, 720981692, 1775148986, 1140782432, 1240271140, 1401874616, 1692851142, 2794166075, 826915029, 735946224, 3787551975, 271025114, 1148636114, 3662011708, 2254838561, 195264874, 1642571153, 2628864601, 287639927, 4247575144, 3325145638, 2626612274, 1776447500, 4136639730, 1936450687, 1972169521, 860985845, 2925308600, 1043353575, 1634823346, 62013364, 3069122110, 4294393969, 3311229445, 1160185753, 2289687531, 3992653060, 2038702459, 1141845983, 4110130152, 895487168, 4205193680, 51526245, 2442642029, 1017197722, 2778708520, 781084184, 3313537175, 2924213803, 1429883128, 2328546392, 2223325536, 641884532, 1111922560, 2372666392, 368467430, 254384864, 2340889844, 960041935, 2388775929, 1477371842, 2305086875, 4271566542, 2911585819, 3783293085, 1388560321, 2381324061, 2879313423, 2201311855, 149670241, 1543000024, 3127174901, 101484676, 2263444653, 3856713647, 132620514, 1414705702, 3957504614, 10575878, 2134237362, 246539754, 2613514110, 2132075163, 3385294990, 840125174, 2528932933, 3925737388, 2443832533, 291967975, 2388784841, 938345541, 2158137238, 376923552, 2391755569, 3183922158, 2514008342, 1090063300, 2894045126, 2700022623, 1654621821, 2948785471, 1136077732, 220626925, 2540745933, 375321608, 2887774569, 1313420670, 472519803, 2920185888, 739350232, 574202953, 128585609, 2849069346, 3131161054, 3285949925, 661841087, 2342952145, 1606250822, 3058592130, 1414805631, 2666503285, 2385627271, 3861465726, 4229920348, 3703827984, 1496762829, 3326377974, 1978482607, 1167568398, 2491837766, 3627036399, 3717137080, 1414397933, 3698178328, 1636055405, 2246084815, 1533233764, 322578868, 4226203633, 1402580679, 127206521, 3634617231, 3559375418, 1618342189, 606523218, 621521914, 745863931, 3915798968, 1960416985, 1802163069, 1163417280, 349697540, 271961308, 4204276959, 1284440414, 1222311033, 2109153000, 3055887417, 4191198224, 3408167108, 1421633153, 2888797160, 3658059744, 95625730, 1427552733, 1056998492, 315284296, 566470416, 136890407, 4272337730, 1206540696, 2707458537, 3816668534, 3775659601, 1946360202, 2029191337, 2543085758, 3386524130, 3072383890, 1392653552, 839710844, 2667859584, 1434661193, 929671936, 2273163907, 3004864078, 1890026722, 1909212287, 3046571464, 2162748519, 2499462514, 2969929317, 214958837, 2750074569, 638119832, 3441133351, 2723485457, 3277269270, 3333715478, 3766535300, 3005043891, 2477286381, 375621329, 2877582561, 2047350808, 321455664, 1409879168, 1909809997, 2702241041, 4079275454, 2154649136, 3454715810, 3411931313, 1600074000, 3339798888, 322090109, 3170848896, 2972648202, 750136610, 793236930, 1904573536, 769191417, 2690323228, 3798140459, 1797714322, 4140517412, 775591934, 2713776145, 1920425104, 1552784780, 1431152812, 2835349519, 3715009506, 1572569530, 537975892, 2030190502, 3287012384, 3407729402, 1369006797, 2495698181, 1126974116, 4185099956, 2355779643, 809258994, 1907987615, 2857521463, 3790651456, 3186753495, 3456652606, 2788203457, 3134393715, 2450711152, 3739373620, 3914792714, 2219173001, 1192274059, 1467334073, 449441582, 3482726560, 2645016244, 4084213005, 1126485021, 1973888613, 3288340636, 4161824387, 415876046, 909194328, 2073740706, 748804308, 2571712981, 351609572, 1755708289, 1922853881, 1763344113, 169387514, 1354753129, 1121519667, 3947609031, 3179353132, 145048546, 1750424928, 1171152050, 1640962698, 2118876960, 3402840592, 1966991108, 850008765, 1841820888, 1145712361, 1297734395, 4063987854, 3158587025, 2630971506, 4158595949, 2750348381, 2091590722, 4067056253, 83283098, 3785170991, 2183827963, 274811911, 4014308921, 3646693204, 2819672198, 3430089944, 3505959203, 1175307952, 2923477860, 868978798, 3656546523, 3527376019, 662159573, 2956021134, 1882909114, 3521514112, 2794700378, 2793450123, 1377525281, 900992029, 3802075154, 1030766716, 334651238, 130152437, 3965336362, 3712928372, 293885426, 2527735393, 3749222267, 2163624535, 228133853, 1408566025, 1033977817, 3422834629, 3224939976, 1768370140, 3292433792, 3469081293, 3241409763, 3523922323, 2527405560, 2829759019, 445243388, 2297476307, 2263622072, 3828717731, 61331938, 932674048, 1896114890, 1608794907, 1714948940, 2095632877, 3667353762, 1243227339, 4243716586, 2849681726, 4146720687, 4131223740, 615933150, 2313039170, 2651049422, 2094377459, 3914650399, 3482443014, 3120835440, 1483512517, 981852104, 2978180335, 1312664588, 250297655, 3751554489, 2262627489, 2382270816, 848980143, 4281696160, 28744765, 2757119211, 3139452831, 1098105073, 2899751242, 3273912223, 3777797513, 1016280294, 1761734252, 1121133524, 1834556081, 3990715957, 831334863, 1407054552, 1561848194, 3885311781, 1100286040, 1729800347, 2702792271, 1240039449, 3696120292, 1953333085, 132060646, 883238136, 1908364952, 3974297904, 328580209, 1263185644, 3097261595, 3598253374, 1118191323, 4241105895, 1860286212, 2960050743, 4161486300, 2910270767, 2664872994, 2091639379, 794667240, 732930159, 652891413, 2744174160, 1451988725, 1735577106, 4032670716, 1939364797, 637321123, 4082700363, 2752566145, 2317883847, 3805352069, 362028889, 2440982516, 1068285473, 1488586852, 2283142646, 3188631285, 2710105631, 593658761, 3518900088, 1790648401, 1357055687, 2616680098, 81398103, 236114240, 1590240213, 1956597413, 2682758294, 3596038133, 1388641188, 2578546944, 4128922543, 2604973361, 2834769202, 1403490523, 3866866602, 3856236837, 213082863, 2598051127, 3215630888, 2702323815, 1825471041, 1475220004, 872539704, 915821884, 2206034168, 1860694830, 4227809351, 1779205456, 3823542226, 137675546, 3756600942, 435046124, 2842357559, 794207264, 3280117767, 1956525338, 1699475450, 1693192767, 2329514035, 552602476, 2864055387, 1529856935, 2525302499, 2847224691, 1232855034, 2988132380, 3802051754, 259846817, 2242868322, 4184014163, 2825321620, 13534986, 1685503649, 384385435, 1304163609, 1141547320, 1348176993, 1359003024, 1366067306, 1655431191, 2340918079, 1136617961, 2221954843, 155659301, 1885664703, 2545577293, 2067440331, 758485997, 1127703486, 1112906866, 2946885148, 2372018278, 780273444, 1459029787, 3534448768, 2886845175, 619835831, 537701446, 1262187453, 2403120953, 3467810099, 1381500954, 2667838332, 2696363531, 1694065466, 3886560532, 1742556582, 3803079711, 533031983, 2432838223, 1081056868, 3544141361, 3137627459, 1843582974, 3854340981, 1909579154, 115295846, 1658305106, 1100571719, 3750969320, 1879947804, 3880820583, 3585742593, 348290146, 2395402028, 4018307593, 307554892, 1109247882, 480663901, 3841337215, 3969132665, 1249511307, 247848238, 1226074025, 1158848660, 3367293446, 2356329539, 1998125859, 2892161465, 418274456, 3512426131, 4179931644, 1083763791, 2448369157, 3604925494, 1384264685, 399314487, 329491597, 2141135546, 1282874215, 103046312, 1406865802, 3078408480, 1335164879, 3164442880, 1367494749, 3729855894, 1034138485, 1193373705, 1295460939, 277998263, 3283810292, 1398615835, 1648971479, 342377357, 1404841455, 2793768216, 329677284, 3014874788, 3605511596, 1139145812, 3185034003, 4027818039, 1827030370, 2649145172, 2174231519, 1983896064, 2672618830, 3572126180, 3024656566, 3928770295, 3713579450, 4192432122, 3393072710, 3930455523, 1540248472, 4210019567, 1528184414, 2489059390, 2382921539, 2284746314, 2440433121, 2274431747, 3477784399, 3486495613, 135167947, 1791732668, 1256311850, 1615540681, 3658308418, 1521310150, 4075157030, 3478497250, 2648749653, 1904340621, 800591401, 2337381395, 1444719659, 481948852, 2568386652, 3578247243, 257893273, 1990952984, 4049848971, 1822812899, 2771185582, 3906214541, 2847954351, 225840234, 3350282473, 2179161857, 3141962805, 1757701555, 3006637500, 2158751912, 284714304, 4121460627, 2599487248, 2019352924, 2576609378, 2235276959, 1788680407, 3285349178, 1524848012, 3381160503, 2843162695, 2619261578, 1951237336, 2394879713, 2356170324, 2792701016, 3404008547, 1002368440, 1419997935, 4274316820, 4272792312, 2600711761, 2924208006, 3799196687, 696950966, 2896574900, 1320867021, 1371125429, 458156178, 2490470440, 2219426620, 973212528, 962603818, 3028036675, 1092766318, 700077671, 1961668807, 1413467709, 3551952291, 2243578803, 124518171, 2990223204, 2950073079, 3732478177, 3288060071, 1919120565, 3812014614, 3608862831, 431424612, 1131510838, 1974205493, 2177660085, 3387256777, 1464414294, 3144390273, 170625084, 2670108972, 322520664, 407651574, 3367433081, 1023268981, 4294542649, 1648604185, 2282100174, 848163558, 2648686607, 3586320674, 1942931408, 4181145468, 2084670734, 4055061939, 321659295, 2205837499, 1179724475, 2633022175, 3579309098, 1108502074, 2058030166, 3314941730, 3818763523, 4282431620, 1146563866, 555631220, 210570370, 2184821613, 2272729339, 2413880982, 3638531794, 3361320941, 2401767708, 1529464072, 2466734206, 2243057527, 2980199868, 2760710742, 483732721, 1704383348, 2325064790, 1848981566, 1424373545, 752210258, 1368884955, 1406336094, 1181447224, 544293349, 1292965073, 2805498791, 1820046192, 700731872, 4049120088, 2684807093, 3593706742, 1357350837, 1557310514, 2737286502, 1779747765, 2809114953, 2903685924, 2909304208, 2740902951, 274591554, 677369814, 3606800113, 2822291002, 2897175326, 3215594664, 3603579319, 1575627831, 567987898, 3848728359, 624094145, 919703489, 754070899, 414406002, 2869059975, 3046079982, 1339376144, 1559336480, 3496687851, 2087336061, 1128673960, 1287181558, 6801363, 2206476874, 2270106891, 3776867137, 3083213895, 664755430, 1045570718, 480207222, 416593112, 3695211324, 1478672597, 2113676978, 1968648315, 3769994202, 1651225661, 2162955146, 596615403, 221244731, 1567173201, 131815261, 1905585902, 1525265951, 2833077531, 4254008891, 243311322, 1797634919, 3818580251, 245397321, 172381663, 3367885612, 3038857154, 1317817258, 2553131875, 4164019646, 50317131, 2414368718, 2895502227, 2596980644, 2678300439, 3009869408, 3613859575, 1851711752, 3168922032, 3166142976, 2929184727, 3374941605, 2459483718, 1080087746, 61398623, 439523566, 944147042, 520666539, 4075307057, 419618599, 488558627, 598073463, 2111765089, 2909341655, 1514592426, 4195923145, 930569264, 1840813304, 947863014, 823083115, 2405319331, 768413657, 2396078648, 909652819, 3152305242, 1688520310, 2429923569, 11969372, 2792921291, 3595735387, 645583735, 1763222155, 406035086, 502382158, 2286036272, 604883859, 93252416, 973498843, 3589122701, 3759485421, 1921560734, 2310360674, 3648192948, 1681279423, 2372135375, 2402107098, 730662941, 696917368, 2093078477, 1278935804, 1472617163, 1498514050, 2649616273, 232019852, 1095401883, 4172674766, 1874215631, 510878190, 2452331703, 4284764625, 586391767, 3208727113, 3898750327, 3295423717, 2560283486, 708895219, 2170682566, 477352602, 4051489561, 3562386811, 705265709, 1650521096, 1202519480, 489140025, 1969535439, 58606358, 93891914, 1841522806, 140685194, 3546428899, 3832794904, 455507987, 3720870270, 180443184, 3540558889, 3308294696, 2765417614, 1384336507, 1436383559, 3339787431, 1106706963, 932556649, 2743889112, 1589032423, 3823186543, 943259448, 2501729856, 2881943698, 1588826062, 3022507748, 711020356, 4235526837, 2730014119, 3400977460, 2436065017, 2540234136, 584958300, 2547355104, 97484500, 869793999, 373708060, 3740163416, 2234476329, 2379585292, 1412978683, 2938563218, 2150151462, 4223150016, 3106644146, 1213466128, 950688665, 3314775082, 1776896636, 2923356624, 2444208017, 1167632176, 1833074594, 1227825631, 2552435445, 3966806405, 2523342892, 2057618336, 3528260322, 2414341212, 3917418837, 1915630902, 570704484, 4033976909, 53600857, 2643690281, 2227184609, 1577165305, 1671824914, 1839206768, 2962846209, 384523954, 1491795207, 3289639366, 3899575807, 3016198223, 3513611710, 206164226, 1226423815, 2787287316, 2431131724, 2949124558, 192537088, 2589742310, 4241132407, 3454706241, 2272299924, 2343268121, 2007664022, 3486236986, 1307823360, 3815894767, 1706356681, 2286333014, 1172330234, 495453859, 1046648281, 3554171162, 2485118989, 2812329861, 3607384768, 1544157683, 3992580504, 848079470, 3041542447, 4191338899, 2535200345, 656156612, 798092116, 3658473430, 571201790, 2441096018, 3438206813, 1410565612, 154709992, 3000801529, 1645448996, 462508027, 3752855082, 3361294979, 2870413033, 3186126758, 3923983810, 1941850370, 4188429895, 273242189, 1234068746, 1114370913, 3054592005, 811913349, 821035974, 397564902, 4126316445, 3844378680, 568208165, 2320060208, 3320099290, 1271423531, 1417324103, 2282105257, 1190417363, 3034381859, 1109805343, 370453535, 979626402, 3474549307, 4291146241, 3377129404, 3291758307, 774000051, 995035488, 585172188, 2893340736, 2715811960, 2086085581, 1107324609, 4127015079, 1485151586, 2201091928, 250469230, 1046502600, 3254239709, 2755089305, 1009697895, 2528081218, 175600315, 3501448994, 901728738, 3792338128, 676379456, 914862393, 2487801970, 2509611351, 1348159682, 2405746514, 3927344777, 2520198449, 1858031069, 1267233997, 693640692, 2552228259, 1176133014, 691074585, 3487438997, 937358127, 2850322587, 3606231003, 3315787338, 3528575623, 3792904805, 3340389738, 3871976702, 1561677598, 1196983476, 3835201149, 1493591339, 3619973128, 1568693526, 3397453130, 2024517474, 941427061, 868472907, 1670534029, 2109215696, 732821883, 78723504, 2165599025, 3692799882, 2155894668, 1499816103, 2229107099, 2640254266, 2982369738, 3441086384, 1946967080, 3019637624, 3329989489, 3687311326, 1640598327, 3808087146, 269142855, 1632664872, 3971707738, 2595313115, 373724739, 1093408840, 3051853113, 2584567206, 103558321, 3430090342, 792289162, 3873977595, 3598337913, 767197210, 1460432796, 1886348351, 3876026993, 4149481356, 3182221952, 4149477985, 1535479140, 3221741234, 2088144508, 2891186820, 192364089, 2457101308, 2560921925, 1874540478, 2103951833, 2037245347, 305042345, 1192631085, 822111081, 2898851741, 3090755911, 4001741650, 3404041017, 2229679043, 1501885861, 2746117072, 105272378, 4000328722, 1730967292, 2879040406, 2228889849, 3935773512, 2743499755, 1015108212, 1902739887, 3548958212, 696646080, 51845250, 618062993, 4161267246, 3250756120, 3530821289, 1872608424, 1327674787, 1049501143, 2604703217, 4282993202, 814117162, 4286943736, 1679860498, 2716783833, 3820210854, 3551989926, 310556439, 1161723426, 2331730604, 2265791844, 2232838156, 2309910773, 3273385984, 402061132, 4055947717, 2919809338, 39737082, 728397586, 3368287744, 1913781737, 356739286, 320426938, 2854675109, 4170900323, 2135551061, 1408689164, 3551724697, 1428803680, 2473143223, 2778970560, 2044748953, 675097387, 3029388016, 2523777647, 1763435060, 1885071665, 1036444383, 3186560831, 3114038268, 1180129171, 130714909, 3208725601, 4216192743, 3616366956, 417664759, 3926591346, 1738904961, 4211154712, 912944107, 1629830711, 871221953, 418125851, 4071702998, 1426552588, 3778594430, 180628425, 2476787581, 1172160691, 3804443737, 2764856832, 3069288908, 185423547, 3484350312, 3648696802, 2342856441, 399914340, 3055160038, 3836607482, 3255985104, 1118320215, 1800683547, 4207165378, 302057947, 2117451818, 3599110671, 2090826921, 2545297052, 2337434219, 801687905, 3585807895, 2490547894, 4098575672, 3562147265, 1042825839, 1983600385, 2882927473, 3703873500, 1062240801, 4234476471, 2316622712, 1226362031, 1959943587, 2234381439, 769453343, 3612386847, 1368156543, 3714930252, 1684872084, 1995417666, 3075331313, 3070227268, 1232161167, 2698899334, 92292651, 540999128, 4198132946, 2133994742, 3338783854, 3239937259, 1102454444, 2805328653, 3237282504, 2775707532, 1855321241, 4100055610, 821312910, 4250038806, 2417481505, 1919116829, 807740557, 2784193945, 317410769, 1107864, 4106569599, 2668922018, 1252276797, 4165875163, 1262425792, 1181202529, 1204492292, 1091213975, 547422582, 1667091094, 3626891978, 3188901382, 1670312384, 852381115, 873164949, 1225723946, 3024021999, 2333634790, 1121998456, 2606044480, 658476826, 1998781478, 3460417791, 4118344782, 3842479887, 8729057, 3693800364, 3081254562, 292234496, 1705338491, 814275332, 4062806813, 4236863682, 1743214436, 1719955450, 565231168, 2540025880, 179148131, 975806207, 3177793110, 3634924939, 2810229628, 2852242573, 348883471, 3726673895, 4205680801, 1237876094, 3727439460, 2857556789, 2326582979, 2541482340, 2812726871, 310417785, 653618250, 4062576739, 907492906, 3391207180, 3648164122, 1057470372, 3348198382, 937233976, 806383731, 680128455, 864251865, 3500284945, 4023961571, 2390935430, 1806389126, 1697546596, 740341438, 3671279504, 1938647717, 1760034242, 897323370, 2166361656, 2666954004, 854163493, 2289629179, 715574306, 2624834367, 2891155278, 2670730351, 4154407366, 1184288084, 788038744, 1086874695, 258685701, 263608388, 2890830088, 4237171759, 2144648923, 1264350348, 3792453194, 2177861553, 425834265, 3231381881, 2680532761, 2723748038, 412636769, 446860443, 2129492853, 108888206, 3010940704, 2052769050, 902830204, 261347494, 2096151215, 3255146790, 1190113744, 3779823974, 3307502753, 3836881007, 1361451517, 1114493739, 1107418610, 4049121627, 1423854880, 3070549565, 460774681, 2255609896, 684993156, 435683891, 1462359457, 157554082, 916291012, 2973071116, 460497646, 550166729, 2082590399, 2258337337, 3381630551, 131289371, 623708770, 1200952313, 649523733, 315603821, 3320198398, 4059943705, 1913914549, 399696933, 2011926856, 1771562550, 291774797, 3374823179, 2988580785, 2046729079, 3901782055, 98246793, 2744219335, 2488774582, 1572936160, 4275986582, 4225514994, 1143146995, 1116718058, 3990493156, 2888075196, 2088935215, 4189017949, 1553375433, 2698493767, 407434025, 3779073778, 3804782452, 1165223537, 295758051, 490236184, 2738060982, 3087660405, 1841549113, 4180083526, 2749239620, 3714751679, 1672025085, 3140215530, 3009632415, 1209108272, 570308889, 2802884211, 3030503551, 2116750586, 293015859, 3290404025, 1770348074, 2671919246, 3116355602, 3452673120, 1931588313, 2102625355, 3132825505, 3175902582, 3464288220, 3480074360, 745212889, 1835459712, 4277081137, 2714763947, 3237994475, 4044967160, 1647749244, 1374837907, 2582877611, 1201004268, 921634247, 2220869864, 3027062644, 1054796739, 905830666, 3521669019, 3284878354, 937944827, 761915506, 971846036, 528166716, 2850153542, 1059398882, 902843557, 1495645084, 2160845409, 1158895420, 1019405983, 611283040, 3569640190, 2707285971, 4187363037, 1425830687, 700469064, 2707046806, 3082933918, 4234168121, 2097093701, 396294844, 2639258447, 1334341965, 30434512, 3792466979, 2584859082, 557326107, 2443283535, 353463532, 3534700728, 2261680231, 352605913, 672321308, 4087006832, 3908938513, 3066183096, 307866759, 1701861111, 3328534252, 2318093938, 221450551, 3956223792, 608052154, 113632748, 845599116, 1512064043, 802121572, 1660895572, 480799984, 2953814970, 96040099, 3232765534, 2506507236, 2107024367, 1116268238, 644977591, 2459624397, 1836110127, 2795351966, 1953160332, 3093663887, 1595447375, 3598507437, 394763339, 3318090570, 2229066651, 1324108080, 3603332253, 3657268899, 450031508, 327209329, 3625706177, 3316400357, 3969755726, 2380028787, 1362781297, 1668799974, 3193538468, 1736866519, 1550621094, 1827667605, 1175662960, 1228207257, 983409684, 171357785, 2527567966, 1030068253, 4127402632, 3293125659, 1050084238, 3520716777, 1390168934, 2554184178, 1534715750, 4180983266, 3436179552, 3787329602, 2841499792, 1607590379, 1967261304, 3954455056, 1720176254, 2650496224, 1062864095, 307369638, 2614533958, 3099524173, 1864555180, 169444038, 3528109345, 138525419, 266176654, 4252526977, 795024827, 2482298300, 58113327, 1539210032, 3688183310, 2077198384, 1766547342, 3613151084, 1117122266, 1161268109, 3046447660, 2045364360, 3737405386, 1712515142, 1537326753, 3048303239, 2243753905, 1392785134, 2788611894, 853306679, 200327078, 4087771536, 1846518339, 3899730276, 3931283678, 1571846451, 788063881, 3487960746, 2811845215, 1087251553, 3793476453, 2802083246, 3403453517, 335973593, 2959741217, 2996421233, 72481483, 3813313057, 2728109877, 3484703806, 14273447, 3682550110, 3367944329, 1854597479, 1373450928, 363870760, 122952613, 4120955894, 873241611, 1771185986, 869868137, 3570824371, 2490309337, 3109464591, 3887570918, 3060237949, 3713580925, 473123855, 1894373719, 2848143089, 184018536, 395971998, 3236963542, 151430042, 1188183148, 1737870603, 1272861569, 3403483907, 1555936647, 3092113289, 1728890358, 581794434, 2202026784, 4282240350, 1426739104, 837691724, 1873143743, 4204050927, 2688946535, 988743082, 1751923340, 1452333792, 2726360806, 3841074380, 3343082695, 3912861862, 1499405555, 2894517394, 1592536766, 435257859, 4017288440, 764404416, 4088651793, 1407410401, 1468627205, 1009212307, 415315239, 573418150, 2454463686, 2778024763, 1586512190, 3004428681, 3812471857, 2248470257, 2804161761, 1749517575, 718381758, 3813803894, 388965471, 3457108715, 2255002604, 840340435, 1254745861, 3141172526, 177319654, 3393919903, 2958147073, 1052552674, 3131511984, 388462961, 2146014958, 211422549, 907976493, 3993853304, 2399488462, 1531574847, 397175238, 4274905841, 2467401495, 352405655, 2549545263, 1601303587, 399921336, 2155413841, 2090616815, 1008308945, 3720510223, 2253616576, 2651339690, 1636736278, 117591397, 3184690661, 1574250940, 67202842, 904525851, 4294668151, 270793828, 4002238376, 3905604747, 1187315293, 3159841725, 1418670849, 1323987250, 3111622414, 2428481088, 2793638719, 4034362607, 3407645889, 1225774062, 850266927, 1572371206, 1105993877, 2238211171, 3786679406, 1866345201, 3177363642, 439803347, 803306985, 728250721, 2419782417, 2712141592, 39370187, 4234872735, 2796092422, 3060298645, 1452562652, 3052772106, 661873466, 86489014, 880178217, 1825417245, 2237276118, 1786332761, 3385759141, 2897645436, 3076631493, 2058173377, 1412980193, 630369411, 4224380572, 3642562991, 1666967992, 1814063688, 1139541483, 154144250, 2997702880, 1156183524, 3456397196, 1913196553, 1397329607, 3221735951, 921938885, 3516033374, 2776338272, 3739350936, 788685068, 2985815728, 2725118129, 1005477623, 2338963002, 4199686985, 1067019890, 1080962074, 2259381993, 4002647069, 4209680047, 2530541980, 2580337890, 2522222580, 1885408812, 2200474118, 2878409080, 3430332448, 3865678220, 3522200575, 2063735558, 1483045394, 4111936566, 1718474670, 2212743205, 1217124780, 800146347, 1476572233, 3064787349, 1755315880, 3115812683, 57229346, 3959929460, 3655762442, 367811550, 1623486459, 3816380886, 238817236, 3204320329, 2391833889, 273675414, 3867840908, 3418813394, 3505425192, 198297710, 1196731827, 1080266588, 2238244788, 3215387457, 3066142755, 2420600605, 1353896034, 2842799203, 3431102053, 3328982426, 1467477451, 3598811481, 468755741, 3070152154, 3409562602, 2115593442, 2612915009, 3604090599, 2900163372, 2768201188, 352140182, 4170954278, 3528187549, 228347097, 2428797274, 3319272559, 3946050647, 1780469041, 2369460249, 2507185330, 177514964, 1094683242, 2721764983, 1453001434, 2620606992, 2987338631, 3385207513, 322417003, 3743869145, 4028254011, 2521047899, 3411779166, 1961279478, 2121068159, 1818205857, 2626957519, 2392491079, 3089431296, 4148137057, 2054803913, 693700093, 1852796979, 418153377, 2993989189, 1118759508, 2462265844, 4252676396, 1827422154, 2853584033, 4263232169, 3526442301, 3396238301, 676400433, 372384106, 4262374413, 3085212613, 2389018358, 2518874572, 4154449287, 4188615869, 1898755180, 2925336142, 665681401, 356394422, 2882057590, 2073712992, 2832515206, 427704737, 3339240143, 2298514605, 3133714048, 2380206310, 1208168216, 3074973564, 3198370332, 916435603, 165025200, 702451762, 3334036350, 2801802414, 3102545301, 3350875114, 3356386457, 1689206656, 1300914858, 4099436937, 1079522713, 2832156414, 469527224, 2892988268, 730638094, 81568989, 1138345577, 3141886985, 422513438, 3163550331, 935761740, 147209105, 2917755136, 2563667472, 2335572089, 1221189960, 2797845746, 2030922336, 3222268500, 3350222423, 1875012915, 913188073, 3567103213, 649728956, 3969843102, 2413407459, 1271772265, 1864515029, 3024387086, 1978738762, 2189306248, 701767000, 4022539850, 1244508846, 3037860943, 3565142121, 4055972254, 4039612409, 3950871459, 3361569301, 3931672015, 1861671761, 287990818, 2054985720, 3293981435, 1142436636, 3663004182, 548830099, 860056494, 1427050437, 3917853727, 3476367382, 1324861241, 292863807, 1353344334, 3790692228, 564501663, 2726953240, 3788978939, 1870949982, 2443187462, 1598704649, 869102240, 2747345603, 2949652746, 882557613, 626721427, 3695475979, 3761275500, 3081065612, 953290733, 2427634287, 275675311, 3489237999, 1409364854, 22217310, 3874277252, 1919987194, 3902061512, 499875881, 3522873046, 1548371975, 2916528714, 2063113374, 3254579903, 1392044035, 180743283, 2367877209, 910252700, 1181472732, 3554936362, 4290901884, 4168855147, 1188172325, 2727259401, 1739795606, 3080265682, 1523028493, 755772959, 1288302043, 3958780095, 3349284085, 1735981011, 3678391283, 3239250635, 2600989056, 2036489834, 4212989537, 1955851223, 3606017501, 1120160994, 4028423131, 200588549, 2366817149, 400871322, 769262945, 2059073003, 2356801840, 3524924991, 2024955325, 2611073008, 3316635354, 2586877408, 2574570817, 3288285968, 3316540252, 79958527, 3493504889, 2494984173, 3604286779, 3598216062, 2929295835, 794042362, 2532914920, 4047765126, 2491728548, 2186423348, 2253477564, 604589379, 2541876140, 4106404473, 2814291199, 2560278225, 2153221030, 2527102764, 1288005380, 1549478298, 2560147492, 952112495, 1046208290, 2391816412, 1535338719, 3657759417, 2755788456, 3677822993, 3324252966, 1093184621, 3670757654, 3026219609, 1803459579, 859745042, 2730960697, 4068091083, 3509813172, 3616032323, 2745598914, 47676937, 3644965991, 2751422476, 1097690794, 269494746, 449697168, 3024502437, 1415350991, 1996683536, 2261977964, 1085166666, 1877967942, 2715095845, 4166792300, 1743341316, 381857324, 3821179457, 1723896926, 1247122208, 841729074, 4169012172, 2813574348, 1572879825, 275757080, 1041062159, 1368580102, 2932653601, 542459056, 4106763326, 1849102470, 2488382884, 2087183037, 3937055408, 1172384853, 3542358815, 2985225033, 1651176377, 3760113257, 1726765558, 2304291514, 2377492920, 764618425, 3732778722, 1784727556, 2182102498, 4098181398, 2817350407, 2635941002, 3500518689, 1589605794, 1510884064, 1758425907, 2678316955, 4284769685, 3912417566, 967620981, 1751079430, 2264298092, 3461692092, 2928904353, 1427120450, 2118753864, 2943198082, 2080830041, 1516990312, 3883727268, 1268445995, 1694692175, 3532738804, 3120289928, 3434046077, 3576154697, 2184913964, 640584551, 227663130, 259848690, 3336027860, 2415066272, 3082535578, 2301394991, 1588650804, 375226244, 3699352654, 2718641779, 3183377046, 874447418, 2842724036, 2471767194, 3147413748, 3877376880, 1543146870, 1389267320, 2735683577, 541110467, 2003402921, 2323261055, 1995585029, 2078957184, 1722646036, 4108532331, 1121473970, 1039665322, 3414434525, 906460656, 3117668002, 225845505, 3409232119, 2461929525, 1724951223, 1963726472, 3394880502, 585381174, 2591220974, 386213493, 3888854262, 263404412, 2940814018, 3970267185, 273816627, 1475532173, 3548757054, 2548378170, 3153240798, 3672329238, 211278910, 104001302, 3241280754, 3545740470, 16820164, 3261213740, 1374371295, 155978151, 1424468358, 335271082, 2119870322, 1003124001, 2110005140, 3764914231, 1539971252, 1382834410, 3573508484, 3223808912, 3565385154, 3404514425, 3479535893, 1602777654, 1954338368, 4240079299, 47465300, 677186395, 3109052018, 3868633854, 3512324627, 1769082803, 4110833394, 1939263141, 3036644270, 1849505923, 2546805449, 388638738, 794064742, 2122155858, 3625992790, 3073047023, 670005027, 2225552682, 3627587828, 4179871718, 13559252, 1708029046, 2175593997, 4005385631, 1338521947, 2733942192, 2136341441, 1823237869, 1824920472, 1310150834, 2076174418, 448989204, 3947179076, 1006675266, 4100366005, 733281401, 704513131, 1653636794, 579085773, 1576941907, 2165874708, 3058837103, 94571879, 3585387343, 2256365577, 1610131515, 833206413, 3056541718, 1302315231, 282161551, 6001006, 2381565878, 2248935472, 2764634345, 3811890309, 1363389136, 539639285, 3330861532, 2829911450, 2892949980, 2065749461, 1828402443, 4207168170, 506185334, 2024407027, 1891970038, 1709318193, 3836575075, 48277532, 2283948714, 4228381373, 3101512181, 3246162054, 1701183039, 767347589, 2447138416, 479840359, 1765112324, 3330783749, 3402276932, 984697268, 4147301491, 2170080507, 516140004, 1465842957, 1192146667, 556677166, 1774938725, 1064094261, 2457567145, 955985826, 2776909393, 1664365780, 1245955022, 4139315012, 3332423935, 3584383456, 959550365, 2851581095, 2765081174, 312015845, 2925122154, 831150802, 2225638909, 2164098389, 1191447415, 1117010628, 135561721, 4276963837, 845458518, 2851510357, 969679932, 1796734039, 2511313129, 2522970427, 448789704, 4073504765, 659076456, 30688278, 678042678, 988391597, 2657818481, 3122219921, 2252457867, 381833280, 39664823, 798312169, 1342169064, 685136713, 343784474, 1999891332, 2648989534, 3121328072, 2094704341, 875054259, 1539951585, 3426006595, 2948462920, 4241999564, 480237018, 76339523, 993214506, 212508648, 1761289874, 1458847695, 2815784859, 3828413800, 2112473099, 1970671077, 3585191439, 3453953161, 1715148319, 782577083, 3559195779, 666863548, 3269449590, 1738497402, 3327440058, 2235043279, 763967509, 2723962306, 1300681724, 1644634995, 1020883713, 3134902007, 167254450, 3835378367, 2890825816, 1882600156, 3842475942, 1580439250, 3304510024, 3564220150, 585616996, 1124865185, 4039703682, 3346376390, 2926107577, 1428383569, 1403186104, 3499989938, 1755509293, 1722103947, 331432201, 2568758684, 1646728996, 4243446314, 1526164470, 3471547995, 2444662401, 1294209014, 2516383774, 2221663104, 3846549522, 1159773243, 3094344486, 2618544842, 3939291411, 2606083838, 1226639076, 851733441, 2230701030, 2250669365, 3466438617, 1644286935, 2339513487, 1809184493, 2145665846, 759905197, 1355986255, 1263473014, 95463257, 2059590240, 2375277619, 3763920231, 1647395486, 2208600025, 1743033782, 1070898946, 559884107, 2246218814, 4107598716, 1163859100, 1747538253, 600091417, 555425760, 1717835270, 3807124353, 2597656066, 365296128, 113127124, 2236845020, 1660665852, 1952113073, 1994841776, 3920008566, 261384886, 1775714106, 3369232672, 579093206, 2485710549, 3177362285, 3814071502, 3332073094, 2727071987, 4079756356, 74907460, 182436247, 457222487, 2657753313, 543162418, 779804662, 2792813646, 2080884976, 2097955208, 2900604543, 103301967, 3930415991, 308718593, 1552419335, 749043430, 2411193439, 1098424808, 2570118989, 2526694181, 3400415626, 826639960, 3742302823, 2133662427, 620256904, 2591646669, 2532798009, 505294613, 318811638, 1036220366, 1873158787, 3081676522, 1897558064, 4139471411, 1934597655, 184383759, 3377149482, 1315956985, 3503258655, 2995273328, 3760695601, 811451116, 826293446, 2369821295, 4075827518, 2893132959, 2626882418, 2631502734, 343778694, 3078185303, 4109408861, 2364496718, 2398698968, 833238139, 2426477338, 2544790438, 3418780531, 1729437941, 1426848541, 703366009, 1593001628, 3832885374, 121887589, 3714704746, 1887598275, 2635541559, 645673967, 2633766892, 2138371399, 3489491357, 860025592, 2858956168, 3707495752, 988417647, 3143123665, 403011270, 361217919, 1292362439, 3072108637, 3266764040, 3135891208, 4255030170, 1819294900, 3774725854, 704946905, 3914456762, 2548645109, 2835934260, 1917802734, 72414571, 3545740638, 3036114677, 328334211, 2279999972, 1684556682, 4115980801, 4158737999, 2349331837, 1184362158, 1377163853, 1447406213, 251946304, 2054699319, 4162300527, 3154732537, 800830595, 2345623351, 4186958457, 2597505670, 1622655415, 4094370742, 3495169030, 3050889288, 2811297024, 2100924914, 414823337, 1155175373, 588370150, 3539521602, 1785268161, 1238354232, 1999419243, 1956013442, 2727088474, 2772169915, 1034439403, 3016448032, 644479533, 20455836, 3152088005, 141608454, 3167589853, 108693017, 165857307, 1677180682, 1912847266, 163072558, 3296918496, 1238554706, 2913139339, 3250494328, 2656026782, 1814001636, 983005525, 3581042682, 1273295181, 559488001, 1513853211, 2674226464, 1496174110, 2676038553, 2913291535, 1553836470, 397263220, 2255512214, 4154190644, 595917305, 261247893, 2624933658, 2121607555, 1122170555, 2052329115, 2719924412, 2564565254, 1268524644, 3877295800, 3658790481, 2358266462, 1007723483, 1447765616, 3423692597, 265739651, 901379688, 3385164778, 1406671308, 131685138, 3713756304, 3654640221, 2736543153, 2472622330, 296454307, 852438478, 7174775, 1578146007, 2337741740, 3285588755, 4121241537, 2506803918, 1111804407, 2993267143, 3847761998, 4003822560, 3451790762, 3677812854, 4098046969, 3705675793, 1671683662, 3986647063, 3787473835, 1085779680, 63990554, 3052414141, 4084321971, 1680156006, 3808683942, 2589092699, 2363032620, 2314644674, 2410842488, 3482027906, 2194963213, 2213653516, 1545508186, 1257471342, 1898594301, 56389295, 4031070285, 1283603427, 3223663229, 1352935921, 2738160650, 2000719221, 2676319895, 3353571606, 2387345702, 3369949082, 4206766813, 1997790391, 3247095723, 1895752266, 3138635348, 2024797579, 727824971, 3740942574, 3691088316, 3523830306, 1083845175, 3611575859, 96129162, 1426405506, 3576582890, 1324911621, 139050613, 1381515152, 1350361631, 3260093458, 4009561124, 2902641247, 3421888551, 2157764063, 1677483974, 3548504518, 3149100719, 950890023, 1000765812, 1798951241, 234444169, 1840745749, 3227267033, 601588165, 4270830694, 1265160837, 2245119744, 1832861096, 2441788779, 291223082, 1354813178, 3108244631, 220388565, 4210917215, 4010444702, 2886283367, 82311693, 4239286067, 3456441667, 1629365021, 2963465439, 1481069014, 2097168120, 2243459591, 2045960661, 173328679, 3482434896, 4284957309, 484819561, 1740171710, 2555325273, 2661539433, 2396132170, 36487093, 3114330075, 2734356016, 3976205591, 2505500864, 2126002765, 3266217676, 1302423724, 1562426791, 3510406517, 348852671, 1734927396, 300810933, 1937707904, 613817860, 2938633657, 1159075264, 2784013920, 2444220279, 727962070, 3989787881, 943588331, 368304548, 1020941872, 1481150501, 2674628368, 3420429396, 1684097634, 959541097, 2941757332, 3236364940, 1880542357, 2764924294, 3213027040, 2726761407, 877837400, 832388117, 1170376228, 2599645276, 3592924439, 2127941493, 2180317916, 3401584289, 1283238252, 2111779714, 1312217909, 880488523, 3747191761, 3711419005, 1565267457, 245583610, 2584971161, 3274236273, 2816685199, 2298120534, 1736377983, 3433000851, 3570653415, 1300835749, 3494473256, 1405825069, 782120632, 3333110654, 3015387134, 4240837245, 298089611, 3437707558, 4195547439, 2116756321, 2127250135, 2657834510, 146019804, 871958202, 3619635538, 1886354488, 2191743571, 1673640959, 2801677351, 1855160805, 2825509812, 1076198034, 1092011304, 2923986417, 1440398202, 1366248429, 999842069, 2853432030, 887296075, 745344340, 3915444423, 137214069, 2109947701, 593011704, 3709740023, 72054388, 594605309, 3120971686, 1754070837, 469577850, 1123863468, 422939802, 2499811560, 2041182159, 3663197764, 699866274, 2992511944, 2023300152, 2818667039, 2554586998, 16195633, 1464495199, 1878983070, 3221705578, 3894377975, 2206566824, 3621602204, 4112584541, 1654655134, 2046462885, 1199949442, 4028644735, 1342750738, 715825979, 2473867245, 2481829200, 1427831000, 3897677309, 4273940493, 304354183, 3863817587, 4269371494, 1564245555, 2690956328, 288229216, 2908021585, 3808602115, 837771623, 2087448898, 240864044, 4075189389, 1540749110, 601012683, 1956916011, 7208633, 292882766, 739164803, 1310072295, 3748433258, 900592441, 2286857773, 258207382, 2077585386, 791503051, 504679761, 366569024, 1987480819, 677624392, 2756754647, 1824926503, 1397874406, 2300475673, 1607388792, 621827211, 685564454, 3229937113, 2189260300, 1536150535, 2703653614, 1454082497, 383977876, 3206916677, 3326425559, 3234811301, 1391974329, 3418166122, 2128451694, 1067074505, 4143057672, 3276489313, 2067297467, 402789558, 685511549, 574592745, 3436352270, 56094572, 3027611471, 2499065862, 3669703867, 1412618951, 2879910062, 1711740277, 2589693067, 2451752439, 1639484565, 1006926125, 2330433969, 3269248718, 593755649, 493557873, 2040814187, 4042466278, 703016478, 3817283497, 1327040299, 2339650788, 1088223135, 2890879770, 894916164, 3525926793, 687925230, 4071461475, 2809678788, 3326724253, 2497398932, 2944824582, 619786, 2693209883, 1104276458, 1969261178, 3799324683, 3082249155, 3380797409, 3309498417, 3775231428, 677009500, 2430127824, 3663062776, 2346270068, 3211924049, 1075408881, 3144851064, 3402727872, 988367174, 1033547960, 3541629365, 3398709809, 132394811, 3972795362, 549601471, 3690251852, 1264257864, 1015058312, 31128330, 2654982371, 2307969937, 3805637799, 3191398359, 2330889832, 875573722, 2815460038, 478427945, 1605726371, 1993862125, 3558529989, 842135129, 3201338141, 4027924584, 1355673831, 1758058840, 1681506452, 4233951981, 510811326, 3307971425, 424881303, 732090852, 2369116896, 1265883795, 928486672, 3808814209, 538866645, 1636235088, 2781732247, 2155725650, 77162846, 594984709, 174940515, 1835663652, 3361010167, 952506899, 1212290429, 4255703460, 1527478375, 3610266436, 191984657, 2547818163, 1591637854, 2813508431, 1938555296, 2574817744, 4894775, 2728378906, 3094485006, 3136258558, 3330331604, 561510431, 16764632, 3662304336, 867446159, 2435391430, 1298662597, 1741538909, 2542408617, 831388915, 4056519045, 4230962771, 3119545068, 3094838557, 2921185774, 2889755884, 2765070650, 3885024396, 3820970037, 3033503395, 1507983318, 671096937, 4163926604, 2563597560, 2964706945, 798522642, 3285315751, 3987869649, 2034843484, 3264133905, 2715105430, 4087933875, 4000927090, 3267758277, 483124591, 2550465362, 561317022, 3922611377, 2261254576, 596368429, 1048233448, 1046712137, 558454545, 2595715704, 3013690214, 1787016949, 2189250401, 2316157454, 1818265720, 2185421123, 4165658347, 1907713649, 1893710286, 4099664463, 1276819316, 425702805, 445203476, 2348051421, 1527034417, 2536840666, 2457414079, 3212465580, 3844283979, 149172290, 3840127048, 2066035182, 3306976031, 275322554, 4205168228, 2104640461, 2406877783, 2430950173, 926834869, 2804653836, 3063999404, 2447664420, 929775433, 2245760161, 1420868878, 99771882, 867297838, 231947609, 3067947096, 412334033, 1294146064, 3712546117, 2589442708, 1762494069, 725370604, 3470500765, 569187887, 1813554485, 3500757007, 2339274330, 441804163, 1112526664, 1967412984, 2095036263, 2812277198, 2082442107, 1025233315, 1347449706, 3830746182, 3336428929, 1866116627, 2271859044, 3625797601, 2512906061, 2016994923, 1622547312, 3593915411, 1742821464, 2704347638, 3811537740, 927850246, 1151650537, 2840337814, 1969336484, 4102200979, 1631086872, 1638625162, 2316727680, 4235247593, 917482552, 636357622, 3068660418, 4056094456, 3834156503, 922027306, 4182579749, 2274988128, 3499595696, 4289786147, 2231886640, 2517163615, 234826320, 3037868198, 4027255229, 331541751, 3632090866, 2286914942, 3797088527, 2560327205, 3280688017, 3259387116, 1235033225, 4147077682, 1593860297, 2243793157, 2157850550, 1897571121, 2859168606, 4219683906, 2666409010, 2531913135, 3842064031, 2975299127, 2990270975, 305620767, 782872114, 1873339555, 4232276158, 419317474, 2285813026, 3850705968, 2337077076, 3322746111, 2996510097, 1190051226, 1155768460, 2734815708, 2501355088, 124287211, 9906142, 2128580241, 3592547922, 2519942625, 1063655900, 1649654785, 2244418032, 3260516, 3268324395, 297708159, 1874512676, 486287750, 3564149704, 774430984, 3739444880, 732001975, 2445402284, 44869036, 1494438124, 1765962633, 719773026, 869740160, 109440719, 3468536612, 4037880420, 2289055777, 2983957841, 311658285, 3670474165, 921767218, 1794587058, 627661050, 2640562493, 999822045, 2283399773, 3959369811, 3099450161, 1622663970, 2194124866, 836397807, 1433566075, 1268352364, 77669776, 828388331, 2728941389, 2243554679, 1167640573, 3141548770, 2672572925, 914513872, 2271688138, 3873562732, 1893212049, 3344967591, 3983047802, 1758604789, 1303308479, 2245928210, 1964407979, 2162974362, 4129173562, 1964997693, 480018193, 2867706367, 2085006716, 2004126013, 4184736742, 4047008801, 1661037463, 3689702840, 3692462075, 3570495403, 1364865014, 2233331184, 408350207, 3913046713, 611728663, 1034456977, 4167979042, 2582216639, 1543272331, 2243036145, 993620955, 3292434817, 3705703669, 4204017684, 1197931279, 1537885298, 598587484, 1496557380, 1407378688, 299297600, 810870084, 3310078786, 3404328565, 2207377669, 2173812170, 3707305176, 2712573869, 3193314832, 3843972985, 4252198192, 1484224291, 402231860, 395437141, 3950444976, 3792984519, 2485969210, 1261817135, 510506820, 4081667294, 2576563015, 10291870, 1046774861, 1912347418, 680112214, 413007049, 2846628588, 3071404904, 2794759569, 2198339192, 3592853039, 3486234033, 3576305809, 728252578, 3902444094, 3304912747, 2141705279, 3455300755, 4181535485, 1958004100, 648885967, 3167202263, 3865398392, 3204727215, 3556781006, 3998007739, 3637337910, 2258548376, 610222066, 4137380157, 3485899723, 1481440721, 3809293452, 2331809817, 55941516, 696960978, 4155520153, 1513505295, 1303646374, 3348860949, 2169539231, 4233004251, 2650791723, 184420991, 2181840404, 616602012, 3493535598, 2821415559, 2017490208, 3988940925, 771484360, 1930210967, 3096419012, 332214671, 631623991, 509541241, 3530826069, 170460777, 3332561039, 331027469, 4163183980, 950885024, 2450675408, 4209613469, 4168930708, 255471420, 3341915739, 3242872109, 3952466929, 2322949398, 3738826136, 2023292500, 341901055, 1617070570, 3365510440, 2318847851, 273057587, 2433762968, 162431070, 636937558, 3054507389, 2161972447, 2248138027, 3969671081, 864771593, 1650436443, 602518505, 923483622, 2407318064, 2079913399, 3813197025, 2737361148, 3618309336, 1062375977, 4216115599, 385810045, 3640007380, 2395638560, 1640053682, 669939115, 1122818174, 2107985506, 3426817490, 840389093, 829620248, 1887763809, 1521081185, 3642058843, 1973844100, 12661133, 2162593761, 3891609704, 1784494060, 2044257407, 3329745268, 2903593166, 2970080880, 3249141492, 3503717325, 4116310565, 2391911792, 3681281723, 3445537681, 1315925110, 3124580215, 3133346295, 3192495004, 2051667604, 2300354402, 2658048799, 4163663921, 2878138572, 3677619900, 3717510482, 293400592, 2343381949, 285263469, 430409086, 793442475, 1259436382, 2932738694, 1853719227, 3080593626, 1604887400, 2760813932, 1333186387, 112535360, 2480079744, 3056839474, 4088398262, 102978420, 2214938050, 1102864894, 3840953340, 1518922283, 2478245435, 2255237690, 2557202857, 754791355, 2489061397, 1180224149, 2887214313, 1300933882, 3428131516, 854252016, 2462003431, 2847774286, 1557242088, 2795302849, 3343497084, 3158916462, 2861567530, 3483133831, 4159573894, 3729071224, 4244304879, 1302007918, 1442957325, 2677160330, 3091005783, 2866806232, 473287500, 1276042544, 2344323501, 2287275222, 1644192473, 3124433688, 2127392883, 2688550961, 3791582800, 472767457, 1504801370, 924906298, 2585327461, 2387702605, 1244201168, 2025773180, 3558722261, 1747077076, 2235290026, 3334906670, 2212094521, 2104290540, 425565095, 3063698898, 2984604904, 3526191125, 1273745866, 4130897585, 664565494, 1101389402, 1867294962, 584401257, 2308622611, 84275, 3886843768, 2952936625, 2182803273, 945840420, 564456040, 1231430250, 1116367146, 3977401809, 3856714515, 3438513166, 1962845594, 1462408276, 4038556971, 2717262142, 2071338205, 2378801035, 2471009862, 453380923, 90608020, 256190225, 1772374718, 3904593901, 1085689797, 3449842973, 951219530, 1836802864, 2520977420, 3787372871, 1092477428, 1258530611, 1354179102, 2661601572, 3850874358, 1770282275, 1590227301, 322935988, 140904195, 2406912248, 2558481307, 1355306572, 1520189205, 2564789704, 3954274834, 2912192681, 706547152, 794514058, 3125366095, 319626862, 3514855443, 712083526, 872135422, 822924910, 1989432487, 810528555, 2010240875, 1771372105, 3853827648, 97206440, 238686950, 2637770821, 3349966249, 954870885, 2150207567, 2505394687, 1351977645, 86453836, 3981251342, 3812701846, 497142721, 1320366792, 2329111234, 712386168, 266511744, 486503178, 4022135565, 406620050, 853384444, 2039851954, 109110430, 3458557213, 85195081, 3047334318, 22683743, 2043724899, 2199939527, 2264042797, 1718499784, 2805416797, 757419777, 915604228, 1576803591, 3852258097, 3639831508, 2670143421, 213154520, 3043602459, 647838611, 1905437958, 4072757889, 2787390148, 2039854819, 1939729526, 3803121642, 1094674591, 2036748830, 3463807372, 1281241527, 1015866462, 3281782143, 2113298487, 3127998376, 1433483243, 3628963213, 471288138, 2690609594, 164778934, 4030450999, 865446964, 1328914535, 1198367947, 1798966897, 613291465, 981756857, 917374869, 488654345, 336380642, 1590901230, 2530500574, 1335206373, 1896228377, 1804652122, 2338563765, 4196093694, 1983300845, 2465539904, 2230106746, 1927901962, 3154062705, 2019911523, 297187162, 4133401023, 587417529, 2182479442, 2783086550, 4077929643, 2408484000, 4118084402, 1663858033, 2153330285, 1893288978, 2227570337, 2792183071, 2478571924, 971816454, 1417895397, 3822012116, 9635357, 4237484688, 225829342, 2182755538, 1860897701, 3602842388, 1703972432, 2551822690, 3581820021, 198865239, 1509023965, 1824806788, 1944049937, 2929016700, 1613971390, 3746296790, 4074709837, 763209171, 3979998442, 3540469807, 2459871768, 3275144041, 2371146189, 4121830358, 388143676, 548004372, 2118694623, 2908599826, 1294302384, 3985451175, 2123567685, 2933179033, 3259804451, 3250590638, 2701132546, 2989597316, 772400258, 1999829893, 2563787019, 2883221287, 3666061079, 3755700741, 894587584, 2621054240, 1267104256, 4215384733, 2206234066, 3316466326, 3492273235, 4278029635, 3351867221, 1894616027, 171884857, 1054127276, 2829690294, 1263400165, 2266676616, 3007581899, 2348850132, 2787624864, 2086021499, 1692430249, 181239663, 3508161627, 3214934339, 3378351470, 96996117, 2582528612, 1297906160, 1047551903, 2271168141, 1253922727, 4094829083, 2565553194, 160987488, 3580751373, 3864612055, 3872645531, 801537067, 1681400757, 2786944744, 486903470, 3910046398, 4243547101, 786865425, 3745925990, 1262793521, 1434567391, 3018602424, 3447405592, 1139784776, 188728849, 108704018, 2455363979, 3345223585, 2808532172, 879162620, 54488993, 1690104845, 382951565, 1175914392, 1963926337, 153618720, 607958406, 1257710478, 3743942146, 1772749467, 3009645812, 3229481093, 538807495, 2303716588, 3003260226, 14968305, 3590636424, 2167055731, 2215291096, 1877312016, 876083217, 3396799051, 3280043064, 1582432415, 1596908623, 3318284124, 2138145009, 2755018628, 788499089, 3052718417, 896264690, 1178427313, 3253920579, 862780343, 1677747092, 329979156, 2320067741, 274638595, 530233724, 1081447425, 3785467375, 3355218487, 2315820968, 446079568, 3195316438, 1550806948, 2360613944, 2062562998, 3818832455, 2567415199, 3197903852, 582305102, 518937984, 885775847, 2173785541, 821730276, 2531963536, 2777589429, 2002149639, 57485221, 1904470877, 4152865147, 4237501809, 2961981999, 248308655, 769807700, 2455568897, 3550752081, 2183411410, 3722010400, 4280053225, 1230709424, 991513717, 4230841729, 3023533516, 386479491, 3575779634, 1554861350, 1627686123, 3232693029, 779458098, 859077623, 2007247233, 3257970051, 2778512329, 4218577511, 3115771622, 4022412966, 3975139820, 2603136324, 363568094, 3336979128, 3620765897, 1119391878, 3109917729, 2489742672, 471269191, 2320178771, 1964761822, 3092412188, 1519071250, 162153331, 2842166372, 2873239448, 2644995328, 120613276, 3600654605, 2701049012, 3160886418, 4064728480, 2818119120, 455612595, 2201436309, 2433273364, 2511515835, 2635382963, 4288496041, 1537509013, 3060174282, 3336717897, 1125128551, 582760872, 225958707, 3239484867, 1890747215, 3138471502, 892335098, 3216849692, 2566414941, 2410238677, 1333297221, 679219118, 32388963, 86740378, 882776516, 2355943987, 2701355733, 1963621166, 1750723739, 1536625853, 1768049582, 90473686, 2480131953, 2759897394, 2355182133, 3915991656, 1218848133, 265360925, 1323655301, 3987764797, 382004015, 3767740561, 2223785162, 38405833, 2567493113, 1236409859, 3619143925, 1726964061, 1287783995, 2188453419, 4120310899, 1668016245, 2689772731, 3962734209, 2643081845, 2623816715, 3608422692, 3554559450, 1199196125, 3920552703, 190263297, 1255130923, 1190461783, 2404346477, 3461474856, 4102273686, 372943695, 2100321096, 2791914046, 3397828282, 1004348740, 1277133932, 2535134566, 365291795, 1410872343, 826323707, 669074846, 228169371, 2109343264, 3827612293, 1326788467, 1982272226, 446801148, 2343046098, 3936458810, 3451374065, 618855410, 2511251550, 4228297871, 327584544, 1345196551, 1035293340, 1545828440, 2380087551, 1559766270, 4183128152, 3640266581, 1767178697, 682782465, 285872671, 73850056, 436729226, 4034530898, 542460320, 970655855, 1263508118, 2473209791, 2283657618, 1458173226, 2383878598, 3549213353, 3605161837, 948906137, 3702409148, 1219566104, 2011481394, 508990153, 3159647304, 4266780367, 3798671085, 1640956189, 1884552782, 2082129227, 3653841896, 2842792179, 2828127897, 3958669432, 1999328972, 1187323813, 1982343423, 1559326821, 3877594181, 2447429794, 528223656, 2757983372, 1180114911, 2576423775, 925248716, 4283503804, 454060210, 2607868415, 1962926223, 904160983, 736195764, 1901535476, 294842472, 1140451806, 3610997383, 423324553, 13124655, 974575945, 3650695070, 3504429568, 1445146673, 1166848672, 3337124229, 1337486968, 1498330336, 1235564972, 255630232, 578580783, 2085701895, 2204716003, 669956187, 3895494015, 1069614906, 4195511594, 1819785212, 1916385243, 457917788, 2700002244, 4182459709, 44917490, 3092745965, 481633008, 2568779016, 4233987575, 630329192, 2729385379, 4098124963, 596271756, 1811048447, 4233302074, 3763608447, 1547886565, 1792962870, 3637304311, 3276015905, 2219359868, 490267475, 1992441268, 558160550, 3505528718, 1634797488, 4289002112, 1395116372, 64252250, 564128064, 1466723201, 2892870718, 3867268365, 4280105392, 1963729832, 2573502169, 2788735888, 3493201618, 578831832, 1240512260, 1047750976, 2647293219, 3278318293, 599344328, 2601769059, 3525949051, 750705977, 212188614, 3405024571, 1649740821, 2731036117, 559999954, 3366014280, 1491770839, 817110706, 789077142, 3816405680, 2280247302, 1685988942, 3541058355, 2030544217, 125298212, 1879506747, 3076014922, 785383148, 4121787253, 1345265641, 926055274, 4134008307, 465980587, 2246582348, 1777642358, 793132026, 2879272740, 2002386485, 3985743419, 20316293, 2176974293, 797663027, 1912893000, 1918598806, 246363593, 1239889569, 2666510487, 1974639765, 1472581234, 415382420, 2565151597, 2533428808, 4256721471, 839811574, 2794785401, 865016369, 1187777670, 1008770132, 2022265616, 4173115343, 4119493255, 3763808640, 358943876, 2534110338, 2568212660, 918445798, 4191632840, 1144061024, 2231465328, 4098068927, 3458786493, 978691361, 1172546067, 2445695153, 2730495615, 1368757315, 3475492095, 3583312259, 4005770539, 12828775, 1930751857, 2335311254, 2602572936, 1125478724, 2444276415, 1449082553, 186294652, 1468358108, 3751864840, 1017051329, 3859339995, 1122373606, 3252628246, 4253119433, 3468552953, 2264249734, 3324330478, 217523305, 2141562400, 190690312, 3297300930, 1990897601, 4012332576, 1010093014, 3301795466, 3026848363, 1628241543, 4231034072, 955692066, 3088663484, 3606431013, 4193930784, 2938632616, 1428690959, 158356224, 1221499475, 1431831161, 2280610781, 3014483484, 3590701401, 3333595715, 1277981041, 3901583697, 1750782528, 899872406, 2900611894, 709559225, 596450003, 278435865, 2317114538, 4009418400, 252297572, 3725278947, 685729789, 1680303280, 2223803634, 3417525563, 3973174203, 1497767567, 3448192379, 850298872, 3297260476, 2029688344, 4208553672, 3035191335, 2889430952, 146986036, 47572917, 1776434631, 1775887747, 466903880, 1751890805, 2228766302, 2524702532, 3923882564, 3152925007, 314158386, 2543502412, 2141760185, 1036119263, 1096271477, 4103039493, 840551259, 2442818131, 751636408, 298752933, 756907572, 3588846905, 2486258379, 2963771126, 2805079146, 1072040561, 3034070738, 4173611989, 853813568, 1918058162, 137991992, 2780698588, 699902509, 3511227208, 2930981849, 2996516700, 381922492, 2495326781, 2230556256, 805054665, 3057150347, 391162146, 1126998684, 3015150075, 3068816966, 2743494142, 1608522816, 2788143833, 2668930190, 383445850, 4055024205, 2933282584, 2598909892, 1213272559, 1134166671, 3231660898, 964312685, 4136302428, 3098637657, 3447941058, 701008012, 4291030853, 1342676155, 1512656657, 1107020938, 2725951126, 2936801309, 3224487475, 2608468550, 3318842199, 1277116915, 1136839671, 3663994061, 3135931272, 3534679592, 3793388026, 2228545154, 4282098378, 979545695, 790528343, 1975236923, 3190831975, 2175946267, 510078003, 303818157, 970836976, 1348936391, 2099187245, 2331249485, 2720503938, 403373506, 3207422347, 519492240, 1533426860, 3551034406, 1528102582, 4042292938, 592279471, 3005831738, 3831365163, 81039638, 1363707751, 886088776, 1302391689, 2539447399, 2566603996, 1602805672, 3804350895, 3498967202, 675526007, 3065961771, 10883222, 881074677, 1589405713, 3129199592, 2573939138, 3156782289, 4091279399, 1872368768, 3453629671, 360328772, 1949846085, 1459257771, 2702390247, 3202519788, 1590883880, 1564269014, 3526997253, 1202751835, 2900376167, 2077050306, 4258130845, 1462970763, 1130723611, 3950952299, 3212394086, 616693094, 2551861628, 3822264992, 1065479064, 2021472212, 3802576300, 3913956185, 3059903272, 133076079, 861283410, 1038095439, 1614841818, 1513339226, 383922908, 3307187827, 1218112993, 868745561, 517479669, 145795279, 1240591914, 2790304532, 1166251792, 966049101, 2592025400, 2094385320, 1572651369, 99163486, 2946235134, 2784007713, 213511930, 3666171719, 3713735824, 570870769, 2231830776, 1554341218, 2985036371, 2120289432, 171445355, 3422574720, 1506092472, 1595092727, 846675486, 3276446091, 2719705818, 4119247827, 511210442, 2416191972, 2960932180, 1406812737, 473709555, 3437484482, 1201379765, 3375106560, 1011203594, 3843033248, 2090942959, 4274492859, 3858339017, 305401239, 141075641, 3085549008, 1609507042, 3189704239, 2024844568, 51810256, 238191140, 4045931642, 1835233742, 4255331426, 1768730271, 2343168385, 1569435606, 1304984456, 4053972178, 3042510379, 1715183030, 522056580, 531899892, 2565971810, 3729285704, 679236958, 3155324862, 2866484325, 3008763488, 3697141421, 1002610389, 4185620311, 3571933138, 2299513431, 153326618, 502643612, 3735603128, 3263586666, 4144396962, 2651337427, 4100454671, 1102352789, 3868000056, 1233878305, 3467462226, 3587417001, 1673186395, 3167731748, 3237808426, 3625038718, 3899399541, 116838796, 366982583, 2856877715, 3954053415, 1808150713, 2186966904, 4135046162, 513717067, 3523704565, 560513266, 3836534521, 4230182188, 739328318, 3532675401, 3197816123, 3431120498, 3285235631, 2906129710, 3309473158, 268990707, 3153944340, 420298442, 2655040028, 769190542, 3199046121, 2552862574, 3503402846, 2902722266, 2884348832, 1576048913, 1848754436, 1583492956, 4113039924, 4168616119, 2764495094, 618802219, 3134990836, 4246174469, 1084127029, 751348650, 3907168293, 3219829699, 4190765371, 551642126, 3626522073, 4162988083, 324399665, 380967854, 2585093615, 2180906141, 3625283657, 3800137903, 13991119, 2155472622, 2155774093, 622030628, 1442736754, 1970806076, 759204141, 209491449, 3964065558, 481826519, 256453204, 3554347505, 1672127205, 3016026484, 2555221351, 1373994483, 2912362776, 3687679280, 1466390488, 915127910, 3748219908, 1443695518, 2281153771, 4060149943, 675478236, 32867818, 248988549, 2892642308, 2914989918, 3758841386, 1312485932, 2167184500, 222801702, 3744270248, 2557965905, 3015103559, 3939879317, 3842290107, 1491458225, 3429070238, 163791770, 2656636673, 3355171342, 3334322745, 581864061, 437061973, 733582722, 473333896, 1860425017, 1245771639, 477210324, 2734868759, 828222023, 2173721835, 2895365084, 1832065255, 161124779, 2188798022, 3878120334, 3388801939, 3712250608, 1458897119, 3111329667, 1351718747, 2088010262, 4216531273, 1286954664, 2694868853, 1441728197, 1857210379, 1057640025, 3676175703, 902660331, 1154923192, 3265137822, 3258977308, 3810914534, 2053726249, 234557777, 4103891484, 4083908223, 1102808939, 1536919246, 3298594360, 102979572, 1732671929, 3920164193, 157877592, 1851765860, 2936750113, 4255634317, 1547606444, 3250545051, 3632110887, 3501009098, 1247513365, 3259673774, 3322945570, 127219974, 3687802865, 3153418589, 2945847000, 502594131, 1173398569, 3390392495, 1287139684, 3143475768, 3986612820, 3501834251, 2357122157, 2882229916, 675040996, 75992247, 191304654, 3169757490, 2627309128, 1037489034, 831694113, 2289157368, 814588232, 412944234, 1523548382, 1280062488, 912279418, 4134524876, 3561331126, 2952836061, 391973763, 2171947345, 2803058962, 4219581157, 749403166, 1765714010, 3635570095, 2189556291, 2833029847, 50691004, 4031401715, 988495855, 1975867859, 1285990152, 1906787395, 1657058162, 2623303110, 4460855, 1873551768, 1134531092, 649425076, 3186119327, 2357554526, 2480878696, 1986318134, 2334777297, 2516941077, 3110702662, 775637121, 691059235, 3293158751, 916611588, 2102470845, 440543381, 2122043945, 3299872629, 2447197350, 345838490, 952056422, 3737380636, 3836073069, 2480051526, 2696617729, 1487564431, 1524357662, 1066989902, 1854070813, 3606933446, 2504505722, 1027052576, 886713004, 3966384777, 629819544, 2502533208, 4091395384, 183499480, 2935580005, 4071185399, 2414288862, 4106219877, 1474663394, 547416515, 2156574821, 911188763, 818435665, 1754421967, 684500251, 566140820, 2313681362, 3894954480, 3082332455, 101569154, 4267416930, 1411295468, 2034826130, 2135834550, 2568626914, 2747668541, 3787752642, 1977117047, 4237851309, 2089227413, 3654418612, 1432403748, 2422179291, 1777509197, 3983645652, 1543588653, 2933360645, 3050055960, 3074960094, 1871857415, 2409286493, 2302756883, 4236229597, 1879697196, 4024884993, 1485075691, 590309283, 799266734, 2152390489, 2788575505, 3098150958, 3863364429, 2286350365, 1849538934, 1429560474, 3150859729, 2517189156, 721952961, 2427010059, 4018105464, 239341325, 1090111765, 2847974996, 3963402044, 2078502455, 819767095, 3002777361, 26626817, 1878225427, 3477971299, 556700810, 482097639, 3168172513, 2971104837, 1731824364, 1674077823, 1052685035, 14531894, 1621372517, 780631565, 4004835464, 1577668955, 1844496573, 4248441359, 1120215554, 123325953, 752885209, 1088005680, 2639739158, 213252013, 120914473, 4168629462, 1685359931, 1494535849, 319703818, 4262270752, 235531706, 203791795, 4291818073, 2986617739, 3180977612, 3472448722, 2665256610, 1413942620, 3578346406, 71630198, 3382270940, 1572032557, 4052306710, 979137549, 879471598, 2242835198, 3345416532, 1295638158, 3217276473, 1628940286, 3846385367, 725462666, 1815147120, 1741721172, 1748039107, 3455200354, 2587737613, 332473181, 2109589367, 1311457412, 4185653248, 2370700739, 3480580359, 489778638, 3304822794, 341196562, 1243096869, 3175307630, 1237270306, 4029884052, 683694387, 1913742411, 1587403926, 350837880, 1057382743, 843469358, 1232005660, 2445929269, 3085140141, 2411643855, 1778610160, 1365845422, 2324466381, 2935597392, 632507145, 2537420371, 2912868891, 223052706, 4095548223, 2824493650, 3444734348, 3733394750, 1260169143, 861540270, 835465259, 3623741940, 533822173, 3351246303, 2790966064, 4161566037, 946363984, 307395308, 1913408002, 1113614807, 1360601213, 1390202548, 663998681, 2597539516, 637481144, 2820556439, 824186294, 365295388, 944249314, 903722905, 155662175, 672440150, 1408896573, 3282797134, 610144857, 2515642080, 3442055065, 1516695922, 1173225149, 3884181656, 1363569049, 3963408236, 3627064968, 1570421278, 2739402460, 78723962, 3367629662, 199426279, 3468347165, 3608509525, 3931279583, 2564640181, 868691099, 2581622019, 4260522798, 3465898762, 4073416647, 3369295138, 4179476664, 3805127324, 1527338084, 3325976845, 2906707248, 222431837, 2569466070, 1630714380, 246809401, 559496431, 3668144193, 1615013225, 2862980402, 303506994, 3989332257, 1943313095, 3995932718, 535819414, 1707271089, 3307416185, 2991471979, 4039957684, 1242618052, 2827581004, 666854473, 1371078741, 986025959, 3267739872, 2355522589, 1422744897, 698095966, 3585360514, 2165665102, 2480925110, 174364340, 3462141199, 3486995817, 1314709415, 3792762750, 1323979760, 4147237398, 3552881382, 1750358689, 25370654, 1300310546, 2090406636, 2373606279, 604882297, 867083955, 3252657144, 545765469, 2400383282, 29046100, 3218049764, 1349806938, 1760488404, 1564324224, 2554973906, 214584060, 2423582663, 1842936399, 77666091, 3329399743, 3526188639, 625214673, 1021014022, 1098762163, 1353121452, 4146719507, 1660337852, 743367965, 660842171, 1296213304, 1905952326, 3549231138, 3108395231, 958532497, 1848239991, 134048954, 865953606, 3969874470, 3812383447, 3076548046, 704863629, 4155111087, 2104460204, 1643412691, 3199423424, 3632075197, 97220511, 108174655, 2041700163, 3449831099, 405827140, 508442379, 907483369, 2908229295, 1159974063, 4189530753, 2161194025, 1860914423, 70000089, 1239041264, 1030379370, 313412718, 210876745, 2626252419, 4194607912, 3154233274, 4043050737, 3570338371, 1708032128, 772032136, 1836030671, 2309101058, 1755397995, 51366841, 1268433825, 2991840199, 1373481493, 1635091092, 373555370, 3251606190, 2734152746, 2298107042, 3992922784, 3660874270, 4003491746, 1920760497, 1515733131, 3832202858, 2771494284, 1964991548, 1954015038, 1133935323, 3102778016, 2146840316, 517169168, 366184200, 4182978135, 2874132761, 1279303432, 820840792, 3081439343, 3241059860, 1857904754, 3989441966, 3201435148, 3834105558, 3080811910, 3728986147, 2787079417, 4016533584, 4178500882, 1346507040, 1402054626, 2316227427, 182294507, 373479035, 510963871, 3838176295, 3663912645, 2410375408, 985383593, 344663494, 2542468391, 4157483076, 2196854651, 1678335452, 2492668872, 3632700824, 3611970198, 3536068576, 3074701611, 1309379187, 3125281735, 2307442588, 141971921, 782304183, 9198433, 2682436849, 2066173795, 1121667771, 1555718902, 3167952954, 3005191405, 1198941669, 3026198399, 638154217, 735931579, 1839836455, 3235012406, 1783484065, 2682160941, 2174459606, 2721925162, 3976508920, 1236057956, 2735597091, 4202155251, 914403230, 2130435844, 3662297748, 1475606979, 2229835738, 572187928, 4132958648, 1611004731, 103336474, 4219191972, 4164312923, 3477281808, 3474776027, 1762881398, 3047414394, 2594447346, 3954159490, 2201555488, 204519158, 2197814461, 4209714777, 1423738749, 2155027566, 3800701116, 3947957813, 2199375013, 2117323319, 2754767976, 4003841199, 2589169318, 1586857301, 3829950643, 4195405500, 4178439012, 1361118254, 1904599346, 1221226815, 1151043767, 2913493722, 4004783878, 1878307525, 833330113, 3091321948, 2739566980, 1538811657, 313699025, 1399009251, 1559178441, 233479994, 410794644, 3944560474, 2293255814, 182824700, 150789889, 2834717484, 2569868516, 4085868982, 2173540628, 456991586, 2532307490, 2490868026, 2470765246, 909922886, 347142902, 471165293, 2408404749, 3214975674, 3134763699, 3137834596, 2047159181, 4256592764, 1570273985, 442265476, 3869653389, 669702029, 3245742278, 2061397325, 650389574, 1710659386, 381325535, 3453106113, 3842356333, 697219187, 3870268902, 1051328618, 556056573, 3209970923, 2592924337, 1069292461, 1918262392, 1089122962, 2687888536, 26699763, 1538322861, 1180939959, 904804948, 99817636, 2162936140, 3835727405, 921228004, 1179480255, 1897384771, 28853291, 3907566660, 1613430952, 3564468299, 1239686613, 555206796, 3864734731, 3095950002, 3269088743, 2720336323, 463361991, 29284184, 3952600670, 3974663820, 374869536, 1015147528, 1406932428, 2224101048, 12377689, 3588421789, 3030990595, 3845851903, 3569509358, 895427011, 948557133, 4004116031, 3016306835, 1523243432, 1904281385, 1447154004, 1025242677, 829420000, 3543398557, 245487194, 2418984213, 286167460, 1179631479, 1019309523, 1872820896, 3971354338, 4232365541, 2234444392, 2205742978, 788991714, 1122175341, 3172175672, 3805847238, 1906398206, 2855845213, 3695843824, 751003984, 2739321248, 4170817630, 2336811657, 110654228, 2545690857, 1028124884, 1339728437, 825811919, 1744809042, 643844835, 3898054974, 4151488510, 1042865492, 1101588267, 95409211, 3388807012, 3125560049, 3308139574, 2455294649, 1547217965, 3116952791, 289062940, 1292725861, 1725294274, 2379592986, 2000110994, 3178714620, 3069336247, 2814512441, 765093337, 1683107896, 1662183978, 156191559, 803333180, 1899592838, 2710592116, 76464499, 1170070831, 247477850, 4177285700, 2102278347, 4144698579, 18764388, 1052693064, 3496752313, 822368361, 1904821842, 2838476975, 2824064200, 1084816425, 830380874, 1866693701, 1873949933, 2583534950, 2560271922, 2507469546, 563787708, 72691960, 1495083733, 3292478931, 820973390, 3693515822, 1707076656, 3307589900, 2224673541, 2111332812, 558854092, 3977807931, 539808801, 2097634312, 3565313108, 984386449, 2931005615, 2489185652, 2670806346, 2235750751, 856039251, 1005123064, 902372999, 2315083733, 4136346539, 1823777950, 4220524814, 1479096588, 916090384, 628953069, 3988728168, 4199113414, 185575240, 742926345, 915667656, 2378561861, 576820738, 946379302, 3562376208, 554467224, 4225495744, 3699478632, 2443619664, 94492669, 671172724, 3768491707, 489248152, 1697053139, 796027853, 2627737559, 426752031, 1806703463, 263399799, 3274762101, 2459606407, 1673150840, 2138850413, 2997873959, 2549166475, 3501813433, 2184445602, 703264628, 1111649901, 2355935399, 472225890, 3795203109, 1935701663, 3774174634, 2833148088, 2027427909, 1584580407, 783336210, 2899677050, 1508019500, 848016577, 1665090784, 3988755883, 226753437, 1471254433, 2747438806, 2747332136, 4251975303, 2575209180, 2370190390, 3388192008, 1001231473, 4202599144, 1480430639, 264872714, 1150753378, 1322072688, 475903256, 1193609671, 132392616, 2419080542, 1426144190, 2747435788, 565619832, 269915754, 8706171, 1898187956, 3210527298, 2567374804, 4032850033, 2347111131, 2748231652, 2427401461, 2972811799, 1958314572, 723166844, 3667082753, 3815656736, 1287744578, 3643279308, 1294134314, 3090942973, 2080392831, 329447228, 297806099, 4169236422, 2337155963, 1497028196, 1325143127, 4165813614, 1968500238, 1927806880, 210757072, 717102128, 1537122167, 1048190985, 3437846367, 3615099630, 987835813, 3824400898, 3951469754, 2138794295, 1241942560, 1862190505, 1607506835, 4194930865, 1944971572, 227842456, 3874104869, 4105398614, 3789646543, 2307331029, 3803002369, 1343682944, 3947542833, 2337383738, 3955406112, 1795727209, 1420181440, 3323986304, 714896199, 1260617688, 4035502077, 3956081047, 165332608, 546292116, 1212577785, 789396619, 2246586883, 3735135748, 37822461, 632103394, 691054096, 2779413872, 1933936799, 673303282, 1555234006, 3716678513, 1466066508, 83880536, 983979803, 709926844, 1644725395, 474558041, 2422098504, 637798440, 276597319, 4109798494, 1368782648, 4041420432, 4122000853, 1652948047, 3372226837, 4188387627, 3778617490, 3616270038, 1943862259, 270885474, 2816617219, 1819908164, 3372195426, 3248493243, 2460608344, 3869168830, 1207505847, 1362554737, 2165134835, 1574593464, 2104643850, 3680754435, 3228084551, 3164442407, 987024393, 3424514911, 3020012732, 2430705126, 1883675530, 2715844414, 2642283517, 2393408386, 4193834095, 216412677, 2792759343, 2917248192, 1052637819, 553016942, 2364449207, 3243239014, 1093830618, 1285914493, 2065440490, 548585357, 4234311586, 2977173276, 3278425495, 3473708417, 2382428110, 3719935213, 1029554512, 3770166441, 3032398230, 3643891877, 998101004, 3587125266, 3592706471, 859022194, 3851893326, 885827631, 2618082491, 3465230360, 504915824, 2442274005, 1887576682, 1792297614, 2934158316, 1590899469, 4105950922, 3616784885, 1912256688, 766167404, 1173863702, 1905836114, 2155490294, 3971720342, 1162893424, 3409535264, 4165678373, 1165281733, 724255899, 760021454, 1787710369, 3817734228, 203268801, 3720432653, 1819223929, 1839162912, 2037779055, 2310566195, 579808785, 3502416582, 2028921469, 1441598434, 1526501080, 878588729, 599767789, 1010882067, 3649532718, 1221397081, 1462940534, 3619626269, 729529813, 3374668806, 422562465, 2211147397, 2963370575, 3221247034, 4015126212, 297381234, 4183564372, 939740318, 2611830517, 1096574932, 541011959, 2188242879, 1783580367, 447574367, 2003934559, 2279533547, 2792460002, 2255812646, 3413675186, 580898548, 2229999740, 1096105952, 4244423343, 2935245960, 2254021892, 4163296007, 559478003, 3942857209, 1119963254, 2544484347, 4036705698, 3589160096, 1630423599, 2170477615, 3591187211, 1655689764, 1128785650, 533564648, 995584376, 2386010587, 646223679, 637975734, 3125658035, 4086835803, 881734974, 3965044509, 503517182, 1780731367, 2324255197, 264762062, 3051851940, 1822570831, 2092856474, 3930344837, 2910733392, 690151343, 3083134941, 3525927867, 2216036, 2588605841, 2009111659, 3272096242, 1605450256, 2919537262, 4230888630, 76818604, 3744783779, 2801690509, 1238992268, 2878398840, 3746882099, 3985998978, 3280970869, 3491179263, 380348730, 1657678717, 2934831977, 3071989145, 1133814947, 3483343350, 3087033783, 1146696824, 3954064327, 3779313612, 682331113, 3762102367, 1105315248, 744541178, 3180771490, 4198705492, 1120248603, 3850137932, 2338577224, 1819253145, 649440247, 654987080, 3470072835, 712134453, 3298281108, 1139063469, 23887181, 1569735793, 2333692031, 3611594763, 129452663, 2094749885, 883065966, 3954917082, 578200586, 3500782968, 1934656801, 2883345064, 1931669212, 3147324590, 1464802785, 2965853552, 790501402, 258009254, 2503160616, 2649046567, 3904964681, 1599077734, 3919935570, 1303529763, 3991975809, 3189086331, 1057043550, 3395103804, 2877354301, 2306930273, 3982880750, 2924855815, 2487820297, 2652911164, 3999703772, 2223059040, 1740258037, 803351223, 3981488998, 1064648509, 1360021823, 2337841535, 2146948154, 2440954468, 3130762432, 1813182439, 3074850533, 4283503593, 4270484299, 949490550, 2266372770, 2295246887, 1861688194, 4040174575, 1449464748, 1366853117, 2068858018, 254544809, 3877674561, 3224793088, 3267498751, 2107034611, 563498979, 3449171610, 1195453762, 273177086, 289471273, 616927831, 2074092853, 3899999301, 286740001, 3420933845, 3592214327, 884189525, 222835649, 2225635747, 2188257362, 3190419420, 4025559130, 1478386940, 1558547116, 3231059985, 3442723480, 1257988497, 1230169668, 4204920613, 1680720428, 872302704, 3072235055, 690014443, 2522917836, 514713378, 3021775723, 1321394624, 3884661892, 926882735, 3080333504, 326751408, 3303976139, 4235779168, 2429481693, 1217466369, 3791218516, 2222358465, 1623611345, 2787041527, 4078544859, 1365988909, 3306328170, 3344521067, 4143717872, 2986806940, 761212906, 4154456262, 2789197670, 1624539898, 57869540, 1207526886, 2578669846, 1958234150, 1777451133, 2129169500, 335914812, 4078757930, 3345953932, 150543374, 735284016, 3961834956, 845377072, 2144594832, 1614985729, 1054820689, 2991989080, 3174679142, 2236995668, 62294231, 2873837462, 3142910821, 1199872045, 2601892540, 552738648, 1021074598, 2337595165, 3159932723, 1421373831, 2852138360, 3106767941, 1157694337, 2750128317, 1772017733, 154079587, 141054736, 262862859, 232757713, 221025285, 706028672, 1875436250, 956312777, 2201277682, 3590829191, 1848993676, 4083454028, 3566742977, 3503063328, 1864869341, 3423684506, 1393864104, 2416690788, 2766585002, 2130688952, 3844258502, 3337815280, 3091937789, 349123157, 3807721080, 2444073514, 2451066824, 3998237698, 1140469168, 2919152242, 2217355879, 3278465837, 1742719589, 2157539246, 2811674180, 388712428, 1047685661, 3397021293, 2384054399, 4233122871, 343468428, 1928701525, 3579480071, 905080500, 3365249726, 884089982, 926035997, 2250824413, 3674743698, 1103287857, 2440105975, 616634619, 1923570126, 212857251, 3699939407, 1494175986, 1774922124, 2114576677, 3035124497, 3346065309, 3287177393, 604624215, 2867504980, 634469686, 873242186, 951438535, 4137621355, 2570510799, 2802795193, 2843455931, 767579718, 1890503101, 823769604, 2735068143, 2707525515, 3990479894, 2406919069, 3525918157, 2886294828, 1219864314, 678623495, 2898087551, 3411564190, 3940664382, 652501256, 714531640, 1473865718, 1431021514, 4148189552, 2245159337, 1076941098, 816707811, 1337624501, 297487765, 38600646, 864558622, 2247687860, 4194578366, 1986070170, 2421609970, 1965441963, 145830434, 3241118120, 3157751963, 2400447902, 384736236, 995447386, 1066230612, 1590936359, 2619286511, 2670409058, 1369006695, 4127910546, 3550325184, 3593082767, 3865524409, 2864690582, 2625701841, 2036541147, 3233311212, 4261833975, 2422410440, 2832148170, 1556052639, 215989597, 2416711777, 3463070183, 4177850045, 128323673, 2207385607, 4129145942, 2591595665, 1127555689, 3309249433, 233605789, 4195716420, 1493914608, 450292440, 3106847448, 3325965005, 3474065831, 633209133, 2256155961, 537355112, 562349960, 2920130469, 4257823976, 3194115618, 938036945, 2709711086, 688217007, 2854268270, 570525277, 1074448737, 3022790230, 1408299668, 4264456841, 3634044527, 2475248905, 3407882491, 463826284, 401413402, 2633851237, 2154372447, 2369213365, 3606409779, 555916408, 554764341, 413102912, 268173915, 1243956163, 2236116935, 4256678080, 583906087, 1045370605, 68579465, 3068148389, 1372194493, 3737570643, 1069484043, 4035970320, 3137858625, 2632533173, 1131259704, 1956314450, 2139036495, 1693635173, 1347101027, 297670136, 443676587, 45078526, 9644821, 13024437, 3947779661, 2636099762, 2988059012, 4293595183, 1837930809, 20717789, 2436064584, 2641256380, 1788079499, 487367235, 3952405086, 4293333151, 2001126465, 325450887, 4274005052, 3283754653, 3171965309, 3733966652, 2677265288, 1415645422, 2865801289, 4243528708, 517320369, 2848973825, 4246368793, 4008131504, 3912315722, 75263429, 3901564263, 3163709089, 1915955163, 814314600, 2851014790, 535576064, 2115465923, 791863217, 1513138018, 1817851661, 1430189011, 4026283369, 1273775110, 51363969, 1690706294, 955659596, 1256032279, 4155022186, 3556701285, 2094838304, 2555108598, 3900795263, 2316156865, 2481324589, 2127484379, 3069769195, 3081364624, 4051550903, 3349894137, 4028203007, 2706441518, 1657726911, 2050548647, 3948506061, 514733067, 1245547062, 1253380285, 2573637166, 4106465896, 412749972, 2553016818, 2377954964, 205524185, 1285259001, 3177583366, 1500657131, 2171117540, 3112088774, 4046115004, 3358847120, 3880379733, 1026439335, 2964156688, 1402633360, 832806998, 2662483319, 4181324334, 1074028406, 2451941658, 3177225652, 3621760189, 1874548982, 810317789, 2967519315, 1208802636, 1791699236, 3571146477, 3675119985, 1535945126, 4206799040, 1352166344, 1842547102, 4293941614, 3876325997, 2961520588, 4291024947, 2377690140, 3029882842, 3385028522, 1769584996, 707012955, 1874347097, 1177298139, 567127784, 2932672318, 1359658876, 747935864, 1237299557, 2776872490, 1614516459, 3790384341, 105380764, 60403570, 2028064064, 3360197661, 3778818867, 2554961043, 1815178949, 3990928553, 830885401, 211270252, 3525350720, 3323467237, 3917205905, 1019215603, 4044912638, 531260692, 2490226642, 1538942872, 3984885162, 2095909331, 3397624047, 3141642419, 2359511874, 2416257464, 2152558510, 3304435559, 409172760, 1227269822, 2477906248, 1504972756, 1896065843, 4239329455, 2588059069, 4242041383, 1893351626, 191065276, 491303559, 550803364, 2336149361, 205575547, 2277235038, 3316266813, 3413440406, 592682965, 1167521509, 603267836, 3677750629, 1997620720, 662924749, 2975910429, 399326526, 3566325804, 3744648502, 2769380438, 99343152, 3784246318, 513448785, 2393415065, 422495707, 3451996124, 3755752758, 4238139976, 1256137919, 1929038182, 416741414, 1033632768, 4098162224, 812283983, 2775687609, 473061527, 884032780, 1645375283, 2039912638, 3912362121, 2647404275, 1522690301, 2445104256, 3224841505, 806162779, 2057840740, 3837885470, 378821814, 1838465422, 1718657914, 4119552540, 1297458390, 95059192, 3054019901, 2286395664, 4275269216, 3438586873, 42672948, 3604182870, 3049842594, 1051093617, 3399787737, 4078751625, 1889709174, 1197658687, 2837439980, 4085378267, 2733607213, 2451764203, 1688909613, 4069575565, 326625990, 4253280853, 966786581, 421604840, 327254563, 1528071832, 10462300, 3818080004, 2940970643, 3013330465, 2660097098, 2463359144, 1171642467, 1276891436, 1724827619, 2703108575, 894837839, 3269310186, 475382424, 3662889370, 3594355086, 1516528440, 2451013773, 997304248, 1968670999, 1829941902, 1059902154, 17571430, 576860691, 3670314058, 3602361151, 2098948197, 883466310, 4216409196, 2452232035, 3264668432, 403473066, 2481805251, 3194270322, 2298754401, 2194644105, 3518078865, 873240945, 1134305003, 2718823138, 1935072880, 2982454869, 2259840652, 1962997313, 571550175, 3923923650, 4071690436, 2567657999, 3524990489, 2587473858, 1226545156, 3625555288, 3556467719, 2110084229, 3461707755, 2418321085, 374546082, 3957523870, 224948585, 3030724537, 1587458094, 1553112615, 1495144888, 2084754285, 2082453883, 637245269, 3696621892, 1688129650, 730279191, 3465268303, 1255405508, 1040615754, 810568624, 1668799184, 3442525021, 4140082195, 3028386449, 1523702039, 3605655316, 3570577573, 1507075394, 29511801, 3939152850, 3144976359, 1435969637, 3397347544, 4221009679, 2401616085, 3596889904, 3609628987, 2458799004, 4161626088, 3403711934, 1545958552, 166167265, 3499076534, 3755799521, 1869789413, 2799182131, 1475941476, 4183337562, 1553699990, 551886344, 1396622316, 3796954922, 2471897525, 2588921881, 491219037, 1936711795, 1800777674, 549515442, 2780471991, 1761940382, 1107960962, 3258460594, 4101167737, 762584396, 307636269, 3918528963, 3414785149, 2104232568, 162750571, 2954961311, 1923932531, 1284681664, 3352410700, 1439431743, 2629669571, 2238836884, 4210177312, 3494174832, 3211653097, 912552573, 2474336253, 3573978208, 1057364555, 614776391, 1324746145, 249066267, 3837686961, 2193966233, 340924547, 1102806576, 2983844361, 3529781279, 3367834808, 3382950113, 1309667299, 1090323269, 775712531, 2668006310, 2725521046, 329586582, 2414768443, 1172259265, 2070444509, 3748531265, 3624429180, 3822756442, 2182937819, 626914561, 683265097, 183781819, 3115014037, 1206457943, 261184948, 172603504, 963603907, 116297718, 2855743306, 1783971075, 2293162088, 3030524182, 574274926, 2033701704, 55325736, 1488183704, 581219210, 3449783338, 1279704141, 3006648174, 2991302601, 2132112976, 3234112694, 1817904286, 1936121269, 2727406315, 1183301155, 2903602018, 659536622, 2944731992, 2409868691, 3373266127, 495103010, 1210740340, 2540241558, 2886449017, 3382933128, 775211966, 419822592, 2270163620, 1402243599, 2527473510, 3749362357, 1218685709, 3870335114, 1673723750, 355117338, 1126900312, 3015437466, 992101659, 1472130679, 957991740, 4239133855, 3887118331, 2261380374, 2028837654, 3141065475, 4196104099, 453642977, 69491917, 1330057718, 4179152562, 4107857789, 2125396131, 3765994908, 3681378168, 2598111108, 810493802, 2997165166, 3440220100, 2635968886, 3326491203, 2532338921, 2746426942, 2925062700, 3179436451, 3087566931, 3381995974, 3645951228, 3081265279, 3082214755, 3570053390, 3119031418, 2034695101, 192374580, 912198837, 2109352261, 190830525, 1115967532, 237726305, 4162738665, 1428719284, 2233358430, 1155575897, 2972610565, 3172053941, 2542146091, 1455731394, 3175915255, 2482299510, 3945335119, 2414101673, 310920545, 1312020502, 2335555692, 1250477183, 2678735145, 637556140, 410285385, 1245080894, 329664169, 2363986305, 777907294, 1264914378, 2591577697, 1139226117, 1376439008, 3663618218, 3735999941, 148014699, 1937786323, 2003204549, 3463503815, 4216261183, 2183424674, 4108770158, 1207294525, 4188228135, 2090207882, 1679615060, 4001281264, 1127387594, 3403896653, 2016082475, 840037585, 820318947, 1325022434, 2681082158, 4163024045, 2753175409, 3141650736, 2111643474, 2622216667, 1605419853, 3036795146, 2076521666, 3607996787, 1860969824, 2951256410, 324322002, 3005572564, 2217489733, 841376491, 76563819, 2306858493, 1762304873, 644859256, 2724316491, 968041963, 354106038, 3443116013, 3785347795, 3290263341, 1804296963, 4082496485, 1730333610, 535336840, 344131239, 2921172007, 3212976443, 2178910760, 2089728973, 1551074445, 2595889152, 660413765, 2707363048, 3560363679, 367334559, 1650352065, 181757844, 2757957077, 2465727027, 3526882374, 3051342907, 3974097517, 3799215321, 1727326675, 3606827693, 1251858021, 3644022554, 1324264289, 3523694595, 542893628, 1130017099, 2213365908, 1856876106, 2736148460, 1437757754, 1699569611, 1908229781, 175145590, 88560034, 403821454, 2169375972, 1953512580, 1067810864, 2498758412, 3059308848, 1084385356, 3609111146, 154074856, 2670076756, 3832860747, 3488195097, 3793615554, 3154233107, 829148915, 972017054, 3532896099, 1394043326, 1745342052, 3723773043, 2432449259, 1684610844, 2334315870, 2015323155, 119355700, 1946172831, 902171516, 2666973977, 3280764141, 3863911963, 976100962, 3954221042, 4125369742, 301614008, 873457727, 3054287469, 1474295881, 439505646, 628351466, 3044761275, 4178959217, 3576883954, 2225559639, 3119799456, 4293932528, 294598327, 2636014891, 3151984741, 844906457, 756951325, 1565061935, 2759135208, 2914750231, 335946686, 4053591911, 1306644076, 2867088497, 1925621689, 636330657, 901456329, 2633220805, 1433254352, 2629148402, 4055932742, 702519613, 2731770932, 537755899, 2041341758, 3636947088, 4265420206, 719067811, 1450597050, 1499255908, 698102457, 1867572406, 1247140116, 3796524001, 2241287708, 1597407192, 1676723555, 259493846, 684438679, 4099756632, 1842834018, 3941133149, 1350204237, 2889075141, 1969131420, 1771438289, 1151231640, 2209445833, 3722576031, 3803176863, 953522795, 3347742768, 1061887211, 3708311915, 3593990004, 1167977765, 828280664, 119038264, 302183797, 2981101993, 3970121510, 1231804061, 1707740906, 1274273740, 112377943, 3829779962, 2911412488, 1625730724, 2427113564, 1339177580, 740640082, 109465063, 2804376926, 224774876, 14495342, 3746166469, 3810785443, 4216866731, 3227295475, 843133023, 3860962891, 1282157019, 834330310, 967916332, 2608679422, 3338821092, 2232583570, 2979089228, 3191234183, 2439044458, 58880587, 2140149311, 76254482, 1384425063, 3368409820, 4197084109, 2189549695, 1876658776, 370709836, 4167789283, 1122198992, 3022480384, 862501966, 3109149517, 1288484100, 675690118, 4102231260, 2263994084, 3206960835, 1416626598, 3126235316, 1092247778, 2941811129, 3591527974, 3900742964, 3162371586, 2481483851, 1383268331, 3610895658, 2644555154, 2121256345, 4205854983, 2313559087, 3714845459, 1162578592, 1152343910, 21974893, 1877613671, 3503641460, 1157125657, 3897792353, 1682257288, 1278312892, 2811216685, 2238711941, 2756442767, 1746694256, 2380851297, 455009711, 1559876155, 2714979643, 189725460, 2333833303, 2007575997, 1886996924, 97739722, 2082309058, 1836652900, 1333223437, 1565591222, 1292115745, 1314839493, 4138268668, 3610391999, 3396588894, 1819104170, 1069832449, 4019882623, 1129202117, 1018322743, 2032102993, 2228926898, 1362593766, 988655300, 3625813269, 3797092697, 3541989067, 1136087432, 600961005, 3515063614, 2288318519, 1730805276, 584192093, 2332905361, 3135492088, 2665569047, 1402323662, 3648584422, 4242681354, 868040468, 3687090251, 3891712654, 3741674500, 2414400190, 589221778, 2295398758, 1656931974, 2416678277, 1811181700, 1935067279, 2287397835, 4019946301, 1045675391, 4061487697, 396390504, 981089981, 634459867, 4009720711, 910487098, 1281771789, 737021213, 1350564545, 108626627, 3556994601, 2839574827, 127855259, 14716402, 673997195, 3149898583, 997124220, 3429385172, 537469499, 4283331929, 3568681014, 3005077655, 3625610952, 3831820879, 2396703831, 2351693186, 1718045063, 22515266, 1051945508, 934319527, 1161318636, 1031818079, 1724854168, 2038307849, 3813735308, 446520486, 3906272911, 498217935, 129005616, 3940886270, 3280188771, 2565017665, 2397473022, 1919399688, 3596433229, 3659588424, 192215451, 4114040320, 3639266447, 3730864011, 2338916453, 1477650690, 4091610415, 2785071595, 857115497, 2983851304, 3115229758, 376806224, 2553158862, 1146002735, 2625462473, 4189485248, 237281249, 3598197469, 1027181259, 3784411924, 67203160, 2783469513, 2371642634, 1237235694, 2789060461, 3614521009, 2552957984, 3496002289, 942112758, 663313450, 3668195471, 2422328162, 1690231058, 1241952550, 4235757754, 3280708084, 3608811512, 1364624224, 3910843804, 1278838429, 381458912, 2434384984, 781524834, 4278579487, 802000605, 1241015146, 2292443375, 1324961156, 2548652549, 3467158728, 1271091130, 3202425550, 2191091804, 2179605897, 4099013039, 2127824441, 319480106, 3114849331, 3147437286, 3253695609, 2950724575, 2914122484, 3120761616, 2351082421, 177721330, 2197810508, 709140833, 1989253851, 2493634740, 336779249, 1413220589, 949473005, 1494392105, 2740263730, 2501784403, 4220806161, 3933294228, 1541933957, 3566262720, 434009917, 2279934609, 912550215, 245951768, 218302647, 325459907, 2364228626, 1320321147, 1975318233, 4082548789, 3773543894, 101889398, 1356659502, 4081585714, 3033930576, 1932335743, 4177215091, 2350570326, 1264349611, 1940963484, 2744982985, 2058902147, 2286043998, 1532155570, 2232714445, 623971666, 3500845538, 4001461152, 3102804289, 3747985323, 2632278338, 2623572725, 1099181105, 2129095122, 1396958609, 930365652, 2727081080, 1981259419, 2537562552, 498517317, 3482014832, 1185740029, 3121480370, 1765478484, 3648549704, 1724933006, 3335178704, 3115568496, 961874263, 3970118036, 4122031655, 302743333, 1778266952, 125030821, 2519078260, 3268083827, 3693609103, 43434602, 2113380600, 433971644, 3103058389, 2542373815, 1434919268, 3057243539, 3358332123, 1193637761, 193029813, 2702563964, 339772968, 2738925197, 2784638290, 1899385136, 603938617, 1345134811, 486991224, 2874485578, 4204219025, 1597542264, 1074248689, 984509844, 4167941609, 2381848404, 313653044, 384032373, 3077881229, 3844827855, 1122069313, 2242265217, 3635392782, 1344943788, 1825639354, 2208066605, 3663468475, 692796401, 2331186689, 2016490183, 1088810631, 387839534, 703992647, 572282146, 3674470894, 1383360408, 2613416729, 508217280, 2531182030, 788333147, 458477965, 3015354309, 2399569135, 2736687937, 271512345, 2710115586, 2918699463, 1575429833, 728169406, 212804919, 2426496014, 926502308, 3006915768, 3763410744, 2424022772, 4183352559, 2746319890, 921881192, 3152256318, 1973955117, 2095615106, 3708147068, 1818018474, 948982704, 194925950, 3304721749, 3755537143, 4087860031, 2259098591, 558834084, 2180993286, 3030542193, 585714717, 432440337, 742260317, 2914692478, 2354439062, 1388915005, 3279070310, 2786565964, 499639095, 2414383430, 1778892993, 742869280, 3197848109, 3007221226, 1919446761, 139662818, 2352148533, 2635192414, 816985516, 2882526420, 1209118595, 2974286931, 2509489955, 3728148816, 2067867943, 3093424632, 2158904659, 2015983463, 2954136097, 2619172392, 330943573, 3499812037, 2568442168, 3310969227, 1033699176, 2080514925, 2130560355, 2972087518, 877649428, 237195294, 1628077779, 268278634, 3996156904, 3317657743, 1740192238, 4170517573, 88223419, 3905481708, 3363698028, 498519120, 3625904479, 293203497, 3670985034, 2054541632, 3298725626, 2480593659, 2223776398, 1634347204, 2215844949, 2104841048, 3670995618, 3601255277, 3912366406, 1847441190, 4008054822, 1360293849, 1701300061, 3867389801, 2215311706, 3052888786, 1980513524, 1702529541, 2493432185, 2255860359, 2076780893, 1667830663, 4003910209, 2833684755, 1531188732, 1987865923, 3415289420, 61613019, 3051246731, 2568867322, 2598191743, 394030802, 4091929449, 1887531246, 4187444081, 662091924, 392970282, 165453901, 2704274271, 1493869323, 658786826, 785945344, 510147204, 2901693204, 3423997925, 1198026053, 2692693903, 2059283302, 1742382128, 3424436781, 1390863016, 1044020012, 3994462897, 1961682213, 3190572805, 604285798, 3995695119, 1771261768, 3245100441, 3681080538, 971437554, 3860685960, 279123094, 4238842596, 3405331537, 552167914, 1055008025, 1950134434, 2961646271, 1955302803, 1722485679, 1758190963, 1729359382, 151732431, 2975671854, 247920624, 3388548947, 1553852617, 3655966648, 3293475595, 4136986292, 4125196386, 1761868919, 2084292805, 3742433573, 1850244386, 2206452580, 4156282532, 1346814547, 2820323253, 975032677, 46817533, 2438802842, 2717448888, 816496145, 496096515, 1509137007, 3202912676, 3124438109, 294850928, 76707672, 3576972823, 1434515170, 3797215694, 1139943743, 3191526556, 2676565129, 3057535224, 2781090099, 2408969255, 3940713661, 1925278427, 2418772170, 844586498, 357917292, 1502145715, 3756405733, 2629458815, 2233165797, 624925874, 2292858577, 3949009490, 709906505, 1246333736, 3863077887, 1796645313, 3268312861, 3633646221, 2692509080, 4149887921, 4182468972, 3843101055, 311929642, 400872849, 813964776, 4184855164, 1566874656, 1360324679, 1721466596, 1809473503, 2516710439, 2822530636, 3698913772, 146246892 ]
    
    def __init__(self, seed):
        self.counter = seed % 7823
        self.step = (seed % 17) + 7
        
    def get_double(self):
        self.counter += self.step
        return self.double_constants[self.counter % len(self.double_constants)]
    
    def get_uint32(self):
        self.counter += self.step
        return self.uint32_constants[self.counter % len(self.uint32_constants)]
    
    def get_int8(self):
        self.counter += self.step
        return (self.counter % 0xFF) - 128 
    
def ServiceTest2_create_double_array(gen,len_):
    return numpy.array([gen.get_double() for _ in xrange(len_)])

def ServiceTest2_verify_double_array(gen,a, len_):
    a2=numpy.reshape(a,(a.size,),order="F")
    assert len(a2) == len_
    for d in a2:
        assert gen.get_double() == d

def ServiceTest2_create_uint32_array(gen,len_):
    return [gen.get_uint32() for _ in xrange(len_)]

def ServiceTest2_verify_uint32_array(gen,a, len_):
    assert len(a) == len_
    for d in a:
        assert gen.get_uint32() == d        

def ServiceTest2_create_int8_array(gen,len_):
    return numpy.array([gen.get_int8() for _ in xrange(len_)], dtype=numpy.int8)

def ServiceTest2_verify_int8_array(gen,a, len_):
    assert len(a) == len_
    for d in a:
        assert gen.get_int8() == d

def ServiceTest2_fill_testpod1(seed, obj):        
    gen = ServiceTest2_test_sequence_gen(seed)
    pod_dtype=RobotRaconteurNode.s.GetPodDType('com.robotraconteur.testing.TestService3.testpod1', obj)
    s=numpy.zeros((1,),dtype=pod_dtype)
    s['d1'] = gen.get_double()
    s['d2'] = ServiceTest2_create_double_array(gen, 6)
    d3 = ServiceTest2_create_double_array(gen, (gen.get_uint32() % 6))
    s['d3']['len'] = len(d3)
    s['d3']['array'][0][0:len(d3)] = d3
    s['d4'] = ServiceTest2_create_double_array(gen,9).reshape((3,3), order="F")

    s['s1'] = ServiceTest2_fill_testpod2(gen.get_uint32(), obj)
    s['s2'] = ServiceTest2_create_testpod2_array(gen, 8, obj)
    s3 = ServiceTest2_create_testpod2_array(gen, (gen.get_uint32() % 9), obj)
    s['s3']['len'] = len(s3)
    s['s3']['array'][0][0:len(s3)] = s3 
    s['s4'] = ServiceTest2_create_testpod2_array(gen, 8, obj).reshape((2,4), order="F")
    
    s['t1'] = ServiceTest2_fill_transform(gen.get_uint32(), obj)
    for i in xrange(4):
        s[0]['t2'][i] = ServiceTest2_fill_transform(gen.get_uint32(), obj)
    t3_len = gen.get_uint32() % 15
    s['t3']['len'] = t3_len
    for i in xrange(t3_len):
        s[0]['t3']['array'][i] = ServiceTest2_fill_transform(gen.get_uint32(), obj)
    n_dtype=RobotRaconteurNode.s.GetNamedArrayDType('com.robotraconteur.testing.TestService3.transform', obj)
    t4 = numpy.ndarray((8,), dtype=n_dtype)
    for i in xrange(8):
        t4[i] = ServiceTest2_fill_transform(gen.get_uint32(), obj)
    s['t4'] = t4.reshape((2,4), order="F")
   
    return s

def ServiceTest2_verify_testpod1(s, seed):

    gen = ServiceTest2_test_sequence_gen(seed)
    assert s['d1'] == gen.get_double()
    ServiceTest2_verify_double_array(gen, s['d2'], 6)
    
    ServiceTest2_verify_double_array(gen, s['d3']['array'][0:s['d3']['len']], (gen.get_uint32() % 6))

    ServiceTest2_verify_double_array(gen, s['d4'], 9)     
    ServiceTest2_verify_testpod2(s['s1'], gen.get_uint32())
    ServiceTest2_verify_testpod2_array(gen, s['s2'], 8)
    ServiceTest2_verify_testpod2_array(gen, s['s3']['array'][0:s['s3']['len']], (gen.get_uint32() % 9))
    ServiceTest2_verify_testpod2_array(gen, s['s4'].reshape((8,),order="F"), 8)
    
    ServiceTest2_verify_transform(s['t1'], gen.get_uint32())
    for i in xrange(4):
        ServiceTest2_verify_transform(s['t2'][i], gen.get_uint32())
    t3_len = gen.get_uint32() % 15
    assert s['t3']['len'] == t3_len
    for i in xrange(t3_len):
        ServiceTest2_verify_transform(s['t3']['array'][i], gen.get_uint32())
       
    t4 = s['t4'].flatten(order="F")
    for i in xrange(8):
        ServiceTest2_verify_transform(t4[i], gen.get_uint32())    

def ServiceTest2_fill_testpod2(seed, obj):
    gen = ServiceTest2_test_sequence_gen(seed);
    pod_dtype=RobotRaconteurNode.s.GetPodDType('com.robotraconteur.testing.TestService3.testpod2', obj)
    s=numpy.zeros((1,),dtype=pod_dtype)
    s['i1'] = gen.get_int8()
    s['i2'] = ServiceTest2_create_int8_array(gen, 15)
    i3=ServiceTest2_create_int8_array(gen, (gen.get_uint32() % 15))
    s['i3']['len'] = len(i3)
    s['i3']['array'][0][0:len(i3)] = i3 
    return s

def ServiceTest2_verify_testpod2(s, seed):
    gen = ServiceTest2_test_sequence_gen(seed)
    assert (s['i1'] == gen.get_int8())
    ServiceTest2_verify_int8_array(gen, s['i2'], 15)
    ServiceTest2_verify_int8_array(gen, s['i3']['array'][0:s['i3']['len']], (gen.get_uint32() % 15))

def ServiceTest2_create_testpod1_array(len_, seed, obj):
    pod_dtype=RobotRaconteurNode.s.GetPodDType('com.robotraconteur.testing.TestService3.testpod1', obj)
    s=numpy.zeros((len_,),dtype=pod_dtype)
    gen = ServiceTest2_test_sequence_gen(seed)
    for i in xrange(len_):
        s[i] = ServiceTest2_fill_testpod1(gen.get_uint32(), obj)
    return s
    
def ServiceTest2_verify_testpod1_array(v, len_, seed):

    gen = ServiceTest2_test_sequence_gen(seed)
    assert (len(v) == len_)
    for i in xrange(len_):
        ServiceTest2_verify_testpod1(v[i], gen.get_uint32())
    
def ServiceTest2_create_testpod2_array(gen, len_, obj):
    pod_dtype=RobotRaconteurNode.s.GetPodDType('com.robotraconteur.testing.TestService3.testpod2', obj)
    s=numpy.zeros((len_,),dtype=pod_dtype)
    for i in xrange(len_):
        s[i] = ServiceTest2_fill_testpod2(gen.get_uint32(), obj)
    return s

def ServiceTest2_verify_testpod2_array(gen, v, len_):
    assert (len(v) == len_)
    for i in xrange(len_):    
        ServiceTest2_verify_testpod2(v[i], gen.get_uint32())
   
def ServiceTest2_create_testpod1_multidimarray(m, n, seed, obj):
    gen = ServiceTest2_test_sequence_gen(seed);
    pod_dtype=RobotRaconteurNode.s.GetPodDType('com.robotraconteur.testing.TestService3.testpod1', obj)
    s=numpy.zeros((m*n,),dtype=pod_dtype)
    for i in xrange(m*n):
        s[i] = ServiceTest2_fill_testpod1(gen.get_uint32(), obj)
    
    return s.reshape((m,n), order="F")
    
def ServiceTest2_verify_testpod1_multidimarray(v, m, n, seed):
    assert v.shape == (m,n)
    v2 = v.reshape((m*n,), order="F")    
    ServiceTest2_verify_testpod1_array(v2, m * n, seed)
   
def ServiceTest2_fill_teststruct3(seed, obj):
    o=RobotRaconteurNode.s.NewStructure('com.robotraconteur.testing.TestService3.teststruct3', obj)
    gen = ServiceTest2_test_sequence_gen(seed)   
    o.s1 = ServiceTest2_fill_testpod1(gen.get_uint32(), obj)
    s2_seed = gen.get_uint32()
    o.s2 = ServiceTest2_create_testpod1_array((s2_seed % 17), s2_seed,obj)
    o.s3 = ServiceTest2_create_testpod1_array(11, gen.get_uint32(),obj)
    s4_seed = gen.get_uint32()
    o.s4 = ServiceTest2_create_testpod1_array((s4_seed % 16), s4_seed, obj)
    o.s5 = ServiceTest2_create_testpod1_multidimarray(3, 3, gen.get_uint32(), obj)
    s6_seed = gen.get_uint32()
    o.s6 = ServiceTest2_create_testpod1_multidimarray((s6_seed % 6), (s6_seed % 3), s6_seed, obj)
    o.s7 = []
    o.s7.append(ServiceTest2_fill_testpod1(gen.get_uint32(),obj))
    
    o.s8 =[]
    o.s8.append(ServiceTest2_create_testpod1_array(2, gen.get_uint32(),obj))
    o.s8.append(ServiceTest2_create_testpod1_array(4, gen.get_uint32(),obj))

    o.s9 = []
    o.s9.append(ServiceTest2_create_testpod1_multidimarray(2, 3, gen.get_uint32(),obj))
    o.s9.append(ServiceTest2_create_testpod1_multidimarray(4, 5, gen.get_uint32(),obj))
    
    s10 = ServiceTest2_fill_testpod1(gen.get_uint32(),obj)
    o.s10 = RobotRaconteurVarValue(s10 , 'com.robotraconteur.testing.TestService3.testpod1[]')

    o.s11 = RobotRaconteurVarValue(ServiceTest2_create_testpod1_array(3, gen.get_uint32(),obj) , 'com.robotraconteur.testing.TestService3.testpod1[]')
    o.s12 = RobotRaconteurVarValue(ServiceTest2_create_testpod1_multidimarray(2, 2, gen.get_uint32(), obj), 'com.robotraconteur.testing.TestService3.testpod1[*]')

    s13 = ServiceTest2_fill_testpod1(gen.get_uint32(), obj)
    o.s13 = RobotRaconteurVarValue([s13], 'com.robotraconteur.testing.TestService3.testpod1[]{list}')

    s14 = RobotRaconteurVarValue([], 'com.robotraconteur.testing.TestService3.testpod1[]{list}')
    s14.data.append(ServiceTest2_create_testpod1_array(3, gen.get_uint32(),obj))
    s14.data.append(ServiceTest2_create_testpod1_array(5, gen.get_uint32(),obj))
    o.s14 = s14;

    s15 = RobotRaconteurVarValue([], 'com.robotraconteur.testing.TestService3.testpod1[*]{list}')
    s15.data.append(ServiceTest2_create_testpod1_multidimarray(7, 2, gen.get_uint32(),obj))
    s15.data.append(ServiceTest2_create_testpod1_multidimarray(5, 1, gen.get_uint32(),obj));
    o.s15 = s15;
    
    o.t1 = ServiceTest2_fill_transform(gen.get_uint32(), obj)
    o.t2 = ServiceTest2_create_transform_array(4, gen.get_uint32(),obj)
    o.t3 = ServiceTest2_create_transform_multidimarray(2, 4, gen.get_uint32(), obj)
    
    o.t4 = RobotRaconteurVarValue(ServiceTest2_create_transform_array(10, gen.get_uint32(),obj), 'com.robotraconteur.testing.TestService3.transform[]')
    o.t5 = RobotRaconteurVarValue(ServiceTest2_create_transform_multidimarray(6, 5, gen.get_uint32(), obj), 'com.robotraconteur.testing.TestService3.transform[*]')
    
    o.t6 = [ServiceTest2_fill_transform(gen.get_uint32(), obj)]
    o.t7 = [ServiceTest2_create_transform_array(4, gen.get_uint32(),obj), \
            ServiceTest2_create_transform_array(4, gen.get_uint32(),obj) ]
    
    o.t8 = [ServiceTest2_create_transform_multidimarray(2, 4, gen.get_uint32(), obj), \
            ServiceTest2_create_transform_multidimarray(2, 4, gen.get_uint32(), obj)]
    
    o.t9 = RobotRaconteurVarValue([ServiceTest2_fill_transform(gen.get_uint32(), obj)], 'com.robotraconteur.testing.TestService3.transform{list}')
    
    o.t10 = RobotRaconteurVarValue([ServiceTest2_create_transform_array(3, gen.get_uint32(),obj), \
            ServiceTest2_create_transform_array(5, gen.get_uint32(),obj) ], 'com.robotraconteur.testing.TestService3.transform[]{list}')
    
    o.t11 = RobotRaconteurVarValue([ServiceTest2_create_transform_multidimarray(7, 2, gen.get_uint32(), obj), \
            ServiceTest2_create_transform_multidimarray(5, 1, gen.get_uint32(), obj)], 'com.robotraconteur.testing.TestService3.transform[*]{list}')
    
    
    return o;


def ServiceTest2_verify_teststruct3(v, seed):
    assert v is not None
    gen = ServiceTest2_test_sequence_gen(seed)

    ServiceTest2_verify_testpod1(v.s1[0], gen.get_uint32())
    s2_seed = gen.get_uint32()
    ServiceTest2_verify_testpod1_array(v.s2, (s2_seed % 17), s2_seed)
    ServiceTest2_verify_testpod1_array(v.s3, 11, gen.get_uint32())
    s4_seed = gen.get_uint32();
    ServiceTest2_verify_testpod1_array(v.s4, (s4_seed % 16), s4_seed)
    ServiceTest2_verify_testpod1_multidimarray(v.s5, 3, 3, gen.get_uint32())
    s6_seed = gen.get_uint32()
    ServiceTest2_verify_testpod1_multidimarray(v.s6, (s6_seed % 6), (s6_seed % 3), s6_seed)

    assert v.s7 is not None
    assert len(v.s7) == 1
    s7_0 = v.s7[0]
    ServiceTest2_verify_testpod1(s7_0[0], gen.get_uint32())

    assert v.s8 is not None
    assert len(v.s8)==2            
    ServiceTest2_verify_testpod1_array(v.s8[0], 2, gen.get_uint32())
    ServiceTest2_verify_testpod1_array(v.s8[1], 4, gen.get_uint32())

    assert v.s9 is not None
    assert len(v.s9) == 2
    ServiceTest2_verify_testpod1_multidimarray(v.s9[0], 2, 3, gen.get_uint32())
    ServiceTest2_verify_testpod1_multidimarray(v.s9[1], 4, 5, gen.get_uint32())

    s10 = v.s10.data[0];
    ServiceTest2_verify_testpod1(s10, gen.get_uint32())

    ServiceTest2_verify_testpod1_array(v.s11.data, 3, gen.get_uint32())
    ServiceTest2_verify_testpod1_multidimarray(v.s12.data, 2, 2, gen.get_uint32())

    assert v.s13 is not None
    s13 = v.s13.data[0];
    ServiceTest2_verify_testpod1(s13[0], gen.get_uint32())

    assert  (v.s14 is not None)
    v14 = v.s14.data;
    assert len(v14) == 2
    ServiceTest2_verify_testpod1_array(v14[0], 3, gen.get_uint32())
    ServiceTest2_verify_testpod1_array(v14[1], 5, gen.get_uint32())

    assert v.s15 is not None
    v15 = v.s15.data;
    assert  (len(v15) == 2) 
    ServiceTest2_verify_testpod1_multidimarray(v15[0], 7, 2, gen.get_uint32())
    ServiceTest2_verify_testpod1_multidimarray(v15[1], 5, 1, gen.get_uint32())

    ServiceTest2_verify_transform(v.t1[0], gen.get_uint32())
    ServiceTest2_verify_transform_array(v.t2, 4, gen.get_uint32())
    ServiceTest2_verify_transform_multidimarray(v.t3, 2, 4, gen.get_uint32())
    
    ServiceTest2_verify_transform_array(v.t4.data, 10, gen.get_uint32())
    ServiceTest2_verify_transform_multidimarray(v.t5.data, 6, 5, gen.get_uint32())
    
    assert len(v.t6) == 1
    ServiceTest2_verify_transform(v.t6[0], gen.get_uint32())
    
    assert len(v.t7) == 2
    ServiceTest2_verify_transform_array(v.t7[0], 4, gen.get_uint32())
    ServiceTest2_verify_transform_array(v.t7[1], 4, gen.get_uint32())
    
    assert len(v.t8) == 2
    ServiceTest2_verify_transform_multidimarray(v.t8[0], 2, 4, gen.get_uint32())
    ServiceTest2_verify_transform_multidimarray(v.t8[1], 2, 4, gen.get_uint32())
    
    t9 = v.t9.data
    assert len(t9) == 1
    ServiceTest2_verify_transform(t9[0][0],gen.get_uint32())
    
    t10 = v.t10.data
    assert len(t10) == 2
    ServiceTest2_verify_transform_array(t10[0], 3, gen.get_uint32())
    ServiceTest2_verify_transform_array(t10[1], 5, gen.get_uint32())
    
    t11 = v.t11.data
    assert len(t11) == 2
    ServiceTest2_verify_transform_multidimarray(t11[0], 7, 2, gen.get_uint32())
    ServiceTest2_verify_transform_multidimarray(t11[1], 5, 1, gen.get_uint32())
    
def ServiceTest2_fill_transform(seed, obj):
    gen = ServiceTest2_test_sequence_gen(seed);
    n_dtype=RobotRaconteurNode.s.GetNamedArrayDType('com.robotraconteur.testing.TestService3.transform', obj)
    s=numpy.zeros((1,),dtype=n_dtype)
    s1 = s.view(numpy.float64)
    s1[:] = numpy.array([gen.get_double() for _ in xrange(7)])
    return s

def ServiceTest2_verify_transform(s, seed):
    gen = ServiceTest2_test_sequence_gen(seed)    
    s1 = numpy.atleast_1d(s).view(numpy.float64)
    numpy.testing.assert_allclose(s1, numpy.array([gen.get_double() for _ in xrange(7)]))

def ServiceTest2_create_transform_array(len_, seed, obj):
    gen = ServiceTest2_test_sequence_gen(seed) 
    n_dtype=RobotRaconteurNode.s.GetNamedArrayDType('com.robotraconteur.testing.TestService3.transform', obj)
    s=numpy.zeros((len_,),dtype=n_dtype)
    for i in xrange(len_):
        s[i] = ServiceTest2_fill_transform(gen.get_uint32(), obj)
    return s

def ServiceTest2_verify_transform_array(v, len_, seed):
    gen = ServiceTest2_test_sequence_gen(seed) 
    assert (len(v) == len_)
    for i in xrange(len_):    
        ServiceTest2_verify_transform(v[i], gen.get_uint32())

def ServiceTest2_create_transform_multidimarray(m, n, seed, obj):
    gen = ServiceTest2_test_sequence_gen(seed);
    n_dtype=RobotRaconteurNode.s.GetNamedArrayDType('com.robotraconteur.testing.TestService3.transform', obj)
    s=numpy.zeros((m*n,),dtype=n_dtype)
    for i in xrange(m*n):
        s[i] = ServiceTest2_fill_transform(gen.get_uint32(), obj)
    
    return s.reshape((m,n), order="F")
    
def ServiceTest2_verify_transform_multidimarray(v, m, n, seed):
    assert v.shape == (m,n)
    v2 = v.reshape((m*n,), order="F")    
    ServiceTest2_verify_transform_array(v2, m * n, seed)

class ServiceTestClient3:
    def __init__(self):
        pass
    
    def RunFullTest(self, url):
        self.ConnectService(url)
        
        self.TestProperties()

        self.TestFunctions()
                
        self.DisconnectService()
    
    def ConnectService(self, url):
        self._r = RobotRaconteurNode.s.ConnectService(url)        

    def DisconnectService(self):
        RobotRaconteurNode.s.DisconnectService(self._r)

    def TestProperties(self):
        _ = self._r.d1
        self._r.d1 = 3.0819
        
        try:
            _ = self._r.err
        except InvalidArgumentException as e:
            if e.message != "Test message 1":
                raise Exception()
        else:
            raise Exception()

        try:
            self._r.err = 100
        except InvalidOperationException as e:
            pass
        else:
            raise Exception()

    def TestFunctions(self):

        self._r.f1()
        self._r.f2(247)

        res = self._r.f3(1,2)
        if res != 3:
            raise Exception()

        try:
            self._r.err_func()
        except InvalidOperationException:
            pass
        else:
            raise Exception()

        asynctestexp = RobotRaconteurNode.s.GetExceptionType("com.robotraconteur.testing.TestService5.asynctestexp")
        try:
            self._r.err_func2()
        except asynctestexp:
            pass
        else:
            raise Exception()

class asynctestroot_impl(object):
    def async_get_d1(self,handler):
        RobotRaconteurNode.s.PostToThreadPool(lambda: handler(8.5515,None))

    def async_set_d1(self,value,handler):
        if value != 3.0819:
            raise Exception()
        RobotRaconteurNode.s.PostToThreadPool(lambda: handler(None))

    def async_get_err(self,handler):
        RobotRaconteurNode.s.PostToThreadPool(lambda: handler(None,InvalidArgumentException("Test message 1")))

    def async_set_err(self,val,handler):
        RobotRaconteurNode.s.PostToThreadPool(lambda: handler(InvalidOperationException("")))

    def async_f1(self,handler):
        RobotRaconteurNode.s.PostToThreadPool(lambda: handler(None))
    
    def async_f2(self,a,handler):
        if a != 247:
            RobotRaconteurNode.s.PostToThreadPool(lambda: handler(InvalidArgumentException()))
        RobotRaconteurNode.s.PostToThreadPool(lambda: handler(None))

    def async_f3(self, a, b, handler):
        res = int(a+b)
        RobotRaconteurNode.s.PostToThreadPool(lambda: handler(res,None))

    def async_err_func(self,handler):
        RobotRaconteurNode.s.PostToThreadPool(lambda: handler(InvalidOperationException()))

    def async_err_func2(self,handler):
        asynctestexp = RobotRaconteurNode.s.GetExceptionType("com.robotraconteur.testing.TestService5.asynctestexp")
        RobotRaconteurNode.s.PostToThreadPool(lambda: handler(None,asynctestexp("")))

    

def print_ServiceInfo2(s):
    print ("Name: " + s.Name)
    print ("RootObjectType: " + s.RootObjectType)
    print ("RootObjectImplements: " + str(s.RootObjectImplements))
    print ("ConnectionURL: " + str(s.ConnectionURL))
    print ("Attributes: " + str(s.Attributes))
    print ("NodeID: " + str(s.NodeID))
    print ("NodeName: " + s.NodeName)
    print ("")

def print_NodeInfo2(s):
    print ("NodeID: " + str(s.NodeID))
    print ("NodeName: " + s.NodeName)
    print ("ConnectionURL: " + str(s.ConnectionURL))

def errhandler(err):
    print (err)


if __name__ == '__main__':
    main()
