from enum import Enum
from uagents import (
        Agent,
        Bureau,
        Context,
        Model,
        Protocol
)


class BookTableRequest(Model):
    table_number: int


class BookTableResponse(Model):
    success: bool


book_protocol = Protocol()


@book_protocol.on_message(model=BookTableRequest, replies={BookTableResponse})
async def handle_book_request(ctx: Context, sender: str, request: BookTableRequest):
    if ctx.storage.has(str(request.table_number)):
        success = False
    else:
        ctx.storage.set(str(request.table_number), sender)
        success = True

    await ctx.send(sender, BookTableResponse(success=success))
