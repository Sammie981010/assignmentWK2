from PIL import Image, ImageDraw, ImageFont
import os

# Create a simple icon for the app
def create_app_icon():
    # Create a 256x256 image with light blue background
    size = 256
    img = Image.new('RGB', (size, size), '#E3F2FD')
    draw = ImageDraw.Draw(img)
    
    # Draw a circle background
    circle_margin = 20
    draw.ellipse([circle_margin, circle_margin, size-circle_margin, size-circle_margin], 
                fill='#1976D2', outline='#0D47A1', width=4)
    
    # Try to add text (fallback if font not available)
    try:
        font = ImageFont.truetype("arial.ttf", 60)
    except:
        font = ImageFont.load_default()
    
    # Add "CF" text for CESS FOODS
    text = "CF"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - 10
    
    draw.text((x, y), text, fill='white', font=font)
    
    # Add small subtitle
    try:
        small_font = ImageFont.truetype("arial.ttf", 20)
    except:
        small_font = ImageFont.load_default()
    
    subtitle = "FOODS"
    bbox = draw.textbbox((0, 0), subtitle, font=small_font)
    sub_width = bbox[2] - bbox[0]
    sub_x = (size - sub_width) // 2
    sub_y = y + text_height + 10
    
    draw.text((sub_x, sub_y), subtitle, fill='#BBDEFB', font=small_font)
    
    # Save as ICO file
    img.save('app_icon.ico', format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
    print("Icon created: app_icon.ico")

if __name__ == "__main__":
    try:
        create_app_icon()
    except ImportError:
        print("PIL not installed. Creating simple icon...")
        # Create a simple text file as placeholder
        with open('app_icon.ico', 'w') as f:
            f.write("# Icon placeholder - install PIL to create proper icon")