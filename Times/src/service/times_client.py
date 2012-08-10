from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from times import TimeService

transport = None

def connect():
    global transport
    transport = TSocket.TSocket('monitor0', 7855)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = TimeService.Client(protocol)
    transport.open()
    return client

def close():
    transport.close()
