# Import modules
from PIL import Image
import pytesseract
import pandas as pd
import numpy as np
import os
import sys


class ReadOrder:

    def __init__(self, PATH="images/close_orders/"):
        self.PATH = PATH
        self.df = pd.DataFrame()


    def __crop_image(self, filename):
        # Load image
        img = Image.open(filename)
        width, height = img.size
        cropped_img = img.crop((0, height-580, width, height-100))

        # Save cropped image
        return cropped_img


    def __scan_order(self, cropped_img):
        config = "--psm 6 --oem 1 -c tessedit_char_whitelist=.,-:/%0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz' '"
        text = pytesseract.image_to_string(cropped_img, lang="eng", config=config)
        split_text = text.replace(",", "").split("\n")
        split_text[-1] == "" and split_text.pop()
        split_text = list(map(lambda x: x.split(" "), split_text))
        for i in split_text:
            for j in i:
                if j == "" or len(j) == 1:
                    i.remove(j)

                if j[-1] == ".":
                    i[i.index(j)] = j[:-1]

        split_text = np.array(split_text)
        
        return split_text


    def __order_df(self, split_text, close=True):
        if close:
            columns = ("Contracts", "Closing Direction", "Direction", "Qty", "Coin", "Entry Price", "Exit Price", "Closed P&L", "Exit Type", "Trade Date", "Trade Time")        
            df = pd.DataFrame(split_text, columns=columns)
            df["Entry Price"] = list(map(lambda x: float(x[:-1] if x[-1] == "." else x), df["Entry Price"]))
            df["Exit Price"] = list(map(lambda x: float(x[:-1] if x[-1] == "." else x), df["Exit Price"]))
            df["Closed P&L"] = list(map(lambda x: float(x[:-1] if x[-1] == "." else x), df["Closed P&L"]))

            df["Qty"] = df["Qty"] + df["Coin"]
            df["Trade Time"] = df["Trade Date"] + " " + df["Trade Time"]
            df["Closing Direction"] = df["Closing Direction"] + " " + df["Direction"]
            df.drop(["Direction", "Coin", "Trade Date"], axis=1, inplace=True)
            
            df["Trade Time"] = pd.to_datetime(df["Trade Time"], format="%Y/%m/%d %H:%M:%S")

        else:
            columns = ("Contracts", "Leverage", "Filled Type", "Filled/Total", "Filled Price/Order Price", "Fee Rate", "Fee Paid", "Trade Type", "Type", "Order Type", "Trade ID", "Trade Date", "Trade Time")
            df = pd.DataFrame(split_text, columns=columns)
            df["Fee Paid"] = list(map(lambda x: float(x[:-1] if x[-1] == "." else x), df["Fee Paid"]))
            df["Leverage"] = list(map(lambda x: x.replace("4", "1"), df["Leverage"]))
            
            df["Trade Type"] = df["Trade Type"] + " " + df["Type"]
            df["Trade Time"] = df["Trade Date"] + " " + df["Trade Time"]
            df.drop(["Type", "Trade Date"], axis=1, inplace=True)

            df["Trade Time"] = pd.to_datetime(df["Trade Time"], format="%Y/%m/%d %H:%M:%S")

        return df


    def export_orders(self, close=True):
        img_list = []
        for filename in os.listdir(self.PATH):
            img_list.append(self.PATH + filename)

        for filename in img_list:
            cropped_img = self.__crop_image(filename)
            split_text = self.__scan_order(cropped_img)
            self.df = pd.concat([self.df, self.__order_df(split_text, close)], ignore_index=True)
            self.df.sort_values(by="Trade Time", inplace=True)
        
        if close:
            self.df.to_csv("close_orders.csv", index=False)
        else:
            self.df.to_csv("open_orders.csv", index=False)

        return self.df


if __name__ == "__main__":

    PATH = "images/{}_orders/".format(sys.argv[1])

    ro = ReadOrder(PATH)
    ro.export_orders(close=True if sys.argv[1] == "close" else False)