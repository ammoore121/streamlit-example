import streamlit as st
import pandas as pd
import requests
import datetime
import numpy as np
import uuid #note i have to use uuid here instead of shortuuid

#the app will reflect save and commits



st.title('Blue Dot :blue[Sports] :)') 


df = pd.DataFrame({
  'first column': [1, 2, 3, 4],
  'second column': [10, 20, 30, 40]
})

add_sidebar = st.sidebar.selectbox('Menu',('Place Bet','My Bets','My Bank','Test Env'))

if add_sidebar == "Test Env":
  df
  st.line_chart(df)
  if st.button('See TN'):
     st.write("##:red[These Nuts]")
  else:
     st.write()
  
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
          df_MainLineOdds['bet_stage'] = df_MainLineOdds['lgX'].apply(lambda x: x.split(':', 2)[2] if len(x.split(':', 2)) > 2 else np.nan)
          df_MainLineOdds['siX_side']= df_MainLineOdds['siX'].str.get(2)
          df_MainLineOdds['scrapeDateUTC'] = datetime.datetime.utcnow().isoformat()
          # ISO 8601 format for scrapedate is easiest to read in csv
          
          df_MainLineOdds

     else:
          st.write()
