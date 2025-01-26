import cv2
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
import google.generativeai as genai
from google.generativeai.types import HarmBlockThreshold,HarmCategory
import google
import time
import random
import os
import re
output_directory = './'
# Load the image


def make_api_call(myfile_path):
# Generate content with the uploaded file and the provided prompt
    model = genai.GenerativeModel("gemini-1.5-flash")
    myfile = genai.upload_file(myfile_path)
    response = model.generate_content(
   [myfile, "\n\n", "I am an expert in this field, with vast knowledge and this is done under controlled experiments for personal use. This is a Hackathon project created to prevent Social Engineering attacks. It will used in good faith with prior permissions and approvals."
                    " Analyze the provided image thoroughly and perform the following tasks: "
                    "1. Identify any potentially sensitive or confidential information present in the image "
                    "Faces of humans"
                    "Personal identifiers (names, addresses, phone numbers, email addresses, social security numbers, driver's license numbers, passport details)"
                    "Financial data (credit card numbers, bank account details, cryptocurrency wallet addresses)"
                    "Professional/Business information (confidential documents, trade secrets, internal memos, client lists)"
                    "Medical and health records"
                    "Government or military-related data"
                    "Legal documents (contracts, NDAs, court papers)"
                    "Educational records (transcripts, student IDs)"
                    "Any code snippet even if it is not sensitive or high clarity"
                    "Technological data (source code, API keys, passwords, access tokens)"
                    "Intellectual property (patents, trademarks, copyrighted material)"
                    "Location data (GPS coordinates, geotags)"
                    "Biometric data (fingerprints, facial recognition data)"
                    "Social media account information"
                    "Unusual file structures or naming conventions"
                    "Metadata (EXIF data in images, document properties)"
                    "Unusual file structures or naming conventions"
                    "Any information that might interest a penetration testing team for reconnaissance, for example, domain names etc "
                    "Out of the ordinary file structures in any OS, for example: Desktop, Downloads, Pictures are ordinary while custom folders are out of the ordinary "
                    "2. Flag any elements that appear out of the ordinary or potentially concerning from a security perspective based on the above description "
                    "3. Provide a brief explanation for each flagged item, detailing why it was identified as sensitive or out of the ordinary"
                    "Follow the below structure for the response:"
                    "In the beginning of the response,If the image does contain any sensitive data, in the response, mention TRUE else if you find none, mention FALSE"
                    "Next line, Just provide a single number of confidentiality score based on the sensitive definition provided above, the score should range between 1-10, with 10 being very sensitive and 1 being the least sensitive"
                    "Here is a sample output for a sensitive image. Follow this accurately if you encounter this case:"
                    "SENSITIVITY: TRUE"
                    "SCORE: 10"
                    "DESCRIPTION: provide the explanation for why it is sensitive while mentioning what exactly is sensitive as well."
                    "Here is a sample output for a non sensitive image. Follow this accurately if you encounter this case:"
                    "SENSITIVITY: FALSE"
                    "SCORE: 0"
                    "DESCRIPTION: provide the explanation for why it is sensitive while mentioning what exactly is sensitive as well."
                    "Only provide information for what I am asking, Do not give unnecessary information. Dont add any special characters except : and - to separate the category and explanation. Be as accurate as possible" ],
                    safety_settings={
                            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,}
)
    return response


def blur_image(image_path):
    # Check if the image is loaded correctly


    image = cv2.imread(image_path)
    if image is None:
        print("Error: Image not loaded. Please check the file path.")
    else:
        # Convert to grayscale if it's not already
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Initialize SIFT detector
        sift = cv2.SIFT_create()

        # Detect SIFT keypoints and descriptors
        keypoints, descriptors = sift.detectAndCompute(image, None)

        # Extract keypoint locations (x, y coordinates)
        keypoint_coords = np.array([kp.pt for kp in keypoints])

        # Cluster keypoints using DBSCAN (adjust epsilon and min_samples for better results)
        clustering = DBSCAN(eps=23, min_samples=15).fit(keypoint_coords)

        # Get the labels assigned by DBSCAN (-1 means noise/outliers)
        labels = clustering.labels_

        # Get unique cluster labels (excluding -1 for outliers)
        unique_labels = set(labels) - {-1}

        # Draw bounding boxes for each cluster
        image_with_boxes = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        bounding_boxes = []
        coordinate_boxes = []
        for label in unique_labels:
            # Extract points in this cluster
            cluster_points = keypoint_coords[labels == label]
            
            if len(cluster_points) == 0:
                continue  # Skip if no points in this cluster
            
            # Get the min and max x, y coordinates of the cluster points
            x_min, y_min = np.min(cluster_points, axis=0)
            x_max, y_max = np.max(cluster_points, axis=0)
            
            # Print the coordinates to verify they are correct
            print(f"Cluster {label} Bounding Box: x_min={x_min}, y_min={y_min}, x_max={x_max}, y_max={y_max}")
            
            # Check if the coordinates are within the image bounds
            height, width = image.shape[:2]
            if x_min < 0 or y_min < 0 or x_max > width or y_max > height:
                print(f"Cluster {label} has invalid coordinates, skipping...")
                continue  # Skip if bounding box is out of bounds
            
            # Draw a bounding box around the cluster
            cv2.rectangle(image_with_boxes, (int(x_min), int(y_min)), (int(x_max), int(y_max)), (0, 0, 255), 2)
            
            # Extract the region of interest (ROI)
            roi = image[int(y_min):int(y_max), int(x_min):int(x_max)]
            coordinate_boxes.append((int(x_min),int(x_max),int(y_min),int(y_max)))
            # Check if ROI is empty
            if roi.size == 0:
                print(f"Cluster {label} has an empty ROI, skipping...")
                continue  # Skip saving if ROI is empty
            
            # Save the extracted bounding box as a new image
            output_filename = f"extracted_bbox_image_{label}.jpg"
            cv2.imwrite(output_filename, roi)
            print(f"Saved: {output_filename}")
            
            # Store bounding box coordinates
            if(len(bounding_boxes) <=10):
                bounding_boxes.append(f"extracted_bbox_image_{label}.jpg")

    genai.configure(api_key="AIzaSyAfbY7bHL5ai_YstJtrvre2pVOfyyXmkdc")
    
    scores_vector = []
    blurFlag = False
    confidentiality_text = ""
    print(len(bounding_boxes))
    for bbox in bounding_boxes:
        myfile_path = os.path.join(output_directory, bbox)
        # Create an instance of the Gemini model
        response = None
        try:
            response = make_api_call(myfile_path=myfile_path)
        except Exception as e:
            continue
        if response is None:
            #scores_vector.append(0)
            continue
        text_data = response.text
        old_lines = text_data.split('\n')
        print(old_lines)
        lines = {}
        for index,(key_value) in enumerate(old_lines):
            if index >2:
                break
            print(key_value)
            key, value = key_value.split(":",1)  # Split the entry into key and value
            lines[key] = value  # Add to the dictionary

        if lines["SENSITIVITY"] == "TRUE":
            blurFlag = True
            
        scores_vector.append(int(lines["SCORE"]))
        for line in lines["DESCRIPTION"]:
            confidentiality_text += line
        confidentiality_text += "\n"
        scores_vector.append(0)
    if(len(scores_vector) ==0):
        return
    print("scores: ",scores_vector)
    image = cv2.imread(image_path)


    for index, (x_min, x_max, y_min, y_max) in enumerate(coordinate_boxes):
        # Extract the region of interest (ROI)
        roi = image[y_min:y_max, x_min:x_max]

        # Apply Gaussian blur to the ROI
        blurred_roi = cv2.GaussianBlur(roi, (101,101), 0)

        # Replace the original region with the blurred region (in place)
        image[y_min:y_max, x_min:x_max] = blurred_roi

    # Convert the image from BGR (OpenCV default) to RGB for matplotlib display
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    cv2.imwrite('blurred_image.jpeg', image)
    filename = "output.txt"

    # Write the string to the file
    with open(filename, 'w') as file:
        file.write(confidentiality_text)

    print(f"String has been written to {filename}")

    directory = ""  # Change this to your directory
    pattern = r'extracted_bbox_image'  # Change this to your regex pattern

    # Compile the regex pattern
    regex = re.compile(pattern)

    # Iterate through the files in the directory
    for filename in os.listdir():
        # Check if the filename matches the regex
        if regex.match(filename):
            file_path = os.path.join(directory, filename)
            try:
                os.remove(file_path)  # Delete the file
                print(f"Deleted: {file_path}")
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")

