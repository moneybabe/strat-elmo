import pandas as pd
import configparser
from pybit.unified_trading import HTTP
from ratelimit import limits
import datetime
import time
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

class FetchHistory:

    def __init__(self, config_PATH="bybit.ini", symbol="BTCUSDT", startTime="", endTime="", category="linear", limit=200):
        config = configparser.ConfigParser()
        config.read(config_PATH)
        self.apiKey = config['bybit']['apiKey']
        self.secret = config['bybit']['secret']
        self.symbol = symbol
        self.category = category
        self.limit = limit

        if startTime == "":
            two_years = datetime.datetime.now() - datetime.timedelta(days=725)
            self.startTime = int(two_years.timestamp() * 1000)
        else:
            self.startTime = int(datetime.datetime.strptime(startTime, "%Y/%m/%d").timestamp() * 1000)

        if endTime == "":
            self.endTime = int(datetime.datetime.now().timestamp() * 1000)
        else:
            self.endTime = int(datetime.datetime.strptime(endTime, "%Y/%m/%d").timestamp() * 1000)

        self.session = HTTP(
            testnet=False,
            api_key=self.apiKey,
            api_secret=self.secret,
        )
        self.df = pd.DataFrame()

    @limits(calls=8, period=1)
    def __single_fetch__closed_PnL(self, symbol, startTime, endTime, category, limit, cursor):
        pnl = self.session.get_closed_pnl(
            category=category,
            limit=limit,
            symbol=symbol,
            startTime=startTime,
            endTime=endTime,
            cursor=cursor
        )

        cursor = pnl["result"]["nextPageCursor"]
        df = pd.DataFrame(pnl["result"]["list"])

        return df, cursor

    def fetch_closed_PnL(self):
        cursor = ""
        while True:
            df, cursor = self.__single_fetch__closed_PnL(self.symbol, self.startTime, self.endTime, self.category, self.limit, cursor)

            if len(df) == 0 or cursor == "":
                break

            self.df = pd.concat([self.df, df], ignore_index=True)

            time.sleep(0.15)

        self.df = self.df.iloc[::-1]

        # create tradeTime column
        self.df['tradeTime'] = pd.to_datetime(self.df[['createdTime', 'updatedTime']].astype(int).mean(axis=1), unit='ms')

        # create cumPnL column
        self.df['cumPnL'] = self.df['closedPnl'].astype(float).cumsum()

        self.df.to_csv("trade_history/{}_closed_PnL.csv".format(self.symbol), index=False)

        return self.df

    def plot(self):
        self.fetch_closed_PnL()
        plt.plot(self.df["tradeTime"], self.df["cumPnL"], label="cumPnL", color="blue", linewidth=1)
        dtFmt = mdates.DateFormatter('%Y-%m-%d') # define the formatting
        plt.gca().xaxis.set_major_formatter(dtFmt) 
        plt.xticks(rotation=45, fontweight='light',  fontsize='x-small')
        plt.ylabel("CumPnL (USD)")
        plt.xlabel("Closed Time")
        plt.title("CumPnL of {}".format(self.symbol))
        y = range(0, int(self.df["cumPnL"].max()), 10000)
        plt.hlines(y, self.df["tradeTime"].min(), self.df["tradeTime"].max(), colors='k', linestyles='dashed', linewidth=0.5, alpha=0.5)
    
    
def plot_cumPnL(filepath="trade_history/BTCUSDT_closed_PnL.csv"):
    df = pd.read_csv(filepath, parse_dates=["tradeTime"])
    plt.plot(df["tradeTime"], df["cumPnL"], label="cumPnL", color="blue", linewidth=1)
    dtFmt = mdates.DateFormatter('%Y-%m-%d') # define the formatting
    plt.gca().xaxis.set_major_formatter(dtFmt) 
    plt.xticks(rotation=45, fontweight='light',  fontsize='x-small')
    plt.ylabel("CumPnL (UCD)")
    plt.xlabel("Closed Time")
    y = range(0, int(df["cumPnL"].max()), 10000)
    plt.hlines(y, df["tradeTime"].min(), df["tradeTime"].max(), colors='k', linestyles='dashed', linewidth=0.5, alpha=0.5)
    
