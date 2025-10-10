import streamlit as st
import pandas as pd

# Inladen data met verwerking van minimale en maximale duur
@st.cache_data
def load_data():
    df = pd.read_csv('reislocatie_filter.csv')
    # Kolomnamen strippen en lowercase maken
    df.columns = df.columns.str.strip().str.lower()
    
    # Zorg dat duurtijden numeriek zijn
    df['minimum duur'] = pd.to_numeric(df['minimum duur'], errors='coerce')
    df['maximum duur'] = pd.to_numeric(df['maximum duur'], errors='coerce')

    # Zet 'budget' om naar numeriek, foute waarden worden NaN
    df['budget'] = pd.to_numeric(df['budget'], errors='coerce')

    return df

data = load_data()

st.title("Ideale Reislocatie Zoeker")

# Duur slider gebaseerd op minimum en maximum duur in dataset
min_duur = int(data['minimum duur'].min())
max_duur = int(data['maximum duur'].max())
duur_slider = st.slider(
    'Hoe lang wil je weg? (dagen)', 
    min_value=min_duur, 
    max_value=max_duur, 
    value=(min_duur, max_duur),
    step=1
)

# Budget slider
min_budget = int(data['budget'].min())
max_budget = int(data['budget'].max())
budget = st.slider(
    'Wat is je budget? (min - max)', 
    min_value=min_budget, 
    max_value=max_budget, 
    value=(min_budget, max_budget), 
    step=100
)

# Continent selectbox (vervanging voor bestemming)
continent_options = sorted(data['continent'].dropna().unique())
continent = st.selectbox('Op welk continent wil je reizen?', ['Maak een keuze...'] + continent_options)

# Reistype / Doel selectbox (verschijnt pas als continent gekozen)
if continent != 'Maak een keuze...':
    reistype_options = sorted(data['reistype / doel'].dropna().unique())
    reistype = st.selectbox('Wat is het doel van je reis?', ['Maak een keuze...'] + reistype_options)
else:
    reistype = 'Maak een keuze...'

# Seizoen multiselect (meerdere opties selecteerbaar)
if reistype != 'Maak een keuze...':
    seizoen_raw_options = data['seizoen'].dropna().unique()
    seizoen_split = set()
    for item in seizoen_raw_options:
        for s in item.split(';'):
            seizoen_split.add(s.strip())
    seizoen_options = sorted(seizoen_split)
    
    seizoen = st.multiselect(
        'In welk seizoen wil je reizen? (Meerdere mogelijk)', 
        options=seizoen_options
    )
else:
    seizoen = []

# Accommodatie selectbox (verschijnt pas als seizoen gekozen)
if seizoen:
    accommodatie_options = sorted(data['accommodatie'].dropna().unique())
    accommodatie = st.selectbox('Welke type accommodatie wil je?', ['Maak een keuze...'] + accommodatie_options)
else:
    accommodatie = 'Maak een keuze...'

# Filteren op basis van alle keuzes
if all(selection != 'Maak een keuze...' for selection in [continent, reistype, accommodatie]) and seizoen:
    filtered_data = data.dropna(subset=['budget', 'minimum duur', 'maximum duur'])
    filtered_data = filtered_data[
        (filtered_data['budget'] >= budget[0]) & (filtered_data['budget'] <= budget[1]) &
        (filtered_data['continent'] == continent) &
        (filtered_data['reistype / doel'] == reistype) &
        (filtered_data['seizoen'].apply(lambda x: any(s in [s.strip() for s in x.split(';')] for s in seizoen))) &
        (filtered_data['accommodatie'] == accommodatie) &
        (filtered_data['maximum duur'] >= duur_slider[0]) &  
        (filtered_data['minimum duur'] <= duur_slider[1])    
    ]

    st.write("### Geselecteerde locaties:")
    if not filtered_data.empty:
        for _, row in filtered_data.iterrows():
            naam = row['land / regio']
            url = row.get('url', '')
            if pd.notna(url) and url.strip() != '':
                st.markdown(f"- [{naam}]({url}) : {row['opmerking']}")
            else:
                st.write(f"- {naam}: {row['opmerking']}")
    else:
        st.write("Geen locaties gevonden.")
else:
    st.write("Beantwoord alle vragen om locaties te zien.")
