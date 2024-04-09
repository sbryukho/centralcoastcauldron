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

# with db.engine.begin() as connection:
#         result = connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_potions = num_green_potions + 1 WHERE num_green_potions < 10"))

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
    
    exchangePrice = barrels_delivered[0].price
    ml_per = barrels_delivered[0].ml_per_barrel
    amt = barrels_delivered[0].quantity
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory"))
    theGold = result.first()[0]
    after_gold = theGold - exchangePrice

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = {after_gold}"))

    newML = ml_per * amt
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_green_ml = {newML}"))


    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)


    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory"))


    numpots = result.first()[0]
    return [
        {
            "sku": "SMALL_GREEN_BARREL",
            "quantity": 1 if numpots < 10 else 0,
        }
    ]
    

