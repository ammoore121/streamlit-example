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
