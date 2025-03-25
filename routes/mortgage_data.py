from fastapi import APIRouter, HTTPException
from models.mortgage_models import FormData
from config.database import  mortgage_form

router = APIRouter(prefix="/mortgage")

@router.post("/save-form-data")
async def save_form_data(form_data: FormData):
    try:
        await mortgage_form.update_one(
            {"formName": form_data.formName},
            {"$set": {"data": form_data.data}},
            upsert=True,
        )

        return {"message": "Form data saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get-form-data/{form_name}")
async def get_form_data(form_name: str):
    try:
        result = await mortgage_form.find_one({"formName": form_name}, {"_id": 0})
        if result:
            return result["data"]
        else:
            return {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
