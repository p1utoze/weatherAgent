from uagents import Agent, Context, Bureau, Model

alice = Agent(name="alice", seed="alice recovery phrase")

@alice.on_interval(period=2.0)
async def say_hello(ctx: Context):
    ctx.logger.info(f"Hello from {ctx.name}")

if __name__ == "__main__":
    alice.run()