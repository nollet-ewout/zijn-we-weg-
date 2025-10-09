import streamlit as st
import pandas as pd

# Inladen data zonder rijen te verwijderen
@st.cache_data
def load_data():
    df = pd.read_csv('reislocatie_filter.csv')
    df.columns = df.columns.str.strip()  # verwijder spaties rondom kolomnamen
    # Converteer Budget naar numeriek; niet-converteerbare waarden worden NaN
    df['Budget'] = pd.to_numeric(df['Budget'], errors='coerce')
    return df

data = load_data()

st.title("Ideale Reislocatie Zoeker")

# Vraag 1 met placeholder
duur = st.selectbox('Hoe lang wil je weg?', ['Maak een keuze...'] + sorted(data['Duur'].dropna().unique()))

# Vraag 2: Budget slider verschijnt pas als vraag 1 beantwoord is met echte keuze
if duur != 'Maak een keuze...':
    # Bereken min/max budget op basis van alle niet-NaN waarden in Budget
    min_budget = int(data['Budget'].min())
    max_budget = int(data['Budget'].max())
    budget = st.slider('Wat is je budget? (min - max)', min_value=min_budget, max_value=max_budget, value=(min_budget, max_budget))
else:
    budget = None

# Vraag 3 verschijnt pas als vraag 2 beantwoord is
if budget is not None:
    bestemming = st.selectbox('Op welk continent wil je reizen?', ['Maak een keuze...'] + sorted(data['Bestemming'].dropna().unique()))
else:
    bestemming = 'Maak een keuze...'

# Vraag 4 verschijnt pas als vraag 3 beantwoord is met echte keuze
if bestemming != 'Maak een keuze...':
    reistype = st.selectbox('Wat is het doel van je reis?', ['Maak een keuze...'] + sorted(data['Reistype / Doel'].dropna().unique()))
else:
    reistype = 'Maak een keuze...'

# Vraag 5 verschijnt pas als vraag 4 beantwoord is met echte keuze
if reistype != 'Maak een keuze...':
    seizoen = st.selectbox('In welk seizoen wil je reizen?', ['Maak een keuze...'] + sorted(data['Seizoen'].dropna().unique()))
else:
    seizoen = 'Maak een keuze...'

# Vraag 6 verschijnt pas als vraag 5 beantwoord is met echte keuze
if seizoen != 'Maak een keuze...':
    accommodatie = st.selectbox('Welke type accommodatie wil je?', ['Maak een keuze...'] + sorted(data['Accommodatie'].dropna().unique()))
else:
    accommodatie = 'Maak een keuze...'

# Pas filtering toe, waarbij rijen zonder budget verwijderd worden
if all(selection != 'Maak een keuze...' for selection in [duur, bestemming, reistype, seizoen, accommodatie]) and budget is not None:
    filtered_data = data.dropna(subset=['Budget'])
    filtered_data = filtered_data[
        (filtered_data['Duur'] == duur) &
        (filtered_data['Budget'] >= budget[0]) & (filtered_data['Budget'] <= budget[1]) &
        (filtered_data['Bestemming'] == bestemming) &
        (filtered_data['Reistype / Doel'] == reistype) &
        (filtered_data['Seizoen'] == seizoen) &
        (filtered_data['Accommodatie'] == accommodatie)
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
