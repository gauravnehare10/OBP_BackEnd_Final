from fastapi import APIRouter, HTTPException, Depends, Query, Body
from schemas.user_auth import get_current_user
from config.bank_data import get_bank_info, BANK_FUNCTIONS
from config.database import pisp_auth_tokens
from models.exchange_models import ExchangeData
from schemas.aisp_apis import *
from models.user_models import User
import httpx


router = APIRouter()


@router.post("/exchange-token/")
async def exchange_token(
    bank: str = Query(...),
    request: ExchangeData = Body(...), 
    current_user: User = Depends(get_current_user)
):
    userId = current_user.userId
    if bank not in BANK_FUNCTIONS:
        raise HTTPException(status_code=404, detail="Bank not supported")

    bank_info = get_bank_info(bank)
    
    payload = {
        "grant_type": "authorization_code",
        "code": request.code,
        "redirect_uri": bank_info["REDIRECT_URI"],
        "client_id": bank_info["CLIENT_ID"],
        "client_secret": bank_info["CLIENT_SECRET"],
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            bank_info["TOKEN_URL"], 
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"})
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        
        token_data = response.json()
        token_data["UserId"] = userId
        token_data["bank"] = bank
        token_data["state"] = request.state
        if request.state == "pisp":
            await pisp_auth_tokens.update_one({"UserId": userId, "bank": bank}, {"$set":token_data}, upsert=True)

        if request.state == "aisp":
            await aisp_auth_tokens.update_one({"UserId": userId, "bank": bank}, {"$set":token_data}, upsert=True)
            await get_account_access_consent(bank, userId)
            accounts_data = await get_accounts(bank, userId)
            for account in accounts_data:
                account_id = account["AccountId"]
                await get_account_transactions(account_id, bank, userId)
                await get_account_beneficiaries(account_id, bank, userId)
                await get_account_balances(account_id, bank, userId)
                await get_account_direct_debits(account_id, bank, userId)
                await get_account_standing_orders(account_id, bank, userId)
                await get_account_product(account_id, bank, userId)
                await get_account_scheduled_payments(account_id, bank, userId)
        
    return {"message": "Bank Authorisation Successful!"}