from PIL import Image, ImageDraw, ImageFont
import qrcode
def drawText(draw, x, y, text, width, alignment, fontSize, isBold=False, lineMargin=10, fontType=None):
    # Define font with optional boldness
    try:
        if(fontType):
            font = ImageFont.truetype(fontType, fontSize)
        elif isBold:
            font = ImageFont.truetype("arialBd.ttf", fontSize)  # Use bold font
        else:
            font = ImageFont.truetype("arial.ttf", fontSize)  # Use regular font
    except IOError:
        print("Font file not found. Please ensure 'arial.ttf' and 'arialbd.ttf' are available or provide valid font files.")
        return 0

    lines = []
    words = text.split()
    currentLine = ""

    # Split text into lines that fit within the max_width
    for word in words:
        testLine = f"{currentLine} {word}".strip()
        bbox = draw.textbbox((0, 0), testLine, font=font)
        textWidth = bbox[2] - bbox[0]
        
        if textWidth > width:
            if currentLine:
                lines.append(currentLine)
                currentLine = word
            else:
                lines.append(testLine)
                currentLine = ""
        else:
            currentLine = testLine

    if currentLine:
        lines.append(currentLine)
    
    # Calculate height needed for the text
    textHeight = sum([draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] for line in lines])
    
    yOffset = y
    
    # Draw each line of text
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        lineWidth = bbox[2] - bbox[0]
        lineHeight = bbox[3] - bbox[1]
        
        if alignment == "center":
            xPosition = x - lineWidth / 2
        elif alignment == "right":
            xPosition = x - lineWidth
        else:  # left
            xPosition = x
        
        draw.text((xPosition, yOffset), line, font=font, fill="black")
        yOffset += lineHeight + lineMargin

    return textHeight + lineMargin * (len(lines) - 1)  # Add margin space for all lines except the last

def generateLotLabel(data,width=696,verticalMargin=45,outputPath="label.png"):
    # Create a drawing context to calculate the required height
    dummyImage = Image.new("RGB", (width, 1), "white")
    draw = ImageDraw.Draw(dummyImage)

    # Define text, positions, and alignments
    texts = [
        {"text": '#'+data['item']+ ' '+data['itemLabel'].upper(), "x": width // 2, "width": width * 0.95, "align": "center", "fontSize": 70, "isBold": True},
        {"text":' ' +'--------------------'*5+' ', "x": width // 2, "width": width * 0.95, "align": "center", "fontSize": 30, "isBold": True},        
        {"text": 'QUANTITY - ' + str(data['quantityToBeBuild']), "x": width // 2, "width": width * 0.95, "align": "center", "fontSize": 70, "isBold": True},
        {"text": "Lot No.: " + data['lotNumber'], "x": 40, "width": width * 0.95, "align": "left", "fontSize": 60, "isBold": True},        
        {"text": "Expiry Date: " + data['expDate'], "x": 40, "width": width * 0.95, "align": "left", "fontSize": 60, "isBold": False},
        {"text": "Date of Manuf.: " + data['timeStamp'].split(' ')[0], "x": 40, "width": width * 0.95, "align": "left", "fontSize": 50, "isBold": False},
        {"text": "Initiated By: " + data['requestedBy'].title(), "x": 40, "width": width * 0.95, "align": "left", "fontSize": 50, "isBold": False}
    ]

    # Calculate total height needed for the label
    totalTextHeight = 0
    currentY = 0

    for textInfo in texts:
        textHeight = drawText(draw, textInfo["x"], currentY, textInfo["text"], textInfo["width"], textInfo['align'], textInfo["fontSize"], textInfo["isBold"], verticalMargin)
        totalTextHeight += textHeight + verticalMargin
        currentY += textHeight + verticalMargin

    # Create the final image with calculated height
    imageHeight = totalTextHeight + 100  # Add some extra padding
    image = Image.new("RGB", (width, imageHeight), "white")
    draw = ImageDraw.Draw(image)

    # Draw each text onto the final image
    currentY = 50
    for textInfo in texts:
        textHeight = drawText(draw, textInfo["x"], currentY, textInfo["text"], textInfo["width"], textInfo['align'], textInfo["fontSize"], textInfo["isBold"], verticalMargin)
        currentY += textHeight + verticalMargin

    # Save the image
    image.save(outputPath)
    print(f"Image saved as {outputPath}")
    return outputPath

def generateSkidLabel(data, logoPath='logoBW.png', width=696, verticalMargin=35, outputPath="label.png"):
    # Create a drawing context to calculate the required height
    dummyImage = Image.new("RGB", (width, 1), "white")
    draw = ImageDraw.Draw(dummyImage)

    # Define text, positions, and alignments
    texts = [
        {"text": '#'+data['item']+ ' '+data['itemLabel'].upper(), "x": width // 2, "width": width * 0.95, "align": "center", "fontSize": 70, "isBold": True},
        {"text":' ' +'--------------------'*6+' ', "x": width // 2, "width": width * 0.95, "align": "center", "fontSize": 30, "isBold": True},        
        {"text": 'BATCH SKID NO. - ' + str(len(data['printedStickers'])), "x": width // 2, "width": width * 0.95, "align": "center", "fontSize": 60, "isBold": True},
        {"text":' ' +'--------------------'*6+' ', "x": width // 2, "width": width * 0.95, "align": "center", "fontSize": 30, "isBold": True},
        {"text": "Lot No.: " + data['lotNumber'], "x": 40, "width": width * 0.95, "align": "left", "fontSize": 60, "isBold": True},           
    ]

    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=15, border=2)
    qr.add_data(data['timeStamp']+'@'+data['item']+'@'+data['lotNumber']+'@'+str(len(data['printedStickers']))+'G')
    qr.make(fit=True)
    qrImage = qr.make_image(fill='black', back_color='white')
    qrWidth, qrHeight = qrImage.size

    # Calculate total height needed for the label
    totalTextHeight = 0
    currentY = 0
    logoHeight = 0

    # If a logo path is provided, load and paste the logo
    if logoPath:
        logo = Image.open(logoPath)
        logo_width, logo_height = logo.size
        logo_resized = logo.resize((width // 3, int((width // 3) * logo_height / logo_width)))  # Resize logo while maintaining aspect ratio
        logo_x = (width - logo_resized.width) // 2
        logoHeight = logo_resized.height

    totalTextHeight = logoHeight
    for textInfo in texts:
        textHeight = drawText(draw, textInfo["x"], currentY, textInfo["text"], textInfo["width"], textInfo['align'], textInfo["fontSize"], textInfo["isBold"], verticalMargin)
        totalTextHeight += textHeight + verticalMargin
        currentY += textHeight + verticalMargin

    # Add space for QR code
    imageHeight = totalTextHeight + qrHeight + 80  # Add some extra padding
    image = Image.new("RGB", (width, imageHeight), "white")
    draw = ImageDraw.Draw(image)

    # If a logo path is provided, load and paste the logo
    if logoPath:
        image.paste(logo_resized, (3, 10)) 
        drawText(draw, logo_resized.width + 4, 10 + logoHeight * 0.4, 'Mr.Goudas', width - logo_resized.width - 10, 'left', 98, True, 0, 'timeNew.ttf')

    # Draw each text onto the final image
    currentY = 30 + logoHeight
    for textInfo in texts:
        textHeight = drawText(draw, textInfo["x"], currentY, textInfo["text"], textInfo["width"], textInfo['align'], textInfo["fontSize"], textInfo["isBold"], verticalMargin)
        currentY += textHeight + verticalMargin

    # Paste the QR code at the bottom
    qr_x = (width - qrWidth) // 2
    image.paste(qrImage, (qr_x, currentY))  # 20 pixels padding from the bottom

    currentY+=qrHeight+10
    drawText(draw, width // 2, currentY, 'www.goudas.ca', width , 'center', 28, True, 0, 'timeNew.ttf')


    # Save the image
    image.save(outputPath)

    print(f"Image saved as {outputPath}")
    return outputPath

# Example usage
if __name__ == "__main__":
    data = {
        'approvedPo': '3184',
        'buildGfp': '0',
        'buildMemo': '',
        'buildQuantity': 0,
        'buildTimestamp': '',
        'casePerSkid': 50,
        'consumption': 484,
        'consumptionRate': 44,
        'expDate': '2027-09-05',
        'gfp': 'GFP0003',
        'gfpLabel': 'WHITE LG RICE',
        'gfpOnHand': 166499.41,
        'isBuild': False,
        'item': '888',
        'itemLabel': 'USA LONG WHITE RICE 1 X 20 KG',
        'itemOnHand': 0,
        'lotNumber': '31840888',
        'maxSkids': 0.22,
        'poAvailableQts': 11.350227272727352,
        'poQuantity': 42000,
        'printedStickers': [{'name': 'Others', 'timeStamp': '2024-09-05 23:03:16_396'}],
        'quantityToBeBuild': 11,
        'requestedBy': 'Santhiran',
        'timeStamp': '2024-09-05 23:02:19_654',
        'type': 'Build'
        }


    generateSkidLabel(data)
