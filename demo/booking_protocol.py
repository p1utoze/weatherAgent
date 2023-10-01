from enum import Enum
from uagents import Agent, Bureau, Context, Model


class TableStatus(str, Enum):
    RESERVED = "reserved"
    FREE = "free"


class QueryTableRequest(Model):
    table_number: int


class QueryTableResponse(Model):
    status: TableStatus


class BookTableRequest(Model):
    table_number: int


class BookTableResponse(Model):
    success: bool


customer = Agent(name="Customer")
restaurant = Agent(name="Restaurant")


@customer.on_interval(period=3.0, messages=QueryTableRequest)
async def interval(ctx: Context):
    started = ctx.storage.get("started")
    if not started:
        await ctx.send(restaurant.address, QueryTableRequest(table_number=43))

    ctx.storage.set("started", True)


@customer.on_message(QueryTableResponse, replies=BookTableRequest)
async def handle_query_response(ctx: Context, __sender: str, response: QueryTableResponse):
    if response.status == TableStatus.FREE:
        ctx.logger.info("Table is free. Attempting to reserve...")
        await ctx.send(restaurant.address, BookTableRequest(table_number=43))
    else:
        ctx.logger.info("Table is not free. Please wait...")


@customer.on_message(BookTableResponse, replies=set())
async def handle_book_response(ctx: Context, __sender: str, response: BookTableResponse):
    if response.success:
        ctx.logger.info("Table reservation has been confirmed!")
    else:
        ctx.logger.info("Table reservation has been rejected!")


@restaurant.on_message(model=QueryTableRequest, replies=QueryTableResponse)
async def handle_query_request(ctx: Context, sender: str, request: QueryTableRequest):
    if ctx.storage.has(str(request.table_number)):
        status = TableStatus.RESERVED
    else:
        status = TableStatus.FREE
    
    ctx.logger.info(f"Table {request.table_number} is {status}")
    await ctx.send(sender, QueryTableResponse(status=status))


@restaurant.on_message(model=BookTableRequest, replies=BookTableResponse)
async def handle_book_request(ctx: Context, sender: str, request: BookTableRequest):
    if ctx.storage.has(str(request.table_number)):
        success = False
    else:
        ctx.storage.set(str(request.table_number), sender)
        success = True

    await ctx.send(sender, BookTableResponse(success=success))


if __name__ == "__main__":
    bureau = Bureau()
    bureau.add(customer)
    bureau.add(restaurant)
    bureau.run()
