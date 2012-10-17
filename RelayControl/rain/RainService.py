#
# Autogenerated by Thrift Compiler (0.9.0-dev)
#
# DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
#
#  options string: py:twisted
#

from thrift.Thrift import TType, TMessageType, TException, TApplicationException
from ttypes import *
from thrift.Thrift import TProcessor
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol, TProtocol
try:
  from thrift.protocol import fastbinary
except:
  fastbinary = None

from zope.interface import Interface, implements
from twisted.internet import defer
from thrift.transport import TTwisted

class Iface(Interface):
  def startBenchmark(controllerTimestamp):
    """
    Parameters:
     - controllerTimestamp
    """
    pass

  def dynamicLoadProfile(profile):
    """
    Parameters:
     - profile
    """
    pass

  def getTrackNames():
    pass

  def getRampUpTime():
    pass

  def getRampDownTime():
    pass

  def getDurationTime():
    pass


class Client:
  implements(Iface)

  def __init__(self, transport, oprot_factory):
    self._transport = transport
    self._oprot_factory = oprot_factory
    self._seqid = 0
    self._reqs = {}

  def startBenchmark(self, controllerTimestamp):
    """
    Parameters:
     - controllerTimestamp
    """
    self._seqid += 1
    d = self._reqs[self._seqid] = defer.Deferred()
    self.send_startBenchmark(controllerTimestamp)
    return d

  def send_startBenchmark(self, controllerTimestamp):
    oprot = self._oprot_factory.getProtocol(self._transport)
    oprot.writeMessageBegin('startBenchmark', TMessageType.CALL, self._seqid)
    args = startBenchmark_args()
    args.controllerTimestamp = controllerTimestamp
    args.write(oprot)
    oprot.writeMessageEnd()
    oprot.trans.flush()

  def recv_startBenchmark(self, iprot, mtype, rseqid):
    d = self._reqs.pop(rseqid)
    if mtype == TMessageType.EXCEPTION:
      x = TApplicationException()
      x.read(iprot)
      iprot.readMessageEnd()
      return d.errback(x)
    result = startBenchmark_result()
    result.read(iprot)
    iprot.readMessageEnd()
    if result.success is not None:
      return d.callback(result.success)
    return d.errback(TApplicationException(TApplicationException.MISSING_RESULT, "startBenchmark failed: unknown result"))

  def dynamicLoadProfile(self, profile):
    """
    Parameters:
     - profile
    """
    self._seqid += 1
    d = self._reqs[self._seqid] = defer.Deferred()
    self.send_dynamicLoadProfile(profile)
    return d

  def send_dynamicLoadProfile(self, profile):
    oprot = self._oprot_factory.getProtocol(self._transport)
    oprot.writeMessageBegin('dynamicLoadProfile', TMessageType.CALL, self._seqid)
    args = dynamicLoadProfile_args()
    args.profile = profile
    args.write(oprot)
    oprot.writeMessageEnd()
    oprot.trans.flush()

  def recv_dynamicLoadProfile(self, iprot, mtype, rseqid):
    d = self._reqs.pop(rseqid)
    if mtype == TMessageType.EXCEPTION:
      x = TApplicationException()
      x.read(iprot)
      iprot.readMessageEnd()
      return d.errback(x)
    result = dynamicLoadProfile_result()
    result.read(iprot)
    iprot.readMessageEnd()
    if result.success is not None:
      return d.callback(result.success)
    return d.errback(TApplicationException(TApplicationException.MISSING_RESULT, "dynamicLoadProfile failed: unknown result"))

  def getTrackNames(self, ):
    self._seqid += 1
    d = self._reqs[self._seqid] = defer.Deferred()
    self.send_getTrackNames()
    return d

  def send_getTrackNames(self, ):
    oprot = self._oprot_factory.getProtocol(self._transport)
    oprot.writeMessageBegin('getTrackNames', TMessageType.CALL, self._seqid)
    args = getTrackNames_args()
    args.write(oprot)
    oprot.writeMessageEnd()
    oprot.trans.flush()

  def recv_getTrackNames(self, iprot, mtype, rseqid):
    d = self._reqs.pop(rseqid)
    if mtype == TMessageType.EXCEPTION:
      x = TApplicationException()
      x.read(iprot)
      iprot.readMessageEnd()
      return d.errback(x)
    result = getTrackNames_result()
    result.read(iprot)
    iprot.readMessageEnd()
    if result.success is not None:
      return d.callback(result.success)
    return d.errback(TApplicationException(TApplicationException.MISSING_RESULT, "getTrackNames failed: unknown result"))

  def getRampUpTime(self, ):
    self._seqid += 1
    d = self._reqs[self._seqid] = defer.Deferred()
    self.send_getRampUpTime()
    return d

  def send_getRampUpTime(self, ):
    oprot = self._oprot_factory.getProtocol(self._transport)
    oprot.writeMessageBegin('getRampUpTime', TMessageType.CALL, self._seqid)
    args = getRampUpTime_args()
    args.write(oprot)
    oprot.writeMessageEnd()
    oprot.trans.flush()

  def recv_getRampUpTime(self, iprot, mtype, rseqid):
    d = self._reqs.pop(rseqid)
    if mtype == TMessageType.EXCEPTION:
      x = TApplicationException()
      x.read(iprot)
      iprot.readMessageEnd()
      return d.errback(x)
    result = getRampUpTime_result()
    result.read(iprot)
    iprot.readMessageEnd()
    if result.success is not None:
      return d.callback(result.success)
    return d.errback(TApplicationException(TApplicationException.MISSING_RESULT, "getRampUpTime failed: unknown result"))

  def getRampDownTime(self, ):
    self._seqid += 1
    d = self._reqs[self._seqid] = defer.Deferred()
    self.send_getRampDownTime()
    return d

  def send_getRampDownTime(self, ):
    oprot = self._oprot_factory.getProtocol(self._transport)
    oprot.writeMessageBegin('getRampDownTime', TMessageType.CALL, self._seqid)
    args = getRampDownTime_args()
    args.write(oprot)
    oprot.writeMessageEnd()
    oprot.trans.flush()

  def recv_getRampDownTime(self, iprot, mtype, rseqid):
    d = self._reqs.pop(rseqid)
    if mtype == TMessageType.EXCEPTION:
      x = TApplicationException()
      x.read(iprot)
      iprot.readMessageEnd()
      return d.errback(x)
    result = getRampDownTime_result()
    result.read(iprot)
    iprot.readMessageEnd()
    if result.success is not None:
      return d.callback(result.success)
    return d.errback(TApplicationException(TApplicationException.MISSING_RESULT, "getRampDownTime failed: unknown result"))

  def getDurationTime(self, ):
    self._seqid += 1
    d = self._reqs[self._seqid] = defer.Deferred()
    self.send_getDurationTime()
    return d

  def send_getDurationTime(self, ):
    oprot = self._oprot_factory.getProtocol(self._transport)
    oprot.writeMessageBegin('getDurationTime', TMessageType.CALL, self._seqid)
    args = getDurationTime_args()
    args.write(oprot)
    oprot.writeMessageEnd()
    oprot.trans.flush()

  def recv_getDurationTime(self, iprot, mtype, rseqid):
    d = self._reqs.pop(rseqid)
    if mtype == TMessageType.EXCEPTION:
      x = TApplicationException()
      x.read(iprot)
      iprot.readMessageEnd()
      return d.errback(x)
    result = getDurationTime_result()
    result.read(iprot)
    iprot.readMessageEnd()
    if result.success is not None:
      return d.callback(result.success)
    return d.errback(TApplicationException(TApplicationException.MISSING_RESULT, "getDurationTime failed: unknown result"))


class Processor(TProcessor):
  implements(Iface)

  def __init__(self, handler):
    self._handler = Iface(handler)
    self._processMap = {}
    self._processMap["startBenchmark"] = Processor.process_startBenchmark
    self._processMap["dynamicLoadProfile"] = Processor.process_dynamicLoadProfile
    self._processMap["getTrackNames"] = Processor.process_getTrackNames
    self._processMap["getRampUpTime"] = Processor.process_getRampUpTime
    self._processMap["getRampDownTime"] = Processor.process_getRampDownTime
    self._processMap["getDurationTime"] = Processor.process_getDurationTime

  def process(self, iprot, oprot):
    (name, type, seqid) = iprot.readMessageBegin()
    if name not in self._processMap:
      iprot.skip(TType.STRUCT)
      iprot.readMessageEnd()
      x = TApplicationException(TApplicationException.UNKNOWN_METHOD, 'Unknown function %s' % (name))
      oprot.writeMessageBegin(name, TMessageType.EXCEPTION, seqid)
      x.write(oprot)
      oprot.writeMessageEnd()
      oprot.trans.flush()
      return defer.succeed(None)
    else:
      return self._processMap[name](self, seqid, iprot, oprot)

  def process_startBenchmark(self, seqid, iprot, oprot):
    args = startBenchmark_args()
    args.read(iprot)
    iprot.readMessageEnd()
    result = startBenchmark_result()
    d = defer.maybeDeferred(self._handler.startBenchmark, args.controllerTimestamp)
    d.addCallback(self.write_results_success_startBenchmark, result, seqid, oprot)
    return d

  def write_results_success_startBenchmark(self, success, result, seqid, oprot):
    result.success = success
    oprot.writeMessageBegin("startBenchmark", TMessageType.REPLY, seqid)
    result.write(oprot)
    oprot.writeMessageEnd()
    oprot.trans.flush()

  def process_dynamicLoadProfile(self, seqid, iprot, oprot):
    args = dynamicLoadProfile_args()
    args.read(iprot)
    iprot.readMessageEnd()
    result = dynamicLoadProfile_result()
    d = defer.maybeDeferred(self._handler.dynamicLoadProfile, args.profile)
    d.addCallback(self.write_results_success_dynamicLoadProfile, result, seqid, oprot)
    return d

  def write_results_success_dynamicLoadProfile(self, success, result, seqid, oprot):
    result.success = success
    oprot.writeMessageBegin("dynamicLoadProfile", TMessageType.REPLY, seqid)
    result.write(oprot)
    oprot.writeMessageEnd()
    oprot.trans.flush()

  def process_getTrackNames(self, seqid, iprot, oprot):
    args = getTrackNames_args()
    args.read(iprot)
    iprot.readMessageEnd()
    result = getTrackNames_result()
    d = defer.maybeDeferred(self._handler.getTrackNames, )
    d.addCallback(self.write_results_success_getTrackNames, result, seqid, oprot)
    return d

  def write_results_success_getTrackNames(self, success, result, seqid, oprot):
    result.success = success
    oprot.writeMessageBegin("getTrackNames", TMessageType.REPLY, seqid)
    result.write(oprot)
    oprot.writeMessageEnd()
    oprot.trans.flush()

  def process_getRampUpTime(self, seqid, iprot, oprot):
    args = getRampUpTime_args()
    args.read(iprot)
    iprot.readMessageEnd()
    result = getRampUpTime_result()
    d = defer.maybeDeferred(self._handler.getRampUpTime, )
    d.addCallback(self.write_results_success_getRampUpTime, result, seqid, oprot)
    return d

  def write_results_success_getRampUpTime(self, success, result, seqid, oprot):
    result.success = success
    oprot.writeMessageBegin("getRampUpTime", TMessageType.REPLY, seqid)
    result.write(oprot)
    oprot.writeMessageEnd()
    oprot.trans.flush()

  def process_getRampDownTime(self, seqid, iprot, oprot):
    args = getRampDownTime_args()
    args.read(iprot)
    iprot.readMessageEnd()
    result = getRampDownTime_result()
    d = defer.maybeDeferred(self._handler.getRampDownTime, )
    d.addCallback(self.write_results_success_getRampDownTime, result, seqid, oprot)
    return d

  def write_results_success_getRampDownTime(self, success, result, seqid, oprot):
    result.success = success
    oprot.writeMessageBegin("getRampDownTime", TMessageType.REPLY, seqid)
    result.write(oprot)
    oprot.writeMessageEnd()
    oprot.trans.flush()

  def process_getDurationTime(self, seqid, iprot, oprot):
    args = getDurationTime_args()
    args.read(iprot)
    iprot.readMessageEnd()
    result = getDurationTime_result()
    d = defer.maybeDeferred(self._handler.getDurationTime, )
    d.addCallback(self.write_results_success_getDurationTime, result, seqid, oprot)
    return d

  def write_results_success_getDurationTime(self, success, result, seqid, oprot):
    result.success = success
    oprot.writeMessageBegin("getDurationTime", TMessageType.REPLY, seqid)
    result.write(oprot)
    oprot.writeMessageEnd()
    oprot.trans.flush()


# HELPER FUNCTIONS AND STRUCTURES

class startBenchmark_args:
  """
  Attributes:
   - controllerTimestamp
  """

  thrift_spec = (
    None, # 0
    (1, TType.I64, 'controllerTimestamp', None, None, ), # 1
  )

  def __init__(self, controllerTimestamp=None,):
    self.controllerTimestamp = controllerTimestamp

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
          self.controllerTimestamp = iprot.readI64();
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
    oprot.writeStructBegin('startBenchmark_args')
    if self.controllerTimestamp is not None:
      oprot.writeFieldBegin('controllerTimestamp', TType.I64, 1)
      oprot.writeI64(self.controllerTimestamp)
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

class startBenchmark_result:
  """
  Attributes:
   - success
  """

  thrift_spec = (
    (0, TType.BOOL, 'success', None, None, ), # 0
  )

  def __init__(self, success=None,):
    self.success = success

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 0:
        if ftype == TType.BOOL:
          self.success = iprot.readBool();
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
    oprot.writeStructBegin('startBenchmark_result')
    if self.success is not None:
      oprot.writeFieldBegin('success', TType.BOOL, 0)
      oprot.writeBool(self.success)
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

class dynamicLoadProfile_args:
  """
  Attributes:
   - profile
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRUCT, 'profile', (Profile, Profile.thrift_spec), None, ), # 1
  )

  def __init__(self, profile=None,):
    self.profile = profile

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
          self.profile = Profile()
          self.profile.read(iprot)
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
    oprot.writeStructBegin('dynamicLoadProfile_args')
    if self.profile is not None:
      oprot.writeFieldBegin('profile', TType.STRUCT, 1)
      self.profile.write(oprot)
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

class dynamicLoadProfile_result:
  """
  Attributes:
   - success
  """

  thrift_spec = (
    (0, TType.BOOL, 'success', None, None, ), # 0
  )

  def __init__(self, success=None,):
    self.success = success

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 0:
        if ftype == TType.BOOL:
          self.success = iprot.readBool();
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
    oprot.writeStructBegin('dynamicLoadProfile_result')
    if self.success is not None:
      oprot.writeFieldBegin('success', TType.BOOL, 0)
      oprot.writeBool(self.success)
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

class getTrackNames_args:

  thrift_spec = (
  )

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('getTrackNames_args')
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

class getTrackNames_result:
  """
  Attributes:
   - success
  """

  thrift_spec = (
    (0, TType.LIST, 'success', (TType.STRING,None), None, ), # 0
  )

  def __init__(self, success=None,):
    self.success = success

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 0:
        if ftype == TType.LIST:
          self.success = []
          (_etype3, _size0) = iprot.readListBegin()
          for _i4 in xrange(_size0):
            _elem5 = iprot.readString();
            self.success.append(_elem5)
          iprot.readListEnd()
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
    oprot.writeStructBegin('getTrackNames_result')
    if self.success is not None:
      oprot.writeFieldBegin('success', TType.LIST, 0)
      oprot.writeListBegin(TType.STRING, len(self.success))
      for iter6 in self.success:
        oprot.writeString(iter6)
      oprot.writeListEnd()
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

class getRampUpTime_args:

  thrift_spec = (
  )

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('getRampUpTime_args')
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

class getRampUpTime_result:
  """
  Attributes:
   - success
  """

  thrift_spec = (
    (0, TType.I64, 'success', None, None, ), # 0
  )

  def __init__(self, success=None,):
    self.success = success

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 0:
        if ftype == TType.I64:
          self.success = iprot.readI64();
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
    oprot.writeStructBegin('getRampUpTime_result')
    if self.success is not None:
      oprot.writeFieldBegin('success', TType.I64, 0)
      oprot.writeI64(self.success)
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

class getRampDownTime_args:

  thrift_spec = (
  )

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('getRampDownTime_args')
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

class getRampDownTime_result:
  """
  Attributes:
   - success
  """

  thrift_spec = (
    (0, TType.I64, 'success', None, None, ), # 0
  )

  def __init__(self, success=None,):
    self.success = success

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 0:
        if ftype == TType.I64:
          self.success = iprot.readI64();
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
    oprot.writeStructBegin('getRampDownTime_result')
    if self.success is not None:
      oprot.writeFieldBegin('success', TType.I64, 0)
      oprot.writeI64(self.success)
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

class getDurationTime_args:

  thrift_spec = (
  )

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('getDurationTime_args')
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

class getDurationTime_result:
  """
  Attributes:
   - success
  """

  thrift_spec = (
    (0, TType.I64, 'success', None, None, ), # 0
  )

  def __init__(self, success=None,):
    self.success = success

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 0:
        if ftype == TType.I64:
          self.success = iprot.readI64();
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
    oprot.writeStructBegin('getDurationTime_result')
    if self.success is not None:
      oprot.writeFieldBegin('success', TType.I64, 0)
      oprot.writeI64(self.success)
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
