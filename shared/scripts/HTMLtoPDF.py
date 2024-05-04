from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

def create_pdf(text, output_filename):
    # Set up the PDF document
    doc = SimpleDocTemplate(output_filename, pagesize=letter)
    styles = getSampleStyleSheet()
    flowables = []

    # Add the text to the PDF document
    p = Paragraph(text, styles["Normal"])
    flowables.append(p)

    # Build the PDF document
    doc.build(flowables)

# Example ANSI text
ansi_text = "\x1b[37m\x1b[1mNúmero de erros: 0\x1b[33m\x1b[1mNúmero de avisos: 3\x1b[34m\x1b[1m\nTempo total de execução: 4.1 segundos\x1b[0m"

# Convert ANSI text to HTML
html_text = ansi_to_html(ansi_text)

# Create a PDF file from the HTML text
create_pdf(html_text, "output.pdf")
