import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class PlotOrder:

    def __init__(self, close_order_PATH, open_order_PATH, contract="BTCUSDT"):

        close_order_df = pd.read_csv(close_order_PATH)
        close_order_df = close_order_df[close_order_df["Contracts"] == contract]
        close_order_df.drop(columns=["Entry Price", "Exit Type",], inplace=True)
        close_order_df.rename({"Closing Direction": "OrderType", 
                               "Exit Price": "OrderPrice", 
                               "Qty": "OrderQty", 
                               "Trade Time": "OrderTime", 
                               "Closed P&L": "CumPnL"}, axis=1, inplace=True)
        close_order_df["TotalHolding"] = 0


        open_order_df = pd.read_csv(open_order_PATH)
        open_order_df = open_order_df[open_order_df["Contracts"] == contract]
        open_order_df.drop(columns=["Leverage", 
                                    "Filled Type", 
                                    "Fee Rate", 
                                    "Fee Paid", 
                                    "Order Type", 
                                    "Trade ID"], inplace=True)
        open_order_df.rename({"Trade Type": "OrderType", 
                              "Filled Price/Order Price": "OrderPrice", 
                              "Filled/Total": "OrderQty", 
                              "Trade Time": "OrderTime"}, axis=1, inplace=True)
        open_order_df[["TotalHolding", "CumPnL"]] = 0


        total_df = pd.concat([close_order_df, open_order_df])
        self.__analyze(contract, total_df)
        self.total_df.sort_values(by="OrderTime", inplace=True)

        self.contract = contract


    def __analyze(self, contract, total_df):
        arr = np.array(total_df)

        # add CumPnL
        for index, i in np.ndenumerate(arr[1:,4]):
            arr[index[0]+1, 4] = arr[index[0], 4] + i

        # clean Qty
        for index, i in np.ndenumerate(arr[:,2]):
            i = i.replace(contract[:3], "").split("/")[0]
            arr[index[0], 2] = float(i)
            
            if "Close Long" in arr[index, 1] or "Open Short" in arr[index, 1]:
                arr[index, 2] = -arr[index, 2]
            elif "Open Long" in arr[index, 1] or "Close Short" in arr[index, 1]:
                pass
            else: 
                raise ValueError("OrderType error")

        # clean OrderPrice
        for index, i in np.ndenumerate(arr[:,3]):
            i = str(i)
            arr[index[0], 3] = float(i.split("/")[0])

        # calculate holding
        for index, i in np.ndenumerate(arr[:,6]):
            index[0] == 0 and arr[index, 6] == arr[index, 2]
            arr[index, 6] = arr[index[0]-1, 6] + arr[index, 2]

        self.total_df = pd.DataFrame(arr, columns=total_df.columns)



    def plot_holding(self):
        plt.figure(1)
        plt.plot(self.total_df["OrderTime"], self.total_df["TotalHolding"])
        plt.xlabel("Time")
        plt.ylabel("Holding")
        plt.axhline(0, color="k", linestyle="dashed", linewidth=0.5)
        plt.show()



    def plot_cum_pnl(self):
        plt.figure(2)
        plt.plot(self.total_df["OrderTime"], self.total_df["CumPnL"])
        plt.xlabel("Time")
        plt.ylabel("CumPnL")
        plt.axhline(0, color="k", linestyle="dashed", linewidth=0.5)
        plt.show()
