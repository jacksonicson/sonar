from collector import CollectService, ManagementService, ttypes
from thrift import Thrift
from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket, TTransport

def openClient():
    transport = TSocket.TSocket('131.159.41.171', 7931)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = ManagementService.Client(protocol);
    transport.open();
    return transport, client


def closeClient(transport):
    transport.close()