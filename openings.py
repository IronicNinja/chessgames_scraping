from bs4 import BeautifulSoup as soup
from urllib.request import Request, urlopen
import pandas as pd

fname = f'https://www.chessgames.com/chessecohelp.html'
req = Request(fname, headers={'User-Agent': 'Mozilla/5.0'})
webpage = urlopen(req)
page_soup = soup(webpage, "html.parser")
containers = page_soup.findAll("tr")

eco_list = []
for container in containers:
    op = container.findAll("td")
    split_text = op[1].font.text.split('\n')
    eco_list.append([op[0].font.text, split_text[0], split_text[1]])
    
opening_df = pd.DataFrame(eco_list, columns=['ECO', 'Opening Names', 'Moves'])
opening_df.to_csv('openings.csv')