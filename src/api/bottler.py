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


meta = sqlalchemy.MetaData()
potion_table = sqlalchemy.Table("potion_table", meta, autoload_with= db.engine) 
global_inventory = sqlalchemy.Table("global_inventory", meta, autoload_with= db.engine) 
@router.post("/deliver/{order_id}")
def post_deliver_bottles(potions_delivered: list[PotionInventory], order_id: int):
    """ """
    print(f"potions delievered: {potions_delivered} order_id: {order_id}")

    with db.engine.begin() as connection:

        for potion in potions_delivered:
            connection.execute(sqlalchemy.text("SELECT quantity, sku FROM potion_table")).fetchall()

            connection.execute(sqlalchemy.update(potion_table)
                .where(
                    potion_table.c.red == potion.potion_type[0],
                    potion_table.c.green == potion.potion_type[1],
                    potion_table.c.blue == potion.potion_type[2],
                    potion_table.c.dark == potion.potion_type[3]
                ).values(quantity =  potion_table.c.quantity + potion.quantity))
            connection.execute(sqlalchemy.update(global_inventory)
                .values(
                    num_red_ml = global_inventory.c.num_red_ml - potion.potion_type[0] * potion.quantity,
                    num_green_ml = global_inventory.c.num_green_ml - potion.potion_type[1] * potion.quantity,
                    num_blue_ml = global_inventory.c.num_blue_ml - potion.potion_type[2] * potion.quantity,
                    num_dark_ml = global_inventory.c.num_dark_ml - potion.potion_type[3] * potion.quantity))



    # with db.engine.begin() as connection:
    #     result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
    #     for row in result:
    #         ml = [row.num_red_ml, row.num_green_ml, row.num_blue_ml]
    #         potions = [row.num_red_potions, row.num_green_potions, row.num_blue_potions]

    #     potion_names = ["num_red_potions", "num_green_potions", "num_blue_potions"]
    #     ml_names = ["num_red_ml", "num_green_ml", "num_blue_ml"]

    #     for type in potions_delivered:
    #         for i in range(3):
    #             potionType = [0,0,0,0]
    #             potionType[i] = 100

    #             if type.potion_type == potionType:

    #                 potions[i] += type.quantity
    #                 ml[i] -= 100 * type.quantity

    #                 connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET {potion_names[i]} = {potions[i]}"))
    #                 connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET {ml_names[i]} = {ml[i]}"))


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
    meta = sqlalchemy.MetaData()
    potion_table = sqlalchemy.Table("potion_table", meta, autoload_with= db.engine) 

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.
    with db.engine.begin() as connection:
        ml = connection.execute(sqlalchemy.text("SELECT num_red_ml, num_green_ml, num_blue_ml, num_dark_ml FROM global_inventory")).fetchall()[0]
        my_plan = []
        qdict = {}
        
        potions = connection.execute(sqlalchemy.select(potion_table))
        for row in potions:
            qdict[row.sku] = ([row.red, row.green, row.blue, row.dark], row.quantity) 

        
        # PURPLE POTION
        if ml[0] >= 100 and ml[2] >= 100 and qdict["PURPLE_0"][1] < 5:
            my_plan.append({
                "potion_type": qdict["PURPLE_0"][0],
                "quantity": 5
            })

            for i in range(len(ml)):
                ml[i] -= qdict["PURPLE_0"][0][i] * 5


        # AQUA(?)
        if ml[1] >= 100 and ml[2] >= 100 and qdict["AQUA_0"][1] < 5: 
            my_plan.append({
                "potion_type": qdict["AQUA_0"][0],
                "quantity": 5
            })
            for i in range(len(ml)):
                ml[i] -= qdict["AQUA_0"][0][i]*5
        # RED
        if ml[0] >= 100 and qdict["RED_POTION_0"][1] < 5:
            q = ml[0]//200
            if q > 0:
                my_plan.append({
                    "potion_type": qdict["RED_POTION_0"][0],
                    "quantity": q
                })
            for i in range(len(ml)):
                ml[i] -= qdict["RED_POTION_0"][0][i]*5
        # GREEN
        if ml[1] >= 100 and qdict["GREEN_POTION_0"][1] < 5:
            q = ml[1]//200

            if q > 0: 
                my_plan.append({
                    "potion_type": qdict["GREEN_POTION_0"][0],
                    "quantity": q
                })
            for i in range(len(ml)):
                ml[i] -= qdict["GREEN_POTION_0"][0][i]*5
        # BLUEE
        if ml[2] >= 100 and qdict["BLUE_POTION_0"][1] < 5:
            q = ml[2]//200


            if q > 0:
                my_plan.append({
                    "potion_type": qdict["BLUE_POTION_0"][0],
                    "quantity": q
                })
            for i in range(len(ml)):
                ml[i] -= qdict["BLUE_POTION_0"][0][i]*5
        
    return my_plan
    # my_plan = []

    # with db.engine.begin() as connection:
    #     result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
    #     for row in result:
    #         math = [row.num_red_ml // 100, row.num_green_ml // 100, row.num_blue_ml // 100]
    #     for i in range(3):
    #         if math[i] >0:
    #             type = [0,0,0,0]
    #             type[i] += 100
    #             my_plan.append({"potion_type": type, "quantity": math[i]})

    # return my_plan

if __name__ == "__main__":
    print(get_bottle_plan())