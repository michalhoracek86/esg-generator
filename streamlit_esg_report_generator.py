import streamlit as st
import openai
from fpdf import FPDF
import tempfile
import os

# --- CONFIG ---
openai.api_key = "YOUR_OPENAI_API_KEY"
MODEL = "gpt-4o"

# --- UI ---
st.title("ESG Report Generátor VSME")

uploaded_files = st.file_uploader(
    "Nahrajte soubory (PDF, XLSX, CSV)", 
    type=["pdf", "xlsx", "csv"], 
    accept_multiple_files=True
)

# ESG format template
ESG_PROMPT_TEMPLATE = """
Vytvoř ESG report podle následující struktury:

1. Environment (E)
- Emise CO2
- Spotřeba energie
- Obnovitelné zdroje

2. Social (S)
- Zaměstnanci
- Bezpečnost práce
- Diverzita

3. Governance (G)
- Řízení společnosti
- Etika
- Compliance

Použij data z přiložených souborů a vytvoř strukturovaný report.
"""


def read_file(file):
    try:
        return file.read().decode("utf-8", errors="ignore")
    except:
        return str(file.read())


def generate_esg_report(files):
    combined_text = ""

    for f in files:
        content = read_file(f)
        combined_text += f"\n\n--- FILE: {f.name} ---\n{content}"

    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Jsi expert na ESG reporting."},
            {"role": "user", "content": ESG_PROMPT_TEMPLATE + "\n\n" + combined_text}
        ],
        temperature=0.3
    )

    return response["choices"][0]["message"]["content"]


def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=10)

    for line in text.split("\n"):
        pdf.multi_cell(0, 8, line)

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(tmp_file.name)
    return tmp_file.name


if st.button("Generovat ESG Report"):
    if not uploaded_files:
        st.warning("Nahrajte prosím alespoň jeden soubor.")
    else:
        with st.spinner("Generuji ESG report..."):
            report = generate_esg_report(uploaded_files)

        st.subheader("Výsledek")
        st.text_area("ESG Report", report, height=400)

        pdf_path = create_pdf(report)

        with open(pdf_path, "rb") as f:
            st.download_button(
                label="Stáhnout jako PDF",
                data=f,
                file_name="esg_report.pdf",
                mime="application/pdf"
            )

        os.remove(pdf_path)
