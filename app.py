import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
import base64
import requests

# --- Google Sheets Service Setup ---
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

# --- Load Travel Data ---
@st.cache_data
def load_travel_data():
    service = get_gsheets_service()
    spreadsheet_id = st.secrets["spreadsheet_id"]
    sheet = service.spreadsheets()
    try:
        result = sheet.values().get(spreadsheetId=spreadsheet_id, range="Opties!A1:P").execute()
        values = result.get('values', [])
    except Exception as e:
        st.error(f"Error bij ophalen data van Google Sheets: {e}")
        return pd.DataFrame()
    if not values:
        st.error("Geen data gevonden in Google Sheet.")
        return pd.DataFrame()
    cols = values[0]
    data = values[1:]
    for row in data:
        if len(row) < len(cols):
            row += [''] * (len(cols) - len(row))
    df = pd.DataFrame(data, columns=cols)
    df.columns = df.columns.str.strip().str.lower()
    for col in ['minimum duur', 'maximum duur', 'budget', 'temperatuur']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

# --- Load Restaurants Data ---
@st.cache_data
def load_restaurants_data():
    service = get_gsheets_service()
    spreadsheet_id = st.secrets["spreadsheet_id"]
    sheet = service.spreadsheets()
    try:
        result = sheet.values().get(spreadsheetId=spreadsheet_id, range="Restaurants!A1:G").execute()
        values = result.get('values', [])
    except Exception as e:
        st.error(f"Error bij ophalen restaurantdata: {e}")
        return pd.DataFrame()
    if not values:
        st.error("Geen data gevonden in Restaurants-sheet.")
        return pd.DataFrame()
    cols = values[0]
    data = values[1:]
    for row in data:
        if len(row) < len(cols):
            row += [''] * (len(cols) - len(row))
    df = pd.DataFrame(data, columns=cols)
    df.columns = df.columns.str.strip().str.lower()
    return df

# --- Filtering Travel ---
def filter_travel(df, duur_slider, budget_slider, continent, reistype, seizoen, accommodatie, temp_slider, vervoersmiddelen):
    df = df.dropna(subset=['budget', 'minimum duur', 'maximum duur'])
    df = df[
        (df['maximum duur'] >= duur_slider[0]) &
        (df['minimum duur'] <= duur_slider[1]) &
        (df['budget'] >= budget_slider[0]) &
        (df['budget'] <= budget_slider[1])
    ]
    if 'temperatuur' in df.columns:
        df = df[(df['temperatuur'] >= temp_slider[0]) & (df['temperatuur'] <= temp_slider[1])]
    if continent:
        df = df[df['continent'].isin(continent)]
    if reistype:
        df = df[df['reistype / doel'].isin(reistype)]
    if seizoen:
        df = df[df['seizoen'].apply(lambda x: any(s in [s.strip() for s in x.split(';')] for s in seizoen))]
    if accommodatie:
        df = df[df['accommodatie'].isin(accommodatie)]
    if vervoersmiddelen:
        df = df[df['vervoersmiddel'].apply(lambda x: any(vm.strip() in x.split(';') for vm in vervoersmiddelen))]
    return df

# --- Filtering Restaurants ---
def filter_restaurants(df, keuken, locatie, prijs_range):
    if keuken:
        df = df[df['keuken'].isin(keuken)]
    if locatie:
        df = df[df['locatie'].str.contains(locatie, case=False, na=False)]
    if prijs_range:
        df = df[df['prijs'].apply(lambda p: len(p.strip()) >= prijs_range[0] and len(p.strip()) <= prijs_range[1])]
    return df

# --- Image to Base64 helper ---
def image_to_base64(image_url):
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        img_bytes = response.content
        encoded = base64.b64encode(img_bytes).decode()
        return f"data:image/jpeg;base64,{encoded}"
    except Exception:
        return None

# --- Travel Card ---
def bestemming_kaartje(row):
    foto_url = row.get('foto', '').strip()
    url = row.get('url', '').strip()
    img_block = ""
    if foto_url:
        img_b64 = image_to_base64(foto_url)
        if img_b64:
            img_block = f'<img src="{img_b64}" width="200" style="border-radius:8px; float:right; margin-left:30px;" />'
        else:
            img_block = "<div style='width:200px; height:150px; background:#444; border-radius:8px; float:right;'></div>"
    else:
        img_block = "<div style='width:200px; height:150px; background:#444; border-radius:8px; float:right;'></div>"
    naam_html = f'<a href="{url}" target="_blank" style="color:#1e90ff; text-decoration:none;">{row["land / regio"]}</a>' if url else f'<span style="color:#fff; font-weight:bold;">{row["land / regio"]}</span>'
    vervoersmiddel_clean = ', '.join([v.strip() for v in row.get('vervoersmiddel', '').split(';') if v.strip()])
    kaart_html = f"""
    <div style='border:1px solid #ddd; border-radius:8px; padding:20px; margin-bottom:15px; box-shadow:2px 2px 8px rgba(0,0,0,0.2); background-color:#18181b; overflow:auto;'>
        {img_block}
        <div style="text-align:left; max-width: calc(100% - 250px);">
            <h3 style='margin-bottom:10px; color:#fff;'>{naam_html}</h3>
            <div style='color:#ccc; font-style:italic;'>{row.get('opmerking', '') or ''}</div>
            <div style='color:#fff;'><b>Prijs:</b> €{row.get('budget', '')}</div>
            <div style='color:#fff;'><b>Duur:</b> {row.get('minimum duur', '')} - {row.get('maximum duur', '')} dagen</div>
            <div style='color:#fff;'><b>Temperatuur:</b> {row.get('temperatuur', '')} °C</div>
            <div style='color:#fff;'><b>Vervoersmiddel:</b> {vervoersmiddel_clean}</div>
        </div>
    </div>
    """
    st.markdown(kaart_html, unsafe_allow_html=True)

# --- Restaurant Card ---
def restaurant_kaartje(row):
    foto_url = row.get('foto', '').strip()
    url = row.get('url', '').strip()
    img_block = ""
    if foto_url:
        img_b64 = image_to_base64(foto_url)
        if img_b64:
            img_block = f'<img src="{img_b64}" width="200" style="border-radius:8px; float:right; margin-left:30px;" />'
        else:
            img_block = "<div style='width:200px; height:150px; background:#444; border-radius:8px; float:right;'></div>"
    else:
        img_block = "<div style='width:200px; height:150px; background:#444; border-radius:8px; float:right;'></div>"
    naam_html = f'<a href="{url}" target="_blank" style="color:#1e90ff; text-decoration:none;">{row["naam"]}</a>' if url else f'<span style="color:#fff; font-weight:bold;">{row["naam"]}</span>'
    kaart_html = f"""
    <div style='border:1px solid #ddd; border-radius:8px; padding:20px; margin-bottom:15px; box-shadow:2px 2px 8px rgba(0,0,0,0.2); background-color:#18181b; overflow:auto;'>
        {img_block}
        <div style="text-align:left; max-width: calc(100% - 250px);">
            <h3 style='margin-bottom:10px; color:#fff;'>{naam_html}</h3>
            <div style='color:#fff;'><b>Keuken:</b> {row.get('keuken', '')}</div>
            <div style='color:#fff;'><b>Prijs:</b> {row.get('prijs', '')}</div>
            <div style='color:#fff;'><b>Locatie:</b> {row.get('locatie', '')}</div>
            <div style='color:#ccc; font-style:italic;'>{row.get('opmerking', '') or ''}</div>
        </div>
    </div>
    """
    st.markdown(kaart_html, unsafe_allow_html=True)

# --- Main Function ---
def main():
    st.title("Ideale Reislocatie & Restaurant Zoeker")

    tab1, tab2 = st.tabs(["Reislocaties", "Restaurants"])

    with tab1:
        data = load_travel_data()
        if data.empty:
            st.stop()

        min_duur = int(data['minimum duur'].min())
        max_duur = int(data['maximum duur'].max())
        min_budget = int(data['budget'].min())
        max_budget = int(data['budget'].max())
        min_temp = int(data['temperatuur'].min()) if 'temperatuur' in data.columns else 0
        max_temp = int(data['temperatuur'].max()) if 'temperatuur' in data.columns else 40

        vervoersmiddelen_options = sorted(set(
            v.strip()
            for row in data['vervoersmiddel'].dropna()
            for v in row.split(';')
        )) if 'vervoersmiddel' in data.columns else []

        with st.sidebar:
            duur_slider = st.slider('Hoe lang wil je weg? (dagen)', min_duur, max_duur, (min_duur, max_duur), step=1)
            budget_slider = st.slider('Wat is je budget? (min - max)', min_budget, max_budget, (min_budget, max_budget), step=100)
            temp_slider = st.slider('Temperatuurbereik (°C)', min_temp, max_temp, (min_temp, max_temp), step=1)
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
            seizoen = st.multiselect('In welk seizoen wil je reizen?', seizoen_options)
            accommodatie_options = sorted(data['accommodatie'].dropna().unique())
            accommodatie = st.multiselect('Welke type accommodatie wil je?', accommodatie_options)
            vervoersmiddelen = st.multiselect('Vervoersmiddel', vervoersmiddelen_options)
        
        filtered_data = filter_travel(data, duur_slider, budget_slider, continent, reistype, seizoen, accommodatie, temp_slider, vervoersmiddelen)
        st.write("### Geselecteerde locaties:")
        if not filtered_data.empty:
            for _, row in filtered_data.iterrows():
                bestemming_kaartje(row)
        else:
            st.write("Geen locaties gevonden.")

    with tab2:
        restaurants = load_restaurants_data()
        if restaurants.empty:
            st.stop()

        keuken_options = sorted(restaurants['keuken'].dropna().unique())
        selected_keuken = st.multiselect("Kies type keuken", keuken_options)
        locatie_input = st.text_input("Voer een locatie in (stad of regio)")
        prijs_slider = st.slider("Prijsniveau (€ - €€€€)", 1, 4, (1, 4), step=1)

        filtered_restaurants = filter_restaurants(restaurants, selected_keuken, locatie_input, prijs_slider)
        st.write("### Geselecteerde restaurants:")
        if not filtered_restaurants.empty:
            for _, row in filtered_restaurants.iterrows():
                restaurant_kaartje(row)
        else:
            st.write("Geen restaurants gevonden.")

if __name__ == "__main__":
    main()
