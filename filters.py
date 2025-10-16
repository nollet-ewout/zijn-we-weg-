# --- Filtering functies ---
def filter_travel_in_memory(df, duur_slider, budget_slider, continent, reistype, seizoen, accommodatie, temp_slider, vervoersmiddelen):
    df = df.dropna(subset=['budget', 'minimum duur', 'maximum duur'])
    df = df[
        (df['maximum duur'] >= duur_slider[0]) &
        (df['minimum duur'] <= duur_slider[1]) &
        (df['budget'] >= budget_slider[0]) &
        (df['budget'] <= budget_slider[1])
    ]
    if 'temperatuur' in df.columns:
        df = df[(df['temperatuur'] >= temp_slider[0]) & (df['temperatuur'] <= temp_slider[1])]
    if continent:
        df = df[df['continent'].isin(continent)]
    if reistype:
        df = df[df['reistype / doel'].isin(reistype)]
    if seizoen:
        df = df[df['seizoen'].apply(lambda x: any(s in [s.strip() for s in x.split(';')] for s in seizoen))]
    if accommodatie:
        df = df[df['accommodatie'].isin(accommodatie)]
    if vervoersmiddelen:
        df = df[df['vervoersmiddel'].apply(lambda x: any(vm.strip() in x.split(';') for vm in vervoersmiddelen))]
    return df

def filter_restaurants_in_memory(df, keuken, locaties, prijs_range):
    if keuken:
        df = df[df['keuken'].isin(keuken)]
    if locaties:
        df = df[df['locatie'].isin(locaties)]
    if prijs_range:
        df = df[df['prijs'].apply(lambda p: len(p.strip()) >= prijs_range[0] and len(p.strip()) <= prijs_range[1])]
    return df
