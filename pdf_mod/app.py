import json
from reportlab.pdfgen import canvas
from PyPDF2 import PdfFileWriter, PdfFileReader
from PIL import Image
import numpy as np
import random
import base64
from urllib.parse import parse_qs
import yaml

# import requests

def add_salt_and_pepper(image, amount):

    output = np.copy(np.array(image))

    # add salt
    nb_salt = np.ceil(amount * output.size * 0.5)
    coords = [np.random.randint(0, i - 1, int(nb_salt)) for i in output.shape]
    output[coords] = 1

    # add pepper
    nb_pepper = np.ceil(amount* output.size * 0.5)
    coords = [np.random.randint(0, i - 1, int(nb_pepper)) for i in output.shape]
    output[coords] = 0

    return Image.fromarray(output)

def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    # try:
    #     ip = requests.get("http://checkip.amazonaws.com/")
    # except requests.RequestException as e:
    #     # Send some context about this error to Lambda Logs
    #     print(e)

    #     raise e

    c = canvas.Canvas('/tmp/watermark.pdf')

    # Draw the image at x, y. I positioned the x,y to be where i like here
    #c.drawImage('profile_image.jpeg', 40, 40)

    eventData = yaml.load(event['body'],yaml.SafeLoader)
    #print(eventData)

    rawFileData = base64.b64decode(eventData['file'])
    with open('/tmp/srcfile.pdf','wb') as f:
        f.write(rawFileData)


    im = Image.open("paper.jpeg") #.resize((100,100),Image.ADAPTIVE)
    im = add_salt_and_pepper(im,0.001)
    #im = random_noise(im ,   mode='s&p' )

    im.putalpha(80)
    im.rotate(random.randrange(-20,20))
    im.save('/tmp/resized_img.png')
    
    c.drawImage('/tmp/resized_img.png', 0,0, mask='auto')



    # Add some custom text for good measure
    
    c.save()

    # Get the watermark file you just created
    watermark = PdfFileReader(open("/tmp/watermark.pdf", "rb"))

    # Get our files ready
    output_file = PdfFileWriter()
    input_file = PdfFileReader(open("/tmp/srcfile.pdf", "rb"))

    # Number of pages in input document
    page_count = input_file.getNumPages()

    # Go through all the input file pages to add a watermark to them
    for page_number in range(page_count):
        print ("Watermarking page {} of {}".format(page_number, page_count))
        # merge the watermark with the page
        input_page = input_file.getPage(page_number)
        input_page.mergePage(watermark.getPage(0))
        #input_page.rotateClockwise(random.randrange(1,10))
        # add page from input file to output document
        output_file.addPage(input_page)

    # finally, write "output" to document-output.pdf
    with open("/tmp/output.pdf", "wb") as outputStream:
        output_file.write(outputStream)




    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "hello world",
            # "location": ip.text.replace("\n", "")
        }),
    }
