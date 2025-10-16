import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
import base64
import requests
from fpdf import FPDF
import io

# --- Google Sheets API setup ---
def get_gsheets_service():
    creds_info = {
        "type": "service_account",
        "project_id": st.secrets["project_id"],
        "private_key_id": st.secrets["private_key_id"],
        "private_key": st.secrets["private_key"].replace("\\n", "\n"),
        "client_email": st.secrets["client_email"],
        "client_id": st.secrets["client_id"],
        "auth_uri": st.secrets["auth_uri"],
        "token_uri": st.secrets["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["client_x509_cert_url"]
    }
    creds = service_account.Credentials.from_service_account_info(creds_info, scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"])
    return build('sheets', 'v4', credentials=creds)

@st.cache_data(ttl=600)
def load_travel_data():
    service = get_gsheets_service()
    sheet_id = st.secrets["spreadsheet_id"]
    try:
        result = service.spreadsheets().values().get(spreadsheetId=sheet_id, range='Opties!A1:P').execute()
        values = result.get('values', [])
    except Exception as e:
        st.error(f"Fout bij ophalen reizen data: {e}")
        return pd.DataFrame()
    if not values:
        st.error("Geen reizen data gevonden in Google Sheets")
        return pd.DataFrame()

    cols = values[0]
    data = values[1:]
    for row in data:
        if len(row) < len(cols):
            row += ['']*(len(cols)-len(row))
    df = pd.DataFrame(data, columns=cols)
    df.columns = df.columns.str.strip().str.lower()
    for col in ['minimum duur','maximum duur','budget','temperatuur']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

@st.cache_data(ttl=600)
def load_restaurants_data():
    service = get_gsheets_service()
    sheet_id = st.secrets["spreadsheet_id"]
    try:
        result = service.spreadsheets().values().get(spreadsheetId=sheet_id, range='Restaurants!A1:G').execute()
        values = result.get('values', [])
    except Exception as e:
        st.error(f"Fout bij ophalen restaurant data: {e}")
        return pd.DataFrame()
    if not values:
        st.error("Geen restaurant data gevonden in Google Sheets")
        return pd.DataFrame()

    cols = values[0]
    data = values[1:]
    for row in data:
        if len(row) < len(cols):
            row += ['']*(len(cols)-len(row))
    df = pd.DataFrame(data, columns=cols)
    df.columns = df.columns.str.strip().str.lower()
    return df

# base64 encoding image helper
@st.cache_data(ttl=600)
def image_to_base64_cached(image_url):
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        return "data:image/jpeg;base64," + base64.b64encode(response.content).decode()
    except Exception:
        return None

# filters
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

def filter_restaurants(df, keuken, locaties, prijs_range):
    if keuken:
        df = df[df['keuken'].isin(keuken)]
    if locaties:
        df = df[df['locatie'].isin(locaties)]
    if prijs_range:
        df = df[df['prijs'].apply(lambda p: len(p.strip()) >= prijs_range[0] and len(p.strip()) <= prijs_range[1])]
    return df

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

    if 'weekplanning' not in st.session_state:
        st.session_state['weekplanning'] = []

    locaties = sorted(reizen_df['land / regio'].dropna().unique())
    gekozen_locatie = st.selectbox("Kies je bestemming", locaties)

    if gekozen_locatie:
        restaurants_locatie = restaurants_df[restaurants_df['locatie'].str.contains(gekozen_locatie, case=False, na=False)]

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

        ontbijt_keuze = st.selectbox("Ontbijt restaurant", ["- geen -"] + ontbijt_restaurants)
        lunch_keuze = st.selectbox("Lunch restaurant", ["- geen -"] + lunch_restaurants)
        diner_keuze = st.selectbox("Diner restaurant", ["- geen -"] + diner_restaurants)

        if st.button("Toevoegen aan weekplanning"):
            dag = {
                "bestemming": gekozen_locatie,
                "ontbijt": ontbijt_keuze if ontbijt_keuze != "- geen -" else "",
                "lunch": lunch_keuze if lunch_keuze != "- geen -" else "",
                "diner": diner_keuze if diner_keuze != "- geen -" else ""
            }
            st.session_state.weekplanning.append(dag)
            st.success(f"Dag {len(st.session_state.weekplanning)} succesvol toegevoegd!")

        if st.session_state.weekplanning:
            st.markdown("## Overzicht weekplanning")
            for i, dag in enumerate(st.session_state.weekplanning, 1):
                st.markdown(f"### Dag {i} - Bestemming: {dag['bestemming']}")
                st.markdown(f"Ontbijt: {dag['ontbijt']}  \nLunch: {dag['lunch']}  \nDiner: {dag['diner']}")

            if st.button("Exporteer weekplanning naar PDF"):
                pdf_buffer = create_pdf(st.session_state.weekplanning)
                st.download_button(
                    label="Download PDF",
                    data=pdf_buffer,
                    file_name="weekplanning.pdf",
                    mime="application/pdf"
                )

# --- Main ---
def main():
    st.title("Zijn we weg? Reis- en Restaurantplanner")

    tab = st.sidebar.radio("Kies tab", ["Reislocaties", "Restaurants", "Plan je dag"])

    reizen_df = load_travel_data()
    restaurants_df = load_restaurants_data()

    if tab == "Reislocaties":
        if reizen_df.empty:
            st.warning("Geen reisdata beschikbaar.")
        else:
            # filters en kaartweergave toevoegen als gewenst
            st.dataframe(reizen_df)

    elif tab == "Restaurants":
        if restaurants_df.empty:
            st.warning("Geen restaurantdata beschikbaar.")
        else:
            # filters en kaartweergave toevoegen als gewenst
            st.dataframe(restaurants_df)

    else:
        if reizen_df.empty or restaurants_df.empty:
            st.warning("Data niet beschikbaar om te plannen.")
        else:
            plan_je_dag_tab(reizen_df, restaurants_df)

if __name__ == "__main__":
    main()
