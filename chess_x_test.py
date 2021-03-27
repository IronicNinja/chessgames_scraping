from bs4 import BeautifulSoup as soup
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from datetime import date, datetime
from time import sleep
import pandas as pd
import numpy as np
import multiprocessing
import psutil

def scrape(indices):
    event_list = []
    site_list = []
    date_list = []
    event_date_list = []
    round_list = []
    result_list = []
    white_players_list = []
    black_players_list = []
    ECO_list = []
    white_elo_list = []
    black_elo_list = []
    move_count_list = []
    game_pgn_list = []

    for i in indices:
        try:
            if i%100 == 0:
                print(i)
            fname = f'https://www.chessgames.com/perl/chessgame?gid={i}'
            req = Request(fname, headers={'User-Agent': 'Mozilla/5.0'})
            webpage = urlopen(req)
            page_soup = soup(webpage, "html.parser")
            containers = page_soup.findAll("div", {"id": "olga-data"})
            game = str(containers[0]).split('\n')
        except Exception as e:
            with open('except.txt', 'a') as f:
                f.write(f"ID: {i}; Error: {e}\n")
            continue
        
        def helper(index, name):
            """helper function which makes this code less wordy"""
            thing = game[index]
            thing_tmp = thing[thing.index(name)+len(name)+2:]
            real_thing = thing_tmp[:thing_tmp.index('"')]
            return real_thing

        try:
            event_list.append(helper(0, "Event"))
            site_list.append(helper(1, "Site"))
            date_list.append(helper(2, "Date"))
            event_date_list.append(helper(3, "EventDate"))
            round_list.append(helper(4, "Round"))

            result = helper(5, "Result")
            true_result = ""
            if result == "1/2-1/2":
                true_result = "Draw"
            elif result == "1-0":
                true_result = "White Wins"
            else:
                true_result = "Black Wins"
            result_list.append(true_result)

            white_players_list.append(helper(6, "White"))
            black_players_list.append(helper(7, "Black"))
            ECO_list.append(helper(8, "ECO"))

            white_elo = helper(9, "WhiteElo")
            white_elo_list.append(white_elo if white_elo != '?' else -1)

            black_elo = helper(10, "BlackElo")
            black_elo_list.append(black_elo if black_elo != '?' else -1)

            try:
                move_count_list.append(helper(11, "PlyCount"))
            except:
                move_count_list.append(helper(12, "PlyCount"))

            pgn = game[-2]
            game_pgn_list.append(pgn[:pgn.index(result)-1])
        except Exception as e:
            print(f"There is an error at game ID {i}", e)
            with open('error.txt', 'a') as f:
                f.write(f"{i}\n")

    everything_list = [event_list, site_list, date_list, event_date_list, round_list, result_list, 
    white_players_list, black_players_list, ECO_list, white_elo_list, black_elo_list, move_count_list, game_pgn_list]
    columns = ["Event", "Site", "Date", "Event Date", "Round", "Result", "White Player", "Black Player", "ECO", "White Elo", "Black Elo", "Move Count", "PGN"]

    df = pd.DataFrame(everything_list).T
    df.columns = columns

    for column in columns:
        if column != "Date":
            try:
                df[column] = pd.to_numeric(df[column])
            except:
                df[column] = df[column].astype("string")

    df.to_csv(f"master_games{indices[0]}.csv")

splits = 4
start = 1996000
look_at = 1000
index_list = []
for num in range(splits):
    index_list.append(np.arange(start+look_at*num, start+look_at*(num+1)))

RUN = True
if RUN:
    if __name__ == '__main__':
        with multiprocessing.Pool(processes=splits) as pool:
            pool.map(scrape, index_list)

"""
With multiprocessing, 4000 games took 50 mins

Not found games:
1019672
1019675
1048371
1056020
1054860
1061462
1059928
1067494
1075210
1075725
1081155
1080483
1080584
1078973
1084094
1082212
1082774
1087033
1088706
1090520
1107073
1151142
1151979
1120838
1122039
1128398
1127913
1132585
1211018
1139511
1139729
1144033
1216885
1147859
1306162
1224815
1234282
1404430
1243397
1243789
1243797
1427923
1430415
1457756
1457766
1449022
1480218
1480677
1511945
1525632
1531128
1536414
1555915
1581428
1580824
1591433
1591752
1591781
1255559
1255590
1610027
1612746
1627943
1648853
1671162
1676233
1697613
1715123
1718594
1739681
1740441
1751462
1758158
"""

#scrape(np.arange(1005000, 1006000))