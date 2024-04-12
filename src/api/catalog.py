from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter()

# with db.engine.begin() as connection:
#         result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
#         for row in result:
#             print(row)
        

@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    green_potion_sku = "GRN_POTION_1" 
    

    with db.engine.begin() as connection:
        # the current number of green potions in inventory
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
        
        for row in result:
            print(row)    
        
        

    catalog = [
        {
            "sku": "GREEN_POTION_0",
            "name": "green potion",
            "quantity": 1,
            "price": 5,
            "potion_type": [0, 100, 0, 0], 
        }
    ]

    return catalog
