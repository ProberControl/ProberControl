import os
import fnmatch


rootDir = "C:\\Users\\Graham\\Documents\\CodeRepository2\\AutoProber\\"
lineCollection = []

for dirName, subDirList, fileList in os.walk(rootDir):
    for file in fileList:
        if '.py' in file:
            path = os.path.join(dirName, file)
            with open(path, 'r') as f:
                for line in f:
                    if 'import' in line:
                        lineCollection.append(line)

with open('dependencies.txt', 'w') as f:
    for item in lineCollection:
        f.write(item+'\n')