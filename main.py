import asyncio
import json
import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
log = logging.getLogger("reseller-bot")

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


intents = discord.Intents.default()
intents.members = True          # Χρειάζεται για welcome / autorole / member join events
intents.message_content = True  # Χρειάζεται για prefix commands (προαιρετικό)


class ResellerBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=self._get_prefix, intents=intents)
        self.config = load_config()

    def _get_prefix(self, bot, message):
        return self.config.get("prefix", "!")

    def reload_config(self):
        self.config = load_config()
        return self.config

    def save_config(self):
        save_config(self.config)

    async def setup_hook(self):
        # Φόρτωση όλων των cogs (λειτουργικών modules)
        for ext in ("cogs.tickets", "cogs.catalog", "cogs.welcome", "cogs.admin"):
            try:
                await self.load_extension(ext)
                log.info(f"Φορτώθηκε: {ext}")
            except Exception as e:
                log.exception(f"Αποτυχία φόρτωσης {ext}: {e}")

    async def on_ready(self):
        log.info(f"Συνδέθηκε ως {self.user} (ID: {self.user.id})")
        
        # Άμεσoς συγχρονισμός σε κάθε server που βρίσκεται το bot
        try:
            for guild in self.guilds:
                self.tree.copy_global_to(guild=guild)
                synced = await self.tree.sync(guild=guild)
                log.info(f"Συγχρονίστηκαν {len(synced)} slash commands στον server: {guild.name} (ID: {guild.id})")
        except Exception as e:
            log.exception(f"Αποτυχία sync slash commands: {e}")

        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="τις παραγγελίες σας 🛒"
            )
        )


bot = ResellerBot()


async def main():
    if not TOKEN:
        raise SystemExit(
            "❌ Δεν βρέθηκε DISCORD_TOKEN. Αντέγραψε το .env.example σε .env "
            "και βάλε εκεί το token του bot σου."
        )
    async with bot:
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())