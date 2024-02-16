import os, traceback
from disnake.ext.commands import InteractionBot as BotBase, errors, CommandSyncFlags
from disnake import Intents, Activity, ActivityType, AllowedMentions
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from ..db import db
from glob import glob
from dotenv import load_dotenv

load_dotenv()

main_token = os.getenv("MAIN_TOKEN")

COGS = [path.split("\\")[-1][:-3] for path in glob("./cogs/*.py")]

class Ready(object):
    def __init__(self):
        for cog in COGS:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f"{cog} is ready.")

    def all_ready(self):
        return all([getattr(self, cog) for cog in COGS])

class Bot(BotBase):
    def __init__(self):
        self.scheduler = AsyncIOScheduler()

        db.autosave(self.scheduler)
        super().__init__(intents=Intents.all(), command_sync_flags=CommandSyncFlags(sync_global_commands=True), allowed_mentions=AllowedMentions(roles=False, everyone=False, users=False), activity=Activity(type=ActivityType.playing, name=f"v1.0.0 | /help"), reload=True)

    def setup(self):
        for cog in os.listdir('./cogs'):
            if cog.endswith(".py"):
                try:
                    cog = f"cogs.{cog.replace('.py', '')}"
                    self.load_extension(cog)
                except Exception:
                    print(f"{cog} can not be loaded.\nReason: {traceback.format_exc()}")

    def run(self):
        print("Running setup...")
        self.setup()

        print("Getting the token...")

        super().run(main_token, reconnect=True)

    async def on_connect(self):
        print("Connected!")

    async def on_disconnect(self):
        print("Disconnected!")

    async def on_ready(self):
        self.scheduler.start()
        print("Ready!")

    async def on_slash_command_error(self, ctx, error):
        if isinstance(error, errors.CommandOnCooldown):
            await ctx.send(f"{ctx.author.mention}, please try again after {round(error.retry_after)} seconds.")
        else:
            raise error

bot = Bot()