import streamlit as st
import pandas as pd

# Inladen data
@st.cache_data
def load_data():
    return pd.read_csv('reislocatie_filter.csv')

data = load_data()

st.title("Ideale Reislocatie Zoeker")

# Filters
duur = st.selectbox('Hoe lang wil je weg?', sorted(data['Duur'].unique()))
bestemming = st.selectbox('Op welk continent wil je reizen?', sorted(data['Bestemming'].unique()))
reistype = st.selectbox('Wat is het doel van je reis?', sorted(data['Reistype / Doel'].unique()))
seizoen = st.selectbox('In welk seizoen wil je reizen?', sorted(data['Seizoen'].unique()))
accommodatie = st.selectbox('Welke type accommodatie wil je?', sorted(data['Accommodatie'].unique()))

# Filteren
filtered_data = data[
    (data['Duur'] == duur) &
    (data['Bestemming'] == bestemming) &
    (data['Reistype / Doel'] == reistype) &
    (data['Seizoen'] == seizoen) &
    (data['Accommodatie'] == accommodatie)
]

st.write("### Geselecteerde locaties:")
if not filtered_data.empty:
    for _, row in filtered_data.iterrows():
        st.write(f"- {row['Land / Regio']}: {row['Opmerking']}")
else:
    st.write("Geen locaties gevonden.")

