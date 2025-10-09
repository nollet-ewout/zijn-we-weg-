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

# Initialize or reset form inputs in session state
if "land_regio" not in st.session_state:
    st.session_state.land_regio = ""
if "duur" not in st.session_state:
    st.session_state.duur = ""
if "bestemming" not in st.session_state:
    st.session_state.bestemming = ""
if "reistype" not in st.session_state:
    st.session_state.reistype = ""
if "seizoen" not in st.session_state:
    st.session_state.seizoen = ""
if "budget" not in st.session_state:
    st.session_state.budget = ""
if "accommodatie" not in st.session_state:
    st.session_state.accommodatie = ""
if "opmerking" not in st.session_state:
    st.session_state.opmerking = ""
if "url" not in st.session_state:
    st.session_state.url = ""

with st.form("locatie_form"):
    land_regio = st.text_input("Land / Regio", value=st.session_state.land_regio)
    duur = st.text_input("Duur", value=st.session_state.duur)
    bestemming = st.text_input("Bestemming", value=st.session_state.bestemming)
    reistype = st.text_input("Reistype / Doel", value=st.session_state.reistype)
    seizoen = st.text_input("Seizoen", value=st.session_state.seizoen)
    budget = st.text_input("Budget", value=st.session_state.budget)
    accommodatie = st.text_input("Accommodatie", value=st.session_state.accommodatie)
    opmerking = st.text_area("Opmerking", value=st.session_state.opmerking)
    url = st.text_input("URL", value=st.session_state.url)
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

        # Reset form fields in session_state
        st.session_state.land_regio = ""
        st.session_state.duur = ""
        st.session_state.bestemming = ""
        st.session_state.reistype = ""
        st.session_state.seizoen = ""
        st.session_state.budget = ""
        st.session_state.accommodatie = ""
        st.session_state.opmerking = ""
        st.session_state.url = ""

        # Trigger rerun to clear form inputs
        st.experimental_rerun()

    except Exception as e:
        st.error(f"Fout bij toevoegen locatie: {e}")
