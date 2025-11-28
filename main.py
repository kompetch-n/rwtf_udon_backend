from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymongo import MongoClient
from bson import ObjectId
import cloudinary
import cloudinary.uploader
from PIL import Image
import io

# -----------------------------
# CONFIG Cloudinary
# -----------------------------
cloudinary.config(
    cloud_name="dmdgnqg9b",
    api_key="873313492956343",
    api_secret="Q5uRhGNFsWhtCM09ew4RJ0TXEyQ",
    secure=True
)

# -----------------------------
# FASTAPI
# -----------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# MongoDB
# -----------------------------
client = MongoClient("mongodb+srv://kompetch:1234@cluster0.0ng1kw5.mongodb.net/?appName=Cluster0")
db = client["rwtf_udon"]
collection = db["rwtf_runners"]

def serialize_doc(doc):
    doc["_id"] = str(doc["_id"])
    return doc

# -----------------------------
# CREATE (Register Runner)
# -----------------------------
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
    age: str = Form(None),            # 👈 เพิ่ม age
    gender: str = Form(""),           # 👈 เพิ่ม gender
    file: UploadFile = File(None)
):
    try:
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
            "age": age,                 # 👈 เพิ่ม
            "gender": gender,           # 👈 เพิ่ม
            "registration_status": False,
            "image_url": None
        }

        # Upload image
        if file:
            contents = await file.read()
            image = Image.open(io.BytesIO(contents))
            image.thumbnail((1280, 1280))
            buffer = io.BytesIO()
            image.save(buffer, format="JPEG", quality=85)
            buffer.seek(0)
            result_cloud = cloudinary.uploader.upload(buffer, folder="rwtf_udon/")
            doc["image_url"] = result_cloud.get("secure_url")

        result = collection.insert_one(doc)
        doc["_id"] = str(result.inserted_id)
        return {"message": "success", "data": doc}

    except Exception as e:
        return {"error": str(e)}

# -----------------------------
# READ (Get all runners)
# -----------------------------
@app.get("/runners")
def get_runners():
    try:
        docs = [serialize_doc(doc) for doc in collection.find()]
        return {"message": "success", "data": docs}
    except Exception as e:
        return {"error": str(e)}

# -----------------------------
# READ (Get single runner)
# -----------------------------
@app.get("/runner/{runner_id}")
def get_runner(runner_id: str):
    try:
        doc = collection.find_one({"_id": ObjectId(runner_id)})
        if not doc:
            return JSONResponse(status_code=404, content={"error": "Runner not found"})
        return {"message": "success", "data": serialize_doc(doc)}
    except Exception as e:
        return {"error": str(e)}

# -----------------------------
# UPDATE Runner
# -----------------------------
@app.put("/runner/{runner_id}")
async def update_runner(
    runner_id: str,
    full_name: str = Form(None),
    phone: str = Form(None),
    citizen_id: str = Form(None),
    reward: str = Form(None),
    distance: str = Form(None),
    shirt_size: str = Form(None),
    shirt_status: bool = Form(None),
    bib: str = Form(None),
    health_package: bool = Form(None),
    medical_condition: str = Form(None),
    medications: str = Form(None),
    note: str = Form(None),
    registration_status: bool = Form(None),
    age: str = Form(None),             # 👈 เพิ่ม
    gender: str = Form(None),          # 👈 เพิ่ม
    file: UploadFile = File(None)
):
    try:
        update_data = {}

        fields = [
            "full_name", "phone", "citizen_id", "reward", "distance",
            "shirt_size", "shirt_status", "bib", "health_package",
            "medical_condition", "medications", "note",
            "registration_status", "age", "gender"   # 👈 เพิ่ม field ใหม่
        ]

        for field in fields:
            value = locals()[field]
            if value is not None:
                update_data[field] = value

        if file:
            contents = await file.read()
            image = Image.open(io.BytesIO(contents))
            image.thumbnail((1280, 1280))
            buffer = io.BytesIO()
            image.save(buffer, format="JPEG", quality=85)
            buffer.seek(0)
            result_cloud = cloudinary.uploader.upload(buffer, folder="rwtf_udon/")
            update_data["image_url"] = result_cloud.get("secure_url")

        result = collection.update_one({"_id": ObjectId(runner_id)}, {"$set": update_data})
        if result.matched_count == 0:
            return JSONResponse(status_code=404, content={"error": "Runner not found"})

        doc = collection.find_one({"_id": ObjectId(runner_id)})
        return {"message": "success", "data": serialize_doc(doc)}

    except Exception as e:
        return {"error": str(e)}
    
# -----------------------------
# DELETE Runner
# -----------------------------
@app.delete("/runner/{runner_id}")
def delete_runner(runner_id: str):
    try:
        result = collection.delete_one({"_id": ObjectId(runner_id)})
        if result.deleted_count == 0:
            return JSONResponse(status_code=404, content={"error": "Runner not found"})
        return {"message": "success", "data": {"_id": runner_id}}
    except Exception as e:
        return {"error": str(e)}
