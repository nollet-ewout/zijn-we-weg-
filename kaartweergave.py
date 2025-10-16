import streamlit as st
import base64
import requests

from data_loading import image_to_base64_cached

# --- Kaartweergaves ---
def bestemming_kaartje(row):
    foto_url = row.get('foto', '').strip()
    url = row.get('url', '').strip()
    img_block = ""
    if foto_url:
        img_b64 = image_to_base64_cached(foto_url)
        if img_b64:
            img_block = f'<img src="{img_b64}" width="200" style="border-radius:8px; float:right; margin-left:30px;" />'
        else:
            img_block = "<div style='width:200px; height:150px; background:#444; border-radius:8px; float:right;'></div>"
    else:
        img_block = "<div style='width:200px; height:150px; background:#444; border-radius:8px; float:right;'></div>"
    naam_html = f'<a href="{url}" target="_blank" style="color:#1e90ff; text-decoration:none;">{row["land / regio"]}</a>' if url else f'<span style="color:#fff; font-weight:bold;">{row["land / regio"]}</span>'
    vervoersmiddel_clean = ', '.join([v.strip() for v in row.get('vervoersmiddel', '').split(';') if v.strip()])
    kaart_html = f"""
    <div style='border:1px solid #ddd; border-radius:8px; padding:20px; margin-bottom:15px; box-shadow:2px 2px 8px rgba(0,0,0,0.2); background-color:#18181b; overflow:auto;'>
        {img_block}
        <div style="text-align:left; max-width: calc(100% - 250px);">
            <h3 style='margin-bottom:10px; color:#fff;'>{naam_html}</h3>
            <div style='color:#ccc; font-style:italic;'>{row.get('opmerking', '') or ''}</div>
            <div style='color:#fff;'><b>Prijs:</b> €{row.get('budget', '')}</div>
            <div style='color:#fff;'><b>Duur:</b> {row.get('minimum duur', '')} - {row.get('maximum duur', '')} dagen</div>
            <div style='color:#fff;'><b>Temperatuur:</b> {row.get('temperatuur', '')} °C</div>
            <div style='color:#fff;'><b>Vervoersmiddel:</b> {vervoersmiddel_clean}</div>
        </div>
    </div>
    """
    st.markdown(kaart_html, unsafe_allow_html=True)

def restaurant_kaartje(row):
    foto_url = row.get('foto', '').strip()
    url = row.get('url', '').strip()
    img_block = ""
    if foto_url:
        img_b64 = image_to_base64_cached(foto_url)
        if img_b64:
            img_block = f'<img src="{img_b64}" width="200" style="border-radius:8px; float:right; margin-left:30px;" />'
        else:
            img_block = "<div style='width:200px; height:150px; background:#444; border-radius:8px; float:right;'></div>"
    else:
        img_block = "<div style='width:200px; height:150px; background:#444; border-radius:8px; float:right;'></div>"
    naam_html = f'<a href="{url}" target="_blank" style="color:#1e90ff; text-decoration:none;">{row["naam"]}</a>' if url else f'<span style="color:#fff; font-weight:bold;">{row["naam"]}</span>'
    kaart_html = f"""
    <div style='border:1px solid #ddd; border-radius:8px; padding:20px; margin-bottom:15px; box-shadow:2px 2px 8px rgba(0,0,0,0.2); background-color:#18181b; overflow:auto;'>
        {img_block}
        <div style="text-align:left; max-width: calc(100% - 250px);">
            <h3 style='margin-bottom:10px; color:#fff;'>{naam_html}</h3>
            <div style='color:#fff;'><b>Keuken:</b> {row.get('keuken', '')}</div>
            <div style='color:#fff;'><b>Prijs:</b> {row.get('prijs', '')}</div>
            <div style='color:#fff;'><b>Locatie:</b> {row.get('locatie', '')}</div>
            <div style='color:#ccc; font-style:italic;'>{row.get('opmerking', '') or ''}</div>
        </div>
    </div>
    """
    st.markdown(kaart_html, unsafe_allow_html=True)
