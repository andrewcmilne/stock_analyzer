import pandas as pd
import numpy as np
import yaml


class Config():

    def __init__(self):

        file_name = 'stock.yaml'
        with open(file_name, 'r') as f:
            self.data = yaml.load(f)
        

    def get_generic_config_property(self, branch: str(), leaf: str())->str():
        return self.data[branch][leaf]
