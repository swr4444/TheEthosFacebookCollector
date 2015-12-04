import pickle

class InteractivePlot:
        
    def __init__(self,scatter):
    
        self.af_list = []
        self.fig = ""
        self.entities = ""
        self.measure = ""
    
    def get_af(self):
        return self.af_list
            
    def get_fig(self):
        return self.fig