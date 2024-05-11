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

    # Determine sorting column based on user's choice
    if sort_col == search_sort_options.customer_name:
        order_by = db.search_view.c.customer_name
    elif sort_col == search_sort_options.item_sku:
        order_by = db.search_view.c.item_sku
    elif sort_col == search_sort_options.line_item_total:
        order_by = db.search_view.c.quantity
    elif sort_col == search_sort_options.timestamp:
        order_by = db.search_view.c.created_at
    else:
        raise ValueError("Invalid sorting column")


    order_by = order_by.asc() if sort_order == search_sort_order.asc else order_by.desc()

    offset = 0 if not search_page else int(search_page)

    stmt = sqlalchemy.select(db.search_view).order_by(order_by).limit(6).offset(5 * offset)

    if customer_name:
        stmt = stmt.where(db.search_view.c.customer_name.ilike(f"%{customer_name}%"))
    if potion_sku:
        stmt = stmt.where(db.search_view.c.item_sku.ilike(f"%{potion_sku}%"))

    results_list = []
    with db.engine.begin() as conn:
        results = conn.execute(stmt)
        for item in results:
            results_list.append({
                "line_item_id": item.customer_id,
                "item_sku": item.item_sku,
                "customer_name": item.customer_name,
                "line_item_total": item.gold,
                "timestamp": item.created_at,
            })

    
    prev_link = "" if (offset - 1) < 0 else str(offset - 1)
    next_link = str(offset + 1) if len(results_list) > 5 else ""

    response = {
        "previous": prev_link,
        "next": next_link,
        "results": results_list[:5]
    }

    return response


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


@router.post("/")
def create_cart(new_cart: Customer):
    """ """
    meta = sqlalchemy.MetaData()
    carts = sqlalchemy.Table("carts", meta, autoload_with= db.engine) 



    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.insert(carts),[
            {"name": new_cart.customer_name,
             "class": new_cart.character_class,
             "level": new_cart.level}],)
        return {"cart_id": connection.execute(sqlalchemy.text("SELECT MAX(ID) from carts")).scalar_one()}



class CartItem(BaseModel):
    quantity: int



@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("INSERT INTO carts_items (customer_id, quantity, item_id) SELECT id, :quantity, :cart_id FROM potion_table WHERE sku = :item_sku "),[{"cart_id": cart_id, "item_sku": item_sku, "quantity": cart_item.quantity}])

    return "OK"

class CartCheckout(BaseModel):
    payment: str


# -potions +gold
@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    r = 0
    t = 0
    st = ''

    
    with db.engine.begin() as connection:
        potions_bought = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(cart_items.quantity),0) AS total, item_id, price, potion_name 
                                                            FROM cart_items 
                                                            JOIN potion_table ON potion_table.id = item_id
                                                            WHERE customer_id = :cart_id
                                                            GROUP BY item_id, price, potion_name"""),[{"cart_id": cart_id}]).fetchall()
        for potion in potions_bought:   
            t += potion.total
            r += potion.total * potion.price
            st += f'{potion.potion_name}, '
            connection.execute(sqlalchemy.text("""INSERT INTO potion_ledger (potion_id, change, description) VALUES (:item_id, :total, :describe)"""),[{"item_id": potion.item_id, "total": potion.total*-1, "describe": f'sold! {cart_id}'}])
        connection.execute(sqlalchemy.text("""INSERT INTO gold_ledger (change, description) VALUES (:revenue, :describe)"""),[{"revenue": r, "describe": f'sold {t} : {st}'}])



    return {"total_potions_bought": t, "total_gold_paid": r}