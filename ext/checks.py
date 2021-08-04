async def is_correct_channel(ctx):
    print(ctx.channel.name)
    return ctx.channel.name in ctx.bot.gen_channels