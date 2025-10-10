import streamlit as st
import pandas as pd

# Inladen data met verwerking van minimale en maximale duur
@st.cache_data
def load_data():
    df = pd.read_csv('reislocatie_filter.csv')
    df.columns = df.columns.str.strip()  # verwijder spaties rondom kolomnamen
    
    # Zorg dat duurtijden numeriek zijn
    df['Minimum Duur'] = pd.to_numeric(df['Minimum Duur'], errors='coerce')
    df['Maximum Duur'] = pd.to_numeric(df['Maximum Duur'], errors='coerce')

    # Zet 'Budget' om naar numeriek, foute waarden worden NaN
    df['Budget'] = pd.to_numeric(df['Budget'], errors='coerce')

    return df

data = load_data()

st.title("Ideale Reislocatie Zoeker")

# Duur slider gebaseerd op minimum en maximum duur in dataset
min_duur = int(data['Minimum Duur'].min())
max_duur = int(data['Maximum Duur'].max())
duur_slider = st.slider(
    'Hoe lang wil je weg? (dagen)', 
    min_value=min_duur, 
    max_value=max_duur, 
    value=(min_duur, max_duur),
    step=1
)

# Budget slider
min_budget = int(data['Budget'].min())
max_budget = int(data['Budget'].max())
budget = st.slider(
    'Wat is je budget? (min - max)', 
    min_value=min_budget, 
    max_value=max_budget, 
    value=(min_budget, max_budget), 
    step=100
)

# Bestemming selectbox
bestemming_options = sorted(data['Land / Regio'].dropna().unique())
bestemming = st.selectbox('Op welk continent wil je reizen?', ['Maak een keuze...'] + bestemming_options)

# Reistype / Doel selectbox (verschijnt pas als bestemming gekozen)
if bestemming != 'Maak een keuze...':
    reistype_options = sorted(data['Reistype / Doel'].dropna().unique())
    reistype = st.selectbox('Wat is het doel van je reis?', ['Maak een keuze...'] + reistype_options)
else:
    reistype = 'Maak een keuze...'

# Seizoen selectbox (verschijnt pas als reistype gekozen)
if reistype != 'Maak een keuze...':
    seizoen_raw_options = data['Seizoen'].dropna().unique()
    # Om unieke individuele seizoenen te krijgen uit gefuseerde strings:
    seizoen_split = set()
    for item in seizoen_raw_options:
        for s in item.split(';'):
            seizoen_split.add(s.strip())
    seizoen_options = sorted(seizoen_split)
    seizoen = st.selectbox('In welk seizoen wil je reizen?', ['Maak een keuze...'] + seizoen_options)
else:
    seizoen = 'Maak een keuze...'

# Accommodatie selectbox (verschijnt pas als seizoen gekozen)
if seizoen != 'Maak een keuze...':
    accommodatie_options = sorted(data['Accommodatie'].dropna().unique())
    accommodatie = st.selectbox('Welke type accommodatie wil je?', ['Maak een keuze...'] + accommodatie_options)
else:
    accommodatie = 'Maak een keuze...'

# Filteren op basis van alle keuzes
if all(selection != 'Maak een keuze...' for selection in [bestemming, reistype, seizoen, accommodatie]):
    filtered_data = data.dropna(subset=['Budget', 'Minimum Duur', 'Maximum Duur'])
    filtered_data = filtered_data[
        (filtered_data['Budget'] >= budget[0]) & (filtered_data['Budget'] <= budget[1]) &
        (filtered_data['Land / Regio'] == bestemming) &
        (filtered_data['Reistype / Doel'] == reistype) &
        # aangepaste check op seizoen met splitsing
        (filtered_data['Seizoen'].apply(lambda x: seizoen in [s.strip() for s in x.split(';')])) &
        (filtered_data['Accommodatie'] == accommodatie) &
        (filtered_data['Maximum Duur'] >= duur_slider[0]) &  
        (filtered_data['Minimum Duur'] <= duur_slider[1])    
    ]

    st.write("### Geselecteerde locaties:")
    if not filtered_data.empty:
        for _, row in filtered_data.iterrows():
            naam = row['Land / Regio']
            url = row.get('URL', '')
            if pd.notna(url) and url.strip() != '':
                st.markdown(f"- [{naam}]({url}) : {row['Opmerking']}")
            else:
                st.write(f"- {naam}: {row['Opmerking']}")
    else:
        st.write("Geen locaties gevonden.")
else:
    st.write("Beantwoord alle vragen om locaties te zien.")
