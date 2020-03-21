import pandas as pd
import numpy as np
from portfolio import *
from get_data import *
from utils import *
import copy
#from matplotlib import pyplot as plt
#import seaborn

#housekeeping
config = Config()
transaction_fee = config.get_generic_config_property('portfolio','transaction_fee')
max_holdings = config.get_generic_config_property('portfolio','max_holdings')

portfolio = Portfolio()
raw_market_data = GetStocks()
raw_market_data = raw_market_data.stock_data.dropna()
time_window = 580 #days
today = raw_market_data.iloc[2].name.strftime('%Y-%m-%d')



def assess_buy_and_hold(portfolio_dict: dict(), raw_market_data: pd.DataFrame()) -> dict():
    buy_and_hold_keys = list(portfolio_dict.keys())
    buy_and_hold_keys.remove('cash')
    final_close = raw_market_data.Close[buy_and_hold_keys].iloc[-1].to_dict()
    portfolio_dict_buy_and_hold_final = portfolio_dict.copy()
    for k, v in portfolio_dict_buy_and_hold_final.items():
        if k == 'cash':
            pass
        else:
            portfolio_dict_buy_and_hold_final[k]['current_price'] = final_close[k]
    return portfolio_dict_buy_and_hold_final


def run_trading_simulation (period, portfolio_dict, date, raw_market_data):
    print(f'here is the initial dict: {portfolio_dict}')
    days_remaining = period
    sell_side_complete = False
    updated_portfolio = portfolio_dict.copy()
    today_index = 2
    day_before_yesterday_index = today_index - 2

    while days_remaining > 0:
        print(f'analyzing stocks, {days_remaining} days left to analyze')
        market_data = raw_market_data.iloc[day_before_yesterday_index:today_index] #subset the raw market data to a df of three rows, current, previous, previous - 1
        updated_portfolio = run_trading_day(sell_side_complete, updated_portfolio, date, market_data)
        days_remaining -= 1
        today_index += 1   #must advance the date
        day_before_yesterday_index = today_index - 2
        print(f'here is the updated dict {updated_portfolio}')
        print("total value of current portfolio is: " + total_value(updated_portfolio).astype('str'))
        #update the market price of the holdings in the dictionary here
    return updated_portfolio

def run_trading_day (sell_side_complete, portfolio_dict, date, market_data):
    print(sell_side_complete)
    # if sell_side_complete == False:
    #     print('im buying!')
    #     updated_portfolio = run_buy_side(portfolio_dict, date, market_data, portfolio.threshold)
    # else:
    print('im selling!')
        # sell_side_complete, updated_portfolio = run_sell_side(portfolio_dict, date, market_data)
    
    sell_side_complete, updated_portfolio = run_sell_side(portfolio_dict, date, market_data)

    print('im buying!')
    updated_portfolio = run_buy_side(portfolio_dict, date, market_data, portfolio.threshold)
    return updated_portfolio

def run_buy_side (portfolio_dict, date, market_data, threshold):
    ls_to_buy = portfolio.candidates_for_purchase(market_data, threshold) #based on overall candidates recent performance, what if security is already in portfolio? do we differentiate?
    remaining_purchases = len(ls_to_buy)
    portfolio_size = len(portfolio_dict.keys())
    cash = portfolio_dict['cash']
    try:
        cash_for_purchase = (cash / remaining_purchases)
    except:
        cash_for_purchase = 0

    while ((cash - transaction_fee) > 0) & (len(ls_to_buy)>0) & (portfolio_size > 0) & (portfolio_size < max_holdings):
        ticker = ls_to_buy.pop(0)

        if (ticker not in portfolio_dict.keys()) & (portfolio_size > 0) & ((cash_for_purchase - transaction_fee) > 0):
            portfolio_dict[ticker] = portfolio.make_an_empty_holding()
            portfolio_dict[ticker] = portfolio.purchase_shares(ticker, 'buy', cash_for_purchase, market_data, portfolio_dict[ticker])
            portfolio_dict['cash'] -= cash_for_purchase
        portfolio_size = portfolio.how_many_holdings_to_buy(portfolio_dict)
        cash = portfolio_dict['cash']
        portfolio_size = len(portfolio_dict.keys())
    
    return portfolio_dict

def run_sell_side (portfolio_dict, date, market_data):
    ls_to_sell = portfolio.candidates_for_sale(portfolio_dict, market_data, portfolio.threshold ) #based on what is in portfolio now
    action = 'sell'
    print(ls_to_sell)
    for holding in ls_to_sell:
        if holding == 'all holdings are down!':
            pass
        else:
            portfolio_dict = portfolio.sell_shares(holding, action, portfolio_dict, market_data)
    sell_side_complete = True
    return sell_side_complete, portfolio_dict

def total_value (portfolio_dict: dict())->float():
    tmp_value = float()
    for k, v in portfolio_dict.items():
        if k == 'cash':
            pass
        else:
            tmp_value += (portfolio_dict[k]['units'] * portfolio_dict[k]['current_price'])
    
    tmp_value = tmp_value + portfolio_dict['cash']
    return tmp_value


case_studies = {}
total_transactions = []
for sim in range(29):
    portfolio = Portfolio()
    portfolio_dict_raw = {}
    portfolio_dict_raw = portfolio.get_new_portfolio(raw_market_data.iloc[:2], specific_ls=[]).copy()
    print(f'here is the very beginning of dict: {portfolio_dict_raw}')
    portfolio_dict_buy_and_hold = copy.deepcopy(portfolio_dict_raw)
    portfolio_dict_buy_and_hold_final = assess_buy_and_hold(portfolio_dict_buy_and_hold, raw_market_data)
    final_value_buy_and_hold = total_value(portfolio_dict_buy_and_hold_final)
    output_portfolio = run_trading_simulation(time_window, portfolio_dict_raw, today, raw_market_data)
    final_value_buy_and_sell = total_value(output_portfolio)
    case_studies[sim] = {'buy_and_hold':[final_value_buy_and_hold, list(portfolio_dict_buy_and_hold_final.keys())], 'buy_and_sell': [final_value_buy_and_sell, list(output_portfolio.keys())]} #'buy_and_hold':final_value_buy_and_hold,
    total_transactions.append(portfolio.transaction_tracker)


