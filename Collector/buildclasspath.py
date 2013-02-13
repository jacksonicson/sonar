"""
/*******************************************************************************
 * Copyright (c) 2010 Andreas Wolke.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Andreas Wolke - initial API and implementation and initial documentation
 *******************************************************************************/
"""
import sys

def createClasspathList(eclipseProject, killPath=True):
    fProject = open(eclipseProject, "r")
    project = fProject.read()
    
    pattern = "path=\""
    mustContain = [".jar", ".so", ".dll", ".lib"]
    
    li = []
    pointer = 0
    while pointer >= 0:
        nextFind = project.find(pattern, pointer)
        endFind = project.find("\"", nextFind + len(pattern) + 1)
        
        if(endFind < pointer):
            break
        pointer = endFind + 1
                
        extract = project[nextFind + len(pattern) : endFind]
        
        if killPath:
            last = extract.rfind("/");
            if last != -1:
                extract = extract[last + 1 : len(extract)]
        
        # Check if extract is a valid lib file
        isLib = False
        for test in mustContain:
            if(extract.find(test) != -1):
                isLib = True
                break
        
        if isLib is False:
            print "Invalid lib %s" % extract
            continue
                
        li.append(extract)
        
    return li

def createAntClasspath(eclipseProject, killPath):
    output = ""
    for extract in createClasspathList(eclipseProject, killPath):
        print extract
        output += '<pathelement location="./%s" />\n' % extract
        
    return output


def createStartClasspath(eclipseProject, killPath):
    output = ""
    for extract in createClasspathList(eclipseProject, killPath):
        print extract
        output += './%s\n' % extract
        
    return output

def createFileSet(eclipseProject, killPath):
    output = ""
    for extract in createClasspathList(eclipseProject, killPath):
        if len(extract) > 1:
            if extract[0] == '/':
                extract = extract[1:]
                
        output += '<include name="%s" />\n' % extract
    
    return output


def main(args):
    # Remove the first argument (its the name of the script)
    del args[0]
    
    # Check if there is there is an argument
    namePrefix = ""
    if len(args) > 0:
        namePrefix = args[0]
    
    # Create the ANT-File classpath
    output = "<project>"
    cp = createAntClasspath(".classpath", False)
    output += ("<path id='%sclasspath'>" % namePrefix) + cp + "</path>"
    
    fileset = createFileSet(".classpath", False)
    output += ("<fileset dir='../' id='%slibfiles'>" % namePrefix) + fileset + "</fileset>"
    output += "</project>"
    javaFile = open("classpath.xml", "w")
    javaFile.write(output);
    javaFile.close()
    
    # Warite the classpath to a txt file
    output = createStartClasspath(".classpath", False)
    javaFile = open("classpath.txt", "w")
    javaFile.write(output)
    javaFile.close()


if __name__ == "__main__":
    main(sys.argv)
