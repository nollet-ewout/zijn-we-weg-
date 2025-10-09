import streamlit as st
from github import Github
import base64
import csv
import io
import os
from dotenv import load_dotenv

load_dotenv()

# Haal GitHub token en repo info uit environment variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = "nollet-ewout/zijn-we-weg-"
CSV_PATH = "reislocatie_filter.csv"

# Initialize GitHub client
g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

st.title("Nieuwe locatie toevoegen")

with st.form("locatie_form"):
    naam = st.text_input("Naam locatie")
    adres = st.text_input("Adres")
    beschrijving = st.text_area("Beschrijving")
    submitted = st.form_submit_button("Opslaan")

if submitted:
    try:
        # Lees het CSV bestand uit GitHub
        contents = repo.get_contents(CSV_PATH)
        csv_data = base64.b64decode(contents.content).decode('utf-8')

        # Voeg nieuwe rij toe
        f = io.StringIO(csv_data)
        reader = list(csv.reader(f))
        reader.append([naam, adres, beschrijving])

        # Schrijf terug naar CSV string
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(reader)
        updated_csv = output.getvalue()

        # Update het bestand op GitHub
        repo.update_file(
            path=CSV_PATH,
            message=f"Toevoegen locatie: {naam}",
            content=updated_csv,
            sha=contents.sha,
            branch="main"  # Pas aan indien nodig
        )
        st.success(f"Locatie '{naam}' succesvol toegevoegd aan GitHub CSV!")
    except Exception as e:
        st.error(f"Er is een fout opgetreden: {e}")
