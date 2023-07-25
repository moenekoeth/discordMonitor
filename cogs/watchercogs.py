import json
import re
from datetime import datetime, timezone
from discord.ext.commands import Context, command
from discord.ext import commands

from dbloader import db_upsert,db_check,db_insert,db_commit,db_merge,db_update,disHist,disConf

class WatchCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.gconfigs = {}

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            gpk = {'srvid':str(guild.id)}
            if not db_check(gpk,disConf):
                gpk["cjson"] = {"initialized":True}
                db_insert([gpk],disConf)
            gpc = db_check(gpk,disConf)
            self.gconfigs[str(guild.id)] = gpc.cjson
            memberlist = []
            for member in [ x for x in guild.members if not x.bot ]:
                new_hist = {
                 'srvid': str(member.guild.id),
                 'duser': str(member.name),
                 'did': str(member.id),
                 'dlast': datetime.now(timezone.utc),
                 'dmsg': str("Found on connect")
                }
                pk = {'srvid':new_hist["srvid"],'did':new_hist["did"]}
                if not db_check(pk,disHist):
                   memberlist.append(dict(new_hist))
                   print(f"adding user - {guild.name} - {member.name}")
            db_insert(memberlist,disHist)

    @commands.Cog.listener()
    async def on_guild_join(self,guildo):
        print('We have joined a new guild ' + guildo.name )
        gpk = {'srvid':str(guildo.id)}
        if not db_check(gpk,disConf):
            gpk["cjson"] = {}
            db_insert([gpk],disConf)
        for member in [ x for x in guildo.members if not x.bot ]:
            new_hist = {
             'srvid': str(member.guild.id),
             'duser': str(member.name),
             'did': str(member.id),
             'dlast': datetime.now(timezone.utc),
             'dmsg': str("New Server")
            }
            print(f"adding user - {member.guild.name} - {member.name}")
            db_upsert([new_hist],disHist)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not member.bot:
            channel = member.guild.system_channel
            if channel is not None:
                await channel.send(f'Welcome {member.mention}.')
            new_hist = {
            'srvid': str(member.guild.id),
            'duser': str(member.name),
            'did': str(member.id),
            'dlast': datetime.now(timezone.utc),
            'dmsg': str("Joined server")
            }
            db_upsert([new_hist],disHist)

        self._last_member = None
        
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if not member.bot:
            channel = member.guild.system_channel
            if channel is not None:
                await channel.send(f'Goodbye {member.mention}.')
            new_hist = {
            'srvid': str(member.guild.id),
            'duser': str(member.name),
            'did': str(member.id),
            'dlast': datetime.now(timezone.utc),
            'dmsg': str("Left server")
            }
            db_upsert([new_hist],disHist)

        self._last_member = None

    @commands.Cog.listener()
    async def on_voice_state_update(self,member,before,after):
        if not member.bot:
            channel = member.guild.system_channel
            new_hist = {
            'srvid': str(member.guild.id),
            'duser': str(member.name),
            'did': str(member.id),
            'dlast': datetime.now(timezone.utc),
            'dmsg': str("Used voice")
            }
            db_upsert([new_hist],disHist)
    
            self._last_member = None

    @commands.Cog.listener()
    async def on_reaction_add(self,reaction,member):
        if not member.bot:
            channel = member.guild.system_channel
            rmsg = f"{channel.name} : {member.name} : " + str(reaction)
            new_hist = {
            'srvid': str(member.guild.id),
            'duser': str(member.name),
            'did': str(member.id),
            'dlast': datetime.now(timezone.utc),
            'dmsg': str(rmsg)
            }
            db_upsert([new_hist],disHist)

        self._last_member = None

    @commands.Cog.listener()
    async def on_message(self,message):
        if not message.author.bot:
            mmsg = f"{message.channel.name} : {message.content}"
            new_hist = {
            'srvid': str(message.channel.guild.id),
            'duser': str(message.author.name),
            'did': str(message.author.id),
            'dlast': datetime.now(timezone.utc),
            'dmsg': str(re.sub("http:","",re.sub("https","",re.sub("'","",mmsg))))
            }
            db_upsert([new_hist],disHist)
            print(f"{message.channel.guild.name} - {message.channel.name} : {message.author.name} : {message.content}")



    @command(name="test", description='Test command')
    async def test_comm_string(self, ctx):
        await ctx.send(ctx.message.content)

    @command(name="voidrole", description='Role for void')
    async def test_comm_string(self, ctx):
        voidrole = ctx.message.role_mentions[0]
        voidupdate = {"voidrole":str(voidrole.id)}
        self.gconfigs[str(ctx.guild.id)].update(voidupdate)
        db_update(db_field = 'cjson', db_value = self.gconfigs[str(ctx.guild.id)], db_where = disConf.srvid, db_is = str(ctx.guild.id), db_table = disConf)
        await ctx.send('Set void role to ' + str(voidrole.name))

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