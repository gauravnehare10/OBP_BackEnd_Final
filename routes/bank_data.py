from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
import calendar
from config.database import transactions, accounts, aisp_accounts_consents, beneficiaries, balances
from schemas.user_auth import get_current_user
from schemas.aisp_auth import get_account_data
from schemas.bank_auth import check_bank_authorization
from models.user_models import User
from typing import List
from collections import defaultdict

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_data(current_user: User=Depends(get_current_user)):
    userId = current_user.userId
    today = datetime.utcnow().date()
    start_of_week = today - timedelta(days=today.weekday())
    start_of_last_week = start_of_week - timedelta(days=7)
    start_of_month = today.replace(day=1)

    # Fetch transactions for the user
    transactions_data = await transactions.find({"UserId": userId}).to_list(length=None)
    
    # Process data for charts
    weekly_data = {day: {"this_week": 0, "last_week": 0} for day in range(7)}
    monthly_spending = {}
    bank_distribution = {}

    transactions_data.sort(key=lambda x: x["BookingDateTime"], reverse=True)

    latest_transactions = transactions_data[:5]

    for txn in transactions_data:
        amount = float(txn["Amount"]["Amount"])
        txn_date = datetime.fromisoformat(txn["BookingDateTime"].replace("Z", "")).date()
        weekday = txn_date.weekday()
        month = calendar.month_abbr[txn_date.month]
        bank = txn["bank"]

        # Weekly Data
        if txn_date >= start_of_week:
            weekly_data[weekday]["this_week"] += amount
        elif txn_date >= start_of_last_week:
            weekly_data[weekday]["last_week"] += amount

        # Monthly Spending Trend
        if month not in monthly_spending:
            monthly_spending[month] = 0
        monthly_spending[month] += amount

        # Bank Distribution
        if bank not in bank_distribution:
            bank_distribution[bank] = 0
        bank_distribution[bank] += amount

    accounts_data = await accounts.find({"UserId": userId}).to_list(length=None)
    for account in accounts_data:
        account.pop("_id")
        
    # Prepare response data
    response_data = {
        "Accounts": accounts_data,
        "TransactionOverview": {
            "labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            "datasets": [
                {"label": "This Week", "data": [weekly_data[i]["this_week"] for i in range(7)], "backgroundColor": "#1b04ee", "borderRadius": 10},
                {"label": "Last Week", "data": [weekly_data[i]["last_week"] for i in range(7)], "backgroundColor": "#2499dd", "borderRadius": 10}
            ]
        },
        "MonthlyTrends": {
            "labels": list(monthly_spending.keys()),
            "datasets": [{
                    "label": "Monthly Spending Trend", 
                    "data": list(monthly_spending.values()),
                    "borderColor": "#ff4500", 
                    "fill": False
                }]
        },
        "BankTransactions": {
            "labels": list(bank_distribution.keys()),
            "datasets": [{
                "data": list(bank_distribution.values()), 
                "backgroundColor": ["#4169e1", "#32cd32", "#ff8c00"]
                }]
        },
        "LatestTransactions": [
            {
                "TransactionId": txn["TransactionId"],
                "Date": txn["BookingDateTime"],
                "Amount": txn["Amount"]["Amount"],
                "Currency": txn["Amount"]["Currency"],
                "Type": txn["CreditDebitIndicator"],
                "Bank": txn["bank"]
            }
            for txn in latest_transactions
        ]
    }
    
    return response_data

@router.get("/transactions")
async def get_all_transactions(current_user: User=Depends(get_current_user)):
    userId = current_user.userId
    user_transactions = await transactions.find({"UserId": userId}).to_list(length=None)
    if not user_transactions:
        raise HTTPException(status_code=404, detail="Transactions not found.")
    
    for transaction in user_transactions:
        transaction.pop("_id")
    
    return user_transactions

@router.get("/get-banks", response_model=List[str])
async def get_authorized_banks(current_user: User=Depends(get_current_user)):
    authorized_banks = await aisp_accounts_consents.find({"UserId": current_user.userId, "Status": "Authorised"}).to_list()

    if not authorized_banks:
        raise HTTPException(status_code=404, detail="No authorized banks found for this user")

    banks = [bank["bank"] for bank in authorized_banks]
    return banks

@router.get('/{bank}/accounts/{accountId}')
async def get_account_by_id(bank: str, accountId: str, current_user: User=Depends(get_current_user)):
    try:
        authorized = await check_bank_authorization(current_user.userId, bank)
    except HTTPException as e:
        raise e
    
    account_list = await get_account_data(accounts, bank, current_user.userId, accountId)

    account = account_list[0]

    # Fetch balance information
    balance_data = await balances.find({"AccountId": accountId, "UserId": current_user.userId}).to_list(length=None)

    # Format balance data
    formatted_balances = [
        {
            "Type": balance["Type"],
            "Amount": balance["Amount"]["Amount"],
            "Currency": balance["Amount"]["Currency"],
            "CreditDebitIndicator": balance["CreditDebitIndicator"],
            "DateTime": balance["DateTime"]
        } 
        for balance in balance_data
    ]

    # Return structured response
    return {
        "AccountId": account["AccountId"],
        "UserId": account["UserId"],
        "Bank": account["bank"],
        "Nickname": account["Nickname"],
        "AccountType": account["AccountType"],
        "AccountSubType": account["AccountSubType"],
        "Currency": account["Currency"],
        "Description": account["Description"],
        "AccountDetails": account["Account"],
        "Balances": formatted_balances
    }

@router.get("{bank}/transactions/{accountId}")
async def get_all_transactions(bank: str, accountId: str, current_user: User=Depends(get_current_user)):
    userId = current_user.userId
    user_transactions = await transactions.find({"UserId": userId, "bank": bank, "AccountId": accountId}).to_list(length=None)
    if not user_transactions:
        raise HTTPException(status_code=404, detail="Transactions not found.")
    
    for transaction in user_transactions:
        transaction.pop("_id")
    
    return user_transactions

@router.get("/{bank}/beneficiaries")
async def get_beneficiaries(bank: str, current_user: User=Depends(get_current_user)):
    beneficiaries_data = await beneficiaries.find({"UserId": current_user.userId, "bank": bank}).to_list()
    if not beneficiaries_data:
        raise HTTPException(status_code=404, detail="Data not found.")
    
    for beneficiary in beneficiaries_data:
        beneficiary.pop("_id")
        
    return beneficiaries_data
