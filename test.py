import streamlit as st
import pandas as pd
import requests
import datetime
import shortuuid
import numpy as np

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

          df_sportsbooks
     else:
          st.write()
