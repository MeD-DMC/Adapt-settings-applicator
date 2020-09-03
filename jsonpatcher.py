import filetype
import os
from zipfile import ZipFile, ZipInfo
from io import BytesIO
import codecs
import json
import xml.dom.minidom as md
import sys


dirName = os.getcwd()

print(dirName)
valuesToRemove = ['adapt-contrib-languagePicker', 'adapt-pagesInNavBar', 'adapt-close', 'adapt-devtools']
keysToRemove = ['_close', '_pagesInNavBar','_languagePicker']


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
def updateFRlabel(contentData,destJson):
    for (key, value) in contentData.items():
        try:
            if key == destJson[key]:
                destJson[key] = value
        except KeyError as e:
            # print('the missing keys exception, ignored')
            # print(e)
            pass
        if type(value) == type(dict()):
            updateFRlabel(value,destJson)
    #print(json.dumps(destJson,indent=2,ensure_ascii=False))

    return destJson
def updateFRCourseJson(course):
    with open('courseContent.json',encoding='utf8') as f:
        contentData = json.load(f)
    #print(json.dumps(json.loads(course),separators=(',', ': '),indent=2))
    data = updateFRlabel(contentData,json.loads(course))
    print('End of updateFRCourseJson Function, returning the json object...')
    return json.dumps(data,indent=2,separators=(',', ': '),ensure_ascii=False)
def updateCourseJson(course):

    ##################### Load the json files ############################

    data = json.loads(course)

    ################# Remove keys/values from the course.json file #####################
    for key in keysToRemove:
        while True:
            try:
                del data[key]
                del data['_globals']['_extensions'][key]
            except KeyError as e:
                print(e)
                break
    ###################### Patch the course.json file ##################################
    
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




    print('End of updateCourseJson Function, returning the json object...')
    ################# return it to a json data object #####################
    
    
    return json.dumps(data,indent=2,separators=(',', ': '),ensure_ascii=False)
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
    print('End of updateConfigJson Function, returning the json object...')
    return json.dumps(data,indent=2,separators=(',', ': '),ensure_ascii=False)
    #print(json.dumps(data['build']['includes'], indent=4, sort_keys=True))
    #################################################################################    
def updateimsXML(file):
    dom = md.parseString(file)
    dom.getElementsByTagName("resource")[0].setAttribute("href","launch.html")
    dom.getElementsByTagName("file")[0].setAttribute("href","launch.html")
    #print(dom.getElementsByTagName("resource")[0].getAttribute("href"))
    #print(dom.getElementsByTagName("file")[0].getAttribute("href"))
    #print(dom.toxml())
    return dom.toprettyxml()
def isdir(z, name):
    return any(x.startswith("%s/" % name.rstrip("/")) for x in z.namelist())
######################## Update the zip file ###################################
def update_or_insert(path):
    configJSON = None
    courseJSON = None
    imsXML = None
    courseLan = None
    new_zip = BytesIO()
    with ZipFile(path, 'r') as zip_archive:
        with ZipFile(new_zip, 'w') as new_archive:
            ### add HTMl file into the ZIP ###
            ### For Mac
            #new_archive.write('/Users/{your machine name}}/jsonPatcher/launch.html')
            #new_archive.write('/Users/allanyong/jsonPatcher/launch.html')

            ### For Windows
            new_archive.write('launch.html')
            ### determine the language of the course package ###
            if path[-6:] == 'fr.zip' or path[-6:] == 'FR.zip':
                courseLan = 'fr'
            else:
                courseLan = 'en'
            print(courseLan)   
            ### Patch the json and xml files ###
            for file in zip_archive.filelist:
                # If you spot an existing file, create a new object
                #print(file.filename + '====================================')
                if isdir(zip_archive, "course/"+courseLan):
                    if file.filename == 'course/'+courseLan+'/course.json':
                        print("I found a file: " + file.filename)
                        courseJSON = updateCourseJson(zip_archive.read(file))
                        if courseLan == 'fr' and len(sys.argv) == 2:
                            courseJSON = updateFRCourseJson(courseJSON)
                            print('came here======================================')
                        zip_inf = ZipInfo(file.filename)
                        new_archive.writestr(zip_inf, courseJSON)   
                    elif file.filename == 'course/config.json':
                        print("I found a file: " + file.filename)
                        configJSON = updateConfigJson(zip_archive.read(file),courseLan)
                        zip_inf = ZipInfo(file.filename)
                        new_archive.writestr(zip_inf, configJSON)
                    elif file.filename == 'imsmanifest.xml':
                        print("I found a file: " + file.filename)                    
                        imsXML = updateimsXML(zip_archive.read(file))
                        zip_inf = ZipInfo(file.filename)
                        new_archive.writestr(zip_inf, imsXML)
                    else:
                        # Copy other contents as it is
                        new_archive.writestr(file, zip_archive.read(file.filename))  

    return new_zip
def main():
    numOfZip = 0
    # Get the list of all files in directory tree at given path
    listOfFiles = getListOfFiles(dirName)
    for elem in listOfFiles:
        kind = filetype.guess(elem)
        if not (kind is None):
            if kind.mime == 'application/zip' and kind.extension == 'zip':
                numOfZip += 1
                print('Found %s Zip Files' % numOfZip)
                #print(elem)
                ############################################
                # Patching the zip files #
                new_zip = update_or_insert(elem)
                print(sys.argv)
                #Generate new Zips#
                try:
                #     #for mac 
                #    with open('patched/Patched - ' + elem.replace(dirName+'/',''), 'wb') as f:
                #     #for windows
                with open('patched'+'\\'+'Patched - ' + elem.replace(dirName+'\\',''), 'wb') as f:
                        f.write(new_zip.getbuffer())
                        new_zip.close()
                except OSError as e:
                    print(e)

if __name__ == '__main__':
    main()
