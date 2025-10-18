import streamlit as st

from filters import filter_travel_in_memory, filter_restaurants_in_memory
from kaartweergave import bestemming_kaartje, restaurant_kaartje
from data_loading import load_travel_data, load_restaurants_data
from plan_je_dag import plan_je_dag_tab

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

        land_options = sorted(data['land'].dropna().unique())
        regio_options = sorted(data['regio'].dropna().unique())
        stad_options = sorted(data['stad'].dropna().unique())
        continent_options = sorted(data['continent'].dropna().unique())
        reistype_options = sorted(data['reistype / doel'].dropna().unique())
        seizoen_raw_options = data['seizoen'].dropna().unique()
        seizoen_split = set()
        for item in seizoen_raw_options:
            for s in item.split(';'):
                seizoen_split.add(s.strip())
        seizoen_options = sorted(seizoen_split)
        accommodatie_options = sorted(data['accommodatie'].dropna().unique())
        vervoersmiddelen_options = sorted(set(
            v.strip()
            for row in data['vervoersmiddel'].dropna()
            for v in row.split(';')
        )) if 'vervoersmiddel' in data.columns else []

        land = st.sidebar.multiselect('Land', land_options, default=st.session_state.get('filter_land', []), key='filter_land')
        regio = st.sidebar.multiselect('Regio', regio_options, default=st.session_state.get('filter_regio', []), key='filter_regio')
        stad = st.sidebar.multiselect('Stad', stad_options, default=st.session_state.get('filter_stad', []), key='filter_stad')
        continent = st.sidebar.multiselect('Op welk continent wil je reizen?', continent_options, default=st.session_state.get('filter_continent', []), key='filter_continent')
        reistype = st.sidebar.multiselect('Wat is het doel van je reis?', reistype_options, default=st.session_state.get('filter_reistype', []), key='filter_reistype')
        seizoen = st.sidebar.multiselect('In welk seizoen wil je reizen?', seizoen_options, default=st.session_state.get('filter_seizoen', []), key='filter_seizoen')
        accommodatie = st.sidebar.multiselect('Welke type accommodatie wil je?', accommodatie_options, default=st.session_state.get('filter_accommodatie', []), key='filter_accommodatie')
        vervoersmiddelen = st.sidebar.multiselect('Vervoersmiddel', vervoersmiddelen_options, default=st.session_state.get('filter_vervoersmiddel', []), key='filter_vervoersmiddel')

        duur_slider = st.sidebar.slider('Hoe lang wil je weg? (dagen)', min_duur, max_duur, (min_duur, max_duur), step=1, key='filter_duur')
        budget_slider = st.sidebar.slider('Wat is je budget? (min - max)', min_budget, max_budget, (min_budget, max_budget), step=100, key='filter_budget')
        temp_slider = st.sidebar.slider('Temperatuurbereik (°C)', min_temp, max_temp, (min_temp, max_temp), step=1, key='filter_temp')

        filtered_data = filter_travel_in_memory(
            data,
            duur_slider,
            budget_slider,
            continent,
            reistype,
            seizoen,
            accommodatie,
            temp_slider,
            vervoersmiddelen,
            land,
            regio,
            stad
        )

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
        locatie_options = sorted(restaurants['locatie'].dropna().unique())
        land_options = sorted(restaurants['land'].dropna().unique())
        regio_options = sorted(restaurants['regio'].dropna().unique())
        stad_options = sorted(restaurants['stad'].dropna().unique())

        selected_keuken = st.sidebar.multiselect("Kies type keuken", keuken_options, default=st.session_state.get('filter_keuken', []), key='filter_keuken')
        selected_locaties = st.sidebar.multiselect("Selecteer locatie(s)", locatie_options, default=st.session_state.get('filter_locaties', []), key='filter_locaties')
        land = st.sidebar.multiselect('Land', land_options, default=st.session_state.get('filter_rest_land', []), key='filter_rest_land')
        regio = st.sidebar.multiselect('Regio', regio_options, default=st.session_state.get('filter_rest_regio', []), key='filter_rest_regio')
        stad = st.sidebar.multiselect('Stad', stad_options, default=st.session_state.get('filter_rest_stad', []), key='filter_rest_stad')
        prijs_slider = st.sidebar.slider("Prijsniveau (€ - €€€€)", 1, 4, (1, 4), step=1, key='filter_prijs')

        filtered_restaurants = filter_restaurants_in_memory(
            restaurants,
            selected_keuken,
            selected_locaties,
            prijs_slider,
            land,
            regio,
            stad
        )

        if not filtered_restaurants.empty:
            for _, row in filtered_restaurants.iterrows():
                restaurant_kaartje(row)
        else:
            st.write("Geen restaurants gevonden.")

    else:
        reizen_df = load_travel_data()
        restaurants_df = load_restaurants_data()
        if reizen_df.empty or restaurants_df.empty:
            st.warning("Data niet beschikbaar om je dag te plannen.")
            st.stop()
        plan_je_dag_tab(reizen_df, restaurants_df)

if __name__ == "__main__":
    main()

