from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch

def create_test_pdf(filename):
    # Create a new PDF with ReportLab
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Add Table of Contents
    toc_style = styles['Heading1']
    toc_style.fontSize = 16
    toc_style.spaceAfter = 12
    story.append(Paragraph("Table of Contents", toc_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Add TOC entries
    toc_entries = [
        "Chapter 1: Introduction ................... 1",
        "1.1 Background ............................ 2",
        "1.2 Objectives ............................ 3",
        "Chapter 2: Literature Review .............. 4",
        "2.1 Previous Work ........................ 5",
        "2.2 Current State ........................ 6"
    ]
    
    for entry in toc_entries:
        story.append(Paragraph(entry, styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
    
    # Add main content
    story.append(Paragraph("Chapter 1: Introduction", styles['Heading1']))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("1.1 Background", styles['Heading2']))
    story.append(Paragraph("This is the background section.", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("1.2 Objectives", styles['Heading2']))
    story.append(Paragraph("These are the objectives.", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("Chapter 2: Literature Review", styles['Heading1']))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("2.1 Previous Work", styles['Heading2']))
    story.append(Paragraph("This section discusses previous work.", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("2.2 Current State", styles['Heading2']))
    story.append(Paragraph("This section discusses the current state.", styles['Normal']))
    
    # Build the PDF
    doc.build(story)

if __name__ == "__main__":
    create_test_pdf("test.pdf") 