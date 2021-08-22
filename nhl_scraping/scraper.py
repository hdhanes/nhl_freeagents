'''
NHL season scraper of single season player stats
Converts the data into a pandas dataframe, and generates /PG and /60 metrics

Hendrix Hanes
'''

import pandas as pd
from bs4 import BeautifulSoup as BS
from urllib import request
import json
from googlesearch import search

#helper function: convert %M:%S into a float of time
    #str -> float
def time_convert(timestring):
    if ":" in timestring:
        time = timestring.split(":")
        return int(time[0]) + int(time[1])/60
    else:
        return int(timestring)
    

class NHLSeasonScraper():
    
    def __init__(self):
        self.player_data = pd.DataFrame()
        self.freeagent_data = pd.DataFrame()
        
        
    #scrape current team rosters (train set) from NHL API    
    def scraperosters(self,year):
        '''
        scrapes the rosters, create new dataframe (i.e. overwrites)
        '''
        
        year = str(int(year)-1) + year
        team_ids = [i for i in range(1,11)] + [i for i in range(12,27)] + [28,29,30,52,53,54,55]
        player_list = []
        print("1. Scraping rosters...")
        for team in team_ids:
                
            #team rosters
            url = "https://statsapi.web.nhl.com/api/v1/teams/" + str(team) + "/roster"
            html = request.urlopen(url).read()
            soup = BS(html,'html.parser')
            site_json=json.loads(soup.text)
            roster = site_json.get("roster")
            
            #scraping the player stats
            for player in roster:
                player_dict = {}
                if player["position"]["code"] != "G":
                    try:
                        url = "https://statsapi.web.nhl.com/api/v1/people/" + str(player['person']['id']) + "/stats?stats=statsSingleSeason&season=" + str(year)
                        html = request.urlopen(url).read()
                        soup = BS(html,'html.parser')
                        site_json=json.loads(soup.text)
                        player_dict = site_json.get("stats")[0].get('splits')[0].get("stat")
                        player_dict['id'] = player['person']['id']
                        player_dict['name'] = player['person']['fullName']
                        
                        url = "https://statsapi.web.nhl.com/api/v1/people/" + str(player_dict['id'])
                        html = request.urlopen(url).read()
                        soup = BS(html,'html.parser')
                        site_json=json.loads(soup.text)
                        player_dict['position'] = site_json.get('people')[0].get("primaryPosition").get("abbreviation")
            
                        player_list.append(player_dict)
                    except:
                        pass
                else:
                    pass
            
        #reorder columns
        print("2. Feature cleaning/engineering")    
        df = pd.DataFrame(player_list)
        df['C'] = df['position'].apply(lambda k: 1 if k == "C" else 0)
        df['LW'] = df['position'].apply(lambda k: 1 if k == "LW" else 0)
        df['RW'] = df['position'].apply(lambda k: 1 if k == "RW" else 0)
        df['D'] = df['position'].apply(lambda k: 1 if k == "D" else 0)
        df = df[['id','name', 'position'] + [col for col in df.columns if col not in ['id','name','position']]]
        
        #convert time to floats
        df['powerPlayTimeOnIce'] = df['powerPlayTimeOnIce'].apply(lambda x: time_convert(x))
        df['timeOnIce'] = df['timeOnIce'].apply(lambda x: time_convert(x))
        df['evenTimeOnIce'] = df['evenTimeOnIce'].apply(lambda x: time_convert(x))
        df['penaltyMinutes'] = df['penaltyMinutes'].apply(lambda x: time_convert(x))
        df['shortHandedTimeOnIce'] = df['shortHandedTimeOnIce'].apply(lambda x: time_convert(x))
        df['timeOnIcePerGame'] = df['timeOnIcePerGame'].apply(lambda x: time_convert(x))
        df['evenTimeOnIcePerGame'] = df['evenTimeOnIcePerGame'].apply(lambda x: time_convert(x))
        df['shortHandedTimeOnIcePerGame'] = df['shortHandedTimeOnIcePerGame'].apply(lambda x: time_convert(x))
        df['powerPlayTimeOnIcePerGame'] = df['powerPlayTimeOnIcePerGame'].apply(lambda x: time_convert(x))
        
        #feature engineering - per 60 metrics
        df["assists_60"] = df["assists"]/(0.0000001+df['timeOnIce'])*60
        df["goals_60"] = df["goals"]/(0.0000001+df['timeOnIce'])*60
        df["pim_60"] = df["pim"]/(0.0000001+df['timeOnIce'])*60
        df["shots_60"] = df["shots"]/(0.0000001+df['timeOnIce'])*60
        df["hits_60"] = df["hits"]/(0.0000001+df['timeOnIce'])*60
        df["powerPlayGoals_60"] = df["powerPlayGoals"]/(0.0000001+df['powerPlayTimeOnIce'])*60
        df["powerPlayPoints_60"] = df["powerPlayPoints"]/(0.0000001+df['powerPlayTimeOnIce'])*60
        df["gameWinningGoals_60"] = df["gameWinningGoals"]/(0.0000001+df['timeOnIce'])*60
        df["overTimeGoals_60"] = df["overTimeGoals"]/(0.0000001+df['timeOnIce'])*60
        df["shortHandedGoals_60"] = df["shortHandedGoals"]/(0.0000001+df['shortHandedTimeOnIce'])*60
        df["shortHandedPoints_60"] = df["shortHandedPoints"]/(0.0000001+df['shortHandedTimeOnIce'])*60
        df["blocked_60"] = df["blocked"]/(0.0000001+df['timeOnIce'])*60
        df["points_60"] = df["points"]/(0.0000001+df['timeOnIce'])*60
        df["shifts_60"] = df["shifts"]/(0.0000001+df['timeOnIce'])*60
        
        self.player_data = df
        
        print("3. Complete!")
        
        
    #used to get list of viable free agent targets (i.e. test set) from CapFriendly
    def scrapeFA(self, year):
        
        #scrape names from capfriendly
        year = str(int(year)+1)
        print("1. Getting the FAs from Capfriendly...")
        url = "https://www.capfriendly.com/browse/free-agents/" + year + "/caphit/all/all/ufa?hide=goalie-stats&limits=gp-10-90"
        html = request.urlopen(url).read()
        soup = BS(html,'html.parser')
        table = soup.find('table')
        table_rows = table.find_all("tr")
        
        #get list of names
        name_list = []
        for tr in table_rows:
            td = tr.find_all('td')
            row = [tr.text for tr in td]
            if row != [] and row[3] != "G":
                name = row[0]
                true_name = name.split(". ")[1]
                name_list.append(true_name)
                
        #now, use a google search to find player ids as the API for season stats is off
        print("2. Obtaining player ids from Google...")
        player_id_dict = {}
        for name in name_list:
            search_list = list(search(name + " nhl", stop=10))
            final_url = [url for url in search_list if "www.nhl.com/player" in url][0]
            player_id_dict[name] = final_url[-7:]
            
        #now scrape from NHL API
        print("3. Scraping FA data from NHL API...")
        player_list = []
        year_new = str(int(year)-2) + str(int(year)-1)
        for player in player_id_dict:
            url = "https://statsapi.web.nhl.com/api/v1/people/" + str(player_id_dict[player]) + "/stats?stats=statsSingleSeason&season=" + year_new
            html = request.urlopen(url).read()
            soup = BS(html,'html.parser')
            site_json=json.loads(soup.text)
            player_dict = site_json.get("stats")[0].get('splits')[0].get("stat")
            player_dict['id'] = str(player_id_dict[player])
            player_dict['name'] = player
            
            url = "https://statsapi.web.nhl.com/api/v1/people/" + str(player_id_dict[player])
            html = request.urlopen(url).read()
            soup = BS(html,'html.parser')
            site_json=json.loads(soup.text)
            player_dict['position'] = site_json.get('people')[0].get("primaryPosition").get("abbreviation")
            
            player_list.append(player_dict) 
        
        #reorder columns
        print("4. Feature cleaning/engineering")    
        df = pd.DataFrame(player_list)
        df['C'] = df['position'].apply(lambda k: 1 if k == "C" else 0)
        df['LW'] = df['position'].apply(lambda k: 1 if k == "LW" else 0)
        df['RW'] = df['position'].apply(lambda k: 1 if k == "RW" else 0)
        df['D'] = df['position'].apply(lambda k: 1 if k == "D" else 0)
        df = df[['id','name','position'] + [col for col in df.columns if col not in ['id','name','position']]]
        
        #convert time to floats
        df['powerPlayTimeOnIce'] = df['powerPlayTimeOnIce'].apply(lambda x: time_convert(x))
        df['timeOnIce'] = df['timeOnIce'].apply(lambda x: time_convert(x))
        df['evenTimeOnIce'] = df['evenTimeOnIce'].apply(lambda x: time_convert(x))
        df['penaltyMinutes'] = df['penaltyMinutes'].apply(lambda x: time_convert(x))
        df['shortHandedTimeOnIce'] = df['shortHandedTimeOnIce'].apply(lambda x: time_convert(x))
        df['timeOnIcePerGame'] = df['timeOnIcePerGame'].apply(lambda x: time_convert(x))
        df['evenTimeOnIcePerGame'] = df['evenTimeOnIcePerGame'].apply(lambda x: time_convert(x))
        df['shortHandedTimeOnIcePerGame'] = df['shortHandedTimeOnIcePerGame'].apply(lambda x: time_convert(x))
        df['powerPlayTimeOnIcePerGame'] = df['powerPlayTimeOnIcePerGame'].apply(lambda x: time_convert(x))
        
        #feature engineering - per 60 metrics
        df["assists_60"] = df["assists"]/(0.0000001+df['timeOnIce'])*60
        df["goals_60"] = df["goals"]/(0.0000001+df['timeOnIce'])*60
        df["pim_60"] = df["pim"]/(0.0000001+df['timeOnIce'])*60
        df["shots_60"] = df["shots"]/(0.0000001+df['timeOnIce'])*60
        df["hits_60"] = df["hits"]/(0.0000001+df['timeOnIce'])*60
        df["powerPlayGoals_60"] = df["powerPlayGoals"]/(0.0000001+df['powerPlayTimeOnIce'])*60
        df["powerPlayPoints_60"] = df["powerPlayPoints"]/(0.0000001+df['powerPlayTimeOnIce'])*60
        df["gameWinningGoals_60"] = df["gameWinningGoals"]/(0.0000001+df['timeOnIce'])*60
        df["overTimeGoals_60"] = df["overTimeGoals"]/(0.0000001+df['timeOnIce'])*60
        df["shortHandedGoals_60"] = df["shortHandedGoals"]/(0.0000001+df['shortHandedTimeOnIce'])*60
        df["shortHandedPoints_60"] = df["shortHandedPoints"]/(0.0000001+df['shortHandedTimeOnIce'])*60
        df["blocked_60"] = df["blocked"]/(0.0000001+df['timeOnIce'])*60
        df["points_60"] = df["points"]/(0.0000001+df['timeOnIce'])*60
        df["shifts_60"] = df["shifts"]/(0.0000001+df['timeOnIce'])*60
        
        self.freeagent_data = df
        
        print("5. Complete!")
        
    
    #clear the current Dataframes
    def clear_df(self):
        self.player_data =pd.DataFrame()
        self.freeagent_data = pd.DataFrame()
        
        print("Dataframes cleared...")
        
    #save the current Dataframes
    def save_df(self):
        self.player_data.to_csv("current_data/player_data.csv")
        self.freeagent_data.to_csv("current_data/freeagent_data.csv")
        
    def __str__(self):
        print("Players")
        print(self.player_data.head()) 
        print("\n Free Agents")
        print(self.freeagent_data.head())
        return ''
                             
        
#testing                      
if __name__ == '__main__':
    test = NHLSeasonScraper()
    test.scraperosters("2021")
    test.scrapeFA("2021")
    print(test)
    test.save_df()
        