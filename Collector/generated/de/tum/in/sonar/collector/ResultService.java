/**
 * Autogenerated by Thrift Compiler (0.8.0)
 *
 * DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
 *  @generated
 */
package de.tum.in.sonar.collector;

import org.apache.thrift.scheme.IScheme;
import org.apache.thrift.scheme.SchemeFactory;
import org.apache.thrift.scheme.StandardScheme;

import org.apache.thrift.scheme.TupleScheme;
import org.apache.thrift.protocol.TTupleProtocol;
import java.util.List;
import java.util.ArrayList;
import java.util.Map;
import java.util.HashMap;
import java.util.EnumMap;
import java.util.Set;
import java.util.HashSet;
import java.util.EnumSet;
import java.util.Collections;
import java.util.BitSet;
import java.nio.ByteBuffer;
import java.util.Arrays;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ResultService {

  public interface Iface {

    public void writeResults(Identifier id, File file) throws org.apache.thrift.TException;

  }

  public interface AsyncIface {

    public void writeResults(Identifier id, File file, org.apache.thrift.async.AsyncMethodCallback<AsyncClient.writeResults_call> resultHandler) throws org.apache.thrift.TException;

  }

  public static class Client extends org.apache.thrift.TServiceClient implements Iface {
    public static class Factory implements org.apache.thrift.TServiceClientFactory<Client> {
      public Factory() {}
      public Client getClient(org.apache.thrift.protocol.TProtocol prot) {
        return new Client(prot);
      }
      public Client getClient(org.apache.thrift.protocol.TProtocol iprot, org.apache.thrift.protocol.TProtocol oprot) {
        return new Client(iprot, oprot);
      }
    }

    public Client(org.apache.thrift.protocol.TProtocol prot)
    {
      super(prot, prot);
    }

    public Client(org.apache.thrift.protocol.TProtocol iprot, org.apache.thrift.protocol.TProtocol oprot) {
      super(iprot, oprot);
    }

    public void writeResults(Identifier id, File file) throws org.apache.thrift.TException
    {
      send_writeResults(id, file);
      recv_writeResults();
    }

    public void send_writeResults(Identifier id, File file) throws org.apache.thrift.TException
    {
      writeResults_args args = new writeResults_args();
      args.setId(id);
      args.setFile(file);
      sendBase("writeResults", args);
    }

    public void recv_writeResults() throws org.apache.thrift.TException
    {
      writeResults_result result = new writeResults_result();
      receiveBase(result, "writeResults");
      return;
    }

  }
  public static class AsyncClient extends org.apache.thrift.async.TAsyncClient implements AsyncIface {
    public static class Factory implements org.apache.thrift.async.TAsyncClientFactory<AsyncClient> {
      private org.apache.thrift.async.TAsyncClientManager clientManager;
      private org.apache.thrift.protocol.TProtocolFactory protocolFactory;
      public Factory(org.apache.thrift.async.TAsyncClientManager clientManager, org.apache.thrift.protocol.TProtocolFactory protocolFactory) {
        this.clientManager = clientManager;
        this.protocolFactory = protocolFactory;
      }
      public AsyncClient getAsyncClient(org.apache.thrift.transport.TNonblockingTransport transport) {
        return new AsyncClient(protocolFactory, clientManager, transport);
      }
    }

    public AsyncClient(org.apache.thrift.protocol.TProtocolFactory protocolFactory, org.apache.thrift.async.TAsyncClientManager clientManager, org.apache.thrift.transport.TNonblockingTransport transport) {
      super(protocolFactory, clientManager, transport);
    }

    public void writeResults(Identifier id, File file, org.apache.thrift.async.AsyncMethodCallback<writeResults_call> resultHandler) throws org.apache.thrift.TException {
      checkReady();
      writeResults_call method_call = new writeResults_call(id, file, resultHandler, this, ___protocolFactory, ___transport);
      this.___currentMethod = method_call;
      ___manager.call(method_call);
    }

    public static class writeResults_call extends org.apache.thrift.async.TAsyncMethodCall {
      private Identifier id;
      private File file;
      public writeResults_call(Identifier id, File file, org.apache.thrift.async.AsyncMethodCallback<writeResults_call> resultHandler, org.apache.thrift.async.TAsyncClient client, org.apache.thrift.protocol.TProtocolFactory protocolFactory, org.apache.thrift.transport.TNonblockingTransport transport) throws org.apache.thrift.TException {
        super(client, protocolFactory, transport, resultHandler, false);
        this.id = id;
        this.file = file;
      }

      public void write_args(org.apache.thrift.protocol.TProtocol prot) throws org.apache.thrift.TException {
        prot.writeMessageBegin(new org.apache.thrift.protocol.TMessage("writeResults", org.apache.thrift.protocol.TMessageType.CALL, 0));
        writeResults_args args = new writeResults_args();
        args.setId(id);
        args.setFile(file);
        args.write(prot);
        prot.writeMessageEnd();
      }

      public void getResult() throws org.apache.thrift.TException {
        if (getState() != org.apache.thrift.async.TAsyncMethodCall.State.RESPONSE_READ) {
          throw new IllegalStateException("Method call not finished!");
        }
        org.apache.thrift.transport.TMemoryInputTransport memoryTransport = new org.apache.thrift.transport.TMemoryInputTransport(getFrameBuffer().array());
        org.apache.thrift.protocol.TProtocol prot = client.getProtocolFactory().getProtocol(memoryTransport);
        (new Client(prot)).recv_writeResults();
      }
    }

  }

  public static class Processor<I extends Iface> extends org.apache.thrift.TBaseProcessor<I> implements org.apache.thrift.TProcessor {
    private static final Logger LOGGER = LoggerFactory.getLogger(Processor.class.getName());
    public Processor(I iface) {
      super(iface, getProcessMap(new HashMap<String, org.apache.thrift.ProcessFunction<I, ? extends org.apache.thrift.TBase>>()));
    }

    protected Processor(I iface, Map<String,  org.apache.thrift.ProcessFunction<I, ? extends  org.apache.thrift.TBase>> processMap) {
      super(iface, getProcessMap(processMap));
    }

    private static <I extends Iface> Map<String,  org.apache.thrift.ProcessFunction<I, ? extends  org.apache.thrift.TBase>> getProcessMap(Map<String,  org.apache.thrift.ProcessFunction<I, ? extends  org.apache.thrift.TBase>> processMap) {
      processMap.put("writeResults", new writeResults());
      return processMap;
    }

    private static class writeResults<I extends Iface> extends org.apache.thrift.ProcessFunction<I, writeResults_args> {
      public writeResults() {
        super("writeResults");
      }

      protected writeResults_args getEmptyArgsInstance() {
        return new writeResults_args();
      }

      protected writeResults_result getResult(I iface, writeResults_args args) throws org.apache.thrift.TException {
        writeResults_result result = new writeResults_result();
        iface.writeResults(args.id, args.file);
        return result;
      }
    }

  }

  public static class writeResults_args implements org.apache.thrift.TBase<writeResults_args, writeResults_args._Fields>, java.io.Serializable, Cloneable   {
    private static final org.apache.thrift.protocol.TStruct STRUCT_DESC = new org.apache.thrift.protocol.TStruct("writeResults_args");

    private static final org.apache.thrift.protocol.TField ID_FIELD_DESC = new org.apache.thrift.protocol.TField("id", org.apache.thrift.protocol.TType.STRUCT, (short)1);
    private static final org.apache.thrift.protocol.TField FILE_FIELD_DESC = new org.apache.thrift.protocol.TField("file", org.apache.thrift.protocol.TType.STRUCT, (short)2);

    private static final Map<Class<? extends IScheme>, SchemeFactory> schemes = new HashMap<Class<? extends IScheme>, SchemeFactory>();
    static {
      schemes.put(StandardScheme.class, new writeResults_argsStandardSchemeFactory());
      schemes.put(TupleScheme.class, new writeResults_argsTupleSchemeFactory());
    }

    public Identifier id; // required
    public File file; // required

    /** The set of fields this struct contains, along with convenience methods for finding and manipulating them. */
    public enum _Fields implements org.apache.thrift.TFieldIdEnum {
      ID((short)1, "id"),
      FILE((short)2, "file");

      private static final Map<String, _Fields> byName = new HashMap<String, _Fields>();

      static {
        for (_Fields field : EnumSet.allOf(_Fields.class)) {
          byName.put(field.getFieldName(), field);
        }
      }

      /**
       * Find the _Fields constant that matches fieldId, or null if its not found.
       */
      public static _Fields findByThriftId(int fieldId) {
        switch(fieldId) {
          case 1: // ID
            return ID;
          case 2: // FILE
            return FILE;
          default:
            return null;
        }
      }

      /**
       * Find the _Fields constant that matches fieldId, throwing an exception
       * if it is not found.
       */
      public static _Fields findByThriftIdOrThrow(int fieldId) {
        _Fields fields = findByThriftId(fieldId);
        if (fields == null) throw new IllegalArgumentException("Field " + fieldId + " doesn't exist!");
        return fields;
      }

      /**
       * Find the _Fields constant that matches name, or null if its not found.
       */
      public static _Fields findByName(String name) {
        return byName.get(name);
      }

      private final short _thriftId;
      private final String _fieldName;

      _Fields(short thriftId, String fieldName) {
        _thriftId = thriftId;
        _fieldName = fieldName;
      }

      public short getThriftFieldId() {
        return _thriftId;
      }

      public String getFieldName() {
        return _fieldName;
      }
    }

    // isset id assignments
    public static final Map<_Fields, org.apache.thrift.meta_data.FieldMetaData> metaDataMap;
    static {
      Map<_Fields, org.apache.thrift.meta_data.FieldMetaData> tmpMap = new EnumMap<_Fields, org.apache.thrift.meta_data.FieldMetaData>(_Fields.class);
      tmpMap.put(_Fields.ID, new org.apache.thrift.meta_data.FieldMetaData("id", org.apache.thrift.TFieldRequirementType.DEFAULT, 
          new org.apache.thrift.meta_data.StructMetaData(org.apache.thrift.protocol.TType.STRUCT, Identifier.class)));
      tmpMap.put(_Fields.FILE, new org.apache.thrift.meta_data.FieldMetaData("file", org.apache.thrift.TFieldRequirementType.DEFAULT, 
          new org.apache.thrift.meta_data.StructMetaData(org.apache.thrift.protocol.TType.STRUCT, File.class)));
      metaDataMap = Collections.unmodifiableMap(tmpMap);
      org.apache.thrift.meta_data.FieldMetaData.addStructMetaDataMap(writeResults_args.class, metaDataMap);
    }

    public writeResults_args() {
    }

    public writeResults_args(
      Identifier id,
      File file)
    {
      this();
      this.id = id;
      this.file = file;
    }

    /**
     * Performs a deep copy on <i>other</i>.
     */
    public writeResults_args(writeResults_args other) {
      if (other.isSetId()) {
        this.id = new Identifier(other.id);
      }
      if (other.isSetFile()) {
        this.file = new File(other.file);
      }
    }

    public writeResults_args deepCopy() {
      return new writeResults_args(this);
    }

    @Override
    public void clear() {
      this.id = null;
      this.file = null;
    }

    public Identifier getId() {
      return this.id;
    }

    public writeResults_args setId(Identifier id) {
      this.id = id;
      return this;
    }

    public void unsetId() {
      this.id = null;
    }

    /** Returns true if field id is set (has been assigned a value) and false otherwise */
    public boolean isSetId() {
      return this.id != null;
    }

    public void setIdIsSet(boolean value) {
      if (!value) {
        this.id = null;
      }
    }

    public File getFile() {
      return this.file;
    }

    public writeResults_args setFile(File file) {
      this.file = file;
      return this;
    }

    public void unsetFile() {
      this.file = null;
    }

    /** Returns true if field file is set (has been assigned a value) and false otherwise */
    public boolean isSetFile() {
      return this.file != null;
    }

    public void setFileIsSet(boolean value) {
      if (!value) {
        this.file = null;
      }
    }

    public void setFieldValue(_Fields field, Object value) {
      switch (field) {
      case ID:
        if (value == null) {
          unsetId();
        } else {
          setId((Identifier)value);
        }
        break;

      case FILE:
        if (value == null) {
          unsetFile();
        } else {
          setFile((File)value);
        }
        break;

      }
    }

    public Object getFieldValue(_Fields field) {
      switch (field) {
      case ID:
        return getId();

      case FILE:
        return getFile();

      }
      throw new IllegalStateException();
    }

    /** Returns true if field corresponding to fieldID is set (has been assigned a value) and false otherwise */
    public boolean isSet(_Fields field) {
      if (field == null) {
        throw new IllegalArgumentException();
      }

      switch (field) {
      case ID:
        return isSetId();
      case FILE:
        return isSetFile();
      }
      throw new IllegalStateException();
    }

    @Override
    public boolean equals(Object that) {
      if (that == null)
        return false;
      if (that instanceof writeResults_args)
        return this.equals((writeResults_args)that);
      return false;
    }

    public boolean equals(writeResults_args that) {
      if (that == null)
        return false;

      boolean this_present_id = true && this.isSetId();
      boolean that_present_id = true && that.isSetId();
      if (this_present_id || that_present_id) {
        if (!(this_present_id && that_present_id))
          return false;
        if (!this.id.equals(that.id))
          return false;
      }

      boolean this_present_file = true && this.isSetFile();
      boolean that_present_file = true && that.isSetFile();
      if (this_present_file || that_present_file) {
        if (!(this_present_file && that_present_file))
          return false;
        if (!this.file.equals(that.file))
          return false;
      }

      return true;
    }

    @Override
    public int hashCode() {
      return 0;
    }

    public int compareTo(writeResults_args other) {
      if (!getClass().equals(other.getClass())) {
        return getClass().getName().compareTo(other.getClass().getName());
      }

      int lastComparison = 0;
      writeResults_args typedOther = (writeResults_args)other;

      lastComparison = Boolean.valueOf(isSetId()).compareTo(typedOther.isSetId());
      if (lastComparison != 0) {
        return lastComparison;
      }
      if (isSetId()) {
        lastComparison = org.apache.thrift.TBaseHelper.compareTo(this.id, typedOther.id);
        if (lastComparison != 0) {
          return lastComparison;
        }
      }
      lastComparison = Boolean.valueOf(isSetFile()).compareTo(typedOther.isSetFile());
      if (lastComparison != 0) {
        return lastComparison;
      }
      if (isSetFile()) {
        lastComparison = org.apache.thrift.TBaseHelper.compareTo(this.file, typedOther.file);
        if (lastComparison != 0) {
          return lastComparison;
        }
      }
      return 0;
    }

    public _Fields fieldForId(int fieldId) {
      return _Fields.findByThriftId(fieldId);
    }

    public void read(org.apache.thrift.protocol.TProtocol iprot) throws org.apache.thrift.TException {
      schemes.get(iprot.getScheme()).getScheme().read(iprot, this);
    }

    public void write(org.apache.thrift.protocol.TProtocol oprot) throws org.apache.thrift.TException {
      schemes.get(oprot.getScheme()).getScheme().write(oprot, this);
    }

    @Override
    public String toString() {
      StringBuilder sb = new StringBuilder("writeResults_args(");
      boolean first = true;

      sb.append("id:");
      if (this.id == null) {
        sb.append("null");
      } else {
        sb.append(this.id);
      }
      first = false;
      if (!first) sb.append(", ");
      sb.append("file:");
      if (this.file == null) {
        sb.append("null");
      } else {
        sb.append(this.file);
      }
      first = false;
      sb.append(")");
      return sb.toString();
    }

    public void validate() throws org.apache.thrift.TException {
      // check for required fields
    }

    private void writeObject(java.io.ObjectOutputStream out) throws java.io.IOException {
      try {
        write(new org.apache.thrift.protocol.TCompactProtocol(new org.apache.thrift.transport.TIOStreamTransport(out)));
      } catch (org.apache.thrift.TException te) {
        throw new java.io.IOException(te);
      }
    }

    private void readObject(java.io.ObjectInputStream in) throws java.io.IOException, ClassNotFoundException {
      try {
        read(new org.apache.thrift.protocol.TCompactProtocol(new org.apache.thrift.transport.TIOStreamTransport(in)));
      } catch (org.apache.thrift.TException te) {
        throw new java.io.IOException(te);
      }
    }

    private static class writeResults_argsStandardSchemeFactory implements SchemeFactory {
      public writeResults_argsStandardScheme getScheme() {
        return new writeResults_argsStandardScheme();
      }
    }

    private static class writeResults_argsStandardScheme extends StandardScheme<writeResults_args> {

      public void read(org.apache.thrift.protocol.TProtocol iprot, writeResults_args struct) throws org.apache.thrift.TException {
        org.apache.thrift.protocol.TField schemeField;
        iprot.readStructBegin();
        while (true)
        {
          schemeField = iprot.readFieldBegin();
          if (schemeField.type == org.apache.thrift.protocol.TType.STOP) { 
            break;
          }
          switch (schemeField.id) {
            case 1: // ID
              if (schemeField.type == org.apache.thrift.protocol.TType.STRUCT) {
                struct.id = new Identifier();
                struct.id.read(iprot);
                struct.setIdIsSet(true);
              } else { 
                org.apache.thrift.protocol.TProtocolUtil.skip(iprot, schemeField.type);
              }
              break;
            case 2: // FILE
              if (schemeField.type == org.apache.thrift.protocol.TType.STRUCT) {
                struct.file = new File();
                struct.file.read(iprot);
                struct.setFileIsSet(true);
              } else { 
                org.apache.thrift.protocol.TProtocolUtil.skip(iprot, schemeField.type);
              }
              break;
            default:
              org.apache.thrift.protocol.TProtocolUtil.skip(iprot, schemeField.type);
          }
          iprot.readFieldEnd();
        }
        iprot.readStructEnd();

        // check for required fields of primitive type, which can't be checked in the validate method
        struct.validate();
      }

      public void write(org.apache.thrift.protocol.TProtocol oprot, writeResults_args struct) throws org.apache.thrift.TException {
        struct.validate();

        oprot.writeStructBegin(STRUCT_DESC);
        if (struct.id != null) {
          oprot.writeFieldBegin(ID_FIELD_DESC);
          struct.id.write(oprot);
          oprot.writeFieldEnd();
        }
        if (struct.file != null) {
          oprot.writeFieldBegin(FILE_FIELD_DESC);
          struct.file.write(oprot);
          oprot.writeFieldEnd();
        }
        oprot.writeFieldStop();
        oprot.writeStructEnd();
      }

    }

    private static class writeResults_argsTupleSchemeFactory implements SchemeFactory {
      public writeResults_argsTupleScheme getScheme() {
        return new writeResults_argsTupleScheme();
      }
    }

    private static class writeResults_argsTupleScheme extends TupleScheme<writeResults_args> {

      @Override
      public void write(org.apache.thrift.protocol.TProtocol prot, writeResults_args struct) throws org.apache.thrift.TException {
        TTupleProtocol oprot = (TTupleProtocol) prot;
        BitSet optionals = new BitSet();
        if (struct.isSetId()) {
          optionals.set(0);
        }
        if (struct.isSetFile()) {
          optionals.set(1);
        }
        oprot.writeBitSet(optionals, 2);
        if (struct.isSetId()) {
          struct.id.write(oprot);
        }
        if (struct.isSetFile()) {
          struct.file.write(oprot);
        }
      }

      @Override
      public void read(org.apache.thrift.protocol.TProtocol prot, writeResults_args struct) throws org.apache.thrift.TException {
        TTupleProtocol iprot = (TTupleProtocol) prot;
        BitSet incoming = iprot.readBitSet(2);
        if (incoming.get(0)) {
          struct.id = new Identifier();
          struct.id.read(iprot);
          struct.setIdIsSet(true);
        }
        if (incoming.get(1)) {
          struct.file = new File();
          struct.file.read(iprot);
          struct.setFileIsSet(true);
        }
      }
    }

  }

  public static class writeResults_result implements org.apache.thrift.TBase<writeResults_result, writeResults_result._Fields>, java.io.Serializable, Cloneable   {
    private static final org.apache.thrift.protocol.TStruct STRUCT_DESC = new org.apache.thrift.protocol.TStruct("writeResults_result");


    private static final Map<Class<? extends IScheme>, SchemeFactory> schemes = new HashMap<Class<? extends IScheme>, SchemeFactory>();
    static {
      schemes.put(StandardScheme.class, new writeResults_resultStandardSchemeFactory());
      schemes.put(TupleScheme.class, new writeResults_resultTupleSchemeFactory());
    }


    /** The set of fields this struct contains, along with convenience methods for finding and manipulating them. */
    public enum _Fields implements org.apache.thrift.TFieldIdEnum {
;

      private static final Map<String, _Fields> byName = new HashMap<String, _Fields>();

      static {
        for (_Fields field : EnumSet.allOf(_Fields.class)) {
          byName.put(field.getFieldName(), field);
        }
      }

      /**
       * Find the _Fields constant that matches fieldId, or null if its not found.
       */
      public static _Fields findByThriftId(int fieldId) {
        switch(fieldId) {
          default:
            return null;
        }
      }

      /**
       * Find the _Fields constant that matches fieldId, throwing an exception
       * if it is not found.
       */
      public static _Fields findByThriftIdOrThrow(int fieldId) {
        _Fields fields = findByThriftId(fieldId);
        if (fields == null) throw new IllegalArgumentException("Field " + fieldId + " doesn't exist!");
        return fields;
      }

      /**
       * Find the _Fields constant that matches name, or null if its not found.
       */
      public static _Fields findByName(String name) {
        return byName.get(name);
      }

      private final short _thriftId;
      private final String _fieldName;

      _Fields(short thriftId, String fieldName) {
        _thriftId = thriftId;
        _fieldName = fieldName;
      }

      public short getThriftFieldId() {
        return _thriftId;
      }

      public String getFieldName() {
        return _fieldName;
      }
    }
    public static final Map<_Fields, org.apache.thrift.meta_data.FieldMetaData> metaDataMap;
    static {
      Map<_Fields, org.apache.thrift.meta_data.FieldMetaData> tmpMap = new EnumMap<_Fields, org.apache.thrift.meta_data.FieldMetaData>(_Fields.class);
      metaDataMap = Collections.unmodifiableMap(tmpMap);
      org.apache.thrift.meta_data.FieldMetaData.addStructMetaDataMap(writeResults_result.class, metaDataMap);
    }

    public writeResults_result() {
    }

    /**
     * Performs a deep copy on <i>other</i>.
     */
    public writeResults_result(writeResults_result other) {
    }

    public writeResults_result deepCopy() {
      return new writeResults_result(this);
    }

    @Override
    public void clear() {
    }

    public void setFieldValue(_Fields field, Object value) {
      switch (field) {
      }
    }

    public Object getFieldValue(_Fields field) {
      switch (field) {
      }
      throw new IllegalStateException();
    }

    /** Returns true if field corresponding to fieldID is set (has been assigned a value) and false otherwise */
    public boolean isSet(_Fields field) {
      if (field == null) {
        throw new IllegalArgumentException();
      }

      switch (field) {
      }
      throw new IllegalStateException();
    }

    @Override
    public boolean equals(Object that) {
      if (that == null)
        return false;
      if (that instanceof writeResults_result)
        return this.equals((writeResults_result)that);
      return false;
    }

    public boolean equals(writeResults_result that) {
      if (that == null)
        return false;

      return true;
    }

    @Override
    public int hashCode() {
      return 0;
    }

    public int compareTo(writeResults_result other) {
      if (!getClass().equals(other.getClass())) {
        return getClass().getName().compareTo(other.getClass().getName());
      }

      int lastComparison = 0;
      writeResults_result typedOther = (writeResults_result)other;

      return 0;
    }

    public _Fields fieldForId(int fieldId) {
      return _Fields.findByThriftId(fieldId);
    }

    public void read(org.apache.thrift.protocol.TProtocol iprot) throws org.apache.thrift.TException {
      schemes.get(iprot.getScheme()).getScheme().read(iprot, this);
    }

    public void write(org.apache.thrift.protocol.TProtocol oprot) throws org.apache.thrift.TException {
      schemes.get(oprot.getScheme()).getScheme().write(oprot, this);
      }

    @Override
    public String toString() {
      StringBuilder sb = new StringBuilder("writeResults_result(");
      boolean first = true;

      sb.append(")");
      return sb.toString();
    }

    public void validate() throws org.apache.thrift.TException {
      // check for required fields
    }

    private void writeObject(java.io.ObjectOutputStream out) throws java.io.IOException {
      try {
        write(new org.apache.thrift.protocol.TCompactProtocol(new org.apache.thrift.transport.TIOStreamTransport(out)));
      } catch (org.apache.thrift.TException te) {
        throw new java.io.IOException(te);
      }
    }

    private void readObject(java.io.ObjectInputStream in) throws java.io.IOException, ClassNotFoundException {
      try {
        read(new org.apache.thrift.protocol.TCompactProtocol(new org.apache.thrift.transport.TIOStreamTransport(in)));
      } catch (org.apache.thrift.TException te) {
        throw new java.io.IOException(te);
      }
    }

    private static class writeResults_resultStandardSchemeFactory implements SchemeFactory {
      public writeResults_resultStandardScheme getScheme() {
        return new writeResults_resultStandardScheme();
      }
    }

    private static class writeResults_resultStandardScheme extends StandardScheme<writeResults_result> {

      public void read(org.apache.thrift.protocol.TProtocol iprot, writeResults_result struct) throws org.apache.thrift.TException {
        org.apache.thrift.protocol.TField schemeField;
        iprot.readStructBegin();
        while (true)
        {
          schemeField = iprot.readFieldBegin();
          if (schemeField.type == org.apache.thrift.protocol.TType.STOP) { 
            break;
          }
          switch (schemeField.id) {
            default:
              org.apache.thrift.protocol.TProtocolUtil.skip(iprot, schemeField.type);
          }
          iprot.readFieldEnd();
        }
        iprot.readStructEnd();

        // check for required fields of primitive type, which can't be checked in the validate method
        struct.validate();
      }

      public void write(org.apache.thrift.protocol.TProtocol oprot, writeResults_result struct) throws org.apache.thrift.TException {
        struct.validate();

        oprot.writeStructBegin(STRUCT_DESC);
        oprot.writeFieldStop();
        oprot.writeStructEnd();
      }

    }

    private static class writeResults_resultTupleSchemeFactory implements SchemeFactory {
      public writeResults_resultTupleScheme getScheme() {
        return new writeResults_resultTupleScheme();
      }
    }

    private static class writeResults_resultTupleScheme extends TupleScheme<writeResults_result> {

      @Override
      public void write(org.apache.thrift.protocol.TProtocol prot, writeResults_result struct) throws org.apache.thrift.TException {
        TTupleProtocol oprot = (TTupleProtocol) prot;
      }

      @Override
      public void read(org.apache.thrift.protocol.TProtocol prot, writeResults_result struct) throws org.apache.thrift.TException {
        TTupleProtocol iprot = (TTupleProtocol) prot;
      }
    }

  }

}
