import streamlit as st
import pandas as pd
#the app will reflect save and commits



st.title('Blue Dot :blue[Sports] :)') 


df = pd.DataFrame({
  'first column': [1, 2, 3, 4],
  'second column': [10, 20, 30, 40]
})

add_sidebar = st.sidebar.selectbox('Menu',('Place Bet','My Bets','My Bank','Test Env'))

if add_sidebar == "Test Env":
  df = pd.DataFrame({
  'first column': [1, 2, 3, 4],
  'second column': [10, 20, 30, 40]})
  df
  st.line_chart(df)
  
  st.button('Click for TN')
       st.write('##:red[These Nuts])'
else:
  st.write()
