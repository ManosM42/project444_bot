import discord
from discord import app_commands
from discord.ext import commands


class Catalog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="catalog", description="Δείχνει τον κατάλογο υπηρεσιών και τις τιμές.")
    async def catalog(self, interaction: discord.Interaction):
        cfg = self.bot.config
        products = cfg.get("products", [])

        embed = discord.Embed(
            title=f"📋 Κατάλογος - {cfg.get('server_name', 'Shop')}",
            description="Ρίξε μια ματιά στις υπηρεσίες μας! Για παραγγελία, άνοιξε ticket με `/ticket-panel` ή στο κανάλι παραγγελιών.",
            color=discord.Color.blurple(),
        )

        if not products:
            embed.add_field(name="—", value="Δεν έχουν προστεθεί προϊόντα ακόμα.", inline=False)
        else:
            for p in products:
                embed.add_field(
                    name=f"{p.get('name', 'Υπηρεσία')} — {p.get('price', '?')}",
                    value=p.get("description", "—"),
                    inline=False,
                )

        embed.set_footer(text="Οι τιμές ενδέχεται να αλλάξουν χωρίς προειδοποίηση.")
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Catalog(bot))
