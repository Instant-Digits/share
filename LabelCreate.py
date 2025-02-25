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

    casePerSkid = data['printedStickers'][-1]['casesInSkid'] if len(data['printedStickers'])>0 and 'casesInSkid' in data['printedStickers'][-1] else data['casePerSkid']
    # Define text, positions, and alignments
    texts = [
        {"text":str(casePerSkid)+' Cases X #'+data['item']+ ' '+data['itemLabel'].upper(), "x": width // 2, "width": width * 0.98, "align": "center", "fontSize": 65, "isBold": True},
        {"text":' ' +'--------------------'*6+' ', "x": width // 2, "width": width * 0.95, "align": "center", "fontSize": 30, "isBold": True},        
        {"text": 'BATCH SKID NO. - ' + str(len(data['printedStickers'])), "x": width // 2, "width": width * 0.95, "align": "center", "fontSize": 60, "isBold": True},
        {"text":' ' +'--------------------'*6+' ', "x": width // 2, "width": width * 0.95, "align": "center", "fontSize": 30, "isBold": True},
        {"text": "Lot No.: " + data['lotNumber'], "x": 40, "width": width * 0.95, "align": "left", "fontSize": 60, "isBold": True},           
    ]

    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=22, border=1)
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


def generatePickerLabel(data, logoPath='logoBW.png', width=696, verticalMargin=35):
    # Create a drawing context to calculate the required height
    dummyImage = Image.new("RGB", (width, 1), "white")
    draw = ImageDraw.Draw(dummyImage)


    maxSkid=data['usedSkids'] if 'usedSkids' in data else 1
    # Define text, positions, and alignments
    outPut=[]
    for skidNo in range(maxSkid):
        outputPath='PikerLabel_'+str(skidNo+1)+'.png'
        texts = [
            {"text":' ' +'--------------------'*6+' ', "x": width // 2, "width": width * 0.95, "align": "center", "fontSize": 30, "isBold": True},        
            {"text": 'INVOICE - ' + data['invoiceSN']+' ('+str(skidNo+1)+'/'+str(maxSkid)+')', "x": width // 2, "width": width * 0.95, "align": "center", "fontSize": 60, "isBold": True},
            {"text":' ' +'--------------------'*6+' ', "x": width // 2, "width": width * 0.95, "align": "center", "fontSize": 30, "isBold": True},
            {"text":  '#'+ data['nameAcc']+'-'+data['nameAddress'], "x": 30, "width": width * 0.95, "align": "left", "fontSize": 42, "isBold": False},    
        ]

        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=20, border=1)
        qr.add_data('PickerLabel@'+data['timeStamp']+'@'+data['invoiceSN']+'@'+str(skidNo+1)+'G')
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
        verticalMargin=25
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
            drawText(draw, logo_resized.width + 4, 10 + logoHeight * 0.25, 'Mr.Goudas', width - logo_resized.width - 10, 'left', 98, True, 0, 'timeNew.ttf')
            drawText(draw, logo_resized.width + 4, 10 + logoHeight * 0.6, 'Picker Label', width - logo_resized.width - 10, 'left', 78, True, 0, 'timeNew.ttf')

        # Draw each text onto the final image
        currentY = 30 + logoHeight
        
        for textInfo in texts:
            textHeight = drawText(draw, textInfo["x"], currentY, textInfo["text"], textInfo["width"], textInfo['align'], 
                                textInfo["fontSize"], textInfo["isBold"], verticalMargin)
            currentY += textHeight + verticalMargin

        # Paste the QR code at the bottom
        qr_x = (width - qrWidth) // 2
        image.paste(qrImage, (qr_x, currentY))  # 20 pixels padding from the bottom

        currentY+=qrHeight+10
        drawText(draw, width // 2, currentY, 'www.goudas.ca', width , 'center', 28, True, 0, 'timeNew.ttf')


        # Save the image
        image.save(outputPath)
        outPut.append(outputPath)

    print(outPut)
    return outPut

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
        'printedStickers': [{'name': 'Others','casesInSkid' 'timeStamp': '2024-09-05 23:03:16_396'}],
        'quantityToBeBuild': 11,
        'requestedBy': 'Santhiran',
        'timeStamp': '2024-09-05 23:02:19_654',
        'type': 'Build'
        }

    data2 = {
        "comment": " ",
        "itemList": {
            "Goudas Product_Can Beans_MG CANS FAVA BROAD BEANS 24 X 540 ML@80": {
                "label": "MG CANS FAVA BROAD BEANS 24 X 540 ML",
                "unitPrice": "55.09",
                "taxCode": "E",
                "quantity": 1,
                "reqPrice": False,
                "qr": "80",
                "arrange": False,
                "inStock": "20.0",
                "itemsPerCase": 24,
                "id": "Goudas Product_Can Beans_MG CANS FAVA BROAD BEANS 24 X 540 ML@80",
                "cost": "39.37"
            },
            "Goudas Product_other_Pallet@999": {
                "quantity": 1,
                "image2": False,
                "reqPrice": False,
                "id": "Goudas Product_other_Pallet@999",
                "image1": False,
                "label": "Pallet",
                "taxCode": "H",
                "arrange": False,
                "unitPrice": "15",
                "cost": "15",
                "qr": "999"
            }
        },
        "type": "Sales_Progress",
        "chequeUrl": False,
        "alert": False,
        "returnItems": {
            "Goudas Product_Dry Beans_MG GREEN LENTILS RICHLEA 15 X 450 GR@21": {
                "id": "Goudas Product_Dry Beans_MG GREEN LENTILS RICHLEA 15 X 450 GR@21",
                "cases": 4,
                "taxCode": "E",
                "units": 0,
                "label": "MG GREEN LENTILS RICHLEA 15 X 450 GR",
                "qr": "21"
            },
            "Goudas Product_Rice_MG PARBOIL RICE 1 X 40 KG@2": {
                "qr": "2",
                "id": "Goudas Product_Rice_MG PARBOIL RICE 1 X 40 KG@2",
                "taxCode": "E",
                "label": "MG PARBOIL RICE 1 X 40 KG",
                "cases": 4,
                "units": 0
            },
            "Goudas Product_Dry Beans_MG COW PEAS 15 X 450 GR@20": {
                "qr": "20",
                "label": "MG COW PEAS 15 X 450 GR",
                "units": 2,
                "taxCode": "E",
                "id": "Goudas Product_Dry Beans_MG COW PEAS 15 X 450 GR@20",
                "cases": 4
            }
        },
        "name": "BLESSING SUPERMARKET",
        "terms": 30,
        "date": "2024-09-11",
        "salesRepEmail": False,
        "timeStamp": "2024-06-05 16:45:43_700",
        "namePhone": "647 330 5291",
        "itemChanges": False,
        "salesRep": "SALESMEN",
        "signature2": False,
        "salesRepDetails": {
            "userName": "SALESMEN",
            "uid": "123231-SALESMEN",
            "name": "SALESMEN",
            "type": "salesRep"
        },
        "lastLocation": {
            "longitude": -79.5046761,
            "address": "Vaughan, Ontario, Canada.",
            "latitude": 43.7892528
        },
        "supType": False,
        "location": {
            "latitude": 43.7892528,
            "longitude": -79.5046761,
            "address": "Vaughan, Ontario, Canada."
        },
        "printRemarks": False,
        "soldPriceFrom": "2024-03-05",
        "outstandingInfo": False,
        "creditInvoice": False,
        "linkStamps": False,
        "nameAddress": "BLESSING SUPERMARKET 3601 Lawrence Avenue east No 05 Scarborough, ON M1G 1P5 Canada",
        "creditAmount": 0,
        "signature1": False,
        "track": [
            {
                "from": "SALESMEN@salesRep",
                "taskID": "OR1@0",
                "type": "Order",
                "timeStamp": "2024-06-05 16:49:20_727",
                "task": "Order Created",
                "to": "MAINDESK@orderDesk"
            },
            {
                "kioskID": "NOT in Kiosk",
                "taskID": "OR2@1",
                "task": "Order Received",
                "isSign": "MAINDESK",
                "type": "Sales_Progress",
                "to": "MAINDESK@orderDesk",
                "timeStamp": "2024-06-12 23:12:22_736",
                "from": "MAINDESK@orderDesk",
                "buttonName": "RECEIVED ACKNOWLEDGEMENT"
            },
            {
                "task": "Quantity & Price Verfication",
                "to": "MAINDESK@orderDesk",
                "timeStamp": "2024-07-17 17:33:09_491",
                "isSign": "MAINDESK",
                "from": "MAINDESK@orderDesk",
                "kioskID": "NOT in Kiosk",
                "buttonName": "UPDATE QUANTIY & PRICE",
                "taskID": "SP01@2",
                "type": "Sales_Progress"
            },
            {
                "taskID": "SP02@3",
                "kioskID": "NOT in Kiosk",
                "buttonName": "EXPORT EXCELL FOR QB",
                "isSign": "MAINDESK",
                "task": "QB Export",
                "type": "Sales_Progress",
                "timeStamp": "2024-08-24 14:25:28_769",
                "to": "MAINDESK@orderDesk",
                "from": "MAINDESK@orderDesk"
            },
            {
                "isSign": False,
                "timeStamp": "2024-09-11 16:41:29_873",
                "taskID": "SP03@4",
                "to": "MAINDESK@orderDesk",
                "task": "QB Invoice Number Updated",
                "type": "Sales_Progress",
                "buttonName": "SET THE QB INVOICE NUMBER",
                "from": "MAINDESK@orderDesk",
                "kioskID": "NOT in Kiosk"
            }
        ],
        "nameAddressList": [
            "BLESSING SUPERMARKET #3",
            "3601 Lawrence Avenue east",
            "No 05",
            "Scarborough, ON, M1G 1P5."
        ],
        "orderNo": "SA130174",
        "nameAcc": "3",
        "invoiceSN": "105050",
        "nameEmail": "blessingsupermarket01@gmail.com",
        "itemNames": "MG CANS FAVA BROAD BEANS 24 X 540 ML,Pallet",
        "salesRepPhone": "07776658048",
        "time": "04:45:43 pm",
        "nameID": "3",
        'usedSkids':3
    }


    generatePickerLabel(data2)
