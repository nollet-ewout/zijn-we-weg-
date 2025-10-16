import streamlit as st
import pandas as pd
import io
from fpdf import FPDF
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

@st.cache_data(ttl=600)
def load_travel_data():
    service = get_gsheets_service()
    spreadsheet_id = st.secrets["spreadsheet_id"]
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range="Opties!A1:P").execute()
    values = result.get('values', [])
    if not values:
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
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range="Restaurants!A1:G").execute()
    values = result.get('values', [])
    if not values:
        return pd.DataFrame()
    cols = values[0]
    data = values[1:]
    for row in data:
        if len(row) < len(cols):
            row += [''] * (len(cols) - len(row))
    df = pd.DataFrame(data, columns=cols)
    df.columns = df.columns.str.strip().str.lower()
    return df

# --- Plan je dag tab met weekplanning en PDF export ---
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

            # PDF export
            if st.button("Exporteer weekplanning naar PDF"):
                pdf_buffer = create_pdf_from_weekplanning(st.session_state.weekplanning)
                st.download_button(
                    label="Download PDF",
                    data=pdf_buffer,
                    file_name="weekplanning.pdf",
                    mime="application/pdf"
                )

def create_pdf_from_weekplanning(weekplanning):
    from fpdf import FPDF
    import io

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, "Weekplanning Reis en Restaurants", ln=True, align="C")
    pdf.ln(10)
    for i, dag in enumerate(weekplanning, 1):
        text = (
            f"Dag {i}: {dag['bestemming']}  \n"
            f"  Ontbijt: {dag['ontbijt']}\n"
            f"  Lunch: {dag['lunch']}\n"
            f"  Diner: {dag['diner']}\n"
        )
        pdf.multi_cell(0, 10, text)
        pdf.ln(5)
    buf = io.BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return buf

def main():
    tab_names = ["Reislocaties", "Restaurants", "Plan je dag"]
    selected_tab = st.sidebar.radio("Selecteer tabblad", tab_names)

    st.title(f"Ideale {selected_tab} Zoeker")

    if selected_tab == "Reislocaties":
        reizen_df = load_travel_data()
        if reizen_df.empty:
            st.warning("Geen reisdata beschikbaar.")
            return
        # Toon reizen met filters (vraag hier aparte uitwerking als nodig)
        st.write(reizen_df.head())

    elif selected_tab == "Restaurants":
        restaurants_df = load_restaurants_data()
        if restaurants_df.empty:
            st.warning("Geen restaurantdata beschikbaar.")
            return
        # Toon restaurants met filters (vraag hier aparte uitwerking als nodig)
        st.write(restaurants_df.head())

    else:  # Plan je dag tab
        reizen_df = load_travel_data()
        restaurants_df = load_restaurants_data()
        if reizen_df.empty or restaurants_df.empty:
            st.warning("Data niet beschikbaar om te plannen.")
            return
        plan_je_dag_tab(reizen_df, restaurants_df)

if __name__ == "__main__":
    main()
