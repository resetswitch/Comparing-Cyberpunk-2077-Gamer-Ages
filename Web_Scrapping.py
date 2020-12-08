import requests
from bs4 import BeautifulSoup
import re
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

def scrapping():
    # Where the age data will be stored 
    age_data = []

    # Web Scrapping. Cycling through Steam post pages Cyberpunk 2077 and Grand Theft Auto
    URLs = {'Cyberpunk 2077'    : 'https://steamcommunity.com/app/1091500/discussions/0/2966147051985194105/',
            'Grand Theft Auto 5': 'https://steamcommunity.com/app/271590/discussions/0/611703999974654762/'}
    for game_name in URLs:
        URL = URLs[game_name]
        print("Gathering from Steam Post\nURL: {}".format(URL))
        game_age_data = []
        page_number = 1
        while True:
            # URL main page doesnt have Params 
            if page_number == 1: 
                param = ""
            else:
                param = "?ctp="+str(page_number)

            # Exception Handling
            try:
                page = requests.get(URL+param)
                page.raise_for_status()
            except requests.exceptions.HTTPError as err:
                print("page number {},\n{}".format(page_number, err))
                continue

            # Gathering the HTML soup
            # - Ignore replies that have blockquotes (i.e. a user responding to another user's reply, rather than the post)
            # - Breaks out of while loop, when pages no longer have comments
            soup = BeautifulSoup(page.content, 'html.parser')
            if len(soup.find_all(class_="commentthread_comment_text")) == 0:
                print("\r\ncompleted", end="\n\n", flush=True)
                break
            while soup.blockquote != None:
                soup.blockquote.decompose()
            results = soup.find_all(class_="commentthread_comment_text")

            # Filtering out numbers
            for index, result in enumerate(results):
                text    = result.text.strip()
                search  = re.findall('[0-9]+', text)
                if len(search) == 0: pass
                else:
                    age = int(search[0])
                    game_age_data.append(age)
                
            # General sense of progression, when cycling through URL's
            print("\rpage number = {}".format(page_number), end='', flush= True)
            page_number+=1
        
        age_data.append(game_age_data)

    # Exporting Data
    df = pd.DataFrame(age_data)
    df.index = pd.Index(list(URLs.keys()))
    df = df.transpose()
    data_filename = "age_data.csv"
    df.to_csv(data_filename, index = False)
    print("saving {} in {}".format(data_filename, os.getcwd()))
    return data_filename

def graphing(data_filename):
    # Importing Data, Prepping for index logic splicing
    df1 = pd.read_csv (data_filename)
    cp2077_temp = df1["Cyberpunk 2077"].values
    gta5_temp   = df1["Grand Theft Auto 5"].values

    # Source: for Avg Age of Gamers : https://www.theesa.com/wp-content/uploads/2020/07/2020-ESA_Essential_facts_070820_Final_lowres.pdf
    labels      = 'Under 18', '18-34', '35-54', '55-64', '65+'
    avg_sizes   = [21, 38, 26, 9, 6]

    # Cyberpunk 2077 age groupings
    cp2077_age_data = cp2077_temp[(cp2077_temp >=5) & (cp2077_temp <=80)] # Filtering out unlikely ages
    cp2077_sizes = [
            len(cp2077_age_data[(cp2077_age_data < 18)])/len(cp2077_age_data)*100, 
            len(cp2077_age_data[(cp2077_age_data >= 18) & (cp2077_age_data < 35)])/len(cp2077_age_data)*100, 
            len(cp2077_age_data[(cp2077_age_data >= 35) & (cp2077_age_data < 55)])/len(cp2077_age_data)*100, 
            len(cp2077_age_data[(cp2077_age_data >= 55) & (cp2077_age_data < 65)])/len(cp2077_age_data)*100,
            len(cp2077_age_data[(cp2077_age_data >= 65) & (cp2077_age_data < 80)])/len(cp2077_age_data)*100]

    # Grand Theft Auto 5 age groupings
    gta5_age_data = gta5_temp[(gta5_temp >=5) & (gta5_temp <=80)]
    gta5_sizes = [
            len(gta5_age_data[gta5_age_data < 18])/len(gta5_age_data)*100, 
            len(gta5_age_data[(gta5_age_data >= 18) & (gta5_age_data < 35)])/len(gta5_age_data)*100, 
            len(gta5_age_data[(gta5_age_data >= 35) & (gta5_age_data < 55)])/len(gta5_age_data)*100, 
            len(gta5_age_data[(gta5_age_data >= 55) & (gta5_age_data < 65)])/len(gta5_age_data)*100,
            len(gta5_age_data[gta5_age_data >= 65])/len(gta5_age_data)*100]


    # Graphing
    plt.bar(np.arange(0,5) + 0.00, avg_sizes, color = '#32a860', width = 0.25, label = "2020 Age Group Average")
    plt.bar(np.arange(0,5) + 0.25, cp2077_sizes, color = '#9632a8', width = 0.25, label = "2020 Cyberpunk 2077")
    plt.bar(np.arange(0,5) + 0.50, gta5_sizes, color = '#f0ac00', width = 0.25, label = "2015 Grand Theft Auto 5")
    plt.title(label = "Age Groups of Popular Video Games")
    plt.xticks(ticks = np.arange(0,5) + 0.25, labels = labels)
    plt.xlabel(xlabel = "Ages")
    plt.ylabel(ylabel = "Percent")
    plt.legend()
    graph_filename = "Age_Groups_of_Popular_Video_Games.png"
    plt.savefig(graph_filename, dpi=300)
    plt.show()
    print("saving {} in {}".format(graph_filename, os.getcwd()))

# Comment out scrapping() if the data has already been saved
filename = scrapping()
graphing(filename)

