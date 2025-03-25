
async def upsert_data(collection, filter_query, update_data):
    await collection.update_one(filter_query, {"$set": update_data}, upsert=True)

async def get_account_data(collection, bank, userId, account_id):
    data = await collection.find({'UserId': userId, 'bank': bank, "AccountId": account_id}).to_list(length=None)

    for one_data in data:
        one_data.pop("_id")
    return data
