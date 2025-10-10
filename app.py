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

# Continent multiselect
continent_options = sorted(data['continent'].dropna().unique())
continent = st.multiselect('Op welk continent wil je reizen?', continent_options)

# Reistype / Doel multiselect (verschijnt pas als continent(s) gekozen)
if continent:
    reistype_options = sorted(data['reistype / doel'].dropna().unique())
    reistype = st.multiselect('Wat is het doel van je reis?', reistype_options)
else:
    reistype = []

# Seizoen multiselect (verschijnt pas als reistype(s) gekozen)
if reistype:
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

# Accommodatie multiselect (verschijnt pas als seizoen(s) gekozen)
if seizoen:
    accommodatie_options = sorted(data['accommodatie'].dropna().unique())
    accommodatie = st.multiselect('Welke type accommodatie wil je?', accommodatie_options)
else:
    accommodatie = []

# Filteren op basis van alle keuzes
if continent and reistype and seizoen and accommodatie:
    filtered_data = data.dropna(subset=['budget', 'minimum duur', 'maximum duur'])
    filtered_data = filtered_data[
        (filtered_data['budget'] >= budget[0]) & (filtered_data['budget'] <= budget[1]) &
        (filtered_data['continent'].isin(continent)) &
        (filtered_data['reistype / doel'].isin(reistype)) &
        (filtered_data['seizoen'].apply(lambda x: any(s in [s.strip() for s in x.split(';')] for s in seizoen))) &
        (filtered_data['accommodatie'].isin(accommodatie)) &
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
