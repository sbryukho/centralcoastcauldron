from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter()



@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    with db.engine.begin() as connection:
        inventory = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
        for row in inventory:
            num_potions = [row.num_red_potions, row.num_green_potions, row.num_blue_potions]

    catalog = []
    prices = {"GREEN_POTION_0": 5, "RED_POTION_0": 5, "BLUE_POTION_0": 5}

    potion_skus = ["RED_POTION_0", "GREEN_POTION_0", "BLUE_POTION_0"]
    potion_names = ["red potion", "green potion", "blue potion"]
    potion_type = [[100,0,0,0], [0,100,0,0], [0,0,100,0]]
    for i in range(3):
        if num_potions[i] >= 0:
            catalog.append({
                    "sku": potion_skus[i],
                    "name": potion_names[i],
                    "quantity": num_potions[i],
                    "price": prices[potion_skus[i]],
                    "potion_type": potion_type[i],
                })

    return catalog
