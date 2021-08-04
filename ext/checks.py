async def is_correct_channel(ctx):
    return ctx.channel.name in ctx.bot.gen_channels
