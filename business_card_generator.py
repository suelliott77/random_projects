from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
import qrcode
from io import BytesIO
import os
import tempfile

class BusinessCard:
    def __init__(self, name, title, company, email, phone, website=None):
        self.name = name
        self.title = title
        self.company = company
        self.email = email
        self.phone = phone
        self.website = website
    
    def generate_text(self):
        """Generate ASCII text version of the card"""
        card = f"""
╔════════════════════════════════════╗
║  {self.name:<32}  ║
║  {self.title:<32}  ║
║  {self.company:<32}  ║
╠════════════════════════════════════╣
║  Email: {self.email:<25}║
║  Phone: {self.phone:<25}  ║
╚════════════════════════════════════╝
        """
        return card

    def generate_qr_code(self, data):
        """Generate QR code image from data"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=2,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        return img

    def generate_pdf(self, filename="business_card.pdf"):
        """Generate a professional business card PDF with one card per page"""
        # Standard business card size: 3.5 x 2 inches
        card_width = 3.5 * inch
        card_height = 2 * inch
        
        # Create PDF with standard letter size
        page_width, page_height = landscape((8.5 * inch, 11 * inch))
        
        c = canvas.Canvas(filename, pagesize=(page_width, page_height))
        
        # Colors
        primary_color = HexColor("#1f4788")
        accent_color = HexColor("#0099cc")
        
        # Generate QR code image file if website is provided
        qr_img_path = None
        if self.website:
            qr_img = self.generate_qr_code(self.website)
            # Save to temporary file
            temp_dir = tempfile.gettempdir()
            qr_img_path = os.path.join(temp_dir, "qr_code_temp.png")
            qr_img.save(qr_img_path)
        
        # Center the card on the page
        x = (page_width - card_width) / 2
        y = (page_height - card_height) / 2
        
        self._draw_card(c, x, y, card_width, card_height, primary_color, accent_color, qr_img_path)
        
        c.save()
        
        # Clean up temporary file
        if qr_img_path and os.path.exists(qr_img_path):
            os.remove(qr_img_path)
        
        print(f"PDF saved as: {filename}")

    def _draw_card(self, c, x, y, width, height, primary_color, accent_color, qr_img_path=None):
        """Draw a single business card"""
        # Draw border
        c.setLineWidth(1)
        c.setStrokeColor(primary_color)
        c.rect(x, y, width, height)
        
        # Left stripe (accent color)
        stripe_width = 0.3 * inch
        c.setFillColor(accent_color)
        c.rect(x, y, stripe_width, height, fill=1, stroke=0)
        
        # Company name (top)
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(primary_color)
        c.drawString(x + stripe_width + 0.15 * inch, y + height - 0.3 * inch, self.company)
        
        # Name (larger)
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(HexColor("#000000"))
        c.drawString(x + stripe_width + 0.15 * inch, y + height - 0.55 * inch, self.name)
        
        # Title (smaller)
        c.setFont("Helvetica", 8)
        c.setFillColor(accent_color)
        c.drawString(x + stripe_width + 0.15 * inch, y + height - 0.75 * inch, self.title)
        
        # Separator line
        line_y = y + height - 0.95 * inch
        c.setStrokeColor(accent_color)
        c.setLineWidth(0.5)
        c.line(x + stripe_width + 0.15 * inch, line_y, x + width - 0.15 * inch, line_y)
        
        # Contact info (bottom left)
        c.setFont("Helvetica", 7)
        c.setFillColor(HexColor("#333333"))
        contact_y = y + 0.45 * inch
        c.drawString(x + stripe_width + 0.15 * inch, contact_y, f"📧 {self.email}")
        c.drawString(x + stripe_width + 0.15 * inch, contact_y - 0.15 * inch, f"📱 {self.phone}")
        
        if self.website:
            c.drawString(x + stripe_width + 0.15 * inch, contact_y - 0.30 * inch, f"🌐 {self.website}")
        
        # QR Code (bottom right) - only if image path is provided
        if qr_img_path and os.path.exists(qr_img_path):
            qr_size = 0.7 * inch
            qr_x = x + width - qr_size - 0.1 * inch
            qr_y = y + 0.1 * inch
            c.drawImage(qr_img_path, qr_x, qr_y, width=qr_size, height=qr_size)

    def generate(self):
        """Generate ASCII text version (legacy method)"""
        return self.generate_text()

# Example usage
if __name__ == "__main__":
    card = BusinessCard(
        name="Sutton Elliott",
        title="Computer Engineering Student",
        company="Texas A&M University",
        email="sutton.elliott777@gmail.com",
        phone="+1 972-821-3843",
        website="https://www.linkedin.com/in/suelliott77/"
    )
    
    # Print ASCII version
    print("ASCII Version:")
    print(card.generate())
    
    # Generate PDF
    print("\nGenerating PDF...")
    card.generate_pdf("student_cards.pdf")
