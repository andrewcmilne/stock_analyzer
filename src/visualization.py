from matplotlib import pyplot as plt
import pandas as pd


b_h_list = list()
b_s_list = list()
for k, v in case_studies.items():
    b_h_list.append(case_studies[k]['buy_and_hold'][0])
    b_s_list.append(case_studies[k]['buy_and_sell'][0])

plt.hist(b_h_list,alpha = 0.5,  label = 'buy_hold')
plt.hist(b_s_list, alpha = 0.5, label='buy_sell')
plt.legend(loc='upper right')
plt.show()

vs_ls = [x - y for x, y in zip(b_s_list,b_h_list)]
winners  = [x for x in vs_ls if x>0]
print(f'on average your winners are winning by: {sum(winners)/len(winners)}')   
losers = [x for x in vs_ls if x<0] 
print(f'on average your losers are losing by: {sum(losers)/len(losers)}') 
