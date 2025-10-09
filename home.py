import streamlit as st

st.title("Startpagina")

button_html = f"""
<div style="display: flex; justify-content: center; gap: 60px; margin-top: 80px;">
  <a href="https://zijnweweg.streamlit.app/" target="_blank" style="
      background-color: #007BFF; 
      color: white; 
      padding: 30px 70px; 
      text-align: center; 
      text-decoration: none; 
      display: inline-block; 
      font-size: 28px; 
      border-radius: 12px;
      cursor: pointer;
      font-weight: bold;
      box-shadow: 0 4px 8px rgba(0, 123, 255, 0.4);
  ">Applicatie 1</a>

  <a href="https://zijnweweg-nieuwe-locatie.streamlit.app/" target="_blank" style="
      background-color: #007BFF; 
      color: white; 
      padding: 30px 70px; 
      text-align: center; 
      text-decoration: none; 
      display: inline-block; 
      font-size: 28px; 
      border-radius: 12px;
      cursor: pointer;
      font-weight: bold;
      box-shadow: 0 4px 8px rgba(0, 123, 255, 0.4);
  ">Applicatie 2</a>
</div>
"""

st.markdown(button_html, unsafe_allow_html=True)
