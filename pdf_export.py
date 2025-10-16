from fpdf import FPDF
import io
import os

def create_pdf_from_weekplanning(weekplanning):
    pdf = FPDF()
    pdf.add_page()
    font_path = os.path.join(os.path.dirname(__file__), "fonts", "DejaVuSans.ttf")
    pdf.add_font("DejaVu", "", font_path, uni=True)
    pdf.set_font("DejaVu", size=12)

    pdf.cell(0, 10, "Weekplanning Reis en Restaurants", ln=True, align="C")
    pdf.ln(10)

    for i, dag in enumerate(weekplanning, 1):
        text = (
            f"Dag {i}: {dag['bestemming']}  \n"
            f"  Ontbijt: {dag.get('ontbijt', 'geen geselecteerd')}\n"
            f"  Lunch: {dag.get('lunch', 'geen geselecteerd')}\n"
            f"  Diner: {dag.get('diner', 'geen geselecteerd')}\n"
        )
        pdf.multi_cell(0, 10, text)
        pdf.ln(5)

    pdf_bytes = pdf.output(dest='S')
    return io.BytesIO(pdf_bytes)
