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
        self.open_df = pd.DataFrame()
        self.close_df = pd.DataFrame()


    def crop_image(self, filename):
        # Load image
        img = Image.open(filename)
        width, height = img.size
        cropped_img = img.crop((0, height-580, width, height-100))

        # Save cropped image
        return cropped_img


    def scan_order(self, cropped_img):
        config = "--psm 6 --oem 1 -c tessedit_char_whitelist=.,-:/%0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz' '"
        text = pytesseract.image_to_string(cropped_img, lang="eng", config=config)
        split_text = text.replace(",", "").split("\n")
        split_text[-1] == "" and split_text.pop()
        split_text = list(map(lambda x: x.split(" "), split_text))
        for i in split_text:
            for j in i:
                if j == "" or len(j) == 1:
                    i.remove(j)
        split_text = np.array(split_text)
        
        return split_text


    def open_order_df(self, split_text):
        columns = ("Contracts", "Leverage", "Filled Type", "Filled/Total", "Filled Price/Order Price", "Fee Rate", "Fee Paid", "Trade Type", "Transaction Time")
        data = {}
        count = 0
        for column in columns[:-1]:
            data[column] = split_text[count * 10: (count + 1) * 10]
            count += 1

        data["Fee Paid"] = list(map(float, data["Fee Paid"]))

        data[columns[-1]] = split_text[-10:]
        
        df = pd.DataFrame(data)

        return df


    def order_df(self, split_text, close=True):
        if close:
            columns = ("Contracts", "Closing", "Direction", "Qty", "Coin", "Entry Price", "Exit Price", "Closed P&L", "Exit Type", "Trade Date", "Transaction Time")        
            df = pd.DataFrame(split_text, columns=columns)
            df["Qty"] = list(map(lambda x: float(x[:-1] if x[-1] == "." else x), df["Qty"]))
            df["Entry Price"] = list(map(lambda x: float(x[:-1] if x[-1] == "." else x), df["Entry Price"]))
            df["Exit Price"] = list(map(lambda x: float(x[:-1] if x[-1] == "." else x), df["Exit Price"]))
            df["Closed P&L"] = list(map(lambda x: float(x[:-1] if x[-1] == "." else x), df["Closed P&L"]))
        else:
            columns = ("Contracts", "Leverage", "Filled Type", "Filled/Total", "Filled Price/Order Price", "Fee Rate", "Fee Paid", "Trade", "Type", "Order Type", "Transaction ID", "Transaction Time")
            df = pd.DataFrame(split_text, columns=columns)
            df["Fee Paid"] = list(map(lambda x: float(x[:-1] if x[-1] == "." else x), df["Fee Paid"]))
            

        return df


    def export_open_orders(self):
        img_list = []
        for filename in os.listdir(self.PATH):
            img_list.append(self.PATH + filename)

        for filename in img_list:
            cropped_img = self.crop_image(filename)
            split_text = self.scan_order(cropped_img)
            self.open_df = pd.concat([self.open_df, self.open_order_df(split_text)], ignore_index=True)
        
        self.open_df.to_csv("open_orders.csv", index=False)

        return self.open_df


    def export_orders(self, close=True):
        img_list = []
        for filename in os.listdir(self.PATH):
            img_list.append(self.PATH + filename)

        for filename in img_list:
            cropped_img = self.crop_image(filename)
            split_text = self.scan_order(cropped_img)
            self.close_df = pd.concat([self.close_df, self.order_df(split_text, close)], ignore_index=True)
        
        self.close_df.to_csv("close_orders.csv", index=False)

        return self.close_df

if __name__ == "__main__":

    PATH = "images/close_orders/"

    # if sys.argv[1] == "close":
    #     ro = ReadOrder(PATH)
    #     ro.export_close_orders()
    # elif sys.argv[1] == "open":
    #     ro = ReadOrder(PATH)
    #     ro.export_open_orders()
    # else:
    #     print("Invalid argument")

    ro = ReadOrder(PATH)
    ro.export_orders(close=True)