from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import bank_data, user_auth,  aisp_auth, exchange_code, pisp_auth, mortgage_data

app = FastAPI()

app.include_router(bank_data.router)
app.include_router(user_auth.router)
app.include_router(pisp_auth.router)
app.include_router(exchange_code.router)
app.include_router(aisp_auth.router)
app.include_router(mortgage_data.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)