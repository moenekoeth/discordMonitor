from discord.ext.commands import Context, command
from discord.ext import commands
import json

class OtherCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="other", description='Test command')
    async def other_comm_string(self, ctx):
        await ctx.send(ctx.message.content)


async def setup(bot):
    await bot.add_cog(OtherCog(bot))