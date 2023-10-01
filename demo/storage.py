

from uagents import Context, Agent

alice = Agent(name='alice', seed='alice recovery seed')


@alice.on_interval(period=1.0)
async def alice_interval(context: Context):
    current_count = context.storage.get('count') or 0
    context.logger.info(f"Current count = {current_count}")
    context.storage.set('count', current_count + 1)

if __name__ == '__main__':
    alice.run()
