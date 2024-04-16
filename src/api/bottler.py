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


class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_bottles(potions_delivered: list[PotionInventory], order_id: int):
    """ """
    print(f"potions delievered: {potions_delivered} order_id: {order_id}")

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
        for row in result:
            ml = [row.num_red_ml, row.num_green_ml, row.num_blue_ml]
            potions = [row.num_red_potions, row.num_green_potions, row.num_blue_potions]

        potion_names = ["num_red_potions", "num_green_potions", "num_blue_potions"]
        ml_names = ["num_red_ml", "num_green_ml", "num_blue_ml"]

        for type in potions_delivered:
            for i in range(3):
                potionType = [0,0,0,0]
                potionType[i] = 100

                if type.potion_type == potionType:

                    potions[i] += type.quantity
                    ml[i] -= 100 * type.quantity

                    connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET {potion_names[i]} = {potions[i]}"))
                    connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET {ml_names[i]} = {ml[i]}"))


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

    my_plan = []

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
        for row in result:
            math = [row.num_red_ml // 100, row.num_green_ml // 100, row.num_blue_ml // 100]
        for i in range(3):
            if math[i] >0:
                type = [0,0,0,0]
                type[i] += 100
                my_plan.append({"potion_type": type, "quantity": math[i]})

    return my_plan

if __name__ == "__main__":
    print(get_bottle_plan())