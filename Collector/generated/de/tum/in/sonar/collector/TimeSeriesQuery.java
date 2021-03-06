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

public class TimeSeriesQuery implements org.apache.thrift.TBase<TimeSeriesQuery, TimeSeriesQuery._Fields>, java.io.Serializable, Cloneable {
  private static final org.apache.thrift.protocol.TStruct STRUCT_DESC = new org.apache.thrift.protocol.TStruct("TimeSeriesQuery");

  private static final org.apache.thrift.protocol.TField START_TIME_FIELD_DESC = new org.apache.thrift.protocol.TField("startTime", org.apache.thrift.protocol.TType.I64, (short)1);
  private static final org.apache.thrift.protocol.TField STOP_TIME_FIELD_DESC = new org.apache.thrift.protocol.TField("stopTime", org.apache.thrift.protocol.TType.I64, (short)2);
  private static final org.apache.thrift.protocol.TField SENSOR_FIELD_DESC = new org.apache.thrift.protocol.TField("sensor", org.apache.thrift.protocol.TType.STRING, (short)3);
  private static final org.apache.thrift.protocol.TField LABELS_FIELD_DESC = new org.apache.thrift.protocol.TField("labels", org.apache.thrift.protocol.TType.SET, (short)5);
  private static final org.apache.thrift.protocol.TField HOSTNAME_FIELD_DESC = new org.apache.thrift.protocol.TField("hostname", org.apache.thrift.protocol.TType.STRING, (short)4);

  private static final Map<Class<? extends IScheme>, SchemeFactory> schemes = new HashMap<Class<? extends IScheme>, SchemeFactory>();
  static {
    schemes.put(StandardScheme.class, new TimeSeriesQueryStandardSchemeFactory());
    schemes.put(TupleScheme.class, new TimeSeriesQueryTupleSchemeFactory());
  }

  public long startTime; // required
  public long stopTime; // required
  public String sensor; // required
  public Set<String> labels; // required
  public String hostname; // optional

  /** The set of fields this struct contains, along with convenience methods for finding and manipulating them. */
  public enum _Fields implements org.apache.thrift.TFieldIdEnum {
    START_TIME((short)1, "startTime"),
    STOP_TIME((short)2, "stopTime"),
    SENSOR((short)3, "sensor"),
    LABELS((short)5, "labels"),
    HOSTNAME((short)4, "hostname");

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
        case 1: // START_TIME
          return START_TIME;
        case 2: // STOP_TIME
          return STOP_TIME;
        case 3: // SENSOR
          return SENSOR;
        case 5: // LABELS
          return LABELS;
        case 4: // HOSTNAME
          return HOSTNAME;
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
  private static final int __STARTTIME_ISSET_ID = 0;
  private static final int __STOPTIME_ISSET_ID = 1;
  private BitSet __isset_bit_vector = new BitSet(2);
  private _Fields optionals[] = {_Fields.HOSTNAME};
  public static final Map<_Fields, org.apache.thrift.meta_data.FieldMetaData> metaDataMap;
  static {
    Map<_Fields, org.apache.thrift.meta_data.FieldMetaData> tmpMap = new EnumMap<_Fields, org.apache.thrift.meta_data.FieldMetaData>(_Fields.class);
    tmpMap.put(_Fields.START_TIME, new org.apache.thrift.meta_data.FieldMetaData("startTime", org.apache.thrift.TFieldRequirementType.DEFAULT, 
        new org.apache.thrift.meta_data.FieldValueMetaData(org.apache.thrift.protocol.TType.I64        , "long")));
    tmpMap.put(_Fields.STOP_TIME, new org.apache.thrift.meta_data.FieldMetaData("stopTime", org.apache.thrift.TFieldRequirementType.DEFAULT, 
        new org.apache.thrift.meta_data.FieldValueMetaData(org.apache.thrift.protocol.TType.I64        , "long")));
    tmpMap.put(_Fields.SENSOR, new org.apache.thrift.meta_data.FieldMetaData("sensor", org.apache.thrift.TFieldRequirementType.DEFAULT, 
        new org.apache.thrift.meta_data.FieldValueMetaData(org.apache.thrift.protocol.TType.STRING)));
    tmpMap.put(_Fields.LABELS, new org.apache.thrift.meta_data.FieldMetaData("labels", org.apache.thrift.TFieldRequirementType.DEFAULT, 
        new org.apache.thrift.meta_data.SetMetaData(org.apache.thrift.protocol.TType.SET, 
            new org.apache.thrift.meta_data.FieldValueMetaData(org.apache.thrift.protocol.TType.STRING))));
    tmpMap.put(_Fields.HOSTNAME, new org.apache.thrift.meta_data.FieldMetaData("hostname", org.apache.thrift.TFieldRequirementType.OPTIONAL, 
        new org.apache.thrift.meta_data.FieldValueMetaData(org.apache.thrift.protocol.TType.STRING)));
    metaDataMap = Collections.unmodifiableMap(tmpMap);
    org.apache.thrift.meta_data.FieldMetaData.addStructMetaDataMap(TimeSeriesQuery.class, metaDataMap);
  }

  public TimeSeriesQuery() {
  }

  public TimeSeriesQuery(
    long startTime,
    long stopTime,
    String sensor,
    Set<String> labels)
  {
    this();
    this.startTime = startTime;
    setStartTimeIsSet(true);
    this.stopTime = stopTime;
    setStopTimeIsSet(true);
    this.sensor = sensor;
    this.labels = labels;
  }

  /**
   * Performs a deep copy on <i>other</i>.
   */
  public TimeSeriesQuery(TimeSeriesQuery other) {
    __isset_bit_vector.clear();
    __isset_bit_vector.or(other.__isset_bit_vector);
    this.startTime = other.startTime;
    this.stopTime = other.stopTime;
    if (other.isSetSensor()) {
      this.sensor = other.sensor;
    }
    if (other.isSetLabels()) {
      Set<String> __this__labels = new HashSet<String>();
      for (String other_element : other.labels) {
        __this__labels.add(other_element);
      }
      this.labels = __this__labels;
    }
    if (other.isSetHostname()) {
      this.hostname = other.hostname;
    }
  }

  public TimeSeriesQuery deepCopy() {
    return new TimeSeriesQuery(this);
  }

  @Override
  public void clear() {
    setStartTimeIsSet(false);
    this.startTime = 0;
    setStopTimeIsSet(false);
    this.stopTime = 0;
    this.sensor = null;
    this.labels = null;
    this.hostname = null;
  }

  public long getStartTime() {
    return this.startTime;
  }

  public TimeSeriesQuery setStartTime(long startTime) {
    this.startTime = startTime;
    setStartTimeIsSet(true);
    return this;
  }

  public void unsetStartTime() {
    __isset_bit_vector.clear(__STARTTIME_ISSET_ID);
  }

  /** Returns true if field startTime is set (has been assigned a value) and false otherwise */
  public boolean isSetStartTime() {
    return __isset_bit_vector.get(__STARTTIME_ISSET_ID);
  }

  public void setStartTimeIsSet(boolean value) {
    __isset_bit_vector.set(__STARTTIME_ISSET_ID, value);
  }

  public long getStopTime() {
    return this.stopTime;
  }

  public TimeSeriesQuery setStopTime(long stopTime) {
    this.stopTime = stopTime;
    setStopTimeIsSet(true);
    return this;
  }

  public void unsetStopTime() {
    __isset_bit_vector.clear(__STOPTIME_ISSET_ID);
  }

  /** Returns true if field stopTime is set (has been assigned a value) and false otherwise */
  public boolean isSetStopTime() {
    return __isset_bit_vector.get(__STOPTIME_ISSET_ID);
  }

  public void setStopTimeIsSet(boolean value) {
    __isset_bit_vector.set(__STOPTIME_ISSET_ID, value);
  }

  public String getSensor() {
    return this.sensor;
  }

  public TimeSeriesQuery setSensor(String sensor) {
    this.sensor = sensor;
    return this;
  }

  public void unsetSensor() {
    this.sensor = null;
  }

  /** Returns true if field sensor is set (has been assigned a value) and false otherwise */
  public boolean isSetSensor() {
    return this.sensor != null;
  }

  public void setSensorIsSet(boolean value) {
    if (!value) {
      this.sensor = null;
    }
  }

  public int getLabelsSize() {
    return (this.labels == null) ? 0 : this.labels.size();
  }

  public java.util.Iterator<String> getLabelsIterator() {
    return (this.labels == null) ? null : this.labels.iterator();
  }

  public void addToLabels(String elem) {
    if (this.labels == null) {
      this.labels = new HashSet<String>();
    }
    this.labels.add(elem);
  }

  public Set<String> getLabels() {
    return this.labels;
  }

  public TimeSeriesQuery setLabels(Set<String> labels) {
    this.labels = labels;
    return this;
  }

  public void unsetLabels() {
    this.labels = null;
  }

  /** Returns true if field labels is set (has been assigned a value) and false otherwise */
  public boolean isSetLabels() {
    return this.labels != null;
  }

  public void setLabelsIsSet(boolean value) {
    if (!value) {
      this.labels = null;
    }
  }

  public String getHostname() {
    return this.hostname;
  }

  public TimeSeriesQuery setHostname(String hostname) {
    this.hostname = hostname;
    return this;
  }

  public void unsetHostname() {
    this.hostname = null;
  }

  /** Returns true if field hostname is set (has been assigned a value) and false otherwise */
  public boolean isSetHostname() {
    return this.hostname != null;
  }

  public void setHostnameIsSet(boolean value) {
    if (!value) {
      this.hostname = null;
    }
  }

  public void setFieldValue(_Fields field, Object value) {
    switch (field) {
    case START_TIME:
      if (value == null) {
        unsetStartTime();
      } else {
        setStartTime((Long)value);
      }
      break;

    case STOP_TIME:
      if (value == null) {
        unsetStopTime();
      } else {
        setStopTime((Long)value);
      }
      break;

    case SENSOR:
      if (value == null) {
        unsetSensor();
      } else {
        setSensor((String)value);
      }
      break;

    case LABELS:
      if (value == null) {
        unsetLabels();
      } else {
        setLabels((Set<String>)value);
      }
      break;

    case HOSTNAME:
      if (value == null) {
        unsetHostname();
      } else {
        setHostname((String)value);
      }
      break;

    }
  }

  public Object getFieldValue(_Fields field) {
    switch (field) {
    case START_TIME:
      return Long.valueOf(getStartTime());

    case STOP_TIME:
      return Long.valueOf(getStopTime());

    case SENSOR:
      return getSensor();

    case LABELS:
      return getLabels();

    case HOSTNAME:
      return getHostname();

    }
    throw new IllegalStateException();
  }

  /** Returns true if field corresponding to fieldID is set (has been assigned a value) and false otherwise */
  public boolean isSet(_Fields field) {
    if (field == null) {
      throw new IllegalArgumentException();
    }

    switch (field) {
    case START_TIME:
      return isSetStartTime();
    case STOP_TIME:
      return isSetStopTime();
    case SENSOR:
      return isSetSensor();
    case LABELS:
      return isSetLabels();
    case HOSTNAME:
      return isSetHostname();
    }
    throw new IllegalStateException();
  }

  @Override
  public boolean equals(Object that) {
    if (that == null)
      return false;
    if (that instanceof TimeSeriesQuery)
      return this.equals((TimeSeriesQuery)that);
    return false;
  }

  public boolean equals(TimeSeriesQuery that) {
    if (that == null)
      return false;

    boolean this_present_startTime = true;
    boolean that_present_startTime = true;
    if (this_present_startTime || that_present_startTime) {
      if (!(this_present_startTime && that_present_startTime))
        return false;
      if (this.startTime != that.startTime)
        return false;
    }

    boolean this_present_stopTime = true;
    boolean that_present_stopTime = true;
    if (this_present_stopTime || that_present_stopTime) {
      if (!(this_present_stopTime && that_present_stopTime))
        return false;
      if (this.stopTime != that.stopTime)
        return false;
    }

    boolean this_present_sensor = true && this.isSetSensor();
    boolean that_present_sensor = true && that.isSetSensor();
    if (this_present_sensor || that_present_sensor) {
      if (!(this_present_sensor && that_present_sensor))
        return false;
      if (!this.sensor.equals(that.sensor))
        return false;
    }

    boolean this_present_labels = true && this.isSetLabels();
    boolean that_present_labels = true && that.isSetLabels();
    if (this_present_labels || that_present_labels) {
      if (!(this_present_labels && that_present_labels))
        return false;
      if (!this.labels.equals(that.labels))
        return false;
    }

    boolean this_present_hostname = true && this.isSetHostname();
    boolean that_present_hostname = true && that.isSetHostname();
    if (this_present_hostname || that_present_hostname) {
      if (!(this_present_hostname && that_present_hostname))
        return false;
      if (!this.hostname.equals(that.hostname))
        return false;
    }

    return true;
  }

  @Override
  public int hashCode() {
    return 0;
  }

  public int compareTo(TimeSeriesQuery other) {
    if (!getClass().equals(other.getClass())) {
      return getClass().getName().compareTo(other.getClass().getName());
    }

    int lastComparison = 0;
    TimeSeriesQuery typedOther = (TimeSeriesQuery)other;

    lastComparison = Boolean.valueOf(isSetStartTime()).compareTo(typedOther.isSetStartTime());
    if (lastComparison != 0) {
      return lastComparison;
    }
    if (isSetStartTime()) {
      lastComparison = org.apache.thrift.TBaseHelper.compareTo(this.startTime, typedOther.startTime);
      if (lastComparison != 0) {
        return lastComparison;
      }
    }
    lastComparison = Boolean.valueOf(isSetStopTime()).compareTo(typedOther.isSetStopTime());
    if (lastComparison != 0) {
      return lastComparison;
    }
    if (isSetStopTime()) {
      lastComparison = org.apache.thrift.TBaseHelper.compareTo(this.stopTime, typedOther.stopTime);
      if (lastComparison != 0) {
        return lastComparison;
      }
    }
    lastComparison = Boolean.valueOf(isSetSensor()).compareTo(typedOther.isSetSensor());
    if (lastComparison != 0) {
      return lastComparison;
    }
    if (isSetSensor()) {
      lastComparison = org.apache.thrift.TBaseHelper.compareTo(this.sensor, typedOther.sensor);
      if (lastComparison != 0) {
        return lastComparison;
      }
    }
    lastComparison = Boolean.valueOf(isSetLabels()).compareTo(typedOther.isSetLabels());
    if (lastComparison != 0) {
      return lastComparison;
    }
    if (isSetLabels()) {
      lastComparison = org.apache.thrift.TBaseHelper.compareTo(this.labels, typedOther.labels);
      if (lastComparison != 0) {
        return lastComparison;
      }
    }
    lastComparison = Boolean.valueOf(isSetHostname()).compareTo(typedOther.isSetHostname());
    if (lastComparison != 0) {
      return lastComparison;
    }
    if (isSetHostname()) {
      lastComparison = org.apache.thrift.TBaseHelper.compareTo(this.hostname, typedOther.hostname);
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
    StringBuilder sb = new StringBuilder("TimeSeriesQuery(");
    boolean first = true;

    sb.append("startTime:");
    sb.append(this.startTime);
    first = false;
    if (!first) sb.append(", ");
    sb.append("stopTime:");
    sb.append(this.stopTime);
    first = false;
    if (!first) sb.append(", ");
    sb.append("sensor:");
    if (this.sensor == null) {
      sb.append("null");
    } else {
      sb.append(this.sensor);
    }
    first = false;
    if (!first) sb.append(", ");
    sb.append("labels:");
    if (this.labels == null) {
      sb.append("null");
    } else {
      sb.append(this.labels);
    }
    first = false;
    if (isSetHostname()) {
      if (!first) sb.append(", ");
      sb.append("hostname:");
      if (this.hostname == null) {
        sb.append("null");
      } else {
        sb.append(this.hostname);
      }
      first = false;
    }
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
      // it doesn't seem like you should have to do this, but java serialization is wacky, and doesn't call the default constructor.
      __isset_bit_vector = new BitSet(1);
      read(new org.apache.thrift.protocol.TCompactProtocol(new org.apache.thrift.transport.TIOStreamTransport(in)));
    } catch (org.apache.thrift.TException te) {
      throw new java.io.IOException(te);
    }
  }

  private static class TimeSeriesQueryStandardSchemeFactory implements SchemeFactory {
    public TimeSeriesQueryStandardScheme getScheme() {
      return new TimeSeriesQueryStandardScheme();
    }
  }

  private static class TimeSeriesQueryStandardScheme extends StandardScheme<TimeSeriesQuery> {

    public void read(org.apache.thrift.protocol.TProtocol iprot, TimeSeriesQuery struct) throws org.apache.thrift.TException {
      org.apache.thrift.protocol.TField schemeField;
      iprot.readStructBegin();
      while (true)
      {
        schemeField = iprot.readFieldBegin();
        if (schemeField.type == org.apache.thrift.protocol.TType.STOP) { 
          break;
        }
        switch (schemeField.id) {
          case 1: // START_TIME
            if (schemeField.type == org.apache.thrift.protocol.TType.I64) {
              struct.startTime = iprot.readI64();
              struct.setStartTimeIsSet(true);
            } else { 
              org.apache.thrift.protocol.TProtocolUtil.skip(iprot, schemeField.type);
            }
            break;
          case 2: // STOP_TIME
            if (schemeField.type == org.apache.thrift.protocol.TType.I64) {
              struct.stopTime = iprot.readI64();
              struct.setStopTimeIsSet(true);
            } else { 
              org.apache.thrift.protocol.TProtocolUtil.skip(iprot, schemeField.type);
            }
            break;
          case 3: // SENSOR
            if (schemeField.type == org.apache.thrift.protocol.TType.STRING) {
              struct.sensor = iprot.readString();
              struct.setSensorIsSet(true);
            } else { 
              org.apache.thrift.protocol.TProtocolUtil.skip(iprot, schemeField.type);
            }
            break;
          case 5: // LABELS
            if (schemeField.type == org.apache.thrift.protocol.TType.SET) {
              {
                org.apache.thrift.protocol.TSet _set24 = iprot.readSetBegin();
                struct.labels = new HashSet<String>(2*_set24.size);
                for (int _i25 = 0; _i25 < _set24.size; ++_i25)
                {
                  String _elem26; // required
                  _elem26 = iprot.readString();
                  struct.labels.add(_elem26);
                }
                iprot.readSetEnd();
              }
              struct.setLabelsIsSet(true);
            } else { 
              org.apache.thrift.protocol.TProtocolUtil.skip(iprot, schemeField.type);
            }
            break;
          case 4: // HOSTNAME
            if (schemeField.type == org.apache.thrift.protocol.TType.STRING) {
              struct.hostname = iprot.readString();
              struct.setHostnameIsSet(true);
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

    public void write(org.apache.thrift.protocol.TProtocol oprot, TimeSeriesQuery struct) throws org.apache.thrift.TException {
      struct.validate();

      oprot.writeStructBegin(STRUCT_DESC);
      oprot.writeFieldBegin(START_TIME_FIELD_DESC);
      oprot.writeI64(struct.startTime);
      oprot.writeFieldEnd();
      oprot.writeFieldBegin(STOP_TIME_FIELD_DESC);
      oprot.writeI64(struct.stopTime);
      oprot.writeFieldEnd();
      if (struct.sensor != null) {
        oprot.writeFieldBegin(SENSOR_FIELD_DESC);
        oprot.writeString(struct.sensor);
        oprot.writeFieldEnd();
      }
      if (struct.hostname != null) {
        if (struct.isSetHostname()) {
          oprot.writeFieldBegin(HOSTNAME_FIELD_DESC);
          oprot.writeString(struct.hostname);
          oprot.writeFieldEnd();
        }
      }
      if (struct.labels != null) {
        oprot.writeFieldBegin(LABELS_FIELD_DESC);
        {
          oprot.writeSetBegin(new org.apache.thrift.protocol.TSet(org.apache.thrift.protocol.TType.STRING, struct.labels.size()));
          for (String _iter27 : struct.labels)
          {
            oprot.writeString(_iter27);
          }
          oprot.writeSetEnd();
        }
        oprot.writeFieldEnd();
      }
      oprot.writeFieldStop();
      oprot.writeStructEnd();
    }

  }

  private static class TimeSeriesQueryTupleSchemeFactory implements SchemeFactory {
    public TimeSeriesQueryTupleScheme getScheme() {
      return new TimeSeriesQueryTupleScheme();
    }
  }

  private static class TimeSeriesQueryTupleScheme extends TupleScheme<TimeSeriesQuery> {

    @Override
    public void write(org.apache.thrift.protocol.TProtocol prot, TimeSeriesQuery struct) throws org.apache.thrift.TException {
      TTupleProtocol oprot = (TTupleProtocol) prot;
      BitSet optionals = new BitSet();
      if (struct.isSetStartTime()) {
        optionals.set(0);
      }
      if (struct.isSetStopTime()) {
        optionals.set(1);
      }
      if (struct.isSetSensor()) {
        optionals.set(2);
      }
      if (struct.isSetLabels()) {
        optionals.set(3);
      }
      if (struct.isSetHostname()) {
        optionals.set(4);
      }
      oprot.writeBitSet(optionals, 5);
      if (struct.isSetStartTime()) {
        oprot.writeI64(struct.startTime);
      }
      if (struct.isSetStopTime()) {
        oprot.writeI64(struct.stopTime);
      }
      if (struct.isSetSensor()) {
        oprot.writeString(struct.sensor);
      }
      if (struct.isSetLabels()) {
        {
          oprot.writeI32(struct.labels.size());
          for (String _iter28 : struct.labels)
          {
            oprot.writeString(_iter28);
          }
        }
      }
      if (struct.isSetHostname()) {
        oprot.writeString(struct.hostname);
      }
    }

    @Override
    public void read(org.apache.thrift.protocol.TProtocol prot, TimeSeriesQuery struct) throws org.apache.thrift.TException {
      TTupleProtocol iprot = (TTupleProtocol) prot;
      BitSet incoming = iprot.readBitSet(5);
      if (incoming.get(0)) {
        struct.startTime = iprot.readI64();
        struct.setStartTimeIsSet(true);
      }
      if (incoming.get(1)) {
        struct.stopTime = iprot.readI64();
        struct.setStopTimeIsSet(true);
      }
      if (incoming.get(2)) {
        struct.sensor = iprot.readString();
        struct.setSensorIsSet(true);
      }
      if (incoming.get(3)) {
        {
          org.apache.thrift.protocol.TSet _set29 = new org.apache.thrift.protocol.TSet(org.apache.thrift.protocol.TType.STRING, iprot.readI32());
          struct.labels = new HashSet<String>(2*_set29.size);
          for (int _i30 = 0; _i30 < _set29.size; ++_i30)
          {
            String _elem31; // required
            _elem31 = iprot.readString();
            struct.labels.add(_elem31);
          }
        }
        struct.setLabelsIsSet(true);
      }
      if (incoming.get(4)) {
        struct.hostname = iprot.readString();
        struct.setHostnameIsSet(true);
      }
    }
  }

}

