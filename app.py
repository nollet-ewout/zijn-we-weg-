import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
import base64
import requests

def get_gsheets_service():
    creds_info = {
        key: st.secrets[key] for key in [
            "type", "project_id", "private_key_id", "client_email", "client_id",
            "auth_uri", "token_uri", "auth_provider_x509_cert_url", "client_x509_cert_url"
        ]
    }
    creds_info["private_key"] = st.secrets["private_key"].replace('\\n', '\n')
    credentials = service_account.Credentials.from_service_account_info(
        creds_info,
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
    )
    return build('sheets', 'v4', credentials=credentials)

@st.cache_data
def load_data_from_gsheets():
    service = get_gsheets_service()
    try:
        res = service.spreadsheets().values().get(
            spreadsheetId=st.secrets["spreadsheet_id"],
            range="Opties!A1:P"
        ).execute()
        values = res.get('values', [])
    except Exception as e:
        st.error(f"Fout bij ophalen van Google Sheets: {e}")
        return pd.DataFrame()

    if not values:
        st.error("Geen data gevonden.")
        return pd.DataFrame()

    num_cols = len(values[0])
    rows = [row + [''] * (num_cols - len(row)) for row in values[1:]]
    df = pd.DataFrame(rows, columns=values[0])
    df.columns = df.columns.str.strip().str.lower()

    for col in ['minimum duur', 'maximum duur', 'budget', 'temperatuur']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    return df

def filter_data(df, duur_slider, budget_slider, continent, reistype, seizoen, accommodatie, temp_slider, vervoersmiddelen):
    df = df.dropna(subset=['budget', 'minimum duur', 'maximum duur'])
    df = df[
        (df['maximum duur'] >= duur_slider[0]) &
        (df['minimum duur'] <= duur_slider[1]) &
        (df['budget'].between(budget_slider[0], budget_slider[1]))
    ]
    if 'temperatuur' in df.columns:
        df = df[df['temperatuur'].between(temp_slider[0], temp_slider[1])]

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

def image_to_base64(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return f"data:image/jpeg;base64,{base64.b64encode(response.content).decode()}"
    except Exception:
        return None

def bestemming_kaartje(row):
    foto_url, url = row.get('foto', '').strip(), row.get('url', '').strip()
    img_block = "<div style='width:200px; height:150px; background:#444; border-radius:8px; float:right; margin-left:30px; margin-top:5px; margin-bottom:5px;'></div>"
    
    if foto_url:
        img_b64 = image_to_base64(foto_url)
        if img_b64:
            img_block = f'<img src="{img_b64}" width="200" style="border-radius:8px; float:right; margin-left:30px; margin-top:5px; margin-bottom:5px;" />'

    naam_html = f'<a href="{url}" target="_blank" style="color:#1e90ff; text-decoration:none;">{row["land / regio"]}</a>' if url \
        else f'<span style="color:#fff; font-weight:bold;">{row["land / regio"]}</span>'

    vervoersmiddel_clean = ', '.join(v.strip() for v in row.get('vervoersmiddel', '').split(';') if v.strip())

    kaart_html = f"""
    <div style='border:1px solid #ddd; border-radius:8px; padding:20px 25px; margin-bottom:15px; box-shadow:2px 2px 8px rgba(0,0,0,0.2); background-color:#18181b; overflow:auto;'>
        {img_block}
        <div style="text-align:left; max-width: calc(100% - 250px);">
            <h3 style='margin-bottom: 10px; margin-top:0; color:#fff;'>{naam_html}</h3>
            <div style='margin-left: 15px; margin-bottom: 10px; color:#ccc; font-style: italic;'>{row.get('opmerking', '')}</div>
            <div style='margin-bottom: 6px; color:#fff;'><b>Prijs:</b> €{row.get('budget', '')}</div>
            <div style='margin-bottom: 6px; color:#fff;'><b>Duur:</b> {row.get('minimum duur', '')} - {row.get('maximum duur', '')} dagen</div>
            <div style='margin-bottom: 6px; color:#fff;'><b>Temperatuur:</b> {row.get('temperatuur', '')} °C</div>
            <div style='margin-bottom: 6px; color:#fff;'><b>Vervoersmiddel:</b> {vervoersmiddel_clean}</div>
        </div>
    </div>
    """
    st.markdown(kaart_html, unsafe_allow_html=True)

def main():
    st.title("Ideale Reislocatie Zoeker")
    data = load_data_from_gsheets()
    if data.empty:
        st.stop()

    min_duur, max_duur = int(data['minimum duur'].min()), int(data['maximum duur'].max())
    min_budget, max_budget = int(data['budget'].min()), int(data['budget'].max())
    min_temp = int(data['temperatuur'].min()) if 'temperatuur' in data.columns else 0
    max_temp = int(data['temperatuur'].max()) if 'temperatuur' in data.columns else 40
    vervoersmiddelen_options = sorted({v.strip() for row in data['vervoersmiddel'].dropna() for v in row.split(';')}) \
        if 'vervoersmiddel' in data.columns else []

    with st.sidebar:
        duur_slider = st.slider('Hoe lang wil je weg? (dagen)', min_duur, max_duur, (min_duur, max_duur))
        budget_slider = st.slider('Wat is je budget? (min - max)', min_budget, max_budget, (min_budget, max_budget), step=100)
        temp_slider = st.slider('Temperatuurbereik (°C)', min_temp, max_temp, (min_temp, max_temp))

        continent = st.multiselect('Continent?', sorted(data['continent'].dropna().unique()))
        reistype = st.multiselect('Reisdoel?', sorted(data['reistype / doel'].dropna().unique()))

        seizoen_split = sorted({s.strip() for item in data['seizoen'].dropna().unique() for s in item.split(';')})
        seizoen = st.multiselect('Seizoen (meerdere mogelijk)', seizoen_split)
        accommodatie = st.multiselect('Accommodatie?', sorted(data['accommodatie'].dropna().unique()))
        vervoersmiddelen = st.multiselect('Vervoersmiddel', vervoersmiddelen_options)

    filtered_data = filter_data(data, duur_slider, budget_slider, continent, reistype, seizoen, accommodatie, temp_slider, vervoersmiddelen)
    st.write("### Geselecteerde locaties:")
    if not filtered_data.empty:
        for _, row in filtered_data.iterrows():
            bestemming_kaartje(row)
    else:
        st.write("Geen locaties gevonden.")

if __name__ == "__main__":
    main()
