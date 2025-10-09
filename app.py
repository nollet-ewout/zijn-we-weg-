import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    df = pd.read_csv('reislocatie_filter.csv')
    df.columns = df.columns.str.strip()
    return df

data = load_data()

st.title("Ideale Reislocatie Zoeker")

# Vraag 1
duur = st.selectbox('Hoe lang wil je weg?', sorted(data['Duur'].unique()))

# Vraag 2 verschijnt pas als vraag 1 beantwoord is
if duur:
    bestemming = st.selectbox('Op welk continent wil je reizen?', sorted(data['Bestemming'].unique()))
else:
    bestemming = None

# Vraag 3 verschijnt pas als vraag 2 beantwoord is
if bestemming:
    reistype = st.selectbox('Wat is het doel van je reis?', sorted(data['Reistype / Doel'].unique()))
else:
    reistype = None

# Vraag 4 verschijnt pas als vraag 3 beantwoord is
if reistype:
    seizoen = st.selectbox('In welk seizoen wil je reizen?', sorted(data['Seizoen'].unique()))
else:
    seizoen = None

# Vraag 5 verschijnt pas als vraag 4 beantwoord is
if seizoen:
    accommodatie = st.selectbox('Welke type accommodatie wil je?', sorted(data['Accommodatie'].unique()))
else:
    accommodatie = None

# Filteren als alle vragen beantwoord zijn
if all([duur, bestemming, reistype, seizoen, accommodatie]):
    filtered_data = data[
        (data['Duur'] == duur) &
        (data['Bestemming'] == bestemming) &
        (data['Reistype / Doel'] == reistype) &
        (data['Seizoen'] == seizoen) &
        (data['Accommodatie'] == accommodatie)
    ]

    st.write("### Geselecteerde locaties:")
    if not filtered_data.empty:
        for _, row in filtered_data.iterrows():
            naam = row['Land / Regio']
            url = row.get('URL', '')
            if pd.notna(url) and url.strip() != '':
                st.markdown(f"- [{naam}]({url}) : {row['Opmerking']}")
            else:
                st.write(f"- {naam}: {row['Opmerking']}")
    else:
        st.write("Geen locaties gevonden.")
else:
    st.write("Beantwoord alle vragen om locaties te zien.")
