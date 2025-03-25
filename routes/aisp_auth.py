from fastapi import APIRouter, Depends, HTTPException

from schemas.user_auth import get_current_user
from models.user_models import User
from schemas.bank_auth import authorize_consent, get_access_token
from config.bank_data import BANK_FUNCTIONS, get_bank_info
from config.database import aisp_auth_tokens, aisp_accounts_consents
import httpx

router = APIRouter(prefix="/aisp")


@router.post("/authorize/")
async def create_consent(bank: str, current_user: User = Depends(get_current_user)):
    if bank not in BANK_FUNCTIONS:
        raise HTTPException(status_code=404, detail="Bank not supported")
    
    bank_info = get_bank_info(bank)
    
    access_token = await get_access_token(bank, current_user.userId, scope='accounts')

    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    consent_payload = {
        "Data": {
            "Permissions": [
                "ReadAccountsDetail",
                "ReadBalances",
                "ReadBeneficiariesDetail",
                "ReadDirectDebits",
                "ReadProducts",
                "ReadStandingOrdersDetail",
                "ReadTransactionsCredits",
                "ReadTransactionsDebits",
                "ReadTransactionsDetail",
                "ReadScheduledPaymentsBasic",
                "ReadScheduledPaymentsDetail",
                "ReadStatementsBasic", 
                "ReadStatementsDetail",
                "ReadOffers"
            ]
        },
        "Risk": {},
    }

    async with httpx.AsyncClient() as client:
        consent_response = await client.post(
            f"{bank_info['API_BASE_URL']}/aisp/account-access-consents",
            headers=headers,
            json=consent_payload,
        )

        if consent_response.status_code != 201:
            raise HTTPException(status_code=consent_response.status_code, detail=consent_response.text)

        consent_data = consent_response.json()["Data"]
        consent_data["UserId"] = current_user.userId
        consent_data["bank"] = bank
        await aisp_accounts_consents.update_one({"UserId": current_user.userId, "bank": bank}, {"$set":consent_data}, upsert=True)
        consent_id = consent_data["ConsentId"]
        auth_url = await authorize_consent(bank, consent_id, scope="accounts", state="aisp")

    return {"auth_url": auth_url}