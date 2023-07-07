import streamlit as st
import pandas as pd
#the app will reflect save and commits



st.title('Blue Dot :blue[Sports] :)') 


st.write('Hello')


df = pd.DataFrame({
  'first column': [1, 2, 3, 4],
  'second column': [10, 20, 30, 40]
})

df

st.line_chart(df)



st.header('st.button')

if st.button('See Table'):
     df
else:
     st.write()


add_sidebar = st.sidebar.selectbox('My Bets','Place Bet','Test Env')
