from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from enum import Enum
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)



class search_sort_options(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"   

@router.get("/search/", tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.timestamp,
    sort_order: search_sort_order = search_sort_order.desc,
):
    """
    Search for cart line items by customer name and/or potion sku.

    Customer name and potion sku filter to orders that contain the 
    string (case insensitive). If the filters aren't provided, no
    filtering occurs on the respective search term.

    Search page is a cursor for pagination. The response to this
    search endpoint will return previous or next if there is a
    previous or next page of results available. The token passed
    in that search response can be passed in the next search request
    as search page to get that page of results.

    Sort col is which column to sort by and sort order is the direction
    of the search. They default to searching by timestamp of the order
    in descending order.

    The response itself contains a previous and next page token (if
    such pages exist) and the results as an array of line items. Each
    line item contains the line item id (must be unique), item sku, 
    customer name, line item total (in gold), and timestamp of the order.
    Your results must be paginated, the max results you can return at any
    time is 5 total line items.
    """

    return {
        "previous": "",
        "next": "",
        "results": [
            {
                "line_item_id": 1,
                "item_sku": "1 oblivion potion",
                "customer_name": "Scaramouche",
                "line_item_total": 50,
                "timestamp": "2021-01-01T00:00:00Z",
            }
        ],
    }


nextID = 1
carts = {}

class Customer(BaseModel):
    customer_name: str
    character_class: str
    level: int

@router.post("/visits/{visit_id}")
def post_visits(visit_id: int, customers: list[Customer]):
    """
    Which customers visited the shop today?
    """
    print(customers)

    return "OK"



# GOOD return unique id pn cart. global vvariable o=increment every call.
@router.post("/")
def create_cart(new_cart: Customer):
    """ """
    global nextID, carts


    cart = {}
    id = nextID

    carts[nextID] = cart
    nextID += 1
    return {"cart_id": id}


class CartItem(BaseModel):
    quantity: int


prices = {"GREEN_POTION_0": 5,
          "RED_POTION_0": 5,
          "BLUE_POTION_0": 5}
# GOOD make dictionary and look up for this cart, record values that its buying 
@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    if item_sku not in prices.keys():
        print("ERROR")

    global carts
    cart = carts[cart_id]
    cart[item_sku] = cart_item.quantity


    return "OK"


class CartCheckout(BaseModel):
    payment: str


# -potions +gold
@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    global carts
    cart = carts[cart_id]

    bought = [0,0,0,0]
    cost = 0

    for sku, num in cart.items():
        if "RED" in sku:
            bought[0] += num

        elif "GREEN" in sku:
            bought[1] += num

        elif "BLUE" in sku:
            bought[2] += num

        cost += prices[sku] * num


    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
        for row in result:
            potions = [row.num_red_potions, row.num_green_potions, row.num_blue_potions]
            gold = row.gold

        for i in range(3):
            if potions[i] < bought[i]:
                return {}
            
        names = ["num_red_potions", "num_green_potions", "num_blue_potions"]

        for i in range(3):
            potions[i] -= bought[i]
            connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET {names[i]} = {potions[i]}"))



        gold += cost
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = {gold}"))

    return {"total_potions_bought": sum(bought), "total_gold_paid": cost}



