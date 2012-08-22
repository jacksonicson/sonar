from thrift.protocol import TBinaryProtocol, TCompactProtocol
from thrift.server import TServer
from thrift.transport import TSocket, TTransport
from times import TimeService, ttypes
import os
import re
import StringIO

################################
## Configuration              ##
# DATA_DIR = 'C:/temp/times'
DATA_DIR = '/mnt/arr0/times'
PORT = 7855
################################

class Wrapper(ttypes.TimeSeries):
    def __init__(self, data):
        self.data = data
    
    def read(self, iprot):
        print 'WARN: Not implemented'
    
    def write(self, oprot):
        oprot.trans.write(self.data)

class TimeSeries(object):
    
    def __write(self, ts, outfile):
        outfile = os.path.join(DATA_DIR, outfile)
        
        f = open(outfile, 'wb')
        t = TTransport.TFileObjectTransport(f)
        prot = TBinaryProtocol.TBinaryProtocolAccelerated(t)
        ts.write(prot)
        f.close()
    
    def __read(self, infile):
        infile = os.path.join(DATA_DIR, infile)
        if not os.path.exists(infile):
            return None

        f = open(infile, 'rb')
        io = StringIO.StringIO()
        while True:
            chunk = f.read(32)
            if chunk: 
                io.write(chunk)
            else:
                break
        f.close()
        value = io.getvalue()
        io.close()
        
        return Wrapper(value)
    
    def _read_decode(self, infile):
        infile = os.path.join(DATA_DIR, infile)
        
        if not os.path.exists(infile):
            return None
        
        f = open(infile, 'rb')
        t = TTransport.TFileObjectTransport(f)
        prot = TBinaryProtocol.TBinaryProtocolAccelerated(t)
        
        ts = ttypes.TimeSeries()
        ts.read(prot)
        f.close()
        
        return ts
    
    def __filename(self, name):
        return name + '.times'
    
    def __delete(self, name):
        del_file = os.path.join(DATA_DIR, self.__filename(name))
        if os.path.exists(del_file) and os.path.isfile(del_file):
            os.remove(del_file)
    
    def _find(self, pattern):
        result = []
        pattern = re.compile(pattern)
        for element in os.listdir(DATA_DIR):
            element = element.replace('.times', '')
            if pattern.match(element):
                result.append(element)
                
        return result
    
    def _create(self, name, frequency):
        ts = ttypes.TimeSeries()
        ts.name = name
        ts.frequency = frequency
        ts.elements = []
        
        self.__write(ts, self.__filename(name))
    
    def _append(self, name, elements):
        ts = self._read_decode(self.__filename(name))
        if ts is None:
            print 'ERROR: TS not found %s' % (name)
            return 
        
        if ts.elements is None:
            ts.elements = []
            
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
        
    def find(self, pattern):
        return super(TimesHandler, self)._find(pattern)
    
    def remove(self, name):
        return super(TimesHandler, self)._delete(name)
    

def main():
    handler = TimesHandler()
    processor = TimeService.Processor(handler)
    transport = TSocket.TServerSocket(port=PORT)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    
    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
    
    print 'Times listening...'
    server.serve()
