import argparse
import csv
import os

class AggreationWriter(object):
    
    def __init__(self, outputFile):
        self.file = open(outputFile, 'wb')
        self.csvWriter = csv.writer(self.file)
    
    def write(self, start, end, value):
        list = (start, end, value)
        self.csvWriter.writerow(list)
        
    def close(self):
        self.file.close()
        

def processResource(writer, resourcePath, ignoreFirst=True):
    # Open CSV file for reading
    file = open(resourcePath, 'r')
    
    # Read all lines of the CSV file
    reader = csv.reader(file)
    rowCounter = 0
    
    for row in reader:
        # Ignore first line?
        if rowCounter == 0 and ignoreFirst: 
            rowCounter += 1
            continue
        
        # Write the current line to the output 
        writer.write(row[0], row[1], row[2]) 
    
    
def parseArguments():
    parser = argparse.ArgumentParser(description='Merge all CSV files form one week')
    parser.add_argument('--base', action='store', dest='base', help='base directory which contains all week directories')
    parser.add_argument('--output', action='store', dest='output', help='output filename to write the results to')
    parser.add_argument('--resource', action='store', dest='resource', help='name of the resource file inside the week directory')
    parser.add_argument('--ignoreFirst', action='store', dest='ignoreFirst', type=bool, help='ignore the first line of the source CSV files')
    
    results = parser.parse_args()
    return results


class Aggregation(object):
    
    def __init__(self, resourceName, outputFile, ignoreFirst, datasetPath):
        self.resourceName = resourceName
        self.outputFile = outputFile
        self.ignoreFirst = ignoreFirst
        self.datasetPath = datasetPath
        
    def process(self):
        # Create a new aggregation writer
        writer = AggreationWriter(self.outputFile)
        
        # List all week folders in the current data set
        weekFolders = os.listdir(self.datasetPath)
        
        # Iterate over each week folder
        for week in weekFolders:
            weekFolder = os.path.join(self.datasetPath, week)
            
            if os.path.isdir(weekFolder):
                resourcePath = os.path.join(weekFolder, self.resourceName)
                
                if os.path.exists(resourcePath):
                    print resourcePath
                    
                    processResource(writer, resourcePath, self.ignoreFirst)            
                else:
                    print "Week does not contain the specified resourceName %s" % (resourceName)
                    
        writer.close()


if __name__ == '__main__':
    
    # Parse parameters
    result = parseArguments()    
    
    resourceName = result.resource
    if resourceName == None:
        resourceName = '1-resource.csv'

    outputFile = result.output
    if outputFile == None:
        outputFile = 'aggregated.csv'
    
    ignoreFirst = result.ignoreFirst
    if ignoreFirst == None:
        ignoreFirst = False
    
    # Get working directory
    datasetPath = result.base
    if datasetPath is None:
        datasetPath = os.getcwd()
        
    # Process the data set
    aggregation = Aggregation(resourceName, outputFile, ignoreFirst, datasetPath)
    aggregation.process() 
    
    
    


