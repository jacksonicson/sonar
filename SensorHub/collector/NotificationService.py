#
# Autogenerated by Thrift Compiler (0.8.0)
#
# DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
#
#  options string: py
#

from thrift.Thrift import TType, TMessageType, TException
from ttypes import *
from thrift.Thrift import TProcessor
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol, TProtocol
try:
  from thrift.protocol import fastbinary
except:
  fastbinary = None


class Iface:
  def subscribe(self, ip, port, watchlist):
    """
    Parameters:
     - ip
     - port
     - watchlist
    """
    pass

  def unsubscribe(self, ip):
    """
    Parameters:
     - ip
    """
    pass


class Client(Iface):
  def __init__(self, iprot, oprot=None):
    self._iprot = self._oprot = iprot
    if oprot is not None:
      self._oprot = oprot
    self._seqid = 0

  def subscribe(self, ip, port, watchlist):
    """
    Parameters:
     - ip
     - port
     - watchlist
    """
    self.send_subscribe(ip, port, watchlist)
    self.recv_subscribe()

  def send_subscribe(self, ip, port, watchlist):
    self._oprot.writeMessageBegin('subscribe', TMessageType.CALL, self._seqid)
    args = subscribe_args()
    args.ip = ip
    args.port = port
    args.watchlist = watchlist
    args.write(self._oprot)
    self._oprot.writeMessageEnd()
    self._oprot.trans.flush()

  def recv_subscribe(self, ):
    (fname, mtype, rseqid) = self._iprot.readMessageBegin()
    if mtype == TMessageType.EXCEPTION:
      x = TApplicationException()
      x.read(self._iprot)
      self._iprot.readMessageEnd()
      raise x
    result = subscribe_result()
    result.read(self._iprot)
    self._iprot.readMessageEnd()
    return

  def unsubscribe(self, ip):
    """
    Parameters:
     - ip
    """
    self.send_unsubscribe(ip)
    self.recv_unsubscribe()

  def send_unsubscribe(self, ip):
    self._oprot.writeMessageBegin('unsubscribe', TMessageType.CALL, self._seqid)
    args = unsubscribe_args()
    args.ip = ip
    args.write(self._oprot)
    self._oprot.writeMessageEnd()
    self._oprot.trans.flush()

  def recv_unsubscribe(self, ):
    (fname, mtype, rseqid) = self._iprot.readMessageBegin()
    if mtype == TMessageType.EXCEPTION:
      x = TApplicationException()
      x.read(self._iprot)
      self._iprot.readMessageEnd()
      raise x
    result = unsubscribe_result()
    result.read(self._iprot)
    self._iprot.readMessageEnd()
    return


class Processor(Iface, TProcessor):
  def __init__(self, handler):
    self._handler = handler
    self._processMap = {}
    self._processMap["subscribe"] = Processor.process_subscribe
    self._processMap["unsubscribe"] = Processor.process_unsubscribe

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
      return
    else:
      self._processMap[name](self, seqid, iprot, oprot)
    return True

  def process_subscribe(self, seqid, iprot, oprot):
    args = subscribe_args()
    args.read(iprot)
    iprot.readMessageEnd()
    result = subscribe_result()
    self._handler.subscribe(args.ip, args.port, args.watchlist)
    oprot.writeMessageBegin("subscribe", TMessageType.REPLY, seqid)
    result.write(oprot)
    oprot.writeMessageEnd()
    oprot.trans.flush()

  def process_unsubscribe(self, seqid, iprot, oprot):
    args = unsubscribe_args()
    args.read(iprot)
    iprot.readMessageEnd()
    result = unsubscribe_result()
    self._handler.unsubscribe(args.ip)
    oprot.writeMessageBegin("unsubscribe", TMessageType.REPLY, seqid)
    result.write(oprot)
    oprot.writeMessageEnd()
    oprot.trans.flush()


# HELPER FUNCTIONS AND STRUCTURES

class subscribe_args:
  """
  Attributes:
   - ip
   - port
   - watchlist
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRING, 'ip', None, None, ), # 1
    (2, TType.I32, 'port', None, None, ), # 2
    (3, TType.SET, 'watchlist', (TType.STRUCT,(SensorToWatch, SensorToWatch.thrift_spec)), None, ), # 3
  )

  def __init__(self, ip=None, port=None, watchlist=None,):
    self.ip = ip
    self.port = port
    self.watchlist = watchlist

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
          self.ip = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.I32:
          self.port = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.SET:
          self.watchlist = set()
          (_etype45, _size42) = iprot.readSetBegin()
          for _i46 in xrange(_size42):
            _elem47 = SensorToWatch()
            _elem47.read(iprot)
            self.watchlist.add(_elem47)
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
    oprot.writeStructBegin('subscribe_args')
    if self.ip is not None:
      oprot.writeFieldBegin('ip', TType.STRING, 1)
      oprot.writeString(self.ip)
      oprot.writeFieldEnd()
    if self.port is not None:
      oprot.writeFieldBegin('port', TType.I32, 2)
      oprot.writeI32(self.port)
      oprot.writeFieldEnd()
    if self.watchlist is not None:
      oprot.writeFieldBegin('watchlist', TType.SET, 3)
      oprot.writeSetBegin(TType.STRUCT, len(self.watchlist))
      for iter48 in self.watchlist:
        iter48.write(oprot)
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

class subscribe_result:

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
    oprot.writeStructBegin('subscribe_result')
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

class unsubscribe_args:
  """
  Attributes:
   - ip
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRING, 'ip', None, None, ), # 1
  )

  def __init__(self, ip=None,):
    self.ip = ip

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
          self.ip = iprot.readString();
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
    oprot.writeStructBegin('unsubscribe_args')
    if self.ip is not None:
      oprot.writeFieldBegin('ip', TType.STRING, 1)
      oprot.writeString(self.ip)
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

class unsubscribe_result:

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
    oprot.writeStructBegin('unsubscribe_result')
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
