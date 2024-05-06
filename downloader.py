from sec_edgar_downloader import Downloader
import logging
import os
import shutil

#download recent 10K file of a given ticker
def download_10K(ticker) -> None:
    #download 10K from 1995 to 2023 of indicated stock
    try:
        dl = Downloader("gatech", "yliu3680@gatech.edu", "")
        dl.get("10-K", ticker, after="1995-01-01", before="2023-01-01")
    except Exception as e:
        logging.error("An error occurred: %s", e)
    return

def delete_download(ticker):
    folder_path = f"sec-edgar-filings/{ticker}"
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    return

def main():
    download_10K('AAPL')
    delete_download('F')

if __name__ == '__main__':
    main()