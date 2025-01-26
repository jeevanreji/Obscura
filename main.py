# main.py
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import shutil
import os
from obscura import blur_image
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello, Google Cloud Run"}
UPLOAD_DIRECTORY = ""
@app.post("/upload-image-1/")
async def upload_image(image: UploadFile = File(...)):
    # Save the uploaded image to the designated directory
    image_path = os.path.join(UPLOAD_DIRECTORY, image.filename)
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    
    blur_image(image.filename)

    file_path = f'./blurred_image.jpeg'
    if os.path.isfile(file_path):
        # Return the image as a FileResponse
        return FileResponse(file_path, media_type="image/jpeg")
    else:
        return {"error": "File not found."}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

