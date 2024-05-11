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
        in_stock = connection.execute(sqlalchemy.text("""SELECT sku, potion_name, price, red, green, blue, dark, COALESCE(SUM(change),0) AS total
                                                      FROM potion_table
                                                      JOIN potion_ledger ON potion_table.id = potion_id
                                                      GROUP BY sku, price, potion_name, red, green, dark, blue
                                                      """))

        catalog = []
    for row in in_stock:
        if row.total != 0:
            catalog.append({"sku": row.sku,"name": row.potion_name, "quantity": row.total,"price": row.price, "potion_type": [row.red,
                                        row.green,
                                        row.blue,
                                        row.dark]
                    })   
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
