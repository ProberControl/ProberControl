'''
[FileWriter]
This module handles output of test results to files in local storage.
Implements the ProberControl's OutputStream implicit interface.
'''

from . import DataIO

class FileWriter(object):

    def __init__(self,group_designators,resultsPath='', name_convention='.csv', outputMode=None):
        self.group_designators = group_designators
        self.FileMap = {}
        self.outputMode = outputMode
        self.name_convention = name_convention
        self.resultsPath = resultsPath

    def _generateFileName(self, entry):
        '''
        helper function to generate the names of the output files from
        information
        '''
        dot = self.name_convention.rfind('.')
        default_outputMode = self.outputMode is None or self.outputMode == ''
        identifier = '' if default_outputMode else entry[self.outputMode]
        return self.name_convention[0:dot] + '-' + identifier + self.name_convention[dot:]

    def getOutTargets(self, entry):
        '''get an open file handle from measurement entry struct'''
        filename = self._generateFileName(entry)
        if filename in self.FileMap:
            return self.FileMap[filename]
        else:
            path = os.path.join(self.resultsPath, filename)
            file = open(path, 'w')
            self.FileMap[filename] = file
            return file

    def getRelatedFiles(self,script,key,entry): # TODO Should we leave this here ??
        # if binning key equals outputmode or in a lower hierarchy level than the outputMode (bin chips but output wafers) return current file path in a list
        if self.group_designators.index(key) >= self.group_designators.index(self.outputMode):
            return [os.path.join(self.resultsPath, self._generateFileName(entry))]
        else:
            # generate list of entries in which the current binning entity exists
            sub_entries = []
            for elem in script:
                if elem[key] == entry[key]:
                    sub_entries.append(elem)
            # generate list with all related file names
            paths = []
            for elem in sub_entries:
                paths.append(os.path.join(self.resultsPath, self._generateFileName(elem)))
            # clean paths of dubble sub_entries and return
            return list(set(paths))


    def __exit__(self, type, value, traceback):
        '''implementing "with" semantics'''
        for file in list(self.FileMap.values()):
            file.close()

    def write(openFile, data, Data_Name=''):
        '''Takes data in form of nested lists or singular value and a experiment
        name, and writes it to a results file. The parmater is tested to be
        either a file handler (in which case its considered open) or a str in
        which case its considered to be a path to a file to which the data will
        be appended.
        '''

        # check whether call was local or generated from ethernet_interface
        # Traverse Stack and search for the ethernet_interface
        for entry in inspect.stack(context=0):
            if "EthernetInterface" in entry[1]:
                return

        # TODO check data type
        # Test openFile parameter
        if type(openFile) is file:
            # It is already a file handler - everything is good
            pass
        elif type(openFile) is str:
            try:
                # Try to open file
                openFile = open(openFile,'a')
            except:
                print("Cannot open file for writing")
                return
        else:
            print("Wrong argument type for openFile")
            return


        #Check Dimension of data
        if DataIO._test_dim(data) > 2:
            # If Dimension bigger 2 than recursively dive into file
            for substruct in data:
                DataIO.writeData(openFile, substruct, Data_Name+'_'+str(data.index(substruct)))
        elif DataIO._test_dim(data) <= 2 and DataIO._test_dim(data) >= -1:
            # If a 2 dim data block or less write csv block
            DataIO._write_csv(openFile, data ,Data_Name,DataIO._test_dim(data))
        elif type(data) == str :
            # if the data is a str just write it into file
            openFile.write(data)
            openFile.flush()
        else:
            print("Could not write data to file: Error in Data Format")


        # Seperate the experiments by one extra new lines
        openFile.write('\n')
        openFile.flush()
