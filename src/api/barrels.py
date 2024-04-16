from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)



class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    """ """
    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")
    if len(barrels_delivered) == 0:
        return "OK"
    
    # COST AND ADDED ML
    cost = 0
    mlAdd = [0,0,0]
    for b in barrels_delivered:
        cost += b.quantity * b.price
        for i in range(3):
            if b.potion_type[i] >0:
                mlAdd[i] += b.ml_per_barrel * b.quantity



    exchangePrice = barrels_delivered[0].price
    ml_per = barrels_delivered[0].ml_per_barrel
    amt = barrels_delivered[0].quantity
    
    #GET GOLD
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
        for row in result:
            gold = row.gold
            ml = [row.num_red_ml, row.num_green_ml, row.num_blue_ml]

        if gold<cost:
            return "error, cost isnt correct, failed"
        

        #SUB GOLD
        gold -= cost
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = {gold}"))

        #red ml
        ml[0] = ml[0] + mlAdd[0]
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_red_ml = {ml[0]}"))

        #green ml
        ml[1] = ml[1] + mlAdd[1]
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_red_ml = {ml[1]}"))

        #blue ml
        ml[2] = ml[2] + mlAdd[2]
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_red_ml = {ml[2]}"))


    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
        for row in result:
            gold = row.gold
            potions = row.num_green_potions + row.num_red_potions + row.num_blue_potions

    my_plan = []
    i = 0

    while i < len(wholesale_catalog) and gold > 0:
        barrel = wholesale_catalog[i]
        if barrel.sku == "SMALL_GREEN_BARREL" and potions <10 and gold >= barrel.price:
            my_plan.append({
                "sku": barrel.sku, "quantity": 1})
            gold = gold - barrel.price

        elif barrel.sku == "SMALL_RED_BARREL" and potions <10 and gold >= barrel.price:
            my_plan.append({
                "sku": barrel.sku, "quantity": 1})
            gold = gold - barrel.price

        elif barrel.sku == "SMALL_BLUE_BARREL" and potions <10 and gold >= barrel.price:
            my_plan.append({
                "sku": barrel.sku, "quantity": 1})
            gold = gold - barrel.price

        i += 1
    return my_plan
