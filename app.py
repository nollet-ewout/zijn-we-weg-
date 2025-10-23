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

    st.title(f"Ideale {selected_tab} Zoeker")

    # Refresh knop
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

    if st.session_state['needs_refresh']:
        st.session_state['needs_refresh'] = False
        st.rerun()

    if selected_tab == "Reislocaties":
        data = load_travel_data()
        if data.empty:
            st.warning("Geen reisdata beschikbaar.")
            st.stop()
        # Vul relevante kolommen met lege string
        for col in ['land', 'regio', 'stad', 'continent', 'reistype / doel', 'seizoen', 'accommodatie', 'vervoersmiddel']:
            if col in data.columns:
                data[col] = data[col].fillna('')

        min_duur = int(data['minimum duur'].min())
        max_duur = int(data['maximum duur'].max())
        min_budget = int(data['budget'].min())
        max_budget = int(data['budget'].max())
        min_temp = int(data['temperatuur'].min()) if 'temperatuur' in data.columns else 0
        max_temp = int(data['temperatuur'].max()) if 'temperatuur' in data.columns else 40

        land_options = sorted([x for x in data['land'].unique() if x])
        regio_options = sorted([x for x in data['regio'].unique() if x])
        stad_options = sorted([x for x in data['stad'].unique() if x])
        continent_options = sorted([x for x in data['continent'].unique() if x])
        reistype_options = sorted([x for x in data['reistype / doel'].unique() if x])

        seizoen_raw_options = data['seizoen'].unique()
        seizoen_split = set()
        for item in seizoen_raw_options:
            for s in str(item).split(';'):
                s = s.strip()
                if s:
                    seizoen_split.add(s)
        seizoen_options = sorted(seizoen_split)

        accommodatie_options = sorted([x for x in data['accommodatie'].unique() if x])
        vervoersmiddelen_options = sorted(set(
            v.strip()
            for row in data['vervoersmiddel'].dropna()
            for v in row.split(';')
        )) if 'vervoersmiddel' in data.columns else []

        land = st.sidebar.multiselect('Land', land_options, key='filter_land')
        regio = st.sidebar.multiselect('Regio', regio_options, key='filter_regio')
        stad = st.sidebar.multiselect('Stad', stad_options, key='filter_stad')
        continent = st.sidebar.multiselect('Op welk continent?', continent_options, key='filter_continent')
        reistype = st.sidebar.multiselect('Reistype', reistype_options, key='filter_reistype')
        seizoen = st.sidebar.multiselect('Seizoen', seizoen_options, key='filter_seizoen')
        accommodatie = st.sidebar.multiselect('Accommodatie', accommodatie_options, key='filter_accommodatie')
        vervoersmiddelen = st.sidebar.multiselect('Vervoersmiddel', vervoersmiddelen_options, key='filter_vervoersmiddel')

        duur_slider = st.sidebar.slider('Duur (dagen)', min_duur, max_duur, (min_duur, max_duur), step=1)
        budget_slider = st.sidebar.slider('Budget', min_budget, max_budget, (min_budget, max_budget), step=100)
        temp_slider = st.sidebar.slider('Temperatuur (°C)', min_temp, max_temp, (min_temp, max_temp), step=1)

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
        restaurants_df = load_restaurants_data()
        if restaurants_df.empty:
            st.warning("Geen restaurantdata beschikbaar.")
            st.stop()
        # Vul alle relevante kolommen op met lege strings
        for col in ['land', 'regio', 'stad', 'keuken', 'maaltijd', 'prijs']:
            if col in restaurants_df.columns:
                restaurants_df[col] = restaurants_df[col].fillna('')

        keuken_options = sorted([k for k in restaurants_df['keuken'].unique() if k])
        land_options = sorted([l for l in restaurants_df['land'].unique() if l])
        regio_options = sorted([r for r in restaurants_df['regio'].unique() if r])
        stad_options = sorted([s for s in restaurants_df['stad'].unique() if s])

        selected_keuken = st.sidebar.multiselect("Kies type keuken", keuken_options)
        selected_land = st.sidebar.multiselect("Land", land_options)
        selected_regio = st.sidebar.multiselect("Regio", regio_options)
        selected_stad = st.sidebar.multiselect("Stad", stad_options)
        prijs_slider = st.sidebar.slider("Prijsniveau (€ - €€€€)", 1, 4, (1, 4), step=1)

        filtered_restaurants = filter_restaurants_in_memory(
            restaurants_df,
            selected_keuken,
            prijs_slider,
            selected_land,
            selected_regio,
            selected_stad
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
            st.warning("Geen data om je dag te plannen.")
            st.stop()
        plan_je_dag_tab(reizen_df, restaurants_df)

if __name__ == "__main__":
    main()

