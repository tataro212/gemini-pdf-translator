from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
import os

def create_test_pdf():
    # Create output directory if it doesn't exist
    os.makedirs("test_output", exist_ok=True)
    
    # Create a new PDF with ReportLab
    c = canvas.Canvas("test.pdf", pagesize=letter)
    width, height = letter
    
    # Add title
    c.setFont("Helvetica-Bold", 24)
    c.drawString(100, height - 100, "Test PDF Document")
    
    # Add some text
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 150, "This is a test document for the PDF parser.")
    
    # Add a blue rectangle
    c.setFillColor(colors.blue)
    c.rect(100, height - 250, 200, 50, fill=1)
    
    # Add text about the rectangle
    c.setFillColor(colors.black)
    c.drawString(100, height - 270, "This is a blue rectangle in the document.")
    
    # Add a table-like structure
    c.setStrokeColor(colors.black)
    c.line(100, height - 350, 300, height - 350)  # Top line
    c.line(100, height - 400, 300, height - 400)  # Bottom line
    c.line(100, height - 350, 100, height - 400)  # Left line
    c.line(300, height - 350, 300, height - 400)  # Right line
    c.line(200, height - 350, 200, height - 400)  # Middle line
    
    # Add table headers
    c.drawString(120, height - 370, "Column 1")
    c.drawString(220, height - 370, "Column 2")
    
    # Save the PDF
    c.save()
    print("Test PDF created successfully!")

if __name__ == "__main__":
    create_test_pdf() 