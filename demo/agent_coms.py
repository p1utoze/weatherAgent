from uagents import Bureau, Context, Agent, Model

class Message(Model):
    message: str

alice = Agent(name="Alice", seed="alice recovery phrase")
bob = Agent(name="Bob", seed="bob recovery phrase")

@alice.on_interval(period=2.0)
async def alice_sends_message(ctx: Context):
    await ctx.send(bob.address, Message(message="Hello, Bob!"))


@alice.on_message(model=Message)
async def alice_receives_message(ctx: Context, sender: str, message: Message):
    ctx.logger.info(f"Alice received a message from {sender}: {message.message}")


@bob.on_message(model=Message)
async def bob_receives_message(ctx: Context, sender: str, message: Message):
    ctx.logger.info(f"Bob received a message from {sender}: {message.message}")
    await ctx.send(alice.address, Message(message="Hello, Alice!"))

if __name__ == "__main__":
    bureau = Bureau()
    bureau.add(alice)
    bureau.add(bob)
    bureau.run()
