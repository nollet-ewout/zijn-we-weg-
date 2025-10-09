import streamlit as st
from github import Github
import base64
import csv
import io
import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = "nollet-ewout/zijn-we-weg-"
CSV_PATH = "reislocatie_filter.csv"

g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

st.title("Nieuwe locatie toevoegen")

with st.form("locatie_form"):
    land_regio = st.text_input("Land / Regio")
    duur = st.text_input("Duur")
    bestemming = st.text_input("Bestemming")
    reistype = st.text_input("Reistype / Doel")
    seizoen = st.text_input("Seizoen")
    budget = st.text_input("Budget")
    accommodatie = st.text_input("Accommodatie")
    opmerking = st.text_area("Opmerking")
    url = st.text_input("URL")
    submitted = st.form_submit_button("Opslaan")

if submitted:
    try:
        contents = repo.get_contents(CSV_PATH)
        csv_data = base64.b64decode(contents.content).decode('utf-8')

        f = io.StringIO(csv_data)
        reader = list(csv.reader(f))

        # Bepaal nieuw ID op basis van laatste rij
        if len(reader) > 1:
            laatste_id = int(reader[-1][0])
        else:
            laatste_id = 0
        nieuw_id = laatste_id + 1

        # Voeg nieuwe rij toe met ID en alle velden
        nieuwe_rij = [
            str(nieuw_id),
            land_regio,
            duur,
            bestemming,
            reistype,
            seizoen,
            budget,
            accommodatie,
            opmerking,
            url
        ]
        reader.append(nieuwe_rij)

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(reader)
        updated_csv = output.getvalue()

        repo.update_file(
            path=CSV_PATH,
            message=f"Toevoegen locatie ID {nieuw_id}",
            content=updated_csv,
            sha=contents.sha,
            branch="main"
        )
        st.success(f"Locatie met ID {nieuw_id} succesvol toegevoegd!")
    except Exception as e:
        st.error(f"Fout bij toevoegen locatie: {e}")
