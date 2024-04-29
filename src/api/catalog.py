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
        result = connection.execute(sqlalchemy.text("""SELECT * FROM potion_table WHERE quantity > 0 ORDER BY quantity DESC"""))

    catalog = []
    for i in range(6):
        row = result.fetchone()
        if row is None:
            break 
        catalog.append({"sku": row.sku, "name": row.potion_name, "quantity": row.quantity,
                        "price": row.price, "potion_type":[row.red, row.green, row.blue, row.dark] })
    #prices = {"GREEN_POTION_0": 5, "RED_POTION_0": 5, "BLUE_POTION_0": 5}

    #potion_skus = ["RED_POTION_0", "GREEN_POTION_0", "BLUE_POTION_0"]
    # potion_names = ["red potion", "green potion", "blue potion"]
    # potion_type = [[100,0,0,0], [0,100,0,0], [0,0,100,0]]
    # for i in range(3):
    #     if num_potions[i] > 0:
    #         catalog.append({
    #                 "sku": potion_skus[i],
    #                 "name": potion_names[i],
    #                 "quantity": num_potions[i],
    #                 "price": prices[potion_skus[i]],
    #                 "potion_type": potion_type[i],
    #             })

    return catalog
