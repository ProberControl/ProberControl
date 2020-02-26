import numbers
import numpy
import operator
import inspect



class DataIO():
    '''
    This class provides standarized Data IO that should be used in the procedures, scriptcontroller  and DataViewer
    '''
    @staticmethod
    def writeData(openFile, data, Data_Name=''):
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

    @staticmethod
    def _write_csv(openFile, data ,name,dim):
        ''' Writes Single dimensional lists to file'''

        openFile.write("##{}:\n".format(name))
        openFile.flush()

        if dim == 2:
            for sublist in data:
                for elem in sublist:
                    openFile.write("{}\t".format(elem))
                openFile.write("\n")

        elif dim == 1:
            for elem in data:
                openFile.write("{}\n".format(elem))

        elif dim == 0:
            openFile.write("\n")

        elif dim == -1:
            openFile.write(str(data))
            openFile.write("\n")

        openFile.flush()
        return

    @staticmethod
    def _test_dim(testlist, dim=0):
        """tests if testlist is a list and how many dimensions it has.
        Returns -1 if testlist is a number
        returns -2 if it is no list or number, 0 if list is empty
        and otherwise the dimensions of it"""
        if isinstance(testlist, list):
            if testlist == []:
                return dim
            dim = dim + 1
            dim = DataIO._test_dim(testlist[0], dim)
            return dim
        elif isinstance(testlist, numbers.Number) and dim == 0:
            return -1
        else:
            if dim == 0:
                return -2
            else:
                return dim

    @staticmethod
    def get_test_names(path):

        NameList=[]

        try:
            with open(path,'r') as MeasFile:
                if MeasFile is None:
                    print('Problem reading Measurement file.')
                    exit()

                for num, line in enumerate(MeasFile, 1):
                    if line[:2] == '##' :
                        NameList.append(str(num)+'@'+line[2:-2])
        except IOError:
            pass # No file was selected, no reason to report an error
        except Exception as e:
            print(("Error: {}".format(e)))

        if NameList==[]:
            return ['NoName']

        return NameList

    @staticmethod
    def get_test_data(path, test_name):

        Data=[]

        with open(path, 'r') as MeasFile:
            if MeasFile is None:
                print('Problem reading Measurement file.')
                exit()

            in_block = False

            for num, line in enumerate(MeasFile, 1):

                if (in_block and line[0:-1] != ''):
                    SubList = line[0:-1].split('\t')
                    CleanSubList = []
                    for elem in SubList:
                        if elem != '':
                            CleanSubList.append(float(elem))

                    Data.append(CleanSubList)

                if in_block and line[0:-1] == '':
                    return Data

                if test_name in str(num)+'@'+line[2:] or (test_name == 'NoName' and in_block == False):
                    in_block = True

        if in_block == True:
            return Data

        print('Reading Data from File failed')
        return False

    @staticmethod
    def usage_prep(usage_list):
        usage_text = 'USAGE:\n'
        for tool_info in usage_list:
            usage_text += tool_info + '\n'
        return usage_text

    @staticmethod
    def parameter_prep(Stages, Maitre, arg_string,func_parameter_list):
        '''
            The function interpretes Input strings and prepares input paramters for functions.
            It also swaps MAitre/Stages keywords for the objects that are then passed to the functions.

            func_parameter_list are the expected paramters of the function for which the parameters are prepared.
            This allows to swap in Maitre and Stages where needed.
        '''

        PreArgList=arg_string.split(' ')
        ArgList=[]
        # String Interpretation
        for elem in PreArgList:
            if '[' in elem:
                SubList=elem.replace('[','').replace(']','').split(',')
                elem=list(map(float,SubList))
            if 'Stages' in elem:
                elem = Stages
            if 'Maitre' in elem:
                elem = Maitre
            if str(elem).isdigit():
                elem=float(elem)
            if elem == '':
                continue

            ArgList.append(elem)

        direct_list = func_parameter_list

        insert_list = []

        if "Stages" in direct_list:
            insert_list.append([direct_list.index("Stages"),Stages])

        if "stages" in direct_list:
            insert_list.append([direct_list.index("stages"),Stages])

        if "Maitre" in direct_list:
            insert_list.append([direct_list.index("Maitre"),Maitre])

        if "maitre" in direct_list:
            insert_list.append([direct_list.index("maitre"),Maitre])

        insert_list.sort(key=operator.itemgetter(0))

        if insert_list != []:
            for x in insert_list:
                ArgList.insert(x[0],x[1])

        return ArgList




if __name__ == "__main__" :
    openFile = 'HelloWorld.txt'
    openFile = open(openFile,'a')
    data = [[1,2,3],[2,3,4],[3,4,5]]
    Data_Name = 'Exp1'
    print((type(data)))
    print((DataIO._test_dim(data)))
    DataIO.writeData(openFile, data, Data_Name)


'''
Copyright (C) 2017  Robert Polster
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
