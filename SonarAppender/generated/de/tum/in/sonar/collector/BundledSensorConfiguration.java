/**
 * Autogenerated by Thrift Compiler (0.9.0)
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
import org.apache.thrift.protocol.TProtocolException;
import org.apache.thrift.EncodingUtils;
import org.apache.thrift.TException;
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

public class BundledSensorConfiguration implements org.apache.thrift.TBase<BundledSensorConfiguration, BundledSensorConfiguration._Fields>, java.io.Serializable, Cloneable {
  private static final org.apache.thrift.protocol.TStruct STRUCT_DESC = new org.apache.thrift.protocol.TStruct("BundledSensorConfiguration");

  private static final org.apache.thrift.protocol.TField SENSOR_FIELD_DESC = new org.apache.thrift.protocol.TField("sensor", org.apache.thrift.protocol.TType.STRING, (short)1);
  private static final org.apache.thrift.protocol.TField HOSTNAME_FIELD_DESC = new org.apache.thrift.protocol.TField("hostname", org.apache.thrift.protocol.TType.STRING, (short)2);
  private static final org.apache.thrift.protocol.TField LABELS_FIELD_DESC = new org.apache.thrift.protocol.TField("labels", org.apache.thrift.protocol.TType.SET, (short)3);
  private static final org.apache.thrift.protocol.TField CONFIGURATION_FIELD_DESC = new org.apache.thrift.protocol.TField("configuration", org.apache.thrift.protocol.TType.STRUCT, (short)4);
  private static final org.apache.thrift.protocol.TField ACTIVE_FIELD_DESC = new org.apache.thrift.protocol.TField("active", org.apache.thrift.protocol.TType.BOOL, (short)5);

  private static final Map<Class<? extends IScheme>, SchemeFactory> schemes = new HashMap<Class<? extends IScheme>, SchemeFactory>();
  static {
    schemes.put(StandardScheme.class, new BundledSensorConfigurationStandardSchemeFactory());
    schemes.put(TupleScheme.class, new BundledSensorConfigurationTupleSchemeFactory());
  }

  public String sensor; // required
  public String hostname; // required
  public Set<String> labels; // required
  public SensorConfiguration configuration; // required
  public boolean active; // required

  /** The set of fields this struct contains, along with convenience methods for finding and manipulating them. */
  public enum _Fields implements org.apache.thrift.TFieldIdEnum {
    SENSOR((short)1, "sensor"),
    HOSTNAME((short)2, "hostname"),
    LABELS((short)3, "labels"),
    CONFIGURATION((short)4, "configuration"),
    ACTIVE((short)5, "active");

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
        case 1: // SENSOR
          return SENSOR;
        case 2: // HOSTNAME
          return HOSTNAME;
        case 3: // LABELS
          return LABELS;
        case 4: // CONFIGURATION
          return CONFIGURATION;
        case 5: // ACTIVE
          return ACTIVE;
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
  private static final int __ACTIVE_ISSET_ID = 0;
  private byte __isset_bitfield = 0;
  public static final Map<_Fields, org.apache.thrift.meta_data.FieldMetaData> metaDataMap;
  static {
    Map<_Fields, org.apache.thrift.meta_data.FieldMetaData> tmpMap = new EnumMap<_Fields, org.apache.thrift.meta_data.FieldMetaData>(_Fields.class);
    tmpMap.put(_Fields.SENSOR, new org.apache.thrift.meta_data.FieldMetaData("sensor", org.apache.thrift.TFieldRequirementType.DEFAULT, 
        new org.apache.thrift.meta_data.FieldValueMetaData(org.apache.thrift.protocol.TType.STRING)));
    tmpMap.put(_Fields.HOSTNAME, new org.apache.thrift.meta_data.FieldMetaData("hostname", org.apache.thrift.TFieldRequirementType.DEFAULT, 
        new org.apache.thrift.meta_data.FieldValueMetaData(org.apache.thrift.protocol.TType.STRING)));
    tmpMap.put(_Fields.LABELS, new org.apache.thrift.meta_data.FieldMetaData("labels", org.apache.thrift.TFieldRequirementType.DEFAULT, 
        new org.apache.thrift.meta_data.SetMetaData(org.apache.thrift.protocol.TType.SET, 
            new org.apache.thrift.meta_data.FieldValueMetaData(org.apache.thrift.protocol.TType.STRING))));
    tmpMap.put(_Fields.CONFIGURATION, new org.apache.thrift.meta_data.FieldMetaData("configuration", org.apache.thrift.TFieldRequirementType.DEFAULT, 
        new org.apache.thrift.meta_data.StructMetaData(org.apache.thrift.protocol.TType.STRUCT, SensorConfiguration.class)));
    tmpMap.put(_Fields.ACTIVE, new org.apache.thrift.meta_data.FieldMetaData("active", org.apache.thrift.TFieldRequirementType.DEFAULT, 
        new org.apache.thrift.meta_data.FieldValueMetaData(org.apache.thrift.protocol.TType.BOOL)));
    metaDataMap = Collections.unmodifiableMap(tmpMap);
    org.apache.thrift.meta_data.FieldMetaData.addStructMetaDataMap(BundledSensorConfiguration.class, metaDataMap);
  }

  public BundledSensorConfiguration() {
  }

  public BundledSensorConfiguration(
    String sensor,
    String hostname,
    Set<String> labels,
    SensorConfiguration configuration,
    boolean active)
  {
    this();
    this.sensor = sensor;
    this.hostname = hostname;
    this.labels = labels;
    this.configuration = configuration;
    this.active = active;
    setActiveIsSet(true);
  }

  /**
   * Performs a deep copy on <i>other</i>.
   */
  public BundledSensorConfiguration(BundledSensorConfiguration other) {
    __isset_bitfield = other.__isset_bitfield;
    if (other.isSetSensor()) {
      this.sensor = other.sensor;
    }
    if (other.isSetHostname()) {
      this.hostname = other.hostname;
    }
    if (other.isSetLabels()) {
      Set<String> __this__labels = new HashSet<String>();
      for (String other_element : other.labels) {
        __this__labels.add(other_element);
      }
      this.labels = __this__labels;
    }
    if (other.isSetConfiguration()) {
      this.configuration = new SensorConfiguration(other.configuration);
    }
    this.active = other.active;
  }

  public BundledSensorConfiguration deepCopy() {
    return new BundledSensorConfiguration(this);
  }

  @Override
  public void clear() {
    this.sensor = null;
    this.hostname = null;
    this.labels = null;
    this.configuration = null;
    setActiveIsSet(false);
    this.active = false;
  }

  public String getSensor() {
    return this.sensor;
  }

  public BundledSensorConfiguration setSensor(String sensor) {
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

  public String getHostname() {
    return this.hostname;
  }

  public BundledSensorConfiguration setHostname(String hostname) {
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

  public BundledSensorConfiguration setLabels(Set<String> labels) {
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

  public SensorConfiguration getConfiguration() {
    return this.configuration;
  }

  public BundledSensorConfiguration setConfiguration(SensorConfiguration configuration) {
    this.configuration = configuration;
    return this;
  }

  public void unsetConfiguration() {
    this.configuration = null;
  }

  /** Returns true if field configuration is set (has been assigned a value) and false otherwise */
  public boolean isSetConfiguration() {
    return this.configuration != null;
  }

  public void setConfigurationIsSet(boolean value) {
    if (!value) {
      this.configuration = null;
    }
  }

  public boolean isActive() {
    return this.active;
  }

  public BundledSensorConfiguration setActive(boolean active) {
    this.active = active;
    setActiveIsSet(true);
    return this;
  }

  public void unsetActive() {
    __isset_bitfield = EncodingUtils.clearBit(__isset_bitfield, __ACTIVE_ISSET_ID);
  }

  /** Returns true if field active is set (has been assigned a value) and false otherwise */
  public boolean isSetActive() {
    return EncodingUtils.testBit(__isset_bitfield, __ACTIVE_ISSET_ID);
  }

  public void setActiveIsSet(boolean value) {
    __isset_bitfield = EncodingUtils.setBit(__isset_bitfield, __ACTIVE_ISSET_ID, value);
  }

  public void setFieldValue(_Fields field, Object value) {
    switch (field) {
    case SENSOR:
      if (value == null) {
        unsetSensor();
      } else {
        setSensor((String)value);
      }
      break;

    case HOSTNAME:
      if (value == null) {
        unsetHostname();
      } else {
        setHostname((String)value);
      }
      break;

    case LABELS:
      if (value == null) {
        unsetLabels();
      } else {
        setLabels((Set<String>)value);
      }
      break;

    case CONFIGURATION:
      if (value == null) {
        unsetConfiguration();
      } else {
        setConfiguration((SensorConfiguration)value);
      }
      break;

    case ACTIVE:
      if (value == null) {
        unsetActive();
      } else {
        setActive((Boolean)value);
      }
      break;

    }
  }

  public Object getFieldValue(_Fields field) {
    switch (field) {
    case SENSOR:
      return getSensor();

    case HOSTNAME:
      return getHostname();

    case LABELS:
      return getLabels();

    case CONFIGURATION:
      return getConfiguration();

    case ACTIVE:
      return Boolean.valueOf(isActive());

    }
    throw new IllegalStateException();
  }

  /** Returns true if field corresponding to fieldID is set (has been assigned a value) and false otherwise */
  public boolean isSet(_Fields field) {
    if (field == null) {
      throw new IllegalArgumentException();
    }

    switch (field) {
    case SENSOR:
      return isSetSensor();
    case HOSTNAME:
      return isSetHostname();
    case LABELS:
      return isSetLabels();
    case CONFIGURATION:
      return isSetConfiguration();
    case ACTIVE:
      return isSetActive();
    }
    throw new IllegalStateException();
  }

  @Override
  public boolean equals(Object that) {
    if (that == null)
      return false;
    if (that instanceof BundledSensorConfiguration)
      return this.equals((BundledSensorConfiguration)that);
    return false;
  }

  public boolean equals(BundledSensorConfiguration that) {
    if (that == null)
      return false;

    boolean this_present_sensor = true && this.isSetSensor();
    boolean that_present_sensor = true && that.isSetSensor();
    if (this_present_sensor || that_present_sensor) {
      if (!(this_present_sensor && that_present_sensor))
        return false;
      if (!this.sensor.equals(that.sensor))
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

    boolean this_present_labels = true && this.isSetLabels();
    boolean that_present_labels = true && that.isSetLabels();
    if (this_present_labels || that_present_labels) {
      if (!(this_present_labels && that_present_labels))
        return false;
      if (!this.labels.equals(that.labels))
        return false;
    }

    boolean this_present_configuration = true && this.isSetConfiguration();
    boolean that_present_configuration = true && that.isSetConfiguration();
    if (this_present_configuration || that_present_configuration) {
      if (!(this_present_configuration && that_present_configuration))
        return false;
      if (!this.configuration.equals(that.configuration))
        return false;
    }

    boolean this_present_active = true;
    boolean that_present_active = true;
    if (this_present_active || that_present_active) {
      if (!(this_present_active && that_present_active))
        return false;
      if (this.active != that.active)
        return false;
    }

    return true;
  }

  @Override
  public int hashCode() {
    return 0;
  }

  public int compareTo(BundledSensorConfiguration other) {
    if (!getClass().equals(other.getClass())) {
      return getClass().getName().compareTo(other.getClass().getName());
    }

    int lastComparison = 0;
    BundledSensorConfiguration typedOther = (BundledSensorConfiguration)other;

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
    lastComparison = Boolean.valueOf(isSetConfiguration()).compareTo(typedOther.isSetConfiguration());
    if (lastComparison != 0) {
      return lastComparison;
    }
    if (isSetConfiguration()) {
      lastComparison = org.apache.thrift.TBaseHelper.compareTo(this.configuration, typedOther.configuration);
      if (lastComparison != 0) {
        return lastComparison;
      }
    }
    lastComparison = Boolean.valueOf(isSetActive()).compareTo(typedOther.isSetActive());
    if (lastComparison != 0) {
      return lastComparison;
    }
    if (isSetActive()) {
      lastComparison = org.apache.thrift.TBaseHelper.compareTo(this.active, typedOther.active);
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
    StringBuilder sb = new StringBuilder("BundledSensorConfiguration(");
    boolean first = true;

    sb.append("sensor:");
    if (this.sensor == null) {
      sb.append("null");
    } else {
      sb.append(this.sensor);
    }
    first = false;
    if (!first) sb.append(", ");
    sb.append("hostname:");
    if (this.hostname == null) {
      sb.append("null");
    } else {
      sb.append(this.hostname);
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
    if (!first) sb.append(", ");
    sb.append("configuration:");
    if (this.configuration == null) {
      sb.append("null");
    } else {
      sb.append(this.configuration);
    }
    first = false;
    if (!first) sb.append(", ");
    sb.append("active:");
    sb.append(this.active);
    first = false;
    sb.append(")");
    return sb.toString();
  }

  public void validate() throws org.apache.thrift.TException {
    // check for required fields
    // check for sub-struct validity
    if (configuration != null) {
      configuration.validate();
    }
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
      __isset_bitfield = 0;
      read(new org.apache.thrift.protocol.TCompactProtocol(new org.apache.thrift.transport.TIOStreamTransport(in)));
    } catch (org.apache.thrift.TException te) {
      throw new java.io.IOException(te);
    }
  }

  private static class BundledSensorConfigurationStandardSchemeFactory implements SchemeFactory {
    public BundledSensorConfigurationStandardScheme getScheme() {
      return new BundledSensorConfigurationStandardScheme();
    }
  }

  private static class BundledSensorConfigurationStandardScheme extends StandardScheme<BundledSensorConfiguration> {

    public void read(org.apache.thrift.protocol.TProtocol iprot, BundledSensorConfiguration struct) throws org.apache.thrift.TException {
      org.apache.thrift.protocol.TField schemeField;
      iprot.readStructBegin();
      while (true)
      {
        schemeField = iprot.readFieldBegin();
        if (schemeField.type == org.apache.thrift.protocol.TType.STOP) { 
          break;
        }
        switch (schemeField.id) {
          case 1: // SENSOR
            if (schemeField.type == org.apache.thrift.protocol.TType.STRING) {
              struct.sensor = iprot.readString();
              struct.setSensorIsSet(true);
            } else { 
              org.apache.thrift.protocol.TProtocolUtil.skip(iprot, schemeField.type);
            }
            break;
          case 2: // HOSTNAME
            if (schemeField.type == org.apache.thrift.protocol.TType.STRING) {
              struct.hostname = iprot.readString();
              struct.setHostnameIsSet(true);
            } else { 
              org.apache.thrift.protocol.TProtocolUtil.skip(iprot, schemeField.type);
            }
            break;
          case 3: // LABELS
            if (schemeField.type == org.apache.thrift.protocol.TType.SET) {
              {
                org.apache.thrift.protocol.TSet _set40 = iprot.readSetBegin();
                struct.labels = new HashSet<String>(2*_set40.size);
                for (int _i41 = 0; _i41 < _set40.size; ++_i41)
                {
                  String _elem42; // required
                  _elem42 = iprot.readString();
                  struct.labels.add(_elem42);
                }
                iprot.readSetEnd();
              }
              struct.setLabelsIsSet(true);
            } else { 
              org.apache.thrift.protocol.TProtocolUtil.skip(iprot, schemeField.type);
            }
            break;
          case 4: // CONFIGURATION
            if (schemeField.type == org.apache.thrift.protocol.TType.STRUCT) {
              struct.configuration = new SensorConfiguration();
              struct.configuration.read(iprot);
              struct.setConfigurationIsSet(true);
            } else { 
              org.apache.thrift.protocol.TProtocolUtil.skip(iprot, schemeField.type);
            }
            break;
          case 5: // ACTIVE
            if (schemeField.type == org.apache.thrift.protocol.TType.BOOL) {
              struct.active = iprot.readBool();
              struct.setActiveIsSet(true);
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

    public void write(org.apache.thrift.protocol.TProtocol oprot, BundledSensorConfiguration struct) throws org.apache.thrift.TException {
      struct.validate();

      oprot.writeStructBegin(STRUCT_DESC);
      if (struct.sensor != null) {
        oprot.writeFieldBegin(SENSOR_FIELD_DESC);
        oprot.writeString(struct.sensor);
        oprot.writeFieldEnd();
      }
      if (struct.hostname != null) {
        oprot.writeFieldBegin(HOSTNAME_FIELD_DESC);
        oprot.writeString(struct.hostname);
        oprot.writeFieldEnd();
      }
      if (struct.labels != null) {
        oprot.writeFieldBegin(LABELS_FIELD_DESC);
        {
          oprot.writeSetBegin(new org.apache.thrift.protocol.TSet(org.apache.thrift.protocol.TType.STRING, struct.labels.size()));
          for (String _iter43 : struct.labels)
          {
            oprot.writeString(_iter43);
          }
          oprot.writeSetEnd();
        }
        oprot.writeFieldEnd();
      }
      if (struct.configuration != null) {
        oprot.writeFieldBegin(CONFIGURATION_FIELD_DESC);
        struct.configuration.write(oprot);
        oprot.writeFieldEnd();
      }
      oprot.writeFieldBegin(ACTIVE_FIELD_DESC);
      oprot.writeBool(struct.active);
      oprot.writeFieldEnd();
      oprot.writeFieldStop();
      oprot.writeStructEnd();
    }

  }

  private static class BundledSensorConfigurationTupleSchemeFactory implements SchemeFactory {
    public BundledSensorConfigurationTupleScheme getScheme() {
      return new BundledSensorConfigurationTupleScheme();
    }
  }

  private static class BundledSensorConfigurationTupleScheme extends TupleScheme<BundledSensorConfiguration> {

    @Override
    public void write(org.apache.thrift.protocol.TProtocol prot, BundledSensorConfiguration struct) throws org.apache.thrift.TException {
      TTupleProtocol oprot = (TTupleProtocol) prot;
      BitSet optionals = new BitSet();
      if (struct.isSetSensor()) {
        optionals.set(0);
      }
      if (struct.isSetHostname()) {
        optionals.set(1);
      }
      if (struct.isSetLabels()) {
        optionals.set(2);
      }
      if (struct.isSetConfiguration()) {
        optionals.set(3);
      }
      if (struct.isSetActive()) {
        optionals.set(4);
      }
      oprot.writeBitSet(optionals, 5);
      if (struct.isSetSensor()) {
        oprot.writeString(struct.sensor);
      }
      if (struct.isSetHostname()) {
        oprot.writeString(struct.hostname);
      }
      if (struct.isSetLabels()) {
        {
          oprot.writeI32(struct.labels.size());
          for (String _iter44 : struct.labels)
          {
            oprot.writeString(_iter44);
          }
        }
      }
      if (struct.isSetConfiguration()) {
        struct.configuration.write(oprot);
      }
      if (struct.isSetActive()) {
        oprot.writeBool(struct.active);
      }
    }

    @Override
    public void read(org.apache.thrift.protocol.TProtocol prot, BundledSensorConfiguration struct) throws org.apache.thrift.TException {
      TTupleProtocol iprot = (TTupleProtocol) prot;
      BitSet incoming = iprot.readBitSet(5);
      if (incoming.get(0)) {
        struct.sensor = iprot.readString();
        struct.setSensorIsSet(true);
      }
      if (incoming.get(1)) {
        struct.hostname = iprot.readString();
        struct.setHostnameIsSet(true);
      }
      if (incoming.get(2)) {
        {
          org.apache.thrift.protocol.TSet _set45 = new org.apache.thrift.protocol.TSet(org.apache.thrift.protocol.TType.STRING, iprot.readI32());
          struct.labels = new HashSet<String>(2*_set45.size);
          for (int _i46 = 0; _i46 < _set45.size; ++_i46)
          {
            String _elem47; // required
            _elem47 = iprot.readString();
            struct.labels.add(_elem47);
          }
        }
        struct.setLabelsIsSet(true);
      }
      if (incoming.get(3)) {
        struct.configuration = new SensorConfiguration();
        struct.configuration.read(iprot);
        struct.setConfigurationIsSet(true);
      }
      if (incoming.get(4)) {
        struct.active = iprot.readBool();
        struct.setActiveIsSet(true);
      }
    }
  }

}

