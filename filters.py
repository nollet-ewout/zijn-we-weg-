import pandas as pd

# --- Filtering functies ---
def filter_travel_in_memory(df, duur_slider, budget_slider, continent, reistype, seizoen, accommodatie, temp_slider, vervoersmiddelen, land, regio, stad):
    # Vul lege velden
    for col in ['land', 'regio', 'stad', 'continent', 'reistype / doel', 'seizoen', 'accommodatie', 'vervoersmiddel']:
        if col in df.columns:
            df[col] = df[col].fillna('')

    filtered = df[
        (df['minimum duur'] >= duur_slider[0]) &
        (df['maximum duur'] <= duur_slider[1]) &
        (df['budget'] >= budget_slider[0]) &
        (df['budget'] <= budget_slider[1]) &
        (df['temperatuur'].between(temp_slider[0], temp_slider[1]))
    ]

    if continent:
        filtered = filtered[filtered['continent'].isin(continent)]
    if reistype:
        filtered = filtered[filtered['reistype / doel'].isin(reistype)]
    if seizoen:
        filtered = filtered[filtered['seizoen'].str.contains('|'.join(seizoen), case=False, na=False)]
    if accommodatie:
        filtered = filtered[filtered['accommodatie'].isin(accommodatie)]
    if vervoersmiddelen:
        filtered = filtered[filtered['vervoersmiddel'].str.contains('|'.join(vervoersmiddelen), case=False, na=False)]
    if land:
        filtered = filtered[filtered['land'].isin(land)]
    if regio:
        filtered = filtered[filtered['regio'].isin(regio)]
    if stad:
        filtered = filtered[filtered['stad'].isin(stad)]

    return filtered


def filter_restaurants_in_memory(df, keuken, prijs_slider, land, regio, stad):
    # Vul lege velden
    for col in ['land', 'regio', 'stad', 'keuken', 'locatie']:
        if col in df.columns:
            df[col] = df[col].fillna('')

    filtered = df[
        (df['prijsniveau'] >= prijs_slider[0]) &
        (df['prijsniveau'] <= prijs_slider[1])
    ]

    if keuken:
        filtered = filtered[filtered['keuken'].isin(keuken)]
    if land:
        filtered = filtered[filtered['land'].isin(land)]
    if regio:
        filtered = filtered[filtered['regio'].isin(regio)]
    if stad:
        filtered = filtered[filtered['stad'].isin(stad)]

    return filtered
