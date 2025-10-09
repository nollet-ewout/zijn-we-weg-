import streamlit as st
import pandas as pd

# Inladen data
@st.cache_data
def load_data():
    df = pd.read_csv('reislocatie_filter.csv')
    df.columns = df.columns.str.strip()  # verwijder spaties rondom kolomnamen
    return df

data = load_data()

st.title("Ideale Reislocatie Zoeker")

# Vraag 1 met placeholder
duur = st.selectbox('Hoe lang wil je weg?', ['Maak een keuze...'] + sorted(data['Duur'].unique()))

# Vraag 2 verschijnt pas als vraag 1 beantwoord is met echte keuze
if duur != 'Maak een keuze...':
    bestemming = st.selectbox('Op welk continent wil je reizen?', ['Maak een keuze...'] + sorted(data['Bestemming'].unique()))
else:
    bestemming = 'Maak een keuze...'

# Vraag 3 verschijnt pas als vraag 2 beantwoord is met echte keuze
if bestemming != 'Maak een keuze...':
    reistype = st.selectbox('Wat is het doel van je reis?', ['Maak een keuze...'] + sorted(data['Reistype / Doel'].unique()))
else:
    reistype = 'Maak een keuze...'

# Vraag 4 verschijnt pas als vraag 3 beantwoord is met echte keuze
if reistype != 'Maak een keuze...':
    seizoen = st.selectbox('In welk seizoen wil je reizen?', ['Maak een keuze...'] + sorted(data['Seizoen'].unique()))
else:
    seizoen = 'Maak een keuze...'

# Vraag 5 verschijnt pas als vraag 4 beantwoord is met echte keuze
if seizoen != 'Maak een keuze...':
    accommodatie = st.selectbox('Welke type accommodatie wil je?', ['Maak een keuze...'] + sorted(data['Accommodatie'].unique()))
else:
    accommodatie = 'Maak een keuze...'

# Filteren als alle vragen een echte keuze hebben
if all(selection != 'Maak een keuze...' for selection in [duur, bestemming, reistype, seizoen, accommodatie]):
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
            naam = row['Land / Regio']
            url = row.get('URL', '')  # veiliger dan directe index
            if pd.notna(url) and url.strip() != '':
                st.markdown(f"- [{naam}]({url}) : {row['Opmerking']}")
            else:
                st.write(f"- {naam}: {row['Opmerking']}")
    else:
        st.write("Geen locaties gevonden.")
else:
    st.write("Beantwoord alle vragen om locaties te zien.")
