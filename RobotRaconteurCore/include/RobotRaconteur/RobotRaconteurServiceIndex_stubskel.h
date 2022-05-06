// This file is automatically generated. DO NOT EDIT!

#include "RobotRaconteurServiceIndex.h"
#pragma once

namespace RobotRaconteurServiceIndex
{

class ROBOTRACONTEUR_CORE_API RobotRaconteurServiceIndexFactory : public virtual RobotRaconteur::ServiceFactory
{
  public:
    virtual std::string GetServiceName();
    virtual std::string DefString();
    virtual RR_SHARED_PTR<RobotRaconteur::StructureStub> FindStructureStub(boost::string_ref s);
    virtual RR_INTRUSIVE_PTR<RobotRaconteur::MessageElementNestedElementList> PackStructure(
       const RR_INTRUSIVE_PTR<RobotRaconteur::RRStructure>& structin);
    virtual RR_INTRUSIVE_PTR<RobotRaconteur::RRValue> UnpackStructure(
        const RR_INTRUSIVE_PTR<RobotRaconteur::MessageElementNestedElementList>& mstructin);
    virtual RR_INTRUSIVE_PTR<RobotRaconteur::MessageElementNestedElementList> PackPodArray(
       const RR_INTRUSIVE_PTR<RobotRaconteur::RRPodBaseArray>& structure);
    virtual RR_INTRUSIVE_PTR<RobotRaconteur::RRPodBaseArray> UnpackPodArray(
        const RR_INTRUSIVE_PTR<RobotRaconteur::MessageElementNestedElementList>& structure);
    virtual RR_INTRUSIVE_PTR<RobotRaconteur::MessageElementNestedElementList> PackPodMultiDimArray(
       const RR_INTRUSIVE_PTR<RobotRaconteur::RRPodBaseMultiDimArray>& structure);
    virtual RR_INTRUSIVE_PTR<RobotRaconteur::RRPodBaseMultiDimArray> UnpackPodMultiDimArray(
        const RR_INTRUSIVE_PTR<RobotRaconteur::MessageElementNestedElementList>& structure);
    virtual RR_INTRUSIVE_PTR<RobotRaconteur::MessageElementNestedElementList> PackNamedArray(
       const RR_INTRUSIVE_PTR<RobotRaconteur::RRNamedBaseArray>& structure);
    virtual RR_INTRUSIVE_PTR<RobotRaconteur::RRNamedBaseArray> UnpackNamedArray(
        const RR_INTRUSIVE_PTR<RobotRaconteur::MessageElementNestedElementList>& structure);
    virtual RR_INTRUSIVE_PTR<RobotRaconteur::MessageElementNestedElementList> PackNamedMultiDimArray(
       const RR_INTRUSIVE_PTR<RobotRaconteur::RRNamedBaseMultiDimArray>& structure);
    virtual RR_INTRUSIVE_PTR<RobotRaconteur::RRNamedBaseMultiDimArray> UnpackNamedMultiDimArray(
        const RR_INTRUSIVE_PTR<RobotRaconteur::MessageElementNestedElementList>& structure);
    virtual RR_SHARED_PTR<RobotRaconteur::ServiceStub> CreateStub(boost::string_ref objecttype, boost::string_ref path,
                                                                  const RR_SHARED_PTR<RobotRaconteur::ClientContext>& context);
    virtual RR_SHARED_PTR<RobotRaconteur::ServiceSkel> CreateSkel(boost::string_ref objecttype, boost::string_ref path,
                                                                  const RR_SHARED_PTR<RobotRaconteur::RRObject>& obj,
                                                                  const RR_SHARED_PTR<RobotRaconteur::ServerContext>& context);
    virtual void DownCastAndThrowException(RobotRaconteur::RobotRaconteurException& exp) { throw exp; };
    virtual RR_SHARED_PTR<RobotRaconteur::RobotRaconteurException> DownCastException(
        const RR_SHARED_PTR<RobotRaconteur::RobotRaconteurException>& exp)
    {
        return exp;
    };
};

class NodeInfo_stub : public virtual RobotRaconteur::StructureStub
{
  public:
    NodeInfo_stub(const RR_SHARED_PTR<RobotRaconteur::RobotRaconteurNode>& node) : RobotRaconteur::StructureStub(node) {}
    virtual RR_INTRUSIVE_PTR<RobotRaconteur::MessageElementNestedElementList> PackStructure(
       const RR_INTRUSIVE_PTR<RobotRaconteur::RRValue>& s);
    virtual RR_INTRUSIVE_PTR<RobotRaconteur::RRStructure> UnpackStructure(
        const RR_INTRUSIVE_PTR<RobotRaconteur::MessageElementNestedElementList>& m);
};

class ServiceInfo_stub : public virtual RobotRaconteur::StructureStub
{
  public:
    ServiceInfo_stub(const RR_SHARED_PTR<RobotRaconteur::RobotRaconteurNode>& node) : RobotRaconteur::StructureStub(node) {}
    virtual RR_INTRUSIVE_PTR<RobotRaconteur::MessageElementNestedElementList> PackStructure(
       const RR_INTRUSIVE_PTR<RobotRaconteur::RRValue>& s);
    virtual RR_INTRUSIVE_PTR<RobotRaconteur::RRStructure> UnpackStructure(
        const RR_INTRUSIVE_PTR<RobotRaconteur::MessageElementNestedElementList>& m);
};

class async_ServiceIndex
{
  public:
    virtual void async_GetLocalNodeServices(
        boost::function<void(const RR_INTRUSIVE_PTR<RobotRaconteur::RRMap<int32_t, ServiceInfo> >&,
                             const RR_SHARED_PTR<RobotRaconteur::RobotRaconteurException>&)>
            rr_handler,
        int32_t rr_timeout = RR_TIMEOUT_INFINITE) = 0;

    virtual void async_GetRoutedNodes(boost::function<void(const RR_INTRUSIVE_PTR<RobotRaconteur::RRMap<int32_t, NodeInfo> >&,
                                                           const RR_SHARED_PTR<RobotRaconteur::RobotRaconteurException>&)>
                                          rr_handler,
                                      int32_t rr_timeout = RR_TIMEOUT_INFINITE) = 0;

    virtual void async_GetDetectedNodes(
        boost::function<void(const RR_INTRUSIVE_PTR<RobotRaconteur::RRMap<int32_t, NodeInfo> >&,
                             const RR_SHARED_PTR<RobotRaconteur::RobotRaconteurException>&)>
            rr_handler,
        int32_t rr_timeout = RR_TIMEOUT_INFINITE) = 0;
};
class ServiceIndex_stub : public virtual ServiceIndex,
                          public virtual async_ServiceIndex,
                          public virtual RobotRaconteur::ServiceStub
{
  public:
    ServiceIndex_stub(boost::string_ref path, const RR_SHARED_PTR<RobotRaconteur::ClientContext>& c);

    virtual void RRInitStub();
    virtual RR_INTRUSIVE_PTR<RobotRaconteur::RRMap<int32_t, ServiceInfo> > GetLocalNodeServices();

    virtual RR_INTRUSIVE_PTR<RobotRaconteur::RRMap<int32_t, NodeInfo> > GetRoutedNodes();

    virtual RR_INTRUSIVE_PTR<RobotRaconteur::RRMap<int32_t, NodeInfo> > GetDetectedNodes();

    virtual boost::signals2::signal<void()>& get_LocalNodeServicesChanged();

    virtual void DispatchEvent(const RR_INTRUSIVE_PTR<RobotRaconteur::MessageEntry>& m);
    virtual void DispatchPipeMessage(const RR_INTRUSIVE_PTR<RobotRaconteur::MessageEntry>& m);
    virtual void DispatchWireMessage(const RR_INTRUSIVE_PTR<RobotRaconteur::MessageEntry>& m);
    virtual RR_INTRUSIVE_PTR<RobotRaconteur::MessageEntry> CallbackCall(
        const RR_INTRUSIVE_PTR<RobotRaconteur::MessageEntry>& m);
    virtual void RRClose();

  private:
    boost::signals2::signal<void()> rrvar_LocalNodeServicesChanged;

    virtual void async_GetLocalNodeServices(
        boost::function<void(const RR_INTRUSIVE_PTR<RobotRaconteur::RRMap<int32_t, ServiceInfo> >&,
                             const RR_SHARED_PTR<RobotRaconteur::RobotRaconteurException>&)>
            rr_handler,
        int32_t rr_timeout = RR_TIMEOUT_INFINITE);

  protected:
    virtual void rrend_GetLocalNodeServices(
        const RR_INTRUSIVE_PTR<RobotRaconteur::MessageEntry>& m, const RR_SHARED_PTR<RobotRaconteur::RobotRaconteurException>& err,
        boost::function<void(const RR_INTRUSIVE_PTR<RobotRaconteur::RRMap<int32_t, ServiceInfo> >&,
                             const RR_SHARED_PTR<RobotRaconteur::RobotRaconteurException>&)>
            handler);

  public:
    virtual void async_GetRoutedNodes(boost::function<void(const RR_INTRUSIVE_PTR<RobotRaconteur::RRMap<int32_t, NodeInfo> >&,
                                                           const RR_SHARED_PTR<RobotRaconteur::RobotRaconteurException>&)>
                                          rr_handler,
                                      int32_t rr_timeout = RR_TIMEOUT_INFINITE);

  protected:
    virtual void rrend_GetRoutedNodes(const RR_INTRUSIVE_PTR<RobotRaconteur::MessageEntry>& m,
                                      const RR_SHARED_PTR<RobotRaconteur::RobotRaconteurException>& err,
                                      boost::function<void(const RR_INTRUSIVE_PTR<RobotRaconteur::RRMap<int32_t, NodeInfo> >&,
                                                           const RR_SHARED_PTR<RobotRaconteur::RobotRaconteurException>&)>
                                          handler);

  public:
    virtual void async_GetDetectedNodes(
        boost::function<void(const RR_INTRUSIVE_PTR<RobotRaconteur::RRMap<int32_t, NodeInfo> >&,
                             const RR_SHARED_PTR<RobotRaconteur::RobotRaconteurException>&)>
            rr_handler,
        int32_t rr_timeout = RR_TIMEOUT_INFINITE);

  protected:
    virtual void rrend_GetDetectedNodes(
        const RR_INTRUSIVE_PTR<RobotRaconteur::MessageEntry>& m, const RR_SHARED_PTR<RobotRaconteur::RobotRaconteurException>& err,
        boost::function<void(const RR_INTRUSIVE_PTR<RobotRaconteur::RRMap<int32_t, NodeInfo> >&,
                             const RR_SHARED_PTR<RobotRaconteur::RobotRaconteurException>&)>
            handler);

  public:
    virtual std::string RRType();
};

class ServiceIndex_skel : public virtual RobotRaconteur::ServiceSkel
{
  public:
    virtual void Init(boost::string_ref path, const RR_SHARED_PTR<RobotRaconteur::RRObject>& object,
                      const RR_SHARED_PTR<RobotRaconteur::ServerContext>& context);
    virtual RR_INTRUSIVE_PTR<RobotRaconteur::MessageEntry> CallGetProperty(
        const RR_INTRUSIVE_PTR<RobotRaconteur::MessageEntry>& m);

    virtual RR_INTRUSIVE_PTR<RobotRaconteur::MessageEntry> CallSetProperty(
        const RR_INTRUSIVE_PTR<RobotRaconteur::MessageEntry>& m);

    virtual RR_INTRUSIVE_PTR<RobotRaconteur::MessageEntry> CallFunction(
        const RR_INTRUSIVE_PTR<RobotRaconteur::MessageEntry>& m);

    virtual void ReleaseCastObject();

    virtual void RegisterEvents(const RR_SHARED_PTR<RobotRaconteur::RRObject>& rrobj1);

    virtual void UnregisterEvents(const RR_SHARED_PTR<RobotRaconteur::RRObject>& rrobj1);

    virtual RR_SHARED_PTR<RobotRaconteur::RRObject> GetSubObj(boost::string_ref name, boost::string_ref ind);

    virtual void InitPipeServers(const RR_SHARED_PTR<RobotRaconteur::RRObject>& rrobj1);

    virtual void InitWireServers(const RR_SHARED_PTR<RobotRaconteur::RRObject>& rrobj1);

    virtual void DispatchPipeMessage(const RR_INTRUSIVE_PTR<RobotRaconteur::MessageEntry>& m, uint32_t e);

    virtual void DispatchWireMessage(const RR_INTRUSIVE_PTR<RobotRaconteur::MessageEntry>& m, uint32_t e);

    virtual void InitCallbackServers(const RR_SHARED_PTR<RobotRaconteur::RRObject>& o);

    virtual RR_INTRUSIVE_PTR<RobotRaconteur::MessageEntry> CallPipeFunction(
        const RR_INTRUSIVE_PTR<RobotRaconteur::MessageEntry>& m, uint32_t e);

    virtual RR_INTRUSIVE_PTR<RobotRaconteur::MessageEntry> CallWireFunction(
        const RR_INTRUSIVE_PTR<RobotRaconteur::MessageEntry>& m, uint32_t e);

    virtual RR_SHARED_PTR<void> GetCallbackFunction(uint32_t endpoint, boost::string_ref membername);

    virtual RR_INTRUSIVE_PTR<RobotRaconteur::MessageEntry> CallMemoryFunction(
        const RR_INTRUSIVE_PTR<RobotRaconteur::MessageEntry>& m, const RR_SHARED_PTR<RobotRaconteur::Endpoint>& e);

    virtual std::string GetObjectType();
    virtual RR_SHARED_PTR<RobotRaconteurServiceIndex::ServiceIndex> get_obj();

    void rr_LocalNodeServicesChanged_Handler();

  protected:
    boost::signals2::connection LocalNodeServicesChanged_rrconnection;
    bool rr_InitPipeServersRun;
    bool rr_InitWireServersRun;

  public:
  private:
};

} // namespace RobotRaconteurServiceIndex
