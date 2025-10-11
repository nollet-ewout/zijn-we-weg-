# Start met dataset zonder NaN in kritieke kolommen
filtered_data = data.dropna(subset=['budget', 'minimum duur', 'maximum duur'])

# Filter op duur
filtered_data = filtered_data[
    (filtered_data['maximum duur'] >= duur_slider[0]) &
    (filtered_data['minimum duur'] <= duur_slider[1])
]

# Filter op budget
filtered_data = filtered_data[
    (filtered_data['budget'] >= budget[0]) &
    (filtered_data['budget'] <= budget[1])
]

# Filter op continent als er gekozen is
if continent:
    filtered_data = filtered_data[filtered_data['continent'].isin(continent)]

# Filter op reistype als er gekozen is
if reistype:
    filtered_data = filtered_data[filtered_data['reistype / doel'].isin(reistype)]

# Filter op seizoen als er gekozen is
if seizoen:
    filtered_data = filtered_data[
        filtered_data['seizoen'].apply(lambda x: any(s in [s.strip() for s in x.split(';')] for s in seizoen))
    ]

# Filter op accommodatie als er gekozen is
if accommodatie:
    filtered_data = filtered_data[filtered_data['accommodatie'].isin(accommodatie)]

# Resultaten tonen
st.write("### Geselecteerde locaties:")
if not filtered_data.empty:
    for _, row in filtered_data.iterrows():
        naam = row['land / regio']
        url = row.get('url', '')
        if pd.notna(url) and url.strip() != '':
            st.markdown(f"- [{naam}]({url}) : {row['opmerking']}")
        else:
            st.write(f"- {naam}: {row['opmerking']}")
else:
    st.write("Geen locaties gevonden.")
