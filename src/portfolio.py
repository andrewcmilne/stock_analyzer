import pandas as pd
import numpy as np
from config import *
import random
from utils import *
import math


class Portfolio ():
    def __init__(self, run_id = 'last_run', initial_cash = 100000):
        self.config = Config()
        self.run_id = run_id
        self.empty_portfolio = self.get_empty_portfolio()
        self.empty_portfolio['cash'] = initial_cash
        self.possible_securities = list(set(self.config.get_generic_config_property('stocks','tkr_ls') + self.config.get_generic_config_property('stocks', 'top_20')))
        #self.new_portfolio = self.get_new_portfolio()
        #self.historical_data = pd.read_csv(self.config.get_generic_config_property('data','main_save_path') + self.config.get_generic_config_property('data', 'default_history'))
        self.start_date = self.config.get_generic_config_property('stocks','start_date')
        self.end_date = self.config.get_generic_config_property('stocks','end_date')
        self.threshold = self.config.get_generic_config_property('portfolio','threshold')
        self.transaction_fee = self.config.get_generic_config_property('portfolio','transaction_fee')
        self.return_required = self.config.get_generic_config_property('portfolio','return_required')
        self.method = self.config.get_generic_config_property('portfolio','method')
        self.transaction_tracker = 0
    
    def get_empty_portfolio(self):
        return self.config.get_generic_config_property('portfolio','default_portfolio')

    def make_an_empty_holding(self):
        '''select a security from available list and add it to the portfolio object dictionary'''
        #initialize an empty holding dict
        empty_holding = self.config.get_generic_config_property('portfolio','empty_holding_dict')
        #return the empty holding dict
        return empty_holding
    
    def get_new_portfolio(self, market_data: pd.DataFrame(), specific_ls= ['ENB', 'BNS', 'TD', 'RY']):
        self.empty_portfolio = self.get_empty_portfolio()
        if len(specific_ls)>=4:
            self.empty_portfolio.update(dict((i,0) for i in specific_ls))
            cash = self.empty_portfolio['cash']
            for k, v in self.empty_portfolio.items():
                if k == 'cash':
                    pass
                else:
                    self.empty_portfolio[k] = self.make_an_empty_holding()
                    #cash = self.empty_portfolio['cash'] / len(specific_ls)
                    self.empty_portfolio[k] = self.purchase_shares(k, 'buy', 25000, market_data, self.empty_portfolio[k])
                    #print(self.empty_portfolio.values())
                    self.empty_portfolio['cash'] -=  cash / len(specific_ls) 
        else:
            #select random entry from list
            random_4 = random.sample(self.possible_securities, 4)
            print(random_4)
            self.empty_portfolio.update(dict((i,0) for i in random_4))
            cash = self.empty_portfolio['cash']

            for k, v in self.empty_portfolio.items():
                if k == 'cash':
                    pass
                else:
                    self.empty_portfolio[k] = self.make_an_empty_holding()
                    self.empty_portfolio[k] = self.purchase_shares(k, 'buy', 25000, market_data, self.empty_portfolio[k])
                    #print(self.empty_portfolio.values())
                    self.empty_portfolio['cash'] -=  cash / len(random_4) 

        return self.empty_portfolio
    
    # def populate_new_portfolio (self, portfolio: dict()):
    #     '''takes new portfolio object and purchases shares to populate the holdings in the portfolio'''
    #     #get a purchase date
    #     #get candidates for purchase
    #     #while cash > 0
    #     #calculate first purchase amount, <=25$K
    #     #make a purchase of equal value
    #     #add the attributes to the portfolio dictionary
    #     #updates remaining cash

    #     purchase_date = get_initial_purchase_date()
    #     ls_to_buy = self.candidates_for_purchase(self.historical_data.stock_data[:purchase_date], self.threshold)
    #     self.new_portfolio = self.run_buy_side(self.new_portfolio, purchase_date, self.historical_data.stock_data, ls_to_buy)
        

    #     return self.new_portfolio
    
    def candidates_for_purchase (self,raw_df: pd.DataFrame(), threshold:float()):
        '''looks at market price of available securities, compares to prior close and returns set of candidates available for purchase given threshold'''
        #test each security against the close of day before yesterday
        #subset the list of candidates based on which are down >0.25%
        #must be sorted by time index, most recent 2 data points
        s = (1-raw_df.Close.iloc[-2]/raw_df.Close.iloc[-1])*100 #((raw_df.High.iloc[-1]+raw_df.Low.iloc[-1])/2))*100
        s = s.sort_values()
        s = s[s < (threshold-2.0)]
        print(f'here are the candidates that meet threshold for purchase: {s}')
        if s.shape[0]:
            return list(s.index)
        else:
            return []
            #print("sorry there is no historical data that meets the threshold")
            #pass
    
    def candidates_for_sale (self, portfolio_dict: dict(), raw_df: pd.DataFrame(), threshold:float()):
        '''looks at portfolio for winners > 100$ and most recent market value being up more than threshold'''
        #update the portfolio market value
        #test each security against the close of day before yesterday
        #subset the list of candidates based on which are up >0.25%
        #must be sorted by time index, most recent 2 data points
        print(raw_df.Close)
        s = (1-raw_df.Close.iloc[-2]/raw_df.Close.iloc[-1])*100 #((raw_df.High.iloc[-1]+raw_df.Low.iloc[-1])/2))*100
        s = s.sort_values(ascending=False)
        print(f'here are the day over day comparison for sale: {s}')
        s = s[s > -1*threshold]
        print(f'here are the day over day comparisons that make the threshold: {s}')
        possible_candidates = set(s.index)
        holdings_set = set(portfolio_dict.keys())        
        valid_candidates = holdings_set.intersection(possible_candidates)

        #for candidate in valid_candidates:
        #update the market price of each holding in the portfolio
        for k,v in portfolio_dict.items():
            if k == 'cash':
                pass
            else:
                portfolio_dict[k]['current_price'] = self.get_market_price(k, raw_df, self.method)

        made_100 = self.get_current_return_pct(portfolio_dict)

        valid_candidates = valid_candidates.intersection(made_100)
        print(f'here are the valid candidates for sale: {valid_candidates}')

        if (s.shape[0] != 0) & (len(valid_candidates) != 0):
            return list(valid_candidates)
        else:
            return ['all holdings are down!']
            #print("sorry there is no historical data that meets the threshold")    
            
    def get_current_return (self, portfolio_dict: dict())->set():
        
        tmp_dict = {}
        for k,v in portfolio_dict.items():
            if k == 'cash':
                pass
            else:
                tmp_dict[k] = (portfolio_dict[k]['current_price'] - portfolio_dict[k]['book_cost']) * portfolio_dict[k]['units']
                if tmp_dict[k] < self.return_required:
                    del tmp_dict[k]

        return set(tmp_dict.keys())

    def get_current_return_pct (self, portfolio_dict: dict())->set():
        
        tmp_dict = {}
        for k,v in portfolio_dict.items():
            if k == 'cash':
                pass
            else:
                tmp_dict[k] = ((portfolio_dict[k]['current_price'] - portfolio_dict[k]['book_cost']) / portfolio_dict[k]['book_cost'])*100
                if tmp_dict[k] < 3.5:
                    del tmp_dict[k]

        return set(tmp_dict.keys())

    def how_many_holdings_to_buy (self, portfolio_dict: dict())->int():
        #get length of dict minus 1 for cash
        #4 minus length of dict is how many must be bought
        current_holdings = len(portfolio_dict.keys())
        purchase_count = self.config.get_generic_config_property('portfolio','max_holdings') - current_holdings 
        return purchase_count

    def purchase_shares (self, ticker_name: str(), action: str(), cash: float(), market_data: pd.DataFrame(), holding_dict: dict()):
        '''functions takes existing portfolio, ticker name, market price, number of units and returns the new cost/revenue of the purchase/sale'''
        #get most recent close price
        tmp_dict = holding_dict.copy()
        market_price = self.get_market_price(ticker_name, market_data, self.method)
        tmp_dict['units'] = (cash - self.transaction_fee) / market_price
        tmp_dict['book_cost'] = market_price
        tmp_dict['current_price'] = market_price
        #portfolio_dict['cash'] -= cash
        self.transaction_tracker += 1
        return tmp_dict

    def sell_shares (self, ticker_name: str(), action: str(), portfolio_dict: dict(), market_data: pd.DataFrame()):
        '''functions takes existing portfolio, ticker name, market price, number of units and returns the new cost/revenue of the purchase/sale'''
        #get most recent close price
        market_price = self.get_market_price(ticker_name, market_data, self.method)

        #shares to sell
        sale_cash =  (portfolio_dict[ticker_name]['units'] * market_price) - self.transaction_fee
        print("sold: " + ticker_name + " for: " + market_price.astype('str'))

        portfolio_dict['cash'] += sale_cash

        #clear out the dictionary entry
        print(portfolio_dict.keys())
        portfolio_dict.pop(ticker_name, None)
        print(portfolio_dict.keys())
        # portfolio_dict[ticker_name]['units'] = 0
        # portfolio_dict[ticker_name]['book_cost'] = 0
        # portfolio_dict[ticker_name]['current_price'] = 0
        self.transaction_tracker += 1
        return portfolio_dict

    def get_market_price (self, ticker_name: str(), market_data: pd.DataFrame(), method: str()):
        '''function takes the ticker name an retrieves most recent market price, it is the prior day close'''
        #return the most recent price for the given ticker
        if method == 'Close':
            market_price = market_data.Close[ticker_name].iloc[-1]
        else:
            market_price = (market_data.High[ticker_name].iloc[-1] + market_data.Low[ticker_name].iloc[-1])/2
        return market_price
    
    def get_initial_purchase_date (self):
        '''function to initialize a random start date between window'''
        return randomDate(self.start_date, self.end_date, random.random())
    

    

        
    

    