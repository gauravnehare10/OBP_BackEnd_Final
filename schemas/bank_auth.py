from config.database import pisp_auth_tokens, pisp_payments_consents, aisp_accounts_consents, aisp_auth_tokens
from fastapi import HTTPException
import httpx
from config.bank_data import BANK_FUNCTIONS, get_bank_info


async def get_access_token(bank: str, userId: str, scope: str):
    if bank not in BANK_FUNCTIONS:
        raise HTTPException(status_code=404, detail="Bank not supported")
    
    bank_info = get_bank_info(bank)
    payload = {
        "grant_type": "client_credentials",
        "client_id": bank_info["CLIENT_ID"],
        "client_secret": bank_info["CLIENT_SECRET"],
        "scope": scope 
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(bank_info["TOKEN_URL"], data=payload)
        if response.status_code !=200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        
        token_data = response.json()
        token_data["UserId"] = userId
        token_data["bank"] = bank
        if scope == "accounts":
            token_data["state"] = "aisp"
            await aisp_auth_tokens.update_one({"UserId": userId, "bank": bank}, {"$set":token_data}, upsert=True)
        if scope == "payments":
            token_data["state"] = "pisp"
            await pisp_auth_tokens.update_one({"UserId": userId, "bank": bank}, {"$set":token_data}, upsert=True)
        return token_data["access_token"]
    
async def authorize_consent(bank: str, consent_id: str, scope: str, state: str):
    bank_info = get_bank_info(bank)

    auth_url =(
        f"{bank_info["AUTH_URL"]}"
        f"?client_id={bank_info["CLIENT_ID"]}"
        f"&response_type=code id_token"
        f"&scope=openid {scope}"
        f"&redirect_uri={bank_info["REDIRECT_URI"]}"
        f"&request={consent_id}"
        f"&state={state}"
    )

    return auth_url
    
async def fetch_access_token(bank: str, userId: str, state: str):
    if state == "aisp":
        tokens = await aisp_auth_tokens.find_one({'UserId': userId, 'bank': bank})
    if state == "pisp":
        tokens = await pisp_auth_tokens.find_one({'UserId': userId, 'bank': bank})

    return tokens.get("access_token")

async def fetch_consent(bank: str, userId: str, state: str):
    if state == "aisp":
        consent = await aisp_accounts_consents.find_one({'UserId': userId, 'bank': bank})
    if state == "pisp":
        consent = await pisp_payments_consents.find_one({"UserId": userId, "bank": bank})
    if not consent:
        raise HTTPException(status_code=404, detail="Consent not found.")
    return consent

async def check_bank_authorization(userId, bank):
    consent = await aisp_accounts_consents.find_one(
        {"UserId": userId, "bank": bank, "Status": "Authorised"}
    )

    if not consent:
        raise HTTPException(status_code=403, detail="Bank not Authorised")
    
    return consent