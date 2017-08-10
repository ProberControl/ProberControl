import os
import shutil
import fnmatch

rootDir = "."
destination = rootDir+"/fileCollection"
os.mkdir(destination)

for dirName, subDirList, fileList in os.walk(rootDir):
    for fname in fnmatch.filter(fileList, '*.py'):
        filePath = os.path.join(dirName, fname)
        if (
            'est' not in filePath and
            '__init__' not in filePath):
            try:
                shutil.copy(filePath, destination)
            except Exception as e:
                print(e)

for file in os.listdir(destination):
    print("Moved: %s" % file)