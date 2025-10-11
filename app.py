import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Google Sheets koppeling via Streamlit secrets
def load_data_from_gsheets():
    secrets = st.secrets["google_service_account"]
    spreadsheet_id = st.secrets["spreadsheet_id"]

    credentials = service_account.Credentials.from_service_account_info(
        secrets,
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
    )
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()

    # Haal data op uit het tabblad 'Sheet1'
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range="Sheet1").execute()
    values = result.get('values', [])

    if not values:
        st.error("Geen data gevonden in Google Sheet.")
        return pd.DataFrame()  # lege df

    # Eerste rij als kolomnamen gebruiken
    df = pd.DataFrame(values[1:], columns=values[0])

    # Omzetten van kolommen naar juiste typen
    df.columns = df.columns.str.strip().str.lower()
    numeric_cols = ['minimum duur', 'maximum duur', 'budget']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    return df

data = load_data_from_gsheets()
if data.empty:
    st.stop()

st.title("Ideale Reislocatie Zoeker")

# Filter widgets
min_duur = int(data['minimum duur'].min())
max_duur = int(data['maximum duur'].max())
duur_slider = st.slider(
    'Hoe lang wil je weg? (dagen)',
    min_value=min_duur,
    max_value=max_duur,
    value=(min_duur, max_duur),
    step=1
)

min_budget = int(data['budget'].min())
max_budget = int(data['budget'].max())
budget = st.slider(
    'Wat is je budget? (min - max)',
    min_value=min_budget,
    max_value=max_budget,
    value=(min_budget, max_budget),
    step=100
)

continent_options = sorted(data['continent'].dropna().unique())
continent = st.multiselect('Op welk continent wil je reizen?', continent_options)

reistype_options = sorted(data['reistype / doel'].dropna().unique())
reistype = st.multiselect('Wat is het doel van je reis?', reistype_options)

seizoen_raw_options = data['seizoen'].dropna().unique()
seizoen_split = set()
for item in seizoen_raw_options:
    for s in item.split(';'):
        seizoen_split.add(s.strip())
seizoen_options = sorted(seizoen_split)
seizoen = st.multiselect('In welk seizoen wil je reizen? (Meerdere mogelijk)', seizoen_options)

accommodatie_options = sorted(data['accommodatie'].dropna().unique())
accommodatie = st.multiselect('Welke type accommodatie wil je?', accommodatie_options)

# Filteren
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
            st.markdown(f"- [{naam}]({url}) : {row.get('opmerking', '')}")
        else:
            st.write(f"- {naam}: {row.get('opmerking', '')}")
else:
    st.write("Geen locaties gevonden.")
