from sec_edgar_downloader import Downloader
import logging

#download recent 10K file of a given ticker
def download_10K(ticker) -> None:
    #download 10K from 1995 to 2023 of indicated stock
    try:
        dl = Downloader("gatech", "yliu3680@gatech.edu", "dataset")
        dl.get("10-K", ticker, after="1995-01-01", before="2023-01-01")
    except Exception as e:
        logging.error("An error occurred: %s", e)
    return

def main():
    download_10K('F')

if __name__ == '__main__':
    main()