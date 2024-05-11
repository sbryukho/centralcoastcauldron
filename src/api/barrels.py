from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
import math

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
class size:
    def __init__(self, gold: int, ml_cap: int, size: str = ''):
        self.gold = gold
        self.size = size
        self.ml_cap = ml_cap


    def quantity(self, price: int, ml_sum):
        print(ml_sum, self.ml_cap)
        if ml_sum > self.ml_cap:
            return 0
        
        if self.size == 'SMALL' and self.gold >= price:
            return max(1, self.gold//price)
        elif self.size == 'MEDIUM' and self.gold >= price:
            return max(1, self.gold//price)
        elif self.size == 'LARGE' and self.gold >= 1.5*price:
            return max(1, self.gold//price)
        else: 
            return 0

@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    """ """
    with db.engine.begin() as connection:
        for barrel in barrels_delivered:
            connection.execute(sqlalchemy.text("INSERT INTO gold_ledger (change, description) VALUES (:total_cost, :describe)"), [{"total_cost": barrel.quantity*barrel.price*-1, "describe": f'you bought {barrel.quantity} {barrel.sku}'}])
            potion_type = barrel.potion_type
            if potion_type == [0, 1, 0, 0]:
                connection.execute(sqlalchemy.text("INSERT INTO ml_ledger (type, change) VALUES ('green', :barrel_ml)"),[{"barrel_ml": barrel.ml_per_barrel*barrel.quantity}])
            elif potion_type == [1, 0, 0, 0]:
                connection.execute(sqlalchemy.text("INSERT INTO ml_ledger (type, change) VALUES ('red', :barrel_ml)"),[{"barrel_ml": barrel.ml_per_barrel*barrel.quantity}])
            elif potion_type == [0, 0, 1, 0]:
                connection.execute(sqlalchemy.text("INSERT INTO ml_ledger (type, change) VALUES ('blue', :barrel_ml)"),[{"barrel_ml": barrel.ml_per_barrel*barrel.quantity}])
            elif potion_type == [0, 0, 0, 1]:
                connection.execute(sqlalchemy.text("INSERT INTO ml_ledger (type, change) VALUES ('dark', :barrel_ml)"),[{"barrel_ml": barrel.ml_per_barrel*barrel.quantity}])
    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")
    # if len(barrels_delivered) == 0:
    #     return "OK"
    
    # # COST AND ADDED ML
    # cost = 0
    # mlAdd = [0,0,0]
    # for b in barrels_delivered:
    #     cost += b.quantity * b.price
    #     for i in range(3):
    #         if b.potion_type[i] >0:
    #             mlAdd[i] += b.ml_per_barrel * b.quantity

    # exchangePrice = barrels_delivered[0].price
    # ml_per = barrels_delivered[0].ml_per_barrel
    # amt = barrels_delivered[0].quantity
    
    # #GET GOLD
    # with db.engine.begin() as connection:
    #     result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
    #     for row in result:
    #         gold = row.gold
    #         ml = [row.num_red_ml, row.num_green_ml, row.num_blue_ml]

    #     if gold<cost:
    #         return "error, cost isnt correct, failed"
        
    #     #SUB GOLD
    #     gold -= cost
    #     connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = {gold}"))

    #     #red ml
    #     ml[0] = ml[0] + mlAdd[0]
    #     connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_red_ml = {ml[0]}"))
    #     print(ml[0])
    #     #green ml
    #     ml[1] = ml[1] + mlAdd[1]
    #     connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_green_ml = {ml[1]}"))
    #     print(ml[1])

    #     #blue ml
    #     ml[2] = ml[2] + mlAdd[2]
    #     connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_blue_ml = {ml[2]}"))
    #     print(ml[2])
    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)
    cat = wholesale_catalog
    my_plan = []


    with db.engine.begin() as connection:
        ml_cap = connection.execute(sqlalchemy.select(db.capacity.c.ml)).scalar_one()
        db_delta = connection.execute(sqlalchemy.text('''
                                                      SELECT COALESCE(SUM(change), 0) FROM ml_ledger WHERE type = 'red' UNION ALL
                                                      SELECT COALESCE(SUM(change), 0) FROM ml_ledger WHERE type = 'green' UNION ALL
                                                      SELECT COALESCE(SUM(change), 0) FROM ml_ledger WHERE type = 'blue' UNION ALL
                                                      SELECT COALESCE(SUM(change), 0) FROM ml_ledger WHERE type = 'dark'                                                     
                                                      ''')).fetchall()
        ml = []
        for color in db_delta:
            ml.append(color[0])
        gold = connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(change), 0) FROM gold_ledger")).scalar_one()
        sized = size(gold, ml_cap)


        cat.sort(key=lambda x: x.ml_per_barrel, reverse=True)
        
        for barrel in cat:
            sized.size = barrel.sku.split('_')[0]
            q = sized.quantity(barrel.price, (barrel.ml_per_barrel+sum(ml)))
            if barrel.sku == sized.size + "_RED_BARREL" and ml[0] <= 200 and q > 0:
                print(ml, barrel.sku, barrel.price)
                my_plan.append({"sku": barrel.sku, "quantity": min(q, barrel.quantity)}) 
                sized.gold -= barrel.price*q
                ml[0] += barrel.ml_per_barrel


            elif barrel.sku == sized.size + "_GREEN_BARREL" and ml[1] <= 200 and q > 0:
                print(ml, barrel.sku, barrel.price)
                my_plan.append({"sku": barrel.sku, "quantity": min(q, barrel.quantity)}) 
                sized.gold -= barrel.price*q
                ml[1] += barrel.ml_per_barrel


            elif barrel.sku == sized.size + "_BLUE_BARREL" and ml[2] <= 200 and q > 0:
                print(ml, barrel.sku, barrel.price)
                my_plan.append({"sku": barrel.sku, "quantity": min(q, barrel.quantity)}) 
                sized.gold -= barrel.price*q
                ml[2] += barrel.ml_per_barrel


            elif barrel.sku == sized.size + "_DARK_BARREL" and ml[3] <= 200 and q > 0:
                print(ml, barrel.sku, barrel.price)
                my_plan.append({"sku": barrel.sku, "quantity": min(q, barrel.quantity)}) 
                sized.gold -= barrel.price*q
                ml[3] += barrel.ml_per_barrel
            
    return my_plan

        
    