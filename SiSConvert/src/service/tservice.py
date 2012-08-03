from thrift.transport import TSocket
from thrift.transport import TTransport

from thrift.protocol import TBinaryProtocol
from thrift.protocol import TCompactProtocol  
from thrift.server import TServer

from times import ttypes
from times import TimeService

class TimeSeries(object):
    
    def __write(self, ts, outfile):
        f = open(outfile, 'wb')
        t = TTransport.TFileObjectTransport(f)
        prot = TBinaryProtocol.TBinaryProtocol(t)
        ts.write(prot)
        f.close()
    
    def __read(self, infile):
        f = open(infile, 'rb')
        t = TTransport.TFileObjectTransport(f)
        prot = TBinaryProtocol.TBinaryProtocol(t)
        
        ts = ttypes.TimeSeries()
        ts.read(prot)
        f.close()
        
        return ts
    
    def __filename(self, name):
        return name + '.times'
    
    def _create(self, name, frequency):
        ts = ttypes.TimeSeries()
        ts.name = name
        ts.frequency = frequency
        ts.elements = []
        
        self.__write(ts, self.__filename(name))
    
    def _append(self, name, elements):
        ts = self.__read(self.__filename(name))
        if ts is None:
            print 'ERROR: TS not found %s' % (name)
            return 
        
        ts.elements.extend(elements)
        
        self.__write(ts, self.__filename(name))
    
    def _loadFile(self, name):
        ts = self.__read(self.__filename(name))
        return ts

class TimesHandler(TimeSeries):
    
    def load(self, name):
        ts = super(TimesHandler, self)._loadFile(name)
        return ts
        
    def create(self, name, frequency):
        super(TimesHandler, self)._create(name, frequency)
    
    def append(self, name, elements):
        super(TimesHandler, self)._append(name, elements)
    

handler = TimesHandler()
processor = TimeService.Processor(handler)
transport = TSocket.TServerSocket(port=7855)
tfactory = TTransport.TBufferedTransportFactory()
pfactory = TBinaryProtocol.TBinaryProtocolFactory()

server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)

#handler.create('hello', 5*60)
#
#elements = []
#for i in range(0,10):
#    e = ttypes.Element()
#    e.timestamp = 2
#    e.value = i
#    elements.append(e)
#
#handler.append('hello', elements)

print 'Times listening...'
server.serve()