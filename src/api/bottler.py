from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

# with db.engine.begin() as connection:
#         result = connection.execute(sqlalchemy.text("SELECT num_green_potions, num_green_ml FROM global_inventory"))



class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_bottles(potions_delivered: list[PotionInventory], order_id: int):
    """ """
    print(f"potions delievered: {potions_delivered} order_id: {order_id}")
    num_green_potions_delivered = 0

    for i in range(potions_delivered):
        if potions_delivered[i].potion_type == [0, 100, 0, 0]:
            num_green_potions_delivered += 1

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory"))
    ml = result.first()[0]

    green_ml_subtract = ml - num_green_potions_delivered * 100

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = " + green_ml_subtract))


    
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory"))
    potions = result.first()[0]

    green_potions_add = potions + num_green_potions_delivered

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_potions = " + green_potions_add))

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.

    return [
            {
                "potion_type": [0, 100, 0, 0],
                "quantity": 5,
            }
        ]

if __name__ == "__main__":
    print(get_bottle_plan())