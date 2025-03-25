from fastapi import APIRouter, HTTPException, Depends

from schemas.aisp_auth import upsert_data
from schemas.bank_auth import fetch_access_token, fetch_consent
from config.bank_data import get_bank_info
from schemas.user_auth import get_current_user
from config.database import *
import httpx
import uuid
from models.user_models import User

router = APIRouter()

async def get_account_access_consent(bank, userId):
    access_token = await fetch_access_token(bank=bank, userId=userId, state="aisp")
    bank_info = get_bank_info(bank)
    consent = await fetch_consent(bank=bank, userId=userId, state="aisp")
    consent_id = consent["ConsentId"]
    url = f"{bank_info.get("API_BASE_URL")}/aisp/account-access-consents/{consent_id}"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/x-www-form-urlencoded"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        data = response.json()["Data"]

        aisp_accounts_consents.update_one({"ConsentId": consent_id}, {"$set": data}, upsert=True)
        user_account_consent_data = await aisp_accounts_consents.find_one({"ConsentId": consent_id})
        user_account_consent_data.pop("_id")
        return user_account_consent_data

async def get_accounts(bank: str, userId):
    access_token = await fetch_access_token(bank=bank, userId=userId , state="aisp")
    bank_info = get_bank_info(bank)
    url = f"{bank_info.get("API_BASE_URL")}/aisp/accounts"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/x-www-form-urlencoded"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        data = response.json()["Data"]["Account"]
        # Save to MongoDB
        for account in data:
            account["UserId"] = userId
            account["bank"] = bank
            await upsert_data(
                accounts, 
                {
                    "AccountId": account["AccountId"], 
                    "UserId": userId
                }, 
                account
                )

        return data

async def get_account_details(account_id: str, bank: str, current_user: User=Depends(get_current_user)):
    userId = current_user.userId
    access_token = await fetch_access_token(bank=bank, userId=userId , state="aisp")
    bank_info = get_bank_info(bank)
    url = f"{bank_info.get("API_BASE_URL")}/aisp/accounts/{account_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        data = response.json()

        return data


async def get_account_transactions(account_id: str, bank: str, userId):
    access_token = await fetch_access_token(bank=bank, userId=userId , state="aisp")
    bank_info = get_bank_info(bank)
    url = f"{bank_info.get("API_BASE_URL")}/aisp/accounts/{account_id}/transactions"
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        data = response.json()["Data"]["Transaction"]
        # Save to MongoDB
        for transaction in data:
            transaction["UserId"] = userId
            transaction["bank"] = bank
            await upsert_data(
                transactions, 
                {
                    "TransactionId": transaction["TransactionId"],
                    "UserId": userId
                },
                transaction
                )
        
        return data

async def get_account_beneficiaries(account_id: str, bank: str, userId):
    access_token = await fetch_access_token(bank=bank, userId=userId , state="aisp")
    bank_info = get_bank_info(bank)
    url = f"{bank_info.get("API_BASE_URL")}/aisp/accounts/{account_id}/beneficiaries"
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        data = response.json()["Data"]["Beneficiary"]
        # Save to MongoDB
        for beneficiary in data:
            beneficiary["UserId"] = userId
            beneficiary["bank"] = bank
            await upsert_data(
                beneficiaries, 
                {
                    "BeneficiaryId": beneficiary["BeneficiaryId"], 
                    "UserId": userId
                }, 
                beneficiary
                )

        return data

async def get_account_balances(account_id: str, bank: str, userId):
    access_token = await fetch_access_token(bank=bank, userId=userId , state="aisp")
    bank_info = get_bank_info(bank)
    url = f"{bank_info.get("API_BASE_URL")}/aisp/accounts/{account_id}/balances"
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        data = response.json()["Data"]["Balance"]
        # Save to MongoDB
        for balance in data:
            balance["UserId"] = userId
            balance["bank"] = bank
            await upsert_data(
                balances, 
                {
                    "AccountId": balance["AccountId"],
                    "Type": balance["Type"], 
                    "UserId": userId
                },
                balance
                )

        return data


async def get_account_direct_debits(account_id: str, bank: str, userId):
    access_token = await fetch_access_token(bank=bank, userId=userId , state="aisp")
    bank_info = get_bank_info(bank)
    url = f"{bank_info.get("API_BASE_URL")}/aisp/accounts/{account_id}/direct-debits"
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        data = response.json()["Data"]["DirectDebit"]
        # Save to MongoDB
        for direct_debit in data:
            direct_debit["UserId"] = userId
            direct_debit["bank"] = bank
            await upsert_data(
                direct_debits,
                {
                    "AccountId": direct_debit["AccountId"], 
                    "MandateIdentification": direct_debit["MandateIdentification"], 
                    "UserId": userId
                }, 
                direct_debit
                )

        return data

async def get_account_standing_orders(account_id: str, bank: str, userId):
    access_token = await fetch_access_token(bank=bank, userId=userId , state="aisp")
    bank_info = get_bank_info(bank)
    url = f"{bank_info.get("API_BASE_URL")}/aisp/accounts/{account_id}/standing-orders"
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        data = response.json()["Data"]["StandingOrder"]
        # Save to MongoDB
        for standing_order in data:
            standing_order["UserId"] = userId
            standing_order["bank"] = bank
            await upsert_data(
                standing_orders,
                {
                    "AccountId": standing_order["AccountId"],
                    "Frequency": standing_order["Frequency"],
                    "UserId": userId
                }, 
                standing_order
                )

        return data

async def get_account_product(account_id: str, bank: str, userId):
    access_token = await fetch_access_token(bank=bank, userId=userId , state="aisp")
    bank_info = get_bank_info(bank)
    url = f"{bank_info.get("API_BASE_URL")}/aisp/accounts/{account_id}/product"
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        data = response.json()["Data"]["Product"]
        # Save to MongoDB
        for product in data:
            product["UserId"] = userId
            product["bank"] = bank
            await upsert_data(
                products,
                {
                    "AccountId": product["AccountId"],
                    "ProductId": product["ProductId"],
                    "UserId": userId
                }, 
                product
                )

        return data

async def get_account_scheduled_payments(account_id: str, bank: str, userId):
    access_token = await fetch_access_token(bank=bank, userId=userId , state="aisp")
    bank_info = get_bank_info(bank)
    url = f"{bank_info.get("API_BASE_URL")}/aisp/accounts/{account_id}/scheduled-payments"
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        data = response.json()["Data"]["ScheduledPayment"]
        # Save to MongoDB
        for scheduled_payment in data:
            scheduled_payment["UserId"] = userId
            scheduled_payment["bank"] = bank
            await upsert_data(
                scheduled_payments,
                {
                    "AccountId": scheduled_payment["AccountId"],
                    "ScheduledType": scheduled_payment["ScheduledType"],
                    "UserId": userId
                }, 
                scheduled_payment
                )

        return data

async def get_account_statements(account_id: str, bank: str, current_user: User=Depends(get_current_user)):
    userId = current_user.userId
    access_token = await fetch_access_token(bank=bank, userId=userId , state="aisp")
    bank_info = get_bank_info(bank)
    url = f"{bank_info.get("API_BASE_URL")}/aisp/accounts/{account_id}/statements"
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        data = response.json()
        # Save to MongoDB

        return data

async def get_account_offers(account_id: str, bank: str, current_user: User=Depends(get_current_user)):
    userId = current_user.userId
    access_token = fetch_access_token(bank=bank, userId=userId , state="aisp")
    bank_info = get_bank_info(bank)
    url = f"{bank_info.get("API_BASE_URL")}/aisp/accounts/{account_id}/offers"
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        data = response.json()
        # Save to MongoDB

        return data