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

# --- Cached data loading met 10min TTL ---
@st.cache_data(ttl=600)
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

@st.cache_data(ttl=600)
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

@st.cache_data(ttl=600)
def image_to_base64_cached(image_url):
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        img_bytes = response.content
        encoded = base64.b64encode(img_bytes).decode()
        return f"data:image/jpeg;base64,{encoded}"
    except Exception:
        return None

# --- Filtering functies ---
def filter_travel_in_memory(df, duur_slider, budget_slider, continent, reistype, seizoen, accommodatie, temp_slider, vervoersmiddelen):
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

def filter_restaurants_in_memory(df, keuken, locaties, prijs_range):
    if keuken:
        df = df[df['keuken'].isin(keuken)]
    if locaties:
        df = df[df['locatie'].isin(locaties)]
    if prijs_range:
        df = df[df['prijs'].apply(lambda p: len(p.strip()) >= prijs_range[0] and len(p.strip()) <= prijs_range[1])]
    return df

# --- Kaartweergaves ---
def bestemming_kaartje(row):
    foto_url = row.get('foto', '').strip()
    url = row.get('url', '').strip()
    img_block = ""
    if foto_url:
        img_b64 = image_to_base64_cached(foto_url)
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

def restaurant_kaartje(row):
    foto_url = row.get('foto', '').strip()
    url = row.get('url', '').strip()
    img_block = ""
    if foto_url:
        img_b64 = image_to_base64_cached(foto_url)
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

# --- Plan je dag tab ---
def plan_je_dag_tab(reizen_df, restaurants_df):
    st.header("Plan je ideale dag")

    # Initializeer weekplanning in session_state
    if 'weekplanning' not in st.session_state:
        st.session_state['weekplanning'] = []

    # Kies bestemming
    locaties = sorted(reizen_df['land / regio'].dropna().unique())
    gekozen_locatie = st.selectbox("Kies je bestemming", locaties)

    if gekozen_locatie:
        # Filter restaurants op locatie
        restaurants_locatie = restaurants_df[restaurants_df['locatie'].str.contains(gekozen_locatie, case=False, na=False)]

        # Check of 'maaltijd' kolom bestaat
        if 'maaltijd' in restaurants_locatie.columns:
            ontbijt_restaurants = restaurants_locatie[
                restaurants_locatie['maaltijd'].str.contains("ontbijt", case=False, na=False)
            ]['naam'].tolist()
            lunch_restaurants = restaurants_locatie[
                restaurants_locatie['maaltijd'].str.contains("lunch", case=False, na=False)
            ]['naam'].tolist()
            diner_restaurants = restaurants_locatie[
                restaurants_locatie['maaltijd'].str.contains("diner", case=False, na=False)
            ]['naam'].tolist()
        else:
            ontbijt_restaurants = lunch_restaurants = diner_restaurants = []
            st.warning("De kolom 'maaltijd' ontbreekt in je restaurantgegevens.")

        # Kies restaurants met selectbox
        ontbijt_keuze = st.selectbox("Ontbijt restaurant", ["- geen -"] + ontbijt_restaurants)
        lunch_keuze = st.selectbox("Lunch restaurant", ["- geen -"] + lunch_restaurants)
        diner_keuze = st.selectbox("Diner restaurant", ["- geen -"] + diner_restaurants)

        # Toevoegen knop
        if st.button("Toevoegen aan weekplan"):
            dag = {
                "bestemming": gekozen_locatie,
                "ontbijt": ontbijt_keuze if ontbijt_keuze != "- geen -" else None,
                "lunch": lunch_keuze if lunch_keuze != "- geen -" else None,
                "diner": diner_keuze if diner_keuze != "- geen -" else None
            }
            st.session_state['weekplanning'].append(dag)
            st.success(f"Dag {len(st.session_state['weekplanning'])} toegevoegd!")

        # Visuele overzicht weekplan
        if st.session_state['weekplanning']:
            st.markdown("## Overzicht weekplan")
            for i, dag in enumerate(st.session_state['weekplanning'], start=1):
                st.markdown(f"### Dag {i} - {dag['bestemming']}")
                ontbijt = dag['ontbijt'] or "geen geselecteerd"
                lunch = dag['lunch'] or "geen geselecteerd"
                diner = dag['diner'] or "geen geselecteerd"
                st.markdown(f"Ontbijt: {ontbijt}\nLunch: {lunch}\nDiner: {diner}")

def main():
    if 'needs_refresh' not in st.session_state:
        st.session_state['needs_refresh'] = False

    tab_names = ["Reislocaties", "Restaurants", "Plan je dag"]
    selected_tab = st.sidebar.radio("Selecteer tabblad", tab_names)

    titel = "Ideale " + selected_tab + " Zoeker"
    st.title(titel)

    def on_refresh_click():
        load_travel_data.clear()
        load_restaurants_data.clear()
        st.session_state['needs_refresh'] = True

    col1, col2 = st.columns([8, 1])
    with col1:
        if selected_tab == "Reislocaties":
            st.markdown("### Geselecteerde locaties:")
        elif selected_tab == "Restaurants":
            st.markdown("### Geselecteerde restaurants:")
        else:
            st.markdown("### Plan je ideale dag:")

    with col2:
        st.button("🔄", on_click=on_refresh_click, key="refresh_button")
        st.markdown("""
        <style>
        button[kind=primary] > div[role=button] {
            font-size: 24px;
            background-color: transparent;
            border: none;
            padding: 0;
            margin-left: auto;
            cursor: pointer;
        }
        button[kind=primary]:hover > div[role=button] {
            color: #1e90ff;
            transform: rotate(90deg);
            transition: transform 0.3s ease-in-out;
        }
        </style>
        """, unsafe_allow_html=True)

    if st.session_state['needs_refresh']:
        st.session_state['needs_refresh'] = False
        st.rerun()

    if selected_tab == "Reislocaties":
        data = load_travel_data()
        if data.empty:
            st.warning("Geen reisdata beschikbaar.")
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

        duur_slider = st.sidebar.slider('Hoe lang wil je weg? (dagen)', min_duur, max_duur, (min_duur, max_duur), step=1)
        budget_slider = st.sidebar.slider('Wat is je budget? (min - max)', min_budget, max_budget, (min_budget, max_budget), step=100)
        temp_slider = st.sidebar.slider('Temperatuurbereik (°C)', min_temp, max_temp, (min_temp, max_temp), step=1)
        continent_options = sorted(data['continent'].dropna().unique())
        continent = st.sidebar.multiselect('Op welk continent wil je reizen?', continent_options)
        reistype_options = sorted(data['reistype / doel'].dropna().unique())
        reistype = st.sidebar.multiselect('Wat is het doel van je reis?', reistype_options)
        seizoen_raw_options = data['seizoen'].dropna().unique()
        seizoen_split = set()
        for item in seizoen_raw_options:
            for s in item.split(';'):
                seizoen_split.add(s.strip())
        seizoen_options = sorted(seizoen_split)
        seizoen = st.sidebar.multiselect('In welk seizoen wil je reizen?', seizoen_options)
        accommodatie_options = sorted(data['accommodatie'].dropna().unique())
        accommodatie = st.sidebar.multiselect('Welke type accommodatie wil je?', accommodatie_options)
        vervoersmiddelen = st.sidebar.multiselect('Vervoersmiddel', vervoersmiddelen_options)

        filtered_data = filter_travel_in_memory(data, duur_slider, budget_slider, continent, reistype, seizoen, accommodatie, temp_slider, vervoersmiddelen)

        if not filtered_data.empty:
            for _, row in filtered_data.iterrows():
                bestemming_kaartje(row)
        else:
            st.write("Geen locaties gevonden.")

    elif selected_tab == "Restaurants":
        restaurants = load_restaurants_data()
        if restaurants.empty:
            st.warning("Geen restaurantdata beschikbaar.")
            st.stop()

        keuken_options = sorted(restaurants['keuken'].dropna().unique())
        selected_keuken = st.sidebar.multiselect("Kies type keuken", keuken_options)

        locatie_options = sorted(restaurants['locatie'].dropna().unique())
        selected_locaties = st.sidebar.multiselect("Selecteer locatie(s)", locatie_options)

        prijs_slider = st.sidebar.slider("Prijsniveau (€ - €€€€)", 1, 4, (1, 4), step=1)

        filtered_restaurants = filter_restaurants_in_memory(restaurants, selected_keuken, selected_locaties, prijs_slider)

        if not filtered_restaurants.empty:
            for _, row in filtered_restaurants.iterrows():
                restaurant_kaartje(row)
        else:
            st.write("Geen restaurants gevonden.")

    else:  # Plan je dag tab
        reizen_df = load_travel_data()
        restaurants_df = load_restaurants_data()
        if reizen_df.empty or restaurants_df.empty:
            st.warning("Data niet beschikbaar om je dag te plannen.")
            st.stop()
        plan_je_dag_tab(reizen_df, restaurants_df)

if __name__ == "__main__":
    main()



