//This file is automatically generated. DO NOT EDIT!
package com.robotraconteur.testing.TestService1;
import java.util.*;
import com.robotraconteur.*;
public class teststruct1_stub implements IStructureStub {
    public teststruct1_stub(com__robotraconteur__testing__TestService1Factory d) {def=d;}
    private com__robotraconteur__testing__TestService1Factory def;
    public MessageElementNestedElementList packStructure(Object s1) {
    vectorptr_messageelement m=new vectorptr_messageelement();
    try {
    if (s1 ==null) return null;
    teststruct1 s = (teststruct1)s1;
    MessageElementUtil.addMessageElementDispose(m,MessageElementUtil.<double[]>packArray("dat1",s.dat1));
    MessageElementUtil.addMessageElementDispose(m,MessageElementUtil.packString("str2",s.str2));
    MessageElementUtil.addMessageElementDispose(m,MessageElementUtil.<Integer,String>packMapType("vec3",s.vec3,Integer.class,String.class));
    MessageElementUtil.addMessageElementDispose(m,MessageElementUtil.<String,String>packMapType("dict4",s.dict4,String.class,String.class));
    MessageElementUtil.addMessageElementDispose(m,MessageElementUtil.<String>packListType("list5",s.list5,String.class));
    MessageElementUtil.addMessageElementDispose(m,MessageElementUtil.packStructure("struct1",s.struct1));
    MessageElementUtil.addMessageElementDispose(m,MessageElementUtil.<String,teststruct2>packMapType("dstruct2",s.dstruct2,String.class,teststruct2.class));
    MessageElementUtil.addMessageElementDispose(m,MessageElementUtil.<teststruct2>packListType("lstruct3",s.lstruct3,teststruct2.class));
    MessageElementUtil.addMessageElementDispose(m,MessageElementUtil.packMultiDimArray("multidimarray",(MultiDimArray)s.multidimarray));
    MessageElementUtil.addMessageElementDispose(m,MessageElementUtil.packVarType("var3",s.var3));
    return new MessageElementNestedElementList(DataTypes.DataTypes_structure_t,"com.robotraconteur.testing.TestService1.teststruct1",m);
    }
    finally {
    m.delete();
    }
    }
    public <T> T unpackStructure(MessageElementData m) {
    if (m == null ) return null;
    MessageElementNestedElementList m2 = (MessageElementNestedElementList)m;
    vectorptr_messageelement mm=m2.getElements();
    try {
    teststruct1 s=new teststruct1();
    s.dat1 =MessageElementUtil.<double[]>unpackArray(MessageElement.findElement(mm,"dat1"));
    s.str2 =MessageElementUtil.unpackString(MessageElement.findElement(mm,"str2"));
    s.vec3 =MessageElementUtil.<Integer,String>unpackMapType(MessageElement.findElement(mm,"vec3"));
    s.dict4 =MessageElementUtil.<String,String>unpackMapType(MessageElement.findElement(mm,"dict4"));
    s.list5 =MessageElementUtil.<String>unpackListType(MessageElement.findElement(mm,"list5"));
    s.struct1 =MessageElementUtil.<teststruct2>unpackStructure(MessageElement.findElement(mm,"struct1"));
    s.dstruct2 =MessageElementUtil.<String,teststruct2>unpackMapType(MessageElement.findElement(mm,"dstruct2"));
    s.lstruct3 =MessageElementUtil.<teststruct2>unpackListType(MessageElement.findElement(mm,"lstruct3"));
    s.multidimarray =MessageElementUtil.unpackMultiDimArray(MessageElement.findElement(mm,"multidimarray"));
    s.var3 =MessageElementUtil.unpackVarType(MessageElement.findElement(mm,"var3"));
    T st; try {st=(T)s;} catch (Exception e) {throw new RuntimeException(new DataTypeMismatchException("Wrong structuretype"));}
    return st;
    }
    finally {
    if (mm!=null) mm.delete();
    }
    }
}
