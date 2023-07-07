import streamlit as st
import pandas as pd
import requests
import datetime
import numpy as np
import uuid #note i have to use uuid here instead of shortuuid

#the app will reflect save and commits



st.title('Blue Dot :blue[Sports] :)') 
if st.button('See TN'):
     st.write("##:red[These Nuts]")
else:
     st.write()

df = pd.DataFrame({
  'first column': [1, 2, 3, 4],
  'second column': [10, 20, 30, 40]
})

add_sidebar = st.sidebar.selectbox('Menu',('Place Bet','My Bets','My Bank','Test Env'))

if add_sidebar == "Test Env":
  df
  st.line_chart(df)
  
else:
  st.write()


if add_sidebar == "Place Bet":
     if st.button('Execute'):
          url = "https://content.unabated.com/markets/game-odds/v_gameodds.json"
          #Scrape MainLines from Unabated

          querystring = {"v":"23587068-b3e0-4152-99c1-b0bce9523702"}
          payload = ""
          r = requests.request("GET", url, data=payload, params=querystring)
          data = r.json()

          marketSources = (data["marketSources"])
          teams = (data["teams"])
          gameOddsEvents = (data["gameOddsEvents"])


          df_sportsbooks = pd.DataFrame(marketSources)
          df_teams = pd.DataFrame(teams)
          df_teams=df_teams.transpose()

          # create the GameOddsEvents Table. We do this one first to better reflect scrapeDate
          data = []
          for i in gameOddsEvents:
            for j in gameOddsEvents[i]:
              event_teams = j['eventTeams']
              #Sometimes id_1 does not have value of 1
              try:
                  id_0 = event_teams['0']['id']
                  if '1' in event_teams:
                      id_1 = event_teams['1']['id']
              
              
                      # Extract the americanPrice values from gameOddsMarketSourcesLines
                      game_odds_market_sources_lines = j['gameOddsMarketSourcesLines']
                      for market_source, market_data in game_odds_market_sources_lines.items():
                        siX= market_source
                        for bet_type, bet_data in market_data.items():
                              american_price = bet_data['americanPrice']
                              marketLineId= bet_data['marketLineId']
                              marketId= bet_data['marketId']
                              marketSourceId= bet_data['marketSourceId']
                              points= bet_data['points']
                              price= bet_data['price']
                              sourcePrice= bet_data['sourcePrice']
                              btX = bet_type
                              # Store the extracted data in a tuple
                              row = (i, j['eventId'],j['eventStart'],j['eventEnd'] ,id_0, id_1, siX, btX, marketLineId, marketSourceId,
                              marketId, points,american_price, price, sourcePrice)
                              data.append(row)
              except KeyError:
                  print("KeyError caught for event_teams:",event_teams)
          
          # Create the DataFrame with the extracted data
          df_MainLineOdds = pd.DataFrame(data, columns=['lgX', 'eventId','eventStart','eventEnd','Teamid_0', 'Teamid_1', 'siX', 'btX', 'marketLineId','marketSourceId','marketId','points','american_price','price','sourcePrice'])
          df_MainLineOdds['lgX_league'] = df_MainLineOdds['lgX'].str.extract(r'lg([^:]+)')
          df_MainLineOdds['lgX_pt'] = df_MainLineOdds['lgX'].str.extract(r'pt([^:]+)')
          df_MainLineOdds['bet_stage'] = df_MainLineOdds['lgX'].str.split(':', 2).str[2]
          df_MainLineOdds['siX_side']= df_MainLineOdds['siX'].str.get(2)
          df_MainLineOdds['scrapeDateUTC'] = datetime.datetime.utcnow().isoformat()
          # ISO 8601 format for scrapedate is easiest to read in csv
          
          
          
          
          # Transforming the SportsBooks Reference Table
          
          #Removing columns for building purposes 
          #Note a bunch of other sportsbooks exist but are not shown on webpage. 
          df_sb = pd.DataFrame().assign(bookName=df_sportsbooks['name'],bookId=df_sportsbooks['id'],isActive=df_sportsbooks['isActive'],
          statusId=df_sportsbooks['statusId'],modifiedDate=df_sportsbooks['modifiedOn'])
          
          
          #Creating Binary flags 
          df_sb['nyBook']= 0
          df_sb['sharpBook']= 0
          
          
          #store binary flag reference
          df_nyBooks= pd.DataFrame(
              {"bookName" : ["Caesars", "DraftKings", "FanDuel", "FanDuel - Delayed", "BetMGM", "PointsBet", "BetRivers", "WynnBet", "Resorts", "BallyBet"],
              'nyBook': [1,1,1,1,1,1,1,1,1,1]
              }
          )
          df_sharpBooks = pd.DataFrame(
              {"bookName" :['Unabated','Pinnacle','Pinnacle - Delayed','Bookmaker','Prophet Exchange'],
              'sharpBook': [1,1,1,1,1]
              }
          )
          
          #Insert 1 if bookName matches the above
          df_sb=df_sb.set_index('bookName')
          df2 = df_nyBooks.set_index('bookName')
          df_sb.update(df2)
          
          df3=df_sharpBooks.set_index('bookName')
          df_sb.update(df3)
          
          #Move bookName back to a column
          # Step 1: Reset the index
          df_sb = df_sb.reset_index()
          
          # Step 2: Rename the 'index' column to 'ID'
          df_sb = df_sb.rename(columns={'index': 'ID'})
          
          # Step 3: Assign a new continuous integer index
          df_sb = df_sb.reset_index(drop=True)
          
          
          df_sb
          
          
          
          # Now we create the Teams table. 
          
          
          #slimming down df_teams
          df_teams_refined = pd.DataFrame().assign(teamId=df_teams['id'],teamName=df_teams['name'],abbreviation=df_teams['abbreviation'],
          eventId=df_teams['eventId'],sideId=df_teams['sideId'],leagueId=df_teams['leagueId'],divisionId=df_teams['divisionId'],
          modifiedDate=df_teams['modifiedOn'])
          
          df_teams_refined
          #This is our Teams Table
          
          
          
          #manipulate the odds data
          
          #Define bet_type
          bet_type = {
              'bt1': 'Money_Line',
              'bt2':'Spread',
              'bt3': 'Total_Combined'}
          
          # Insert the bet_type & create filtered_df
          filtered_df = df_MainLineOdds[df_MainLineOdds['marketSourceId'].isin(df_sb['bookId'])].copy()
          filtered_df.loc[:, 'bet_type'] = filtered_df['btX'].map(bet_type)
          
          #Insert a league column
          league_dict = {
              '1':'NFL',
              '2':'CFB',
              '3':'NBA',
              '4':'NCAAB',
              '5':'MLB',
              '6':'NHL',
              '7':'WNBA'
              }
          
          filtered_df.loc[:,'league'] = filtered_df['lgX_league'].map(league_dict)
          
          # Insert the TeamNames and side(home/away) for Teamid_0 and Teamid_1
          # Merge the two dataframes on teamId
          filtered_df = df_teams_refined.merge(filtered_df, left_on='teamId', right_on='Teamid_0')
          
          # Rename the columns so they don't overwrite each other
          filtered_df = filtered_df.rename(columns={'teamName':'TeamName_0', 'abbreviation':'TeamAbbrev_0','sideId':'sideId_team0'})
          
          # Drop the now unnecessary merged columns column
          filtered_df = filtered_df.drop(columns={'teamId','TeamAbbrev_0','eventId_x','leagueId','divisionId','modifiedDate'})
          
          
          #repeat for Teamid_1
          filtered_df = filtered_df.merge(df_teams_refined, left_on='Teamid_1', right_on='teamId')
          filtered_df = filtered_df.rename(columns={'teamName':'TeamName_1', 'abbreviation':'TeamAbbrev_1','sideId':'sideId_team1'})
          filtered_df = filtered_df.drop(columns=['teamId','TeamAbbrev_1','leagueId','divisionId','modifiedDate','eventId'])
          filtered_df = filtered_df.rename(columns={'eventId_y' : 'eventId'})
          
          
          
          # Merge bookName into df_filtered
          filtered_df = filtered_df.merge(df_sb, left_on='marketSourceId', right_on='bookId')
          
          # Drop & rename columns. 
          
          filtered_df= filtered_df.drop(columns=['statusId','siX'])
          
          # Rename Columns 
          
          filtered_df= filtered_df.rename(columns={
              'isActive':'bookIsActive',
              'siX_side': 'bet_side'})
          
          
          #Insert betPeriod column
          
          ptX_definiton = {
              '1':'FullGame',
              '2':'Half_1',
              '3':'Half_2',
              '4':'Quarter_1',
              '5':'Quarter_2',
              '6':'Quarter_3',
              '7':'Quarter_4',
              '8':'Period_1',
              '9':'Period_2',
              '10':'Period_3'}
          
          
          filtered_df.loc[:, 'betPeriod'] = filtered_df['lgX_pt'].map(ptX_definiton)
          
          
          
          #Reorder to make it easier to read
          
          easiest_to_read_column_order = ['marketLineId','eventId', 'eventStart', 'eventEnd', 'modifiedDate', 'scrapeDateUTC', 'Teamid_0', 'TeamName_0', 'sideId_team0', 
          'Teamid_1', 'TeamName_1','sideId_team1', 'bet_side','lgX', 'lgX_league','league', 'lgX_pt','betPeriod', 'bet_stage',   
          'marketId', 'btX', 'bet_type', 'points', 'american_price', 
          'price', 'sourcePrice', 'ImpliedProb%','marketSourceId', 'bookName', 'bookId', 'bookIsActive', 'nyBook', 'sharpBook']
          
          filtered_df= filtered_df.reindex(columns=easiest_to_read_column_order)
          
          #bet_side as interger
          filtered_df["bet_side"] = filtered_df["bet_side"].astype(int)
          
          
          
          
          
          
          
          
          
          #remove games which occurred in the past. 
          filtered_df['eventStart'] = pd.to_datetime(filtered_df['eventStart'])
          filtered_df['scrapeDateUTC'] = pd.to_datetime(filtered_df['scrapeDateUTC'])
          
          # Create boolean mask
          mask = filtered_df["eventStart"] >= filtered_df["scrapeDateUTC"]
          
          filtered_df=filtered_df[mask]
          
          #record the source of the bet
          filtered_df['SourceName'] = "Unabated"
          
          
          #Insert a BetID  (short uuid) for each row
          
          bet_ids = [shortuuid.uuid() for _ in range(len(filtered_df))]
          filtered_df.insert(0,'BetID',bet_ids)
          
          
          
          
          
          
          
          
          
          
          #FILTERED_DF is the raw Unabated Odds. SAVE IT HERE
     else:
          st.write()
