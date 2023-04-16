# ocr-trade-history
## Usage

1. 
```
$ git clone https://github.com/moneybabe/ocr-trade-history.git
$ conda create -n ocr
$ conda activate ocr
$ conda install pytesseract pillow
```

2. Change the `PATH` at the top of `main.py` to the directory where you stored the images.
3. Run `$ python main.py close` or `$ python main.py open` depending on the order type of the images.
4. The corresponding csv file will be created in the working directory.

