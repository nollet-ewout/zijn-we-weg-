import streamlit as st
import pandas as pd

# Inladen data
@st.cache_data
def load_data():
    df = pd.read_csv('reislocatie_filter.csv')
    df.columns = df.columns.str.strip()  # verwijder spaties rondom kolomnamen

    # Zet 'Budget' om naar numeriek, foute waarden worden NaN
    df['Budget'] = pd.to_numeric(df['Budget'], errors='coerce')

    return df

data = load_data()

st.title("Ideale Reislocatie Zoeker")

# Vraag 1: Duur
duur_options = sorted(data['Duur'].dropna().unique())
duur = st.selectbox('Hoe lang wil je weg?', ['Maak een keuze...'] + duur_options)

# Vraag 2: Budget slider (stapgrootte 100)
if duur != 'Maak een keuze...':
    min_budget = int(data['Budget'].min())
    max_budget = int(data['Budget'].max())
    budget = st.slider(
        'Wat is je budget? (min - max)',
        min_value=min_budget,
        max_value=max_budget,
        value=(min_budget, max_budget),
        step=100
    )
else:
    budget = None

# Vraag 3: Bestemming
bestemming_options = sorted(data['Bestemming'].dropna().unique()) if budget is not None else []
bestemming = st.selectbox('Op welk continent wil je reizen?', ['Maak een keuze...'] + bestemming_options) if budget is not None else 'Maak een keuze...'

# Vraag 4: Reistype / Doel
reistype_options = sorted(data['Reistype / Doel'].dropna().unique()) if bestemming != 'Maak een keuze...' else []
reistype = st.selectbox('Wat is het doel van je reis?', ['Maak een keuze...'] + reistype_options) if bestemming != 'Maak een keuze...' else 'Maak een keuze...'

# Vraag 5: Seizoen
seizoen_options = sorted(data['Seizoen'].dropna().unique()) if reistype != 'Maak een keuze...' else []
seizoen = st.selectbox('In welk seizoen wil je reizen?', ['Maak een keuze...'] + seizoen_options) if reistype != 'Maak een keuze...' else 'Maak een keuze...'

# Vraag 6: Accommodatie
accommodatie_options = sorted(data['Accommodatie'].dropna().unique()) if seizoen != 'Maak een keuze...' else []
accommodatie = st.selectbox('Welke type accommodatie wil je?', ['Maak een keuze...'] + accommodatie_options) if seizoen != 'Maak een keuze...' else 'Maak een keuze...'

# Filteren als alle vragen beantwoord zijn
if all(selection != 'Maak een keuze...' for selection in [duur, bestemming, reistype, seizoen, accommodatie]) and budget is not None:
    filtered_data = data.dropna(subset=['Budget'])
    filtered_data = filtered_data[
        (filtered_data['Duur'] == duur) &
        (filtered_data['Budget'] >= budget[0]) & (filtered_data['Budget'] <= budget[1]) &
        (filtered_data['Bestemming'] == bestemming) &
        (filtered_data['Reistype / Doel'] == reistype) &
        (filtered_data['Seizoen'] == seizoen) &
        (filtered_data['Accommodatie'] == accommodatie)
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
