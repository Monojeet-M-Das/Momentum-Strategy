from scipy.stats import linregress
import pandas as pd
import yfinance as yf
import numpy as np
import datetime 
import backtrader as bt
import matplotlib.pyplot as plt

def calculate_momentum(data):
    log_data = np.log(data)
    x_data = np.arange(len(log_data))
    beta, _, rvalue, _, _ = linregress(x_data, log_data)
    # we have to annualize the slope
    return (1+beta)**252 * (rvalue**2)

class Momentum(bt.Indicator):
    # every trading day has a momentum parameter except for first 90 days
    lines = ('momentum_trend',)
    params = (('period', 90),)

    def __init__(self):
        self.addminperiod(self.params.period)

    def next(self):
        returns = np.log(self.data.get(size = self.params.period))
        x = np.arange(len(returns))
        beta, _, rvalue, _, _ = linregress(x, returns)
        annualized = (1+beta)**252
        self.lines.momentum_trend[0] = annualized * rvalue**2

class MomentumStrategy(bt.Strategy):

    def __init__(self):
        self.counter = 0
        self.indicators = {}
        self.sorted_data = []
        # we store the SP500 data as the first item of the dataset
        self.spy = self.datas[0]
        # all the other stocks (present in SP500)
        self.stocks = self.datas[1:]

        for stock in self.stocks:
            self.indicators[stock] = {}
            self.indicators[stock]['momentum'] = Momentum(stock.close, period=90)
            self.indicators[stock]['sma100'] = bt.indicators.\
                SimpleMovingAverage(stock.close, period=100)
            self.indicators[stock]['atr20'] = bt.indicators.ATR(stock, period=20)

        # SMA for SP500 index - because open long position when SP500 above SMA(200): BULLISH
        self.sma200 = bt.indicators.MovingAverageSimple(self.spy.close, period=200)

    def prenext(self):
        # we want to count the number of days elapsed
        self.next()

    def next(self):
        # a week has passed so we have to make trades
        if self.counter % 5 == 0:
            self.rebalance_portfolio()
        if self.counter % 10 == 0:
            # 2 weeks have passed
            self.update_positions()

        self.counter +=1

    def rebalance_portfolio(self):
        self.sorted_data = list(filter(lambda stock_data: len(stock_data) > 100, self.stocks))
        # sort SP500 based on momentum
        self.sorted_data.sort(key=lambda stock: self.indicators[stock]['momentum'][0])
        num_stocks = len(self.sorted_data)

        # sell stocks (close the long positions) - top 20%
        for index, single_stock in enumerate(self.sorted_data):
            # we can check for open positions
            if self.getposition(self.data).size:
                if index > 0.2 * num_stocks or single_stock < self.indicators[single_stock]['sma100']:
                    self.close(single_stock)

        # open long position when SMA below SP500 index
        if self.spy < self.sma200:
            return
        
        # we consider the top 20% of the stocks and buy accordingly
        for index, single_stock in enumerate(self.sorted_data[:int(num_stocks*0.2)]):
            cash = self.broker.get_cash()
            value = self.broker.get_value()
            if cash > 0 and not self.getposition(self.data).size:
                size = value * 0.001 / self.indicators[single_stock]['atr20']
                self.buy(single_stock, size=size)

    def update_positions(self): 
        num_stocks = len(self.sorted_data)

        # top 20% momentum range
        for index, single_stock in enumerate(self.sorted_data[:int(num_stocks*0.2)]): 
            cash = self.broker.get_cash()
            value = self.broker.get_value()
            if cash > 0:
                size = value * 0.001 / self.indicators[single_stock]['atr20']
                self.order_target_size(single_stock, size)

        
if __name__ == '__main__':

    stocks = []
    cerebro = bt.Cerebro()

    with open('companies_all') as file_in:
        for line in file_in:
            ticker = line.strip()
            stocks.append(ticker)
            try:
                df = yf.download(ticker, start="2015-01-01", end="2024-12-31")
                df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
                if len(df) > 100:
                    cerebro.adddata(bt.feeds.PandasData(dataname=df, plot=False))
            except Exception as e:
                print(f"Error downloading {ticker}: {e}")

    
    cerebro.addobserver(bt.observers.Value)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, riskfreerate= 0)
    cerebro.addanalyzer(bt.analyzers.Returns)
    cerebro.addanalyzer(bt.analyzers.DrawDown)
    cerebro.addstrategy(MomentumStrategy)

    cerebro.broker.set_cash(100000)
    
    # commission fees - set 0.01%
    cerebro.broker.setcommission(0.01)

    print('initial capital: $%.2f' % cerebro.broker.getvalue())
    results = cerebro.run()

    print('Sharpe ratio: %.2f' % results[0].analyzers.sharperatio.get_analysis()['sharperatio'])
    print('Return: %.2f%%' % results[0].analyzers.returns.get_analysis()['rnorm100'])
    print('Max Drawdown: %.2f%%' % results[0].analyzers.drawdown.get_analysis()['max']['drawdown'])
    print('Capital: $%.2f' % cerebro.broker.getvalue())