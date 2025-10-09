import streamlit as st

st.title("Startpagina")

if st.button("Ga naar Applicatie 1"):
    st.markdown("[Klik hier om naar Applicatie 1 te gaan](https://zijnweweg.streamlit.app/)")

if st.button("Ga naar Applicatie 2"):
    st.markdown("[Klik hier om naar Applicatie 2 te gaan](https://zijnweweg-nieuwe-locatie.streamlit.app/)")
