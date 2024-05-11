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
    colors = ['red', 'green', 'blue', 'dark']
    print(f"potions delievered: {potions_delivered} order_id: {order_id}")

    with db.engine.begin() as connection:
        for potion in potions_delivered:
            match = connection.execute(sqlalchemy.text(""" SELECT id FROM potion_table WHERE red = :red AND green = :green AND blue = :blue AND dark = :dark"""),[{"red": potion.potion_type[0],
                                                            "green": potion.potion_type[1],
                                                            "blue": potion.potion_type[2],
                                                            "dark": potion.potion_type[3]}]).scalar_one()
            connection.execute(sqlalchemy.text("""INSERT INTO potion_ledger (potion_id, change, description) 
                                               VALUES(:match , :quantity, 'mix')"""),[{"quantity": potion.quantity, "match": match}])   
            i = 0
            while i < len(colors):
                ml = potion.potion_type[i]
                color = colors[i]
                i += 1  

                if ml > 0:
                    connection.execute(sqlalchemy.text("INSERT INTO ml_ledger (type, change) VALUES (:color, :ml_quantity)"),[{"color": color, "ml_quantity": ml* potion.quantity*  -1}])                                                                    
    

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
    my_plan = []

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.
    with db.engine.begin() as connection:
        db_delta = connection.execute(sqlalchemy.text('''
                                (SELECT COALESCE(SUM(change), 0) FROM ml_ledger WHERE type = 'red') UNION ALL
                                (SELECT COALESCE(SUM(change), 0) FROM ml_ledger WHERE type = 'green') UNION ALL
                                (SELECT COALESCE(SUM(change), 0) FROM ml_ledger WHERE type = 'blue') UNION ALL
                                (SELECT COALESCE(SUM(change), 0) FROM ml_ledger WHERE type = 'dark')                                
                                ''')).fetchall()
        ml = []
        for color in db_delta:
            ml.append(color[0])       

        potions = connection.execute(sqlalchemy.text("SELECT red, green, blue, dark FROM potion_table"))
        for potion in potions:
            
            potion_type = [potion.red, potion.green, potion.blue, potion.dark]
            if all([m >= t for m,t in ml]):
                
                q = ml//(potion_type)
                if q != 0:
                    my_plan.append({
                        "potion_type": potion_type,
                        "quantity": q
                    })
                    ml = [m - p*q for m, p in zip(ml, potion_type)]
                    print(ml)
    return my_plan

if __name__ == "__main__":
    print(get_bottle_plan())