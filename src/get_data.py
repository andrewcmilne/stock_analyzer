from pandas_datareader.data import DataReader
from datetime import date
import pandas as pd
#import matplotlib.pyplot as plt
from tqdm import tqdm
from config import *
import datetime
import pickle

#here we show how to access the datareader object for any single ticker,
#in this case we are using the 5th item in the list, indexed from zero

class GetStocks():

    def __init__(self, run_id = 'last_run'):
        self.config = Config()
        new_data = input('would you like to pull new data? y/any other key:')
        self.ls_tickers = list(set(self.config.get_generic_config_property('stocks','tkr_ls') + self.config.get_generic_config_property('stocks', 'top_20')))
        self.run_id = run_id
        self.start = datetime.datetime.strptime(self.config.get_generic_config_property('stocks','start_date'), '%Y-%m-%d').date()
        self.end = datetime.datetime.strptime(self.config.get_generic_config_property('stocks','end_date'), '%Y-%m-%d').date()
        self.source = self.config.get_generic_config_property('stocks','data_source')

        if new_data.lower() == 'y':
            
            self._run_read_data(self.ls_tickers, self.source, self.start, self.end)
            path = self.config.get_generic_config_property('data','main_save_path') + self.config.get_generic_config_property('data', 'default_history')
            # with open(path, 'wb') as handle:
            #     pickle.dump(self.stock_data, handle)
            #     handle.close()
            
        else:
            path = self.config.get_generic_config_property('data','main_save_path') + self.config.get_generic_config_property('data', 'default_history')

            with open(path, 'rb') as handle:
                self.stock_data = pickle.load(handle)
                handle.close()

    def _run_read_data(self, ls_tickers: list(), source: str(), start: str(), end: str())->pd.DataFrame():
        self.stock_data = DataReader(self.ls_tickers, self.source, self.start, self.end)

    