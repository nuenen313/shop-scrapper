import cv2
import pytesseract
import os
import re
from firebaseHandler import FirebaseManager

def process_file(files_directory, shop):
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    folders_list = os.listdir(files_directory)
    i=0
    db_data={}
    for folder in folders_list:
        folder_dir = files_directory+folder
        date = folder
        files_list = os.listdir(folder_dir)
        for file in files_list:
            filename = os.path.join(files_directory,folder,file)
            print(f"*   Processing {filename}")
            img = cv2.imread(filename)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            thresh1 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                            cv2.THRESH_BINARY_INV, 11, 2)
            bnt = cv2.bitwise_not(thresh1)
            text = pytesseract.image_to_string(bnt, lang='pol', config='--psm 11')
            if re.search(r'\b(piwo|alkoholu)\b', text, re.IGNORECASE):
                key = f"offer{i}"
                db_data[key] = {
                    "shop": shop,
                    "date": date,
                    "type": "piwo",
                    "storage_path": ""
                }
                print(text)
                storage_url = f"images/{date}_{shop}_{file}"
                image_url = firebase_manager.upload_image(
                     image_path=filename,
                     storage_path=storage_url
                 )
                db_data[key]["storage_path"] = storage_url
                firebase_manager.upload_data(db_data)
                i += 1
                print(f"Image URL: {image_url}")
            else:
                continue

if __name__ == "__main__":
    firebase_manager = FirebaseManager(
        service_account_key="serviceAccountKey.json",
        bucket_name="your-bucket-name",
        database_url="your-firebase-url"
    )
    process_file("C:\\Users\\Marta\\Desktop\\scrape\\", "lidl")
