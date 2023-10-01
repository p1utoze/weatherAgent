from enum import Enum
from uagents import Agent, Bureau, Context, Model, Protocol

class TableStatus(str, Enum):
    RESERVED = "reserved"
    FREE = "free"


class QueryTableRequest(Model):
    table_number: int


class QueryTableResponse(Model):
    status: TableStatus

query_protocol = Protocol()


@query_protocol.on_message(model=QueryTableRequest, replies={QueryTableResponse})
async def handle_query_table_request(context: Context, sender: str, request: QueryTableRequest):
    if context.storage.has(str(request.table_number)):
        status = TableStatus.RESERVED
    else:
        status = TableStatus.FREE

    context.logger.info(f"Table {request.table_number} is {status.value}")
    await context.send(sender, QueryTableResponse(status=status))