import streamlit as st
import pandas as pd

# Data laden met minimale verwerking
@st.cache_data
def load_data():
    df = pd.read_csv('reislocatie_filter.csv')
    # Kolomnamen strippen en lowercase maken
    df.columns = df.columns.str.strip().str.lower()
    
    # Duurtijden en budget omzetten naar numeriek
    df['minimum duur'] = pd.to_numeric(df['minimum duur'], errors='coerce')
    df['maximum duur'] = pd.to_numeric(df['maximum duur'], errors='coerce')
    df['budget'] = pd.to_numeric(df['budget'], errors='coerce')

    return df

data = load_data()

# Debug: kijk kolomnamen
st.write("Kolomnamen in dataset:", data.columns.tolist())

st.title("Ideale Reislocatie Zoeker")

# Duur slider
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

# Reistype / Doel multiselect
if continent:
    reistype_options = sorted(data['reistype / doel'].dropna().unique())
    reistype = st.multiselect('Wat is het doel van je reis?', reistype_options)
else:
    reistype = []

# Seizoen multiselect
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

# Accommodatie multiselect
if seizoen:
    accommodatie_options = sorted(data['accommodatie'].dropna().unique())
    accommodatie = st.multiselect('Welke type accommodatie wil je?', accommodatie_options)
else:
    accommodatie = []

# Filteren op basis van keuzes (optioneel per filter)
filtered_data = data.dropna(subset=['budget', 'minimum duur', 'maximum duur'])

filtered_data = filtered_data[
    (filtered_data['maximum duur'] >= duur_slider[0]) &
    (filtered_data['minimum duur'] <= duur_slider[1])
]

filtered_data = filtered_data[
    (filtered_data['budget'] >= budget[0]) &
    (filtered_data['budget'] <= budget[1])
]

if continent:
    filtered_data = filtered_data[filtered_data['continent'].isin(continent)]

if reistype:
    filtered_data = filtered_data[filtered_data['reistype / doel'].isin(reistype)]

if seizoen:
    filtered_data = filtered_data[
        filtered_data['seizoen'].apply(lambda x: any(s in [s.strip() for s in x.split(';')] for s in seizoen))
    ]

if accommodatie:
    filtered_data = filtered_data[filtered_data['accommodatie'].isin(accommodatie)]

# Resultaten tonen
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
