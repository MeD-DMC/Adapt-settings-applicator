import filetype
import os
from zipfile import ZipFile, ZipInfo
from io import BytesIO
import codecs
import json
import xml.dom.minidom as md



valuesToRemove = ['adapt-contrib-languagePicker', 'adapt-pagesInNavBar', 'adapt-close', 'adapt-devtools']
keysToRemove = ['_close', '_pagesInNavBar','_languagePicker']
dirName = os.getcwd()

def getListOfFiles(dirName):
    # create a list of file and sub directories
    # names in the given directory
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If it is a path, ignore
        if os.path.isdir(fullPath) is not True:
            allFiles.append(fullPath)
    return allFiles        
def isdir(z, name):
    return any(x.startswith("%s/" % name.rstrip("/")) for x in z.namelist())
def updateConfigJson(config, language):
    data = json.loads(config)
    ####################################################################################
    ################# Remove keys/values from the config.json file #####################
    ####################################################################################
    for value in valuesToRemove:
        while True:
            try:
                data['build']['includes'].remove(value)
            except ValueError as e:
                print(e)
                break
    ####################################################################################
    ###################### Patch the config.json file ##################################
    ####################################################################################
    
    data['_defaultLanguage'] = language
    data['_accessibility']['_isEnabled'] = True
    data['_accessibility']['_isTextProcessorEnabled'] = True
    data['_accessibility']['_isSkipNavigationEnabled'] = True
    data['_scrollingContainer']['_isEnabled'] = True
    data['_spoor']['_reporting']['_onAssessmentFailure'] = 'completed'
    data['_homeButton']['_isEnabled'] = True
    data['_completionCriteria']['_requireContentCompleted'] = True
    data['_completionCriteria']['_requireAssessmentCompleted'] = False
    '''
    #debug information
    data['_accessibility']['_isEnabled'] = False
    data['_accessibility']['_isTextProcessorEnabled'] = False
    data['_accessibility']['_isSkipNavigationEnabled'] = False
    data['_scrollingContainer']['_isEnabled'] = False
    data['_spoor']['_reporting']['_onAssessmentFailure'] = 'completed'
    data['_homeButton']['_isEnabled'] = False
    data['_completionCriteria']['_requireContentCompleted'] = False
    data['_completionCriteria']['_requireAssessmentCompleted'] = False
    '''
    #print(json.dumps(data['_defaultLanguage'], indent=4, sort_keys=True))
    return json.dumps(data)
    #print(json.dumps(data['build']['includes'], indent=4, sort_keys=True))
    #################################################################################    
def updateCourseJson(course):

    data = json.loads(course)
    ####################################################################################
    ################# Remove keys/values from the course.json file #####################
    ####################################################################################
    for key in keysToRemove:
        while True:
            try:
                del data[key]
                del data['_globals']['_extensions'][key]
                #data.remove(key)
            except KeyError as e:
                print(e)
                break

    ####################################################################################
    ###################### Patch the course.json file ##################################
    ####################################################################################
    
    data['_pageLevelProgress']['_isEnabled'] = True
    data['_pageLevelProgress']['_showPageCompletion'] = True
    data['_pageLevelProgress']['_isCompletionIndicatorEnabled'] = False
    data['_pageLevelProgress']['_isShownInNavigationBar'] = False
    data['_resources']['_isEnabled'] = True
    data['_glossary']['_isEnabled'] = True
    data['_bookmarking']['_isEnabled'] = True
    data['_bookmarking']['_showPrompt'] = True
    data['_pageIncompletePrompt']['_isEnabled'] = True
    data['_homeButton']['_isEnabled'] = True
    
    '''
    #debug information
    data['_pageLevelProgress']['_isEnabled'] = False
    data['_pageLevelProgress']['_showPageCompletion'] = False
    data['_pageLevelProgress']['_isCompletionIndicatorEnabled'] = False
    data['_pageLevelProgress']['_isShownInNavigationBar'] = False
    data['_resources']['_isEnabled'] = False
    data['_glossary']['_isEnabled'] = False
    data['_bookmarking']['_isEnabled'] = False
    data['_bookmarking']['_showPrompt'] = False
    data['_pageIncompletePrompt']['_isEnabled'] = False
    data['_homeButton']['_isEnabled'] = False
    '''
    print('*******************************************')
    #print(json.dumps(data['title'], indent=2, sort_keys=True))

    return json.dumps(data)
def updateimsXML(file):
    dom = md.parseString(file)

    dom.getElementsByTagName("resource")[0].setAttribute("href","launch.html")
    dom.getElementsByTagName("file")[0].setAttribute("href","launch.html")
    #print(dom.getElementsByTagName("resource")[0].getAttribute("href"))
    #print(dom.getElementsByTagName("file")[0].getAttribute("href"))
    #print(dom.toxml())
    return dom.toprettyxml()
    
######################## Update the zip file ###################################
def update_or_insert(path):
    configJSON = None
    courseJSON = None
    imsXML = None
    courseLan = None
    launchFile = None

    
    """
    Param: path -> file in archive
    Param: data -> data to be updated

    Returns a new zip file with the updated content
    for the given path
    """
    new_zip = BytesIO()

    with ZipFile(path, 'r') as zip_archive:
        with ZipFile(new_zip, 'w') as new_archive:
            ### add HTMl file into the ZIP ###
            new_archive.write('launch.html')
            ### determine the language of the course package ###
            if path[-6:] == 'fr.zip' or path[-6:] == 'FR.zip':
                courseLan = 'fr'
            else:
                courseLan = 'en'
            ### Patch the json and xml files ###
            for file in zip_archive.filelist:
                # If you spot an existing file, create a new object
                if isdir(zip_archive, "course/"+courseLan):
                    if file.filename == 'course/'+courseLan+'/course.json':
                        courseJSON = updateCourseJson(zip_archive.read(file))
                        zip_inf = ZipInfo(file.filename)
                        new_archive.writestr(zip_inf, courseJSON)   
                    elif file.filename == 'course/config.json':
                        configJSON = updateConfigJson(zip_archive.read(file),courseLan)
                        zip_inf = ZipInfo(file.filename)
                        new_archive.writestr(zip_inf, configJSON)
                    elif file.filename == 'imsmanifest.xml':
                        imsXML = updateimsXML(zip_archive.read(file))
                        zip_inf = ZipInfo(file.filename)
                        new_archive.writestr(zip_inf, imsXML)
                    else:
                        # Copy other contents as it is
                        new_archive.writestr(file, zip_archive.read(file.filename))  

    return new_zip
######################## Main Logic (please switch to the correct OS in this block) ###################################
def main():
    numOfZip = 0
    # Get the list of all files in directory tree at given path
    listOfFiles = getListOfFiles(dirName)

    for elem in listOfFiles:
        kind = filetype.guess(elem)
        if not (kind is None):
            if kind.mime == 'application/zip' and kind.extension == 'zip':
                '''
                # DEBUG: check to see what ZIP files are found
                # print(elem)
                # print(kind.extension)
                # print(kind.mime)
                # Debug: Number of Zip Files found
                '''
                numOfZip += 1
                print('Found %s Zip Files' % numOfZip)
                ############################################
                # Patching the zip files #
                new_zip = update_or_insert(elem)
                print(elem)
                #Generate new Zips#
                
                try:
                    #for mac 
                    with open('patched/Patched - ' + elem.replace(dirName+'/',''), 'wb') as f:
                    #for windows
                    #with open('patched'+'\\'+'Patched - ' + elem.replace(dirName+'\\',''), 'wb') as f:
                        f.write(new_zip.getbuffer())
                        new_zip.close()
                except OSError as e:
                    print(e)
                
                
if __name__ == '__main__':
    main()
