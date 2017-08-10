import glob
import importlib as im
import inspect
import procedures as pr

### Make all Modules and Functions from Procedures-Folder Available in GUI.
### The Maitre will hold a list functions and has functions to access them
### and do inquiries, such as: module, name, arguments

# mod_name_list: holds names of all found modules

# func_list[][]: 2 dim array holds function handles. First Index defines array second defines function
 
class Maitre():
    
    def __init__(self, reloading = False):
        # GET ALL MODULES IN FOLDER
        if not reloading:
            self.mod_list = []
            self.mod_name_list = pr.__all__
            for mod_name in self.mod_name_list:
                try:
                    self.mod_list.append(__import__(mod_name))
                except:
                    pass
                    
        # GET ALL FUNCTIONS INSIDE EACH MODULE
        self.func_list=[]
        func_sub_i = 0
        for mod in self.mod_list:
            self.func_sub_list = []
            for func in inspect.getmembers(mod,inspect.isfunction):        
                if func[0][0] != '_':
                    self.func_sub_list.append(func[1])                
            self.func_list.append(self.func_sub_list)
        
    def get_all_modules(self):
        return self.mod_name_list
        
    def get_func_name(self, Mod_Index):
        func_names = []
        for func in self.func_list[Mod_Index]:
            func_names.append(func.__name__)
        return func_names
        
    def get_func_params(self, Mod_Index, Func_Index):
        return inspect.getargspec(self.func_list[Mod_Index][Func_Index])[0]

    def execute_func(self, Mod_Index, Func_Index, Func_Params ):
        return self.func_list[Mod_Index][Func_Index](*Func_Params)
        
    def execute_func_name(self, Mod_Name, Func_Name, Func_Params ):
        Mod_Index = self.get_all_modules().index(Mod_Name)
        Func_Index = self.get_func_name(Mod_Index).index(Func_Name)

        return self.func_list[Mod_Index][Func_Index](*Func_Params)

    def refresh(self):
        '''
         reloads old modules and loads any new ones
        '''
        # reload old modules
        for mod in self.mod_list:
            reload(mod)
        
        # check to see if there are any new modules to import
        reload(pr)
        for mod_name in pr.__all__:
            if mod_name not in self.mod_name_list:
                self.mod_list.append(im.import_module(__import__(mod_name)))
                self.mod_name_list.append(mod_name)
        
        self.__init__(reloading=True)
        

