from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
import cloudinary
import cloudinary.uploader
from PIL import Image
import io

cloudinary.config(
    cloud_name="dmdgnqg9b",
    api_key="873313492956343",
    api_secret="Q5uRhGNFsWhtCM09ew4RJ0TXEyQ",
    secure=True
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = MongoClient("mongodb+srv://kompetch:1234@cluster0.0ng1kw5.mongodb.net/?appName=Cluster0")
db = client["rwtf_udon"]
collection = db["rwtf_runners"]

@app.post("/register-runner")
async def register_runner(
    full_name: str = Form(""),
    phone: str = Form(""),
    citizen_id: str = Form(""),
    reward: str = Form(""),
    distance: str = Form(""),
    shirt_size: str = Form(""),
    shirt_status: bool = Form(False),
    bib: str = Form(""),
    health_package: bool = Form(False),
    medical_condition: str = Form(""),
    medications: str = Form(""),
    note: str = Form(""),
    file: UploadFile = File(None)
):
    try:
        image_url = None

        if file:
            contents = await file.read()
            image = Image.open(io.BytesIO(contents))
            image.thumbnail((1280, 1280))

            buffer = io.BytesIO()
            image.save(buffer, format="JPEG", quality=85)
            buffer.seek(0)

            result_cloud = cloudinary.uploader.upload(buffer, folder="rwtf_udon/")
            image_url = result_cloud.get("secure_url")

        doc = {
            "full_name": full_name,
            "phone": phone,
            "citizen_id": citizen_id,
            "reward": reward,
            "distance": distance,
            "shirt_size": shirt_size,
            "shirt_status": shirt_status,
            "bib": bib,
            "health_package": health_package,
            "medical_condition": medical_condition,
            "medications": medications,
            "note": note,
            "image_url": image_url
        }

        result = collection.insert_one(doc)

        # 🔥 แปลง ObjectId เป็น string ก่อนส่งกลับ
        doc["_id"] = str(result.inserted_id)

        return {"message": "success", "data": doc}

    except Exception as e:
        print("ERROR:", e)
        return {"error": str(e)}
