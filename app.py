import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build

def get_gsheets_service():
    credentials_info = {
        "type": "service_account",
        "project_id": st.secrets["project_id"],
        "private_key_id": st.secrets["private_key_id"],
        "private_key": st.secrets["private_key"].replace('\\n', '\n'),
        "client_email": st.secrets["client_email"],
        "client_id": st.secrets["client_id"],
        "auth_uri": st.secrets["auth_uri"],
        "token_uri": st.secrets["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["client_x509_cert_url"]
    }
    credentials = service_account.Credentials.from_service_account_info(
        credentials_info,
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
    )
    service = build('sheets', 'v4', credentials=credentials)
    return service

@st.cache_data
def load_data_from_gsheets():
    service = get_gsheets_service()
    spreadsheet_id = st.secrets["spreadsheet_id"]
    sheet = service.spreadsheets()

    try:
        result = sheet.values().get(spreadsheetId=spreadsheet_id, range="Opties!A1:L").execute()
        values = result.get('values', [])
    except Exception as e:
        st.error(f"Error bij ophalen data van Google Sheets: {e}")
        return pd.DataFrame()

    if not values:
        st.error("Geen data gevonden in Google Sheet.")
        return pd.DataFrame()

    df = pd.DataFrame(values[1:], columns=values[0])
    df.columns = df.columns.str.strip().str.lower()

    for col in ['minimum duur', 'maximum duur', 'budget']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    return df

def filter_data(df, duur_slider, budget_slider, continent, reistype, seizoen, accommodatie):
    df = df.dropna(subset=['budget', 'minimum duur', 'maximum duur'])
    df = df[
        (df['maximum duur'] >= duur_slider[0]) &
        (df['minimum duur'] <= duur_slider[1]) &
        (df['budget'] >= budget_slider[0]) &
        (df['budget'] <= budget_slider[1])
    ]

    if continent:
        df = df[df['continent'].isin(continent)]

    if reistype:
        df = df[df['reistype / doel'].isin(reistype)]

    if seizoen:
        df = df[df['seizoen'].apply(lambda x: any(s in [s.strip() for s in x.split(';')] for s in seizoen))]

    if accommodatie:
        df = df[df['accommodatie'].isin(accommodatie)]

    return df

def bestemming_kaartje(row):
    col1, col2 = st.columns([1, 2])
    with col1:
        if pd.notna(row.get('foto')) and row['foto'].strip() != '':
            st.image(row['foto'], width=120)
        else:
            st.write("Geen foto beschikbaar")
    with col2:
        st.markdown(f"### {row['land / regio']}")
        uitleg = row.get('opmerking', '') or ''
        st.write(uitleg)
        
        prijs = row.get('budget')
        if pd.notna(prijs):
            st.markdown(f"**Prijs:** €{prijs}")
        
        duur_min = row.get('minimum duur')
        duur_max = row.get('maximum duur')
        if pd.notna(duur_min) and pd.notna(duur_max):
            if duur_min == duur_max:
                st.markdown(f"**Duur:** {duur_min} dagen")
            else:
                st.markdown(f"**Duur:** {duur_min} - {duur_max} dagen")

def main():
    st.title("Ideale Reislocatie Zoeker")

    data = load_data_from_gsheets()
    if data.empty:
        st.stop()

    min_duur = int(data['minimum duur'].min())
    max_duur = int(data['maximum duur'].max())
    min_budget = int(data['budget'].min())
    max_budget = int(data['budget'].max())

    with st.sidebar:
        duur_slider = st.slider('Hoe lang wil je weg? (dagen)', min_duur, max_duur, (min_duur, max_duur), step=1)
        budget_slider = st.slider('Wat is je budget? (min - max)', min_budget, max_budget, (min_budget, max_budget), step=100)

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

    filtered_data = filter_data(data, duur_slider, budget_slider, continent, reistype, seizoen, accommodatie)

    st.write("### Geselecteerde locaties:")

    if not filtered_data.empty:
        for _, row in filtered_data.iterrows():
            with st.container():
                st.markdown(
                    """
                    <div style='border:1px solid #ddd; border-radius:8px; padding:15px; margin-bottom:15px; box-shadow:2px 2px 8px rgba(0,0,0,0.1);'>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                bestemming_kaartje(row)
    else:
        st.write("Geen locaties gevonden.")

if __name__ == "__main__":
    main()
