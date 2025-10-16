from fpdf import FPDF
import io

# --- PDF export functie ---
def create_pdf_from_weekplanning(weekplanning):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, "Weekplanning Reis en Restaurants", ln=True, align="C")
    pdf.ln(10)
    for i, dag in enumerate(weekplanning, 1):
        text = (
            f"Dag {i}: {dag['bestemming']}  \n"
            f"  Ontbijt: {dag.get('ontbijt','geen geselecteerd')}\n"
            f"  Lunch: {dag.get('lunch','geen geselecteerd')}\n"
            f"  Diner: {dag.get('diner','geen geselecteerd')}\n"
        )
        pdf.multi_cell(0, 10, text)
        pdf.ln(5)
    buf = io.BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return buf
