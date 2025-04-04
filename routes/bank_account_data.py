from fastapi import APIRouter, Depends, HTTPException
from models.user_models import User
from schemas.user_auth import get_current_user
from schemas.bank_data import check_bank_authorization, get_data
from config.database import accounts, transactions, balances, beneficiaries, direct_debits, standing_orders, products, scheduled_payments

router = APIRouter()

@router.get('/{bank}/accounts/{account_id}/transactions')
async def get_transactions_by_acc_id(bank: str, account_id: str, current_user: User=Depends(get_current_user)):
    try:
        authorized = await check_bank_authorization(current_user.userId, bank)
    except HTTPException as e:
        raise e
    
    transactions_details = await get_data(transactions, bank, current_user.userId, account_id)

    return transactions_details

@router.get("/{bank}/accounts/{account_id}/transactions/{transaction_id}")
async def get_transaction_by_id(bank: str, account_id: str, transaction_id: str, current_user:User=Depends(get_current_user)):
    try:
        authorized = await check_bank_authorization(current_user.userId, bank)
    except HTTPException as e:
        raise e
    
    transaction_details = await transactions.find_one({"bank": bank, "AccountId": account_id, "TransactionId": transaction_id})
    transaction_details.pop("_id")
    return transaction_details
        

@router.get('/{bank}/accounts/{account_id}/beneficiaries')
async def get_beneficiaries_by_id(bank: str, account_id: str, current_user: User=Depends(get_current_user)):
    try:
        authorized = await check_bank_authorization(current_user.userId, bank)
    except HTTPException as e:
        raise e
    
    beneficiaries_data = await get_data(beneficiaries, bank, current_user.userId, account_id)

    return beneficiaries_data


@router.get("/{bank}/accounts/{account_id}/balances")
async def get_transaction_by_id(bank: str, account_id: str, current_user:User=Depends(get_current_user)):
    print(bank)
    try:
        authorized = await check_bank_authorization(current_user.userId, bank)
    except HTTPException as e:
        raise e
    
    balance_details = await balances.find({"bank": bank, "AccountId": account_id}).to_list(length=None)
    for balance in balance_details:
        balance.pop("_id")
    return balance_details


@router.get('/{bank}/accounts/{account_id}/direct-debits')
async def get_direct_debits_by_id(bank: str, account_id: str, current_user: User=Depends(get_current_user)):
    try:
        authorized = await check_bank_authorization(current_user.userId, bank)
    except HTTPException as e:
        raise e
    
    direct_debits_data = await get_data(direct_debits, bank, current_user.userId, account_id)

    return direct_debits_data

@router.get('/{bank}/accounts/{account_id}/standing-orders')
async def get_direct_debits_by_id(bank: str, account_id: str, current_user: User=Depends(get_current_user)):
    try:
        authorized = await check_bank_authorization(current_user.userId, bank)
    except HTTPException as e:
        raise e
    
    standing_orders_data = await get_data(standing_orders, bank, current_user.userId, account_id)

    return standing_orders_data

@router.get('/{bank}/accounts/{account_id}/product')
async def get_direct_debits_by_id(bank: str, account_id: str, current_user: User=Depends(get_current_user)):
    try:
        authorized = await check_bank_authorization(current_user.userId, bank)
    except HTTPException as e:
        raise e
    
    product_data = await get_data(products, bank, current_user.userId, account_id)

    return product_data

@router.get('/{bank}/accounts/{account_id}/scheduled-payments')
async def get_direct_debits_by_id(bank: str, account_id: str, current_user: User=Depends(get_current_user)):
    try:
        authorized = await check_bank_authorization(current_user.userId, bank)
    except HTTPException as e:
        raise e
    
    scheduled_payments_data = await get_data(scheduled_payments, bank, current_user.userId, account_id)

    return scheduled_payments_data