def add_letterhead(c, width, height):
    """Add company letterhead to PDF"""
    # Logo centered
    logo_width = 60
    logo_x = (width - logo_width) / 2
    c.drawImage("logo.png", logo_x, height - 80, width=logo_width, height=40)
    
    # Company name centere
    c.setFont("Helvetica-Bold", 20)
    text_width = c.stringWidth("CESS FOODS", "Helvetica-Bold", 20)
    c.drawString((width - text_width) / 2, height - 90, "CESS FOODS")
    
    # Company details centered
    c.setFont("Helvetica", 10)
    
    tagline = "Quality Chicken Supplies & Distribution"
    text_width = c.stringWidth(tagline, "Helvetica", 10)
    c.drawString((width - text_width) / 2, height - 105, tagline)
    
    email = "Email: cessfoods@gmail.com"
    text_width = c.stringWidth(email, "Helvetica", 10)
    c.drawString((width - text_width) / 2, height - 120, email)
    
    address = "P.O. Box 220, Nairobi, Kenya"
    text_width = c.stringWidth(address, "Helvetica", 10)
    c.drawString((width - text_width) / 2, height - 135, address)

    # Line separator
    c.line(50, height - 150, width - 50, height - 150)
    
    # Return starting Y position for content
    return height - 180