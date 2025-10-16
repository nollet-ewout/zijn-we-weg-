# --- Cached data loading ---
@st.cache_data(ttl=600)
def load_travel_data():
    service = get_gsheets_service()
    spreadsheet_id = st.secrets["spreadsheet_id"]
    sheet = service.spreadsheets()
    try:
        result = sheet.values().get(spreadsheetId=spreadsheet_id, range="Opties!A1:P").execute()
        values = result.get('values', [])
    except Exception as e:
        st.error(f"Error bij ophalen data van Google Sheets: {e}")
        return pd.DataFrame()
    if not values:
        st.error("Geen data gevonden in Google Sheet.")
        return pd.DataFrame()
    cols = values[0]
    data = values[1:]
    for row in data:
        if len(row) < len(cols):
            row += [''] * (len(cols) - len(row))
    df = pd.DataFrame(data, columns=cols)
    df.columns = df.columns.str.strip().str.lower()
    for col in ['minimum duur', 'maximum duur', 'budget', 'temperatuur']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

@st.cache_data(ttl=600)
def load_restaurants_data():
    service = get_gsheets_service()
    spreadsheet_id = st.secrets["spreadsheet_id"]
    sheet = service.spreadsheets()
    try:
        result = sheet.values().get(spreadsheetId=spreadsheet_id, range="Restaurants!A1:G").execute()
        values = result.get('values', [])
    except Exception as e:
        st.error(f"Error bij ophalen restaurantdata: {e}")
        return pd.DataFrame()
    if not values:
        st.error("Geen data gevonden in Restaurants-sheet.")
        return pd.DataFrame()
    cols = values[0]
    data = values[1:]
    for row in data:
        if len(row) < len(cols):
            row += [''] * (len(cols) - len(row))
    df = pd.DataFrame(data, columns=cols)
    df.columns = df.columns.str.strip().str.lower()
    return df

@st.cache_data(ttl=600)
def image_to_base64_cached(image_url):
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        img_bytes = response.content
        encoded = base64.b64encode(img_bytes).decode()
        return f"data:image/jpeg;base64,{encoded}"
    except Exception:
        return None
