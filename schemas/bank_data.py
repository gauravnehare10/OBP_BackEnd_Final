from fastapi import HTTPException
from config.database import aisp_accounts_consents

async def check_bank_authorization(userId, bank):
    consent = await aisp_accounts_consents.find_one(
        {"UserId": userId, "bank": bank, "Status": "Authorised"}
    )

    if not consent:
        raise HTTPException(status_code=403, detail="Bank not Authorised")
    
    return consent

async def get_data(collection, bank, userId, account_id):
    data = await collection.find({'UserId': userId, 'bank': bank, "AccountId": account_id}).to_list(length=None)

    for one_data in data:
        one_data.pop("_id")
    return data