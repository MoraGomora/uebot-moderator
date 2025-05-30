from dotenv import load_dotenv, dotenv_values

def get_data():
    if load_dotenv():
        data = dotenv_values()
        return data["API_ID"], data["API_HASH"]
    
def get_owner_id() -> int:
    if load_dotenv():
        data = dotenv_values()
        return data["OWNER_ID"]
    
def get_ionet_key() -> str:
    if load_dotenv():
        data = dotenv_values()
        return data["API_IONET_KEY"]
    
def get_mongodb_uri() -> str:
    if load_dotenv():
        data = dotenv_values()
        return data["MONGODB_URI"]