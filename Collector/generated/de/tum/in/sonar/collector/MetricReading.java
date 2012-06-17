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

public class MetricReading implements org.apache.thrift.TBase<MetricReading, MetricReading._Fields>, java.io.Serializable, Cloneable {
  private static final org.apache.thrift.protocol.TStruct STRUCT_DESC = new org.apache.thrift.protocol.TStruct("MetricReading");

  private static final org.apache.thrift.protocol.TField VALUE_FIELD_DESC = new org.apache.thrift.protocol.TField("value", org.apache.thrift.protocol.TType.DOUBLE, (short)1);
  private static final org.apache.thrift.protocol.TField LABELS_FIELD_DESC = new org.apache.thrift.protocol.TField("labels", org.apache.thrift.protocol.TType.SET, (short)3);

  private static final Map<Class<? extends IScheme>, SchemeFactory> schemes = new HashMap<Class<? extends IScheme>, SchemeFactory>();
  static {
    schemes.put(StandardScheme.class, new MetricReadingStandardSchemeFactory());
    schemes.put(TupleScheme.class, new MetricReadingTupleSchemeFactory());
  }

  public double value; // required
  public Set<String> labels; // required

  /** The set of fields this struct contains, along with convenience methods for finding and manipulating them. */
  public enum _Fields implements org.apache.thrift.TFieldIdEnum {
    VALUE((short)1, "value"),
    LABELS((short)3, "labels");

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
        case 1: // VALUE
          return VALUE;
        case 3: // LABELS
          return LABELS;
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
  private static final int __VALUE_ISSET_ID = 0;
  private BitSet __isset_bit_vector = new BitSet(1);
  public static final Map<_Fields, org.apache.thrift.meta_data.FieldMetaData> metaDataMap;
  static {
    Map<_Fields, org.apache.thrift.meta_data.FieldMetaData> tmpMap = new EnumMap<_Fields, org.apache.thrift.meta_data.FieldMetaData>(_Fields.class);
    tmpMap.put(_Fields.VALUE, new org.apache.thrift.meta_data.FieldMetaData("value", org.apache.thrift.TFieldRequirementType.DEFAULT, 
        new org.apache.thrift.meta_data.FieldValueMetaData(org.apache.thrift.protocol.TType.DOUBLE)));
    tmpMap.put(_Fields.LABELS, new org.apache.thrift.meta_data.FieldMetaData("labels", org.apache.thrift.TFieldRequirementType.DEFAULT, 
        new org.apache.thrift.meta_data.SetMetaData(org.apache.thrift.protocol.TType.SET, 
            new org.apache.thrift.meta_data.FieldValueMetaData(org.apache.thrift.protocol.TType.STRING))));
    metaDataMap = Collections.unmodifiableMap(tmpMap);
    org.apache.thrift.meta_data.FieldMetaData.addStructMetaDataMap(MetricReading.class, metaDataMap);
  }

  public MetricReading() {
  }

  public MetricReading(
    double value,
    Set<String> labels)
  {
    this();
    this.value = value;
    setValueIsSet(true);
    this.labels = labels;
  }

  /**
   * Performs a deep copy on <i>other</i>.
   */
  public MetricReading(MetricReading other) {
    __isset_bit_vector.clear();
    __isset_bit_vector.or(other.__isset_bit_vector);
    this.value = other.value;
    if (other.isSetLabels()) {
      Set<String> __this__labels = new HashSet<String>();
      for (String other_element : other.labels) {
        __this__labels.add(other_element);
      }
      this.labels = __this__labels;
    }
  }

  public MetricReading deepCopy() {
    return new MetricReading(this);
  }

  @Override
  public void clear() {
    setValueIsSet(false);
    this.value = 0.0;
    this.labels = null;
  }

  public double getValue() {
    return this.value;
  }

  public MetricReading setValue(double value) {
    this.value = value;
    setValueIsSet(true);
    return this;
  }

  public void unsetValue() {
    __isset_bit_vector.clear(__VALUE_ISSET_ID);
  }

  /** Returns true if field value is set (has been assigned a value) and false otherwise */
  public boolean isSetValue() {
    return __isset_bit_vector.get(__VALUE_ISSET_ID);
  }

  public void setValueIsSet(boolean value) {
    __isset_bit_vector.set(__VALUE_ISSET_ID, value);
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

  public MetricReading setLabels(Set<String> labels) {
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

  public void setFieldValue(_Fields field, Object value) {
    switch (field) {
    case VALUE:
      if (value == null) {
        unsetValue();
      } else {
        setValue((Double)value);
      }
      break;

    case LABELS:
      if (value == null) {
        unsetLabels();
      } else {
        setLabels((Set<String>)value);
      }
      break;

    }
  }

  public Object getFieldValue(_Fields field) {
    switch (field) {
    case VALUE:
      return Double.valueOf(getValue());

    case LABELS:
      return getLabels();

    }
    throw new IllegalStateException();
  }

  /** Returns true if field corresponding to fieldID is set (has been assigned a value) and false otherwise */
  public boolean isSet(_Fields field) {
    if (field == null) {
      throw new IllegalArgumentException();
    }

    switch (field) {
    case VALUE:
      return isSetValue();
    case LABELS:
      return isSetLabels();
    }
    throw new IllegalStateException();
  }

  @Override
  public boolean equals(Object that) {
    if (that == null)
      return false;
    if (that instanceof MetricReading)
      return this.equals((MetricReading)that);
    return false;
  }

  public boolean equals(MetricReading that) {
    if (that == null)
      return false;

    boolean this_present_value = true;
    boolean that_present_value = true;
    if (this_present_value || that_present_value) {
      if (!(this_present_value && that_present_value))
        return false;
      if (this.value != that.value)
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

    return true;
  }

  @Override
  public int hashCode() {
    return 0;
  }

  public int compareTo(MetricReading other) {
    if (!getClass().equals(other.getClass())) {
      return getClass().getName().compareTo(other.getClass().getName());
    }

    int lastComparison = 0;
    MetricReading typedOther = (MetricReading)other;

    lastComparison = Boolean.valueOf(isSetValue()).compareTo(typedOther.isSetValue());
    if (lastComparison != 0) {
      return lastComparison;
    }
    if (isSetValue()) {
      lastComparison = org.apache.thrift.TBaseHelper.compareTo(this.value, typedOther.value);
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
    StringBuilder sb = new StringBuilder("MetricReading(");
    boolean first = true;

    sb.append("value:");
    sb.append(this.value);
    first = false;
    if (!first) sb.append(", ");
    sb.append("labels:");
    if (this.labels == null) {
      sb.append("null");
    } else {
      sb.append(this.labels);
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
      // it doesn't seem like you should have to do this, but java serialization is wacky, and doesn't call the default constructor.
      __isset_bit_vector = new BitSet(1);
      read(new org.apache.thrift.protocol.TCompactProtocol(new org.apache.thrift.transport.TIOStreamTransport(in)));
    } catch (org.apache.thrift.TException te) {
      throw new java.io.IOException(te);
    }
  }

  private static class MetricReadingStandardSchemeFactory implements SchemeFactory {
    public MetricReadingStandardScheme getScheme() {
      return new MetricReadingStandardScheme();
    }
  }

  private static class MetricReadingStandardScheme extends StandardScheme<MetricReading> {

    public void read(org.apache.thrift.protocol.TProtocol iprot, MetricReading struct) throws org.apache.thrift.TException {
      org.apache.thrift.protocol.TField schemeField;
      iprot.readStructBegin();
      while (true)
      {
        schemeField = iprot.readFieldBegin();
        if (schemeField.type == org.apache.thrift.protocol.TType.STOP) { 
          break;
        }
        switch (schemeField.id) {
          case 1: // VALUE
            if (schemeField.type == org.apache.thrift.protocol.TType.DOUBLE) {
              struct.value = iprot.readDouble();
              struct.setValueIsSet(true);
            } else { 
              org.apache.thrift.protocol.TProtocolUtil.skip(iprot, schemeField.type);
            }
            break;
          case 3: // LABELS
            if (schemeField.type == org.apache.thrift.protocol.TType.SET) {
              {
                org.apache.thrift.protocol.TSet _set0 = iprot.readSetBegin();
                struct.labels = new HashSet<String>(2*_set0.size);
                for (int _i1 = 0; _i1 < _set0.size; ++_i1)
                {
                  String _elem2; // required
                  _elem2 = iprot.readString();
                  struct.labels.add(_elem2);
                }
                iprot.readSetEnd();
              }
              struct.setLabelsIsSet(true);
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

    public void write(org.apache.thrift.protocol.TProtocol oprot, MetricReading struct) throws org.apache.thrift.TException {
      struct.validate();

      oprot.writeStructBegin(STRUCT_DESC);
      oprot.writeFieldBegin(VALUE_FIELD_DESC);
      oprot.writeDouble(struct.value);
      oprot.writeFieldEnd();
      if (struct.labels != null) {
        oprot.writeFieldBegin(LABELS_FIELD_DESC);
        {
          oprot.writeSetBegin(new org.apache.thrift.protocol.TSet(org.apache.thrift.protocol.TType.STRING, struct.labels.size()));
          for (String _iter3 : struct.labels)
          {
            oprot.writeString(_iter3);
          }
          oprot.writeSetEnd();
        }
        oprot.writeFieldEnd();
      }
      oprot.writeFieldStop();
      oprot.writeStructEnd();
    }

  }

  private static class MetricReadingTupleSchemeFactory implements SchemeFactory {
    public MetricReadingTupleScheme getScheme() {
      return new MetricReadingTupleScheme();
    }
  }

  private static class MetricReadingTupleScheme extends TupleScheme<MetricReading> {

    @Override
    public void write(org.apache.thrift.protocol.TProtocol prot, MetricReading struct) throws org.apache.thrift.TException {
      TTupleProtocol oprot = (TTupleProtocol) prot;
      BitSet optionals = new BitSet();
      if (struct.isSetValue()) {
        optionals.set(0);
      }
      if (struct.isSetLabels()) {
        optionals.set(1);
      }
      oprot.writeBitSet(optionals, 2);
      if (struct.isSetValue()) {
        oprot.writeDouble(struct.value);
      }
      if (struct.isSetLabels()) {
        {
          oprot.writeI32(struct.labels.size());
          for (String _iter4 : struct.labels)
          {
            oprot.writeString(_iter4);
          }
        }
      }
    }

    @Override
    public void read(org.apache.thrift.protocol.TProtocol prot, MetricReading struct) throws org.apache.thrift.TException {
      TTupleProtocol iprot = (TTupleProtocol) prot;
      BitSet incoming = iprot.readBitSet(2);
      if (incoming.get(0)) {
        struct.value = iprot.readDouble();
        struct.setValueIsSet(true);
      }
      if (incoming.get(1)) {
        {
          org.apache.thrift.protocol.TSet _set5 = new org.apache.thrift.protocol.TSet(org.apache.thrift.protocol.TType.STRING, iprot.readI32());
          struct.labels = new HashSet<String>(2*_set5.size);
          for (int _i6 = 0; _i6 < _set5.size; ++_i6)
          {
            String _elem7; // required
            _elem7 = iprot.readString();
            struct.labels.add(_elem7);
          }
        }
        struct.setLabelsIsSet(true);
      }
    }
  }

}

