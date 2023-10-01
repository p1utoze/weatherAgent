from protocols.book import BookTableRequest, BookTableResponse, book_protocol
from protocols.query import (
    QueryTableRequest,
    QueryTableResponse,
    TableStatus,
    query_protocol,
)
from uagents import Agent, Bureau, Context

restaurant = Agent(name="restaurant")
restaurant.include(protocol=book_protocol)
restaurant.include(protocol=query_protocol)

customer = Agent(name="customer")


@customer.on_interval(period=3.0, messages=QueryTableRequest)
async def interval(ctx: Context):
    started = ctx.storage.get("started")
    if not started:
        await ctx.send(restaurant.address, QueryTableRequest(table_number=43))


@customer.on_message(QueryTableResponse, replies={BookTableRequest})
async def handle_query_response(ctx: Context, sender: str, response: QueryTableResponse):
    if response.status == TableStatus.FREE.value:
        ctx.logger.info("Table is free. Attempting to reserve...")
        await ctx.send(sender, BookTableRequest(table_number=43))
    else:
        ctx.logger.info("Table is not free. Please wait...")


@customer.on_message(BookTableResponse, replies=set())
async def handle_book_response(ctx: Context, __sender: str, response: BookTableResponse):
    if response.success:
        ctx.logger.info("Table reservation has been confirmed!")
    else:
        ctx.logger.info("Table reservation has been rejected!")

    ctx.storage.set("started", True)


bureau = Bureau()
bureau.add(customer)
bureau.add(restaurant)


if __name__ == "__main__":
    bureau.run()
