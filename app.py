from fastapi import (
    FastAPI,
    HTTPException,
    status,
    Header
)
from fastapi.middleware.cors import CORSMiddleware
from bson.objectid import ObjectId
from typing import List, Optional
import math
from datetime import datetime
from utils.database import connect_to_db
import os


# initialize app
app = FastAPI()

"""SET UP CORS"""
origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"],
)

database = connect_to_db()

# root
@app.get("/")
def root():
    return {"message": "Hello Godslighthouse Starter Kit Server"}

"""
Mini User Auth APIS
"""


"""
Notes APIS
"""


@app.post(
    "/api/category/", 
    status_code=status.HTTP_201_CREATED, 
    response_model=dict
)
def create_category(category: Category, token: str = Header()):
    category_data = category.model_dump()
    category_collection = database["categories_collection"]
    try:
        category_collection.insert_one(category_data)
        return {"status": True}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create catgory",
        )


@app.get("/api/category/", response_model=List[CategoryOut])
def get_categories(type: Optional[CategoryType] = None):
    category_collection = database["categories_collection"]
    if type is not None:
        data = list(category_collection.find({"type": type.value}))
    else:
        data = list(category_collection.find({}))
    for d in data:
        d["_id"] = str(d["_id"])
    return data


@app.delete(
    "/api/category/{c_id}/{type}/", 
    status_code=status.HTTP_200_OK, 
    response_model=dict
)
def delete_category(
    c_id: str, 
    type: CategoryType = CategoryType.product, 
    token: str = Header()
):
    # find and verify category
    # category_collection.delete_one({"_id": ObjectId(c_id)})
    pass

@app.put(
    "/api/category/{c_id}/", 
    status_code=status.HTTP_200_OK, 
    response_model=dict
)
def update_category(c_id: str, category: Category, token: str = Header()):

    category_data = category.model_dump()
    category_collection = database["blog_categories_collection"]
    data_target = category_collection.find_one({"_id": ObjectId(c_id)})
    if data_target == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found"
        )
    category_collection.update_one(
        {"_id": ObjectId(c_id)},
        {
            "$set": {
                "name": category_data.get("name"),
                "description": category_data.get("description"),
            }
        },
    )
    return {"status": True}



"""
User Progress APIS
"""


"""
Upload state APIS
"""

