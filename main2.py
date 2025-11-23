from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from PIL import Image
import io

# ---------------------------------
# CONFIG Cloudinary
# ---------------------------------
cloudinary.config(
    cloud_name="dmdgnqg9b",
    api_key="873313492956343",
    api_secret="Q5uRhGNFsWhtCM09ew4RJ0TXEyQ",
    secure=True
)

# ---------------------------------
# FASTAPI
# ---------------------------------
app = FastAPI()

# ---------------------------------
# CORS CONFIG
# ---------------------------------
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------
# Upload API + LOG
# ---------------------------------
@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        # Resize ให้เล็กลง (เช่น กว้างไม่เกิน 1280px)
        image.thumbnail((1280, 1280))

        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=85)
        buffer.seek(0)

        result = cloudinary.uploader.upload(
            buffer,
            folder="rwtf_udon/"
        )

        return {"url": result.get("secure_url")}
    except Exception as e:
        return {"error": str(e)}