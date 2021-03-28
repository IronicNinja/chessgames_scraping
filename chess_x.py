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

splits = 4 # How many cores you want to use. I recommend at max 4 so that the chessgames server is not overloaded.
start = 1000000 # start is your starting ID!
look_at = 1000 # How many games forward you want to look
index_list = []
for num in range(splits):
    index_list.append(np.arange(start+look_at*num, start+look_at*(num+1)))

RUN = True
if RUN:
    if __name__ == '__main__':
        with multiprocessing.Pool(processes=splits) as pool:
            pool.map(scrape, index_list)

# Final note: With multiprocessing, 4000 games took 50 mins