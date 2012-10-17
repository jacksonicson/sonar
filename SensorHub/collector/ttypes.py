#
# Autogenerated by Thrift Compiler (0.9.0-dev)
#
# DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
#
#  options string: py
#

from thrift.Thrift import TType, TMessageType, TException, TApplicationException

from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol, TProtocol
try:
  from thrift.protocol import fastbinary
except:
  fastbinary = None


class SensorType:
  METRIC = 0
  LOG = 1

  _VALUES_TO_NAMES = {
    0: "METRIC",
    1: "LOG",
  }

  _NAMES_TO_VALUES = {
    "METRIC": 0,
    "LOG": 1,
  }


class Identifier:
  """
  Attributes:
   - timestamp
   - sensor
   - hostname
  """

  thrift_spec = (
    None, # 0
    (1, TType.I64, 'timestamp', None, None, ), # 1
    (2, TType.STRING, 'hostname', None, None, ), # 2
    (3, TType.STRING, 'sensor', None, None, ), # 3
  )

  def __init__(self, timestamp=None, sensor=None, hostname=None,):
    self.timestamp = timestamp
    self.sensor = sensor
    self.hostname = hostname

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.I64:
          self.timestamp = iprot.readI64();
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.STRING:
          self.sensor = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRING:
          self.hostname = iprot.readString();
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('Identifier')
    if self.timestamp is not None:
      oprot.writeFieldBegin('timestamp', TType.I64, 1)
      oprot.writeI64(self.timestamp)
      oprot.writeFieldEnd()
    if self.hostname is not None:
      oprot.writeFieldBegin('hostname', TType.STRING, 2)
      oprot.writeString(self.hostname)
      oprot.writeFieldEnd()
    if self.sensor is not None:
      oprot.writeFieldBegin('sensor', TType.STRING, 3)
      oprot.writeString(self.sensor)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class MetricReading:
  """
  Attributes:
   - value
   - labels
  """

  thrift_spec = (
    None, # 0
    (1, TType.DOUBLE, 'value', None, None, ), # 1
    None, # 2
    (3, TType.SET, 'labels', (TType.STRING,None), None, ), # 3
  )

  def __init__(self, value=None, labels=None,):
    self.value = value
    self.labels = labels

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.DOUBLE:
          self.value = iprot.readDouble();
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.SET:
          self.labels = set()
          (_etype3, _size0) = iprot.readSetBegin()
          for _i4 in xrange(_size0):
            _elem5 = iprot.readString();
            self.labels.add(_elem5)
          iprot.readSetEnd()
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('MetricReading')
    if self.value is not None:
      oprot.writeFieldBegin('value', TType.DOUBLE, 1)
      oprot.writeDouble(self.value)
      oprot.writeFieldEnd()
    if self.labels is not None:
      oprot.writeFieldBegin('labels', TType.SET, 3)
      oprot.writeSetBegin(TType.STRING, len(self.labels))
      for iter6 in self.labels:
        oprot.writeString(iter6)
      oprot.writeSetEnd()
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class LogMessage:
  """
  Attributes:
   - logLevel
   - logMessage
   - programName
   - timestamp
  """

  thrift_spec = (
    None, # 0
    (1, TType.I32, 'logLevel', None, None, ), # 1
    (2, TType.STRING, 'logMessage', None, None, ), # 2
    (3, TType.STRING, 'programName', None, None, ), # 3
    (4, TType.I64, 'timestamp', None, None, ), # 4
  )

  def __init__(self, logLevel=None, logMessage=None, programName=None, timestamp=None,):
    self.logLevel = logLevel
    self.logMessage = logMessage
    self.programName = programName
    self.timestamp = timestamp

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.I32:
          self.logLevel = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRING:
          self.logMessage = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.STRING:
          self.programName = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 4:
        if ftype == TType.I64:
          self.timestamp = iprot.readI64();
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('LogMessage')
    if self.logLevel is not None:
      oprot.writeFieldBegin('logLevel', TType.I32, 1)
      oprot.writeI32(self.logLevel)
      oprot.writeFieldEnd()
    if self.logMessage is not None:
      oprot.writeFieldBegin('logMessage', TType.STRING, 2)
      oprot.writeString(self.logMessage)
      oprot.writeFieldEnd()
    if self.programName is not None:
      oprot.writeFieldBegin('programName', TType.STRING, 3)
      oprot.writeString(self.programName)
      oprot.writeFieldEnd()
    if self.timestamp is not None:
      oprot.writeFieldBegin('timestamp', TType.I64, 4)
      oprot.writeI64(self.timestamp)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class LogsQuery:
  """
  Attributes:
   - startTime
   - stopTime
   - sensor
   - hostname
  """

  thrift_spec = (
    None, # 0
    (1, TType.I64, 'startTime', None, None, ), # 1
    (2, TType.I64, 'stopTime', None, None, ), # 2
    (3, TType.STRING, 'sensor', None, None, ), # 3
    (4, TType.STRING, 'hostname', None, None, ), # 4
  )

  def __init__(self, startTime=None, stopTime=None, sensor=None, hostname=None,):
    self.startTime = startTime
    self.stopTime = stopTime
    self.sensor = sensor
    self.hostname = hostname

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.I64:
          self.startTime = iprot.readI64();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.I64:
          self.stopTime = iprot.readI64();
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.STRING:
          self.sensor = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 4:
        if ftype == TType.STRING:
          self.hostname = iprot.readString();
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('LogsQuery')
    if self.startTime is not None:
      oprot.writeFieldBegin('startTime', TType.I64, 1)
      oprot.writeI64(self.startTime)
      oprot.writeFieldEnd()
    if self.stopTime is not None:
      oprot.writeFieldBegin('stopTime', TType.I64, 2)
      oprot.writeI64(self.stopTime)
      oprot.writeFieldEnd()
    if self.sensor is not None:
      oprot.writeFieldBegin('sensor', TType.STRING, 3)
      oprot.writeString(self.sensor)
      oprot.writeFieldEnd()
    if self.hostname is not None:
      oprot.writeFieldBegin('hostname', TType.STRING, 4)
      oprot.writeString(self.hostname)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class File:
  """
  Attributes:
   - filename
   - description
   - file
   - labels
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRING, 'filename', None, None, ), # 1
    (2, TType.STRING, 'description', None, None, ), # 2
    (3, TType.STRING, 'file', None, None, ), # 3
    (4, TType.SET, 'labels', (TType.STRING,None), None, ), # 4
  )

  def __init__(self, filename=None, description=None, file=None, labels=None,):
    self.filename = filename
    self.description = description
    self.file = file
    self.labels = labels

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.STRING:
          self.filename = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRING:
          self.description = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.STRING:
          self.file = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 4:
        if ftype == TType.SET:
          self.labels = set()
          (_etype10, _size7) = iprot.readSetBegin()
          for _i11 in xrange(_size7):
            _elem12 = iprot.readString();
            self.labels.add(_elem12)
          iprot.readSetEnd()
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('File')
    if self.filename is not None:
      oprot.writeFieldBegin('filename', TType.STRING, 1)
      oprot.writeString(self.filename)
      oprot.writeFieldEnd()
    if self.description is not None:
      oprot.writeFieldBegin('description', TType.STRING, 2)
      oprot.writeString(self.description)
      oprot.writeFieldEnd()
    if self.file is not None:
      oprot.writeFieldBegin('file', TType.STRING, 3)
      oprot.writeString(self.file)
      oprot.writeFieldEnd()
    if self.labels is not None:
      oprot.writeFieldBegin('labels', TType.SET, 4)
      oprot.writeSetBegin(TType.STRING, len(self.labels))
      for iter13 in self.labels:
        oprot.writeString(iter13)
      oprot.writeSetEnd()
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class TransferableTimeSeriesPoint:
  """
  Attributes:
   - timestamp
   - value
   - labels
  """

  thrift_spec = (
    None, # 0
    (1, TType.I64, 'timestamp', None, None, ), # 1
    (2, TType.DOUBLE, 'value', None, None, ), # 2
    (3, TType.SET, 'labels', (TType.STRING,None), None, ), # 3
  )

  def __init__(self, timestamp=None, value=None, labels=None,):
    self.timestamp = timestamp
    self.value = value
    self.labels = labels

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.I64:
          self.timestamp = iprot.readI64();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.DOUBLE:
          self.value = iprot.readDouble();
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.SET:
          self.labels = set()
          (_etype17, _size14) = iprot.readSetBegin()
          for _i18 in xrange(_size14):
            _elem19 = iprot.readString();
            self.labels.add(_elem19)
          iprot.readSetEnd()
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('TransferableTimeSeriesPoint')
    if self.timestamp is not None:
      oprot.writeFieldBegin('timestamp', TType.I64, 1)
      oprot.writeI64(self.timestamp)
      oprot.writeFieldEnd()
    if self.value is not None:
      oprot.writeFieldBegin('value', TType.DOUBLE, 2)
      oprot.writeDouble(self.value)
      oprot.writeFieldEnd()
    if self.labels is not None:
      oprot.writeFieldBegin('labels', TType.SET, 3)
      oprot.writeSetBegin(TType.STRING, len(self.labels))
      for iter20 in self.labels:
        oprot.writeString(iter20)
      oprot.writeSetEnd()
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class TimeSeriesQuery:
  """
  Attributes:
   - startTime
   - stopTime
   - sensor
   - labels
   - hostname
  """

  thrift_spec = (
    None, # 0
    (1, TType.I64, 'startTime', None, None, ), # 1
    (2, TType.I64, 'stopTime', None, None, ), # 2
    (3, TType.STRING, 'sensor', None, None, ), # 3
    (4, TType.STRING, 'hostname', None, None, ), # 4
    (5, TType.SET, 'labels', (TType.STRING,None), None, ), # 5
  )

  def __init__(self, startTime=None, stopTime=None, sensor=None, labels=None, hostname=None,):
    self.startTime = startTime
    self.stopTime = stopTime
    self.sensor = sensor
    self.labels = labels
    self.hostname = hostname

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.I64:
          self.startTime = iprot.readI64();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.I64:
          self.stopTime = iprot.readI64();
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.STRING:
          self.sensor = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 5:
        if ftype == TType.SET:
          self.labels = set()
          (_etype24, _size21) = iprot.readSetBegin()
          for _i25 in xrange(_size21):
            _elem26 = iprot.readString();
            self.labels.add(_elem26)
          iprot.readSetEnd()
        else:
          iprot.skip(ftype)
      elif fid == 4:
        if ftype == TType.STRING:
          self.hostname = iprot.readString();
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('TimeSeriesQuery')
    if self.startTime is not None:
      oprot.writeFieldBegin('startTime', TType.I64, 1)
      oprot.writeI64(self.startTime)
      oprot.writeFieldEnd()
    if self.stopTime is not None:
      oprot.writeFieldBegin('stopTime', TType.I64, 2)
      oprot.writeI64(self.stopTime)
      oprot.writeFieldEnd()
    if self.sensor is not None:
      oprot.writeFieldBegin('sensor', TType.STRING, 3)
      oprot.writeString(self.sensor)
      oprot.writeFieldEnd()
    if self.hostname is not None:
      oprot.writeFieldBegin('hostname', TType.STRING, 4)
      oprot.writeString(self.hostname)
      oprot.writeFieldEnd()
    if self.labels is not None:
      oprot.writeFieldBegin('labels', TType.SET, 5)
      oprot.writeSetBegin(TType.STRING, len(self.labels))
      for iter27 in self.labels:
        oprot.writeString(iter27)
      oprot.writeSetEnd()
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class Parameter:
  """
  Attributes:
   - key
   - value
   - extendSensor
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRING, 'key', None, None, ), # 1
    (2, TType.STRING, 'value', None, None, ), # 2
    (3, TType.STRING, 'extendSensor', None, None, ), # 3
  )

  def __init__(self, key=None, value=None, extendSensor=None,):
    self.key = key
    self.value = value
    self.extendSensor = extendSensor

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.STRING:
          self.key = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRING:
          self.value = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.STRING:
          self.extendSensor = iprot.readString();
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('Parameter')
    if self.key is not None:
      oprot.writeFieldBegin('key', TType.STRING, 1)
      oprot.writeString(self.key)
      oprot.writeFieldEnd()
    if self.value is not None:
      oprot.writeFieldBegin('value', TType.STRING, 2)
      oprot.writeString(self.value)
      oprot.writeFieldEnd()
    if self.extendSensor is not None:
      oprot.writeFieldBegin('extendSensor', TType.STRING, 3)
      oprot.writeString(self.extendSensor)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class SensorConfiguration:
  """
  Attributes:
   - interval
   - parameters
   - sensorType
   - sensorExtends
  """

  thrift_spec = (
    None, # 0
    (1, TType.I64, 'interval', None, None, ), # 1
    (2, TType.LIST, 'parameters', (TType.STRUCT,(Parameter, Parameter.thrift_spec)), None, ), # 2
    (3, TType.I32, 'sensorType', None, None, ), # 3
    (4, TType.STRING, 'sensorExtends', None, None, ), # 4
  )

  def __init__(self, interval=None, parameters=None, sensorType=None, sensorExtends=None,):
    self.interval = interval
    self.parameters = parameters
    self.sensorType = sensorType
    self.sensorExtends = sensorExtends

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.I64:
          self.interval = iprot.readI64();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.LIST:
          self.parameters = []
          (_etype31, _size28) = iprot.readListBegin()
          for _i32 in xrange(_size28):
            _elem33 = Parameter()
            _elem33.read(iprot)
            self.parameters.append(_elem33)
          iprot.readListEnd()
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.I32:
          self.sensorType = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 4:
        if ftype == TType.STRING:
          self.sensorExtends = iprot.readString();
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('SensorConfiguration')
    if self.interval is not None:
      oprot.writeFieldBegin('interval', TType.I64, 1)
      oprot.writeI64(self.interval)
      oprot.writeFieldEnd()
    if self.parameters is not None:
      oprot.writeFieldBegin('parameters', TType.LIST, 2)
      oprot.writeListBegin(TType.STRUCT, len(self.parameters))
      for iter34 in self.parameters:
        iter34.write(oprot)
      oprot.writeListEnd()
      oprot.writeFieldEnd()
    if self.sensorType is not None:
      oprot.writeFieldBegin('sensorType', TType.I32, 3)
      oprot.writeI32(self.sensorType)
      oprot.writeFieldEnd()
    if self.sensorExtends is not None:
      oprot.writeFieldBegin('sensorExtends', TType.STRING, 4)
      oprot.writeString(self.sensorExtends)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class BundledSensorConfiguration:
  """
  Attributes:
   - sensor
   - hostname
   - labels
   - configuration
   - active
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRING, 'sensor', None, None, ), # 1
    (2, TType.STRING, 'hostname', None, None, ), # 2
    (3, TType.SET, 'labels', (TType.STRING,None), None, ), # 3
    (4, TType.STRUCT, 'configuration', (SensorConfiguration, SensorConfiguration.thrift_spec), None, ), # 4
    (5, TType.BOOL, 'active', None, None, ), # 5
  )

  def __init__(self, sensor=None, hostname=None, labels=None, configuration=None, active=None,):
    self.sensor = sensor
    self.hostname = hostname
    self.labels = labels
    self.configuration = configuration
    self.active = active

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.STRING:
          self.sensor = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRING:
          self.hostname = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.SET:
          self.labels = set()
          (_etype38, _size35) = iprot.readSetBegin()
          for _i39 in xrange(_size35):
            _elem40 = iprot.readString();
            self.labels.add(_elem40)
          iprot.readSetEnd()
        else:
          iprot.skip(ftype)
      elif fid == 4:
        if ftype == TType.STRUCT:
          self.configuration = SensorConfiguration()
          self.configuration.read(iprot)
        else:
          iprot.skip(ftype)
      elif fid == 5:
        if ftype == TType.BOOL:
          self.active = iprot.readBool();
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('BundledSensorConfiguration')
    if self.sensor is not None:
      oprot.writeFieldBegin('sensor', TType.STRING, 1)
      oprot.writeString(self.sensor)
      oprot.writeFieldEnd()
    if self.hostname is not None:
      oprot.writeFieldBegin('hostname', TType.STRING, 2)
      oprot.writeString(self.hostname)
      oprot.writeFieldEnd()
    if self.labels is not None:
      oprot.writeFieldBegin('labels', TType.SET, 3)
      oprot.writeSetBegin(TType.STRING, len(self.labels))
      for iter41 in self.labels:
        oprot.writeString(iter41)
      oprot.writeSetEnd()
      oprot.writeFieldEnd()
    if self.configuration is not None:
      oprot.writeFieldBegin('configuration', TType.STRUCT, 4)
      self.configuration.write(oprot)
      oprot.writeFieldEnd()
    if self.active is not None:
      oprot.writeFieldBegin('active', TType.BOOL, 5)
      oprot.writeBool(self.active)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class SensorToWatch:
  """
  Attributes:
   - hostname
   - sensor
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRING, 'hostname', None, None, ), # 1
    (2, TType.STRING, 'sensor', None, None, ), # 2
  )

  def __init__(self, hostname=None, sensor=None,):
    self.hostname = hostname
    self.sensor = sensor

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.STRING:
          self.hostname = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRING:
          self.sensor = iprot.readString();
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('SensorToWatch')
    if self.hostname is not None:
      oprot.writeFieldBegin('hostname', TType.STRING, 1)
      oprot.writeString(self.hostname)
      oprot.writeFieldEnd()
    if self.sensor is not None:
      oprot.writeFieldBegin('sensor', TType.STRING, 2)
      oprot.writeString(self.sensor)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class NotificationData:
  """
  Attributes:
   - id
   - reading
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRUCT, 'id', (Identifier, Identifier.thrift_spec), None, ), # 1
    (2, TType.STRUCT, 'reading', (MetricReading, MetricReading.thrift_spec), None, ), # 2
  )

  def __init__(self, id=None, reading=None,):
    self.id = id
    self.reading = reading

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.STRUCT:
          self.id = Identifier()
          self.id.read(iprot)
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRUCT:
          self.reading = MetricReading()
          self.reading.read(iprot)
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('NotificationData')
    if self.id is not None:
      oprot.writeFieldBegin('id', TType.STRUCT, 1)
      self.id.write(oprot)
      oprot.writeFieldEnd()
    if self.reading is not None:
      oprot.writeFieldBegin('reading', TType.STRUCT, 2)
      self.reading.write(oprot)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)
