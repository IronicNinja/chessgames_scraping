from bs4 import BeautifulSoup as soup
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from datetime import date, datetime
from time import sleep
import pandas as pd
import numpy as np
import multiprocessing
import psutil

series_list = []
curr_index = 10000 # Ending index ID

for i in np.arange(curr_index-10000, curr_index):
    try:
        input_id = str(i).zfill(6)
        fname = f'http://www.chessmetrics.com/cm/CM2/PlayerProfile.asp?Params=199510SSSSS3S{input_id}000000151000000000036310100'
        req = Request(fname, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req)
        page_soup = soup(webpage, "html.parser")
        containers = page_soup.findAll("table")
        name = containers[2].tr.td.findAll("font", {"color": "BLUE"})[0].text.strip()
        if name == '-':
            continue

        print(f"Current Successful ID: {i}")
        rating_list = []
        month_list = []
        for entry in containers[-1].findAll("tr"):
            entry_list = entry.findAll("td")
            month = datetime.strptime(entry_list[0].text.replace(' rating list', ''), "%B %Y")
            rating = int(entry_list[1].text.split(',')[0].replace('Rating: ', ''))
            month_list.append(month)
            rating_list.append(rating)
        series_list.append(pd.Series(data=rating_list, index=month_list, name=name))
    except Exception as e:
        print(f"There is an error at player ID {i}", e)

df = pd.concat(series_list, axis=1)
df.to_csv(f"ratings{curr_index}.csv")