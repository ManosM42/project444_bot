import discord
from discord import app_commands
from discord.ext import commands


def admin_only():
    async def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.guild_permissions.administrator
    return app_commands.check(predicate)


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    settings = app_commands.Group(name="settings", description="Ρυθμίσεις του bot (μόνο admin).")
    product = app_commands.Group(name="product", description="Διαχείριση καταλόγου (μόνο admin).")

    # ---------------- SETTINGS ----------------
    @settings.command(name="staff-role", description="Ορίζει τον ρόλο του staff.")
    @admin_only()
    async def set_staff_role(self, interaction: discord.Interaction, role: discord.Role):
        self.bot.config["staff_role_id"] = role.id
        self.bot.save_config()
        await interaction.response.send_message(f"✅ Ο ρόλος staff ορίστηκε σε {role.mention}", ephemeral=True)

    @settings.command(name="ticket-category", description="Ορίζει την κατηγορία όπου θα δημιουργούνται τα tickets.")
    @admin_only()
    async def set_ticket_category(self, interaction: discord.Interaction, category: discord.CategoryChannel):
        self.bot.config["ticket_category_id"] = category.id
        self.bot.save_config()
        await interaction.response.send_message(f"✅ Η κατηγορία tickets ορίστηκε σε **{category.name}**", ephemeral=True)

    @settings.command(name="log-channel", description="Ορίζει το κανάλι logs για tickets/πληρωμές.")
    @admin_only()
    async def set_log_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        self.bot.config["ticket_log_channel_id"] = channel.id
        self.bot.save_config()
        await interaction.response.send_message(f"✅ Το κανάλι logs ορίστηκε σε {channel.mention}", ephemeral=True)

    @settings.command(name="welcome-channel", description="Ορίζει το κανάλι καλωσορίσματος.")
    @admin_only()
    async def set_welcome_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        self.bot.config["welcome_channel_id"] = channel.id
        self.bot.save_config()
        await interaction.response.send_message(f"✅ Το κανάλι καλωσορίσματος ορίστηκε σε {channel.mention}", ephemeral=True)

    @settings.command(name="autorole", description="Ορίζει τον ρόλο που παίρνουν αυτόματα τα νέα μέλη.")
    @admin_only()
    async def set_autorole(self, interaction: discord.Interaction, role: discord.Role):
        self.bot.config["autorole_id"] = role.id
        self.bot.save_config()
        await interaction.response.send_message(f"✅ Το autorole ορίστηκε σε {role.mention}", ephemeral=True)

    # ---------------- PRODUCTS ----------------
    @product.command(name="add", description="Προσθέτει μια υπηρεσία στον κατάλογο.")
    @admin_only()
    async def add_product(self, interaction: discord.Interaction, name: str, price: str, description: str):
        self.bot.config.setdefault("products", []).append(
            {"name": name, "price": price, "description": description}
        )
        self.bot.save_config()
        await interaction.response.send_message(f"✅ Προστέθηκε: **{name}** — {price}", ephemeral=True)

    @product.command(name="remove", description="Αφαιρεί μια υπηρεσία από τον κατάλογο (με το ακριβές όνομα).")
    @admin_only()
    async def remove_product(self, interaction: discord.Interaction, name: str):
        products = self.bot.config.get("products", [])
        new_products = [p for p in products if p.get("name") != name]
        if len(new_products) == len(products):
            await interaction.response.send_message(f"⚠️ Δεν βρέθηκε υπηρεσία με όνομα **{name}**.", ephemeral=True)
            return
        self.bot.config["products"] = new_products
        self.bot.save_config()
        await interaction.response.send_message(f"✅ Αφαιρέθηκε: **{name}**", ephemeral=True)

    @product.command(name="list", description="Λίστα όλων των υπηρεσιών (ωμά δεδομένα, για admin).")
    @admin_only()
    async def list_products(self, interaction: discord.Interaction):
        products = self.bot.config.get("products", [])
        if not products:
            await interaction.response.send_message("Δεν υπάρχουν προϊόντα.", ephemeral=True)
            return
        lines = [f"- **{p['name']}** — {p['price']}" for p in products]
        await interaction.response.send_message("\n".join(lines), ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))
