import filetype
import os
import zipfile


def getListOfFiles(dirName):
    # create a list of file and sub directories
    # names in the given directory
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)

    return allFiles


def main():
    numOfZip = 0
    configJSON = None
    courseJSON = None
    dirName = '/Users/allanyong/applicator/'
    # Get the list of all files in directory tree at given path
    listOfFiles = getListOfFiles(dirName)
    # Print the files
    for elem in listOfFiles:
        kind = filetype.guess(elem)
       # print(elem)
        if not (kind is None):
            if kind.mime == 'application/zip':
                numOfZip += 1
                print('Found %s Zip Files' % numOfZip)
                with zipfile.ZipFile(elem) as zip_archive:
                    for file in zip_archive.filelist:
                        if file.filename == 'course/en/course.json':
                            courseJSON = zip_archive.read(file)
                           # configJSON = zip_archive.read('course/config.json')
                            print('*****')
                # with zipfile.ZipFile(elem) as zip_archive:
                #     for item in zip_archive.filelist:
                #         print(item)

    print("****************")
    ########################extract the json files###################################

    #################################################################################


if __name__ == '__main__':
    main()
