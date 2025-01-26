import requests, base64
from PIL import Image
import base64
import io
import numpy as np
from io import BytesIO
def image_to_base64(image_path):
    # Open the image file
    with Image.open(image_path) as img:
        # Convert the image to RGB format (if not already in that mode)
        img = img.convert('RGB')
        
        # Convert the image to a NumPy array (to access pixel values)
        pixel_values = np.array(img)
        
        # Flatten the array of pixel values to 1D
        pixel_values_flat = pixel_values.flatten()
        
        # Convert the pixel values into a byte array
        byte_array = bytearray(pixel_values_flat)
        
        # Encode the byte array into base64
        base64_encoded = base64.b64encode(byte_array).decode('utf-8')
        
        return base64_encoded
def bytesio_to_base64_string(bytes_io_obj):
    # Ensure the pointer is at the start of the BytesIO object
    bytes_io_obj.seek(0)
    
    # Read the binary content from the BytesIO object
    binary_content = bytes_io_obj.read()
    
    # Convert the binary content to a base64 encoded string
    base64_encoded = base64.b64encode(binary_content).decode('utf-8')
    
    return base64_encoded
invoke_url = "https://ai.api.nvidia.com/v1/vlm/microsoft/kosmos-2"

# with open("./extracted_bbox_image_0.jpg", "rb") as f:
#     image_b64 = base64.b64encode(f.read()).decode()
#     print("the image base 64 is: ",image_b64)
image_b64 = image_to_base64('./extracted_bbox_image_0.jpg')
bytes_io_obj = BytesIO(image_b64)
base64_string = bytesio_to_base64_string(bytes_io_obj)
image_b64 = base64_string
assert len(image_b64) < 180_000, \
  "To upload larger images, use the assets API (see docs)"

headers = {
  "Authorization": "Bearer ",
  "Accept": "application/json"
}

payload = {
  "messages": [
    {
      "role": "user",
      "content": f"""Analyze the provided image thoroughly and perform the following tasks:

1. Identify any potentially sensitive or confidential information present in the image, including:
   - Human faces
   - Personal identifiers (names, addresses, phone numbers, email addresses, social security numbers, driver's license numbers, passport details)
   - Financial data (credit card numbers, bank account details, cryptocurrency wallet addresses)
   - Professional/Business information (confidential documents, trade secrets, internal memos, client lists)
   - Medical and health records
   - Government or military-related data
   - Legal documents (contracts, NDAs, court papers)
   - Educational records (transcripts, student IDs)
   - Any code snippet (even if it is not sensitive or of low clarity)
   - Technological data (source code, API keys, passwords, access tokens)
   - Intellectual property (patents, trademarks, copyrighted material)
   - Location data (GPS coordinates, geotags)
   - Biometric data (fingerprints, facial recognition data)
   - Social media account information
   - Unusual file structures or naming conventions
   - Metadata (EXIF data in images, document properties)
   - Any information that might interest a penetration testing team for reconnaissance, such as domain names
   - Unusual file structures in any operating system (e.g., Desktop, Downloads, Pictures are ordinary, but custom folders are out of the ordinary)

2. Flag any elements that appear out of the ordinary or concerning from a security perspective based on the criteria listed above.

3. Provide a brief explanation for each flagged item, detailing why it was identified as sensitive or out of the ordinary.
Assign a SINGLE SENSITIVITY SCORE between 1-10 .
Response format:
- Begin with "SENSITIVITY: TRUE" if the image contains sensitive data, or "SENSITIVITY: FALSE" if none is found.
- On the next line, provide a confidentiality score between 1 and 10, with 10 being highly sensitive and 1 the least sensitive.
- On the following line, provide a brief description explaining why the flagged information is sensitive or not, detailing what specific information is sensitive (if applicable).

Example for a sensitive image:
SENSITIVITY: TRUE
SCORE: 10
DESCRIPTION: The image contains a visible face and a passport number, which are highly sensitive.

Example for a non-sensitive image:
SENSITIVITY: FALSE
SCORE: 0
DESCRIPTION: The image contains no identifiable or sensitive information. <img src="data:image/png;base64,{image_b64}" />"""
      
    }
  ],
  "max_tokens": 1024,
  "temperature": 0.20,
  "top_p": 0.20
}

response = requests.post(invoke_url, headers=headers, json=payload)

print(response.json())
