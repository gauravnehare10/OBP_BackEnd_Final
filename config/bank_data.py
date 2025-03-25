from dotenv import find_dotenv, load_dotenv
from fastapi import HTTPException

import os

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)


def NatWest():
    return {
        "CLIENT_ID": os.getenv("NATWEST_CLIENT_ID"),
        "CLIENT_SECRET": os.getenv("NATWEST_CLIENT_SECRET"),
        "FINANCIAL_ID": os.getenv("NATWEST_FINANCIAL_ID"),
        "REDIRECT_URI": os.getenv("NATWEST_REDIRECT_URI"),
        "AUTHORIZATION_USERNAME": os.getenv("NATWEST_AUTHORIZATION_USERNAME"),
        "TOKEN_URL": "https://ob.sandbox.natwest.com/token",
        "AUTH_URL": "https://api.sandbox.natwest.com/authorize",
        "API_BASE_URL": "https://ob.sandbox.natwest.com/open-banking/v3.1",
        }

def RBS():
    return {
        "CLIENT_ID": os.getenv("RBS_CLIENT_ID"),
        "CLIENT_SECRET": os.getenv("RBS_CLIENT_SECRET"),
        "REDIRECT_URI": os.getenv("RBS_REDIRECT_URI"),
        "AUTHORIZATION_USERNAME": os.getenv("RBS_AUTHORIZATION_USERNAME"),
        "TOKEN_URL": "https://ob.sandbox.rbs.co.uk/token",
        "AUTH_URL": "https://api.sandbox.rbs.co.uk/authorize",
        "API_BASE_URL": "https://ob.sandbox.rbs.co.uk/open-banking/v3.1"
        }

BANK_FUNCTIONS = {
    "NatWest": NatWest,
    "RBS": RBS,
}

def get_bank_info(bank):
    if bank not in BANK_FUNCTIONS:
        raise HTTPException(status_code=400, detail="Invalid bank name")
    
    return BANK_FUNCTIONS[bank]()
