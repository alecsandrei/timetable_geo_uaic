from __future__ import annotations

import requests
from bs4 import BeautifulSoup, Tag


def request_table(years='2023_2024', semester='1') -> Tag:
    """This function will be used to collect the table from the URL."""
    url = f'https://geomorphologyonline.com/orar/{years}_sem{semester}/{years}_sem{semester}_activities_days_horizontal.html'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0',
    }
    r = requests.get(url, headers=headers, verify=False)
    c = r.content
    c = BeautifulSoup(c, features='html.parser')
    # get the last table on the page, which corresponds to all the activities
    table = c.find_all('table')[2] 
    return table
