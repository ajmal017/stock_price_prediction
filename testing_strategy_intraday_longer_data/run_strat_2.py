import pandas as pd
import numpy as np
import pickle
from collections import Counter

import datetime as dt
import yfinance as yf  # for data
from pandas_datareader import data as pdr
yf.pdr_override()

start_year = 2020
start_month = 4
start_day = 1

end_year = 2020
end_month = 10
end_day = 24

start = dt.datetime(start_year,start_month,start_day)
now = dt.datetime(end_year,end_month,end_day)

series_tickers = pickle.load(open("series_tickers.p", "rb" ))
df = pd.DataFrame(series_tickers).reset_index()

list_of_lists = [['AAPL','AAPL'],['AAPL','AAPL'],['IBM','IBM'],['AMD','AMD'],['T','T'],['DAL','DAL'],['J&J','J&J'],['INTC','INTC'],['GE','GE'],['NIO','NIO'],['JKS','JKS']]
df_new = pd.DataFrame(list_of_lists, columns = ['Symbol','Security Name'])

# new tickers
series_tickers = pd.concat([df,df_new],axis = 0).set_index('Symbol').iloc[:,0]

stock_returns = {}

for stock, name in series_tickers.iteritems():
    
    # Calculating the ema
    #df = pdr.get_data_yahoo(stock,start,now)
    df = pdr.get_data_yahoo(stock,period = "60d",

        # fetch data by interval (including intraday if period < 60 days)
        # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        # (optional, default is '1d')
        interval = "5m")
    
    # calcuting indicators
    
    emasUsed = [26,50]
    for ema in emasUsed:
        df['Ema_' + str(ema)] = round(df['Adj Close'].ewm(span = ema, adjust = False).mean(),2)
        df['Middle Band'] =df['Adj Close'].rolling(window=20).mean()
        df['Upper Band'] = df['Middle Band'] + 1.96*df['Close'].rolling(window=20).std()
        df['Lower Band'] = df['Middle Band'] - 1.96*df['Close'].rolling(window=20).std()
        df['status_lower'] = np.where(df['Close'] < df['Lower Band'],'below_ballinger','normal')
        df['status_upper'] = np.where(df['Close'] > df['Upper Band'],'above_ballinger','normal')
    
    df = df.iloc[20:,:] # remove the 20 nans row
        
    # calculating the cmin and cmax
    pos = 0
    num = 0
    percentchange = []
    
    # applying strategy

    for i in df.index:
        status_upper = df['status_upper'][i]
        status_lower = df['status_lower'][i]


        close = df['Adj Close'][i]

        if(status_lower=='below_ballinger'):
           # print('red white blue')
            if pos ==0:
                bp =close
                pos=1
                print('Buying now at'+ str(bp))


        elif(status_upper=='upper_ballinger'):
            #print('blue white red')
            if pos ==1:
                pos = 0
                sp = close
                print('Selling now at'+ str(sp))
                pc = (sp/bp-1)*100
                percentchange.append(pc)

        if num ==df['Adj Close'].count()-1 and pos==1:
            pos = 0
            sp = close
            print('Selling now at'+ str(bp))
            pc = (sp/bp-1)*100
            percentchange.append(pc)      
        num +=1
   
     # evaluation
    gains = 0
    ng = 0
    losses = 0
    nl = 0
    totallR = 1
    for i in percentchange:
        if i >0:
            gains +=i
            ng +=1
        else:
            losses +=i
            nl +=1
        totallR = totallR*((i/100)+1)
    totallR = round((totallR-1)*100)
    if ng > 0:
        avgGain = gains/ng
        maxR = str(max(percentchange))
    else:
        avgGain = 0
        maxR = 'undefined'

    if nl>0:
        avgLoss = losses/nl
        maxL = str(min(percentchange))
        ratio = str(-(avgGain/avgLoss))
    else:
        avgLoss = 0
        maxL = 'undefined'
        ratio = 'inf'

    if ng >0 and nl >0:
        bettingAvg = ng/ng+nl
    else:
        bettingAvg = 0
    stock_returns[stock] = totallR
    
    
    
#     print()
#     print('Result for '+stock+" going back to "+str(df.index[0])+" Sample size: "+str(ng+nl)+"trades")
#     print('EMAs used : ',str(emasUsed))
#     print('Batting Avg : '+str(bettingAvg))
#     print('Gain/loss ratio: ' + ratio)
#     print('Avg gain: ' + str(avgGain))
#     print('Avg loss: '+ str(avgLoss))
#     print('Max return: '+ str(maxR))
#     print('Max loss: ' + str(maxL))
#     print('Total return over '+str(ng+nl)+' trades: '+str(totallR)+'%')
#     print()
d = Counter(stock_returns)
x= d.most_common()

df = pd.DataFrame(x,columns = ['Stock','Return'])
df.to_csv('lstra_2_stocks.csv')




