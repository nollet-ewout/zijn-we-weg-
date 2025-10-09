import streamlit as st

st.title("Startpagina")

# HTML-knop met link
button_html_1 = """
<a href="https://jouw-eerste-applicatie.nl" target="_blank" style="
    background-color: #4CAF50; 
    color: white; 
    padding: 15px 30px; 
    text-align: center; 
    text-decoration: none; 
    display: inline-block; 
    font-size: 18px; 
    border-radius: 8px;
    cursor: pointer;">Applicatie 1</a>
"""

button_html_2 = """
<a href="https://jouw-tweede-applicatie.nl" target="_blank" style="
    background-color: #4CAF50; 
    color: white; 
    padding: 15px 30px; 
    text-align: center; 
    text-decoration: none; 
    display: inline-block; 
    font-size: 18px; 
    border-radius: 8px;
    cursor: pointer;">Applicatie 2</a>
"""

st.markdown(button_html_1, unsafe_allow_html=True)
st.markdown(button_html_2, unsafe_allow_html=True)
