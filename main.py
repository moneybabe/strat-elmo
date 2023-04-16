# Import modules
from PIL import Image
import pytesseract
import pandas as pd
import os
import sys

PATH = "images/close_orders/" # Path to image


def crop_image(filename):
    # Load image
    img = Image.open(filename)
    width, height = img.size
    cropped_img = img.crop((0, height-580, width, height-100))

    # Save cropped image
    return cropped_img


def scan_order(cropped_img):
    text = pytesseract.image_to_string(cropped_img, lang="eng")
    spliited_text = text.split("\n\n")
    spliited_text[-1] = spliited_text[-1].replace("\n", "")

    return spliited_text


def open_order_df(spliited_text):
    columns = ("Contracts", "Leverage", "Filled Type", "Filled/Total", "Filled Price/Order Price", "Fee Rate", "Fee Paid", "Trade Type", "Transaction Time")
    data = {}
    count = 0
    for column in columns[:-1]:
        data[column] = spliited_text[count * 10: (count + 1) * 10]
        count += 1

    data["Fee Paid"] = list(map(float, data["Fee Paid"]))

    data[columns[-1]] = spliited_text[-10:]
    
    df = pd.DataFrame(data)

    return df


def close_order_df(splitted_text):
    columns = ("Contracts", "Closing Direction", "Qty", "Entry Price", "Exit Price", "Closed P&L", "Exit Type", "Trade Time")
    data = {}
    count = 0
    if len(splitted_text)%10 != 0:
        splitted_text += [None] * (10 - (len(splitted_text) % 10))

    for column in columns:
        data[column] = splitted_text[count * 10: (count + 1) * 10]
        count += 1

    data["Entry Price"] = list(map(lambda x: x.replace(",", ""), data["Entry Price"]))
    data["Exit Price"] = list(map(lambda x: x.replace(",", ""), data["Exit Price"]))
    data["Closed P&L"] = list(map(lambda x: x.replace(",", ""), data["Closed P&L"]))

    data["Entry Price"] = list(map(lambda x: x.replace("~", "-"), data["Entry Price"]))
    data["Exit Price"] = list(map(lambda x: x.replace("~", "-"), data["Exit Price"]))
    data["Closed P&L"] = list(map(lambda x: x.replace("~", "-"), data["Closed P&L"]))

    data["Entry Price"] = list(map(lambda x: x.replace("+", ""), data["Entry Price"]))
    data["Exit Price"] = list(map(lambda x: x.replace("+", ""), data["Exit Price"]))
    data["Closed P&L"] = list(map(lambda x: x.replace("+", ""), data["Closed P&L"]))

    data["Entry Price"] = list(map(float, data["Entry Price"]))
    data["Exit Price"] = list(map(float, data["Exit Price"]))
    data["Closed P&L"] = list(map(float, data["Closed P&L"]))
    
    df = pd.DataFrame(data)

    return df


def export_open_orders(PATH):
    img_list = []
    for filename in os.listdir(PATH):
        img_list.append(PATH + filename)

    df = pd.DataFrame()
    for filename in img_list:
        cropped_img = crop_image(filename)
        spliited_text = scan_order(cropped_img)
        df = pd.concat([df, open_order_df(spliited_text)], ignore_index=True)
    
    df.to_csv("open_orders.csv", index=False)


def export_close_orders(PATH):
    img_list = []
    for filename in os.listdir(PATH):
        img_list.append(PATH + filename)

    df = pd.DataFrame()
    for filename in img_list:
        cropped_img = crop_image(filename)
        spliited_text = scan_order(cropped_img)
        df = pd.concat([df, close_order_df(spliited_text)], ignore_index=True)
    
    df.to_csv("close_orders.csv", index=False)

if __name__ == "__main__":
    if sys.argv[1] == "close":
        export_close_orders(PATH)
    elif sys.argv[1] == "open":
        export_open_orders(PATH)
    else:
        print("Invalid argument")