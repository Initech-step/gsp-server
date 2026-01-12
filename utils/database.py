from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from typing import Dict, Any
import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Access the environment variables
test_mode = os.getenv("TEST", True)
username = os.getenv("ATLAS_USERNAME")
pword = os.getenv("PWORD")


def connect_to_db() -> Dict[str, Any]:
    uri = f"mongodb+srv://{username}:{pword}@atlascluster.doihstd.mongodb.net/?appName=AtlasCluster"
    client = MongoClient(uri, server_api=ServerApi("1"))
    # Send a ping to confirm a successful connection
    try:
        client.admin.command("ping")
        if test_mode:
            print("test mode is true")
            db = client["TestGSP"]
        else:
            print("test mode is false")
            db = client["GSP"]

        print("Connected to MongoDB successfully.")
        return {
            "users_collection": db["Users"],
            "notes_collection": db["Notes"],
            "progress_collection": db["UserProgress"]
        }
    except Exception as e:
        print(e)
        return {}
