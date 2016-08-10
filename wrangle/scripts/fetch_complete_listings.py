"""
Parses HTML from atf.gov/firearms website and extracts URLs belonging to "Complete"
data files. Saves them to disk without attempting to parse the URL slug
(i.e. for year and month)
"""

from pathlib import Path
from lxml import html as htmlparser
from urllib.parse import urljoin
import re
import requests
MIN_YEAR = 2013
MAX_YEAR = 2016

BASE_SRC_URL_PATH = 'https://www.atf.gov/firearms/'
BASE_SRC_URL_PATTERN = BASE_SRC_URL_PATH + 'listing-federal-firearms-licensees-ffls-{year}'

DEST_DIR = Path('wrangle', 'corral', 'fetched', 'complete')
DEST_DIR.mkdir(exist_ok=True, parents=True)

def download_html_page(year):
    desturl = BASE_SRC_URL_PATTERN.format(year=year)
    print("Downloading landing page:", desturl)
    return requests.get(desturl).text


def parse_html_table(htmltxt):
    """
    htmltxt is a String containing the HTML from a proper atf.gov/firearms page

    Returns: a list of URLs
    """
    hdoc = htmlparser.fromstring(htmltxt)
    # urls = hdoc.xpath('//a[contains(@href,"download")]/@href')
    th = hdoc.xpath('//th[contains(text(),"Complete listing")]')[0]
    hrefs = th.getparent().xpath('td//a/@href')
    return [urljoin(BASE_SRC_URL_PATH, h) for h in hrefs]

def fetch_data_and_save(url):
    """
    url is a string that looks like:
        https://www.atf.gov/sites/default/files/legacy/2015/04/16/0415-ffl-list.xlsx
        https://www.atf.gov/firearms/docs/1215-ffl-listtxt/download
        https://www.atf.gov/resource-center/docs/0213-ffl-listxls/download
        https://www.atf.gov/resource-center/docs/october2014fflxlsx/download

    Saves to ./wrangle/corral/fetched/complete/2015-12.txt
    Returns: destination path
    """
    resp = requests.get(url)
    parts = url.split('/')
    slug =  parts[-2] if 'download' in parts[-1] else parts[-1]
    destpath = DEST_DIR / slug
    if 'txt' not in slug:
        destpath.write_bytes(resp.content)
    else:
        destpath.write_text(resp.text)
    return destpath
    # print(url)
    # yr, mth, file_ext = re.search(r'/(\d{2})(\d{2})-ffl-list.*?(txt|xlsx?)', url).groups()
    # destpath = "{month}-{year}.{ext}".format(year='20'+yr, month=mth, ext=file_ext)
    # return destpath


def main():
    for year in range(MIN_YEAR, MAX_YEAR+1):
        htmltxt = download_html_page(year)
        urls = parse_html_table(htmltxt)
        for url in urls:
            print("\tDownloading data file:", url)
            destpath = fetch_data_and_save(url)
            print("\tSaving to:", destpath)

if __name__ == '__main__':
    main()
