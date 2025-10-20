import streamlit as st
from pdf_export import create_pdf_from_weekplanning

# --- Plan je dag tab ---
def plan_je_dag_tab(reizen_df, restaurants_df):
    st.header("Plan je ideale dag")

    if 'weekplanning' not in st.session_state:
        st.session_state['weekplanning'] = []

    # Vul lege velden met lege strings voor veiligheid
    for col in ['land', 'regio', 'stad']:
        if col in reizen_df.columns:
            reizen_df[col] = reizen_df[col].fillna('')
    for col in ['land', 'regio', 'stad', 'keuken', 'maaltijd']:
        if col in restaurants_df.columns:
            restaurants_df[col] = restaurants_df[col].fillna('')

    landen = sorted([l for l in reizen_df['land'].unique() if l])
    gekozen_land = st.selectbox("Kies land", landen)

    regios = sorted([r for r in reizen_df[reizen_df['land'] == gekozen_land]['regio'].unique() if r])
    gekozen_regio = st.selectbox("Kies regio", regios)

    steden = sorted([s for s in reizen_df[(reizen_df['land'] == gekozen_land) & (reizen_df['regio'] == gekozen_regio)]['stad'].unique() if s])
    gekozen_stad = st.selectbox("Kies stad", steden)

    gekozen_locatie = str(gekozen_stad) if gekozen_stad is not None else ""

    # Filter restaurants op geselecteerde stad, veilig met regex=False
    restaurants_locatie = restaurants_df[
        restaurants_df['stad'].str.contains(gekozen_locatie, case=False, na=False, regex=False)
    ]

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
            "ontbijt": ontbijt_keuze if ontbijt_keuze != "- geen -" else None,
            "lunch": lunch_keuze if lunch_keuze != "- geen -" else None,
            "diner": diner_keuze if diner_keuze != "- geen -" else None
        }
        st.session_state['weekplanning'].append(dag)
        st.success(f"Dag {len(st.session_state['weekplanning'])} toegevoegd!")

    if st.session_state['weekplanning']:
        st.markdown("## Overzicht weekplanning")
        for i, dag in enumerate(st.session_state['weekplanning'], 1):
            st.markdown(f"### Dag {i} - {dag['bestemming']}")
            ontbijt = dag['ontbijt'] or "geen geselecteerd"
            lunch = dag['lunch'] or "geen geselecteerd"
            diner = dag['diner'] or "geen geselecteerd"
            st.markdown(f"Ontbijt: {ontbijt}  \nLunch: {lunch}  \nDiner: {diner}")

        pdf_buffer = create_pdf_from_weekplanning(st.session_state['weekplanning'])
        st.download_button(
            label="Download PDF",
            data=pdf_buffer,
            file_name="weekplanning.pdf",
            mime="application/pdf"
        )
