import aggregate
import os
import shutil

class Processor(object):
    def __init__(self):
        pass
    
    def process(self, dataset, datasetPath):
        print "Process not implemented"
        
    def cleanup(self, dataset, datasetPath):
        print "Cleanup not implemented"


class AggregationProcessor(Processor):
    
    def __init__(self):
        pass
    
    def __buildWritePath(self, dataset, datasetPath):
        return os.path.join(datasetPath, 'agg' + dataset + '.csv')        
    
    def process(self, dataset, datasetPath):
        print "processing: %s in %s" % (dataset, datasetPath)
        
        outputFile = self.__buildWritePath(dataset, datasetPath) 
        resourceName = '1-resource.csv'
        ignoreFirst = True
        
        aggregation = aggregate.Aggregation(resourceName, outputFile, ignoreFirst, datasetPath)
        aggregation.process() 
        pass
    
    def cleanup(self, dataset, datasetPath):
        outputFile = self.__buildWritePath(dataset, datasetPath)
        
        if os.path.exists(outputFile):
            if os.path.isfile(outputFile):
                print "removing %s..." % (outputFile)
                os.remove(outputFile)

class ConsolidationProcessor(Processor):
    
    def __init__(self, targetDir=os.getcwd()):
        self.targetDir = targetDir

    def __buildSourcePath(self, dataset, datasetPath):
        return os.path.join(datasetPath, 'agg' + dataset + '.csv')    

    def __buildWritePath(self, dataset, datasetPath):
        return os.path.join(os.getcwd(), 'agg' + dataset + '.csv')

    def process(self, dataset, datasetPath):
        inFile = self.__buildSourcePath(dataset, datasetPath)
        outFile = self.__buildWritePath(dataset, datasetPath)
        
        shutil.move(inFile, outFile); 
        
    def cleanup(self, dataset, datasetPath):
        outFile = self.__buildWritePath(dataset, datasetPath)
        
        if os.path.exists(outFile):
            print "removing %s" % (outFile) 
            os.remove(outFile)
        

if __name__ == '__main__':
    base = 'D:/work/data/SIS time series/csv'
    
    # Create instance of the processor
    processors = []
    processors.append(AggregationProcessor())
    processors.append(ConsolidationProcessor())
    
    dataset = os.listdir(base)
    for set in dataset:
        datasetPath = os.path.join(base, set)
        
        # Do not process files
        if not os.path.isdir(datasetPath):
            continue

        (path, file) = os.path.split(datasetPath)

        for processor in processors:
            processor.process(file, datasetPath)
            # processor.cleanup(file, datasetPath)   
        
