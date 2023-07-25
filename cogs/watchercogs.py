from discord.ext.commands import Context, command
from discord.ext import commands
import json

class WatchCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send(f'Welcome {member.mention}.')

        self._last_member = None

    @command(name="test", description='Test command')
    async def test_comm_string(self, ctx):
        await ctx.send(ctx.message.content)

    @command(name="ask", description='ask the bot a question')
    async def askbot(self, ctx):
        inmsg = ctx.message.content
        ai_prompt = ctx.ai_prompt
        chatpackage = [{
            "role":"system","content": ai_prompt},{
                "role":"user","content": inmsg
            }
        ]
        chatgptm = {"prompt":json.dumps(chatpackage)}
        await ctx.send(json.loads(chatgptm))

async def setup(bot):
    await bot.add_cog(WatchCog(bot))