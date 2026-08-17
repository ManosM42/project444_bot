import discord
from discord.ext import commands


class Welcome(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        cfg = self.bot.config

        # 1. Auto-role
        role_id = cfg.get("autorole_id")
        if role_id:
            role = member.guild.get_role(role_id)
            if role:
                try:
                    await member.add_roles(role, reason="Auto-role νέου μέλους")
                except discord.Forbidden:
                    pass

        # 2. Μήνυμα καλωσορίσματος (Embed)
        channel_id = cfg.get("welcome_channel_id")
        if channel_id:
            channel = member.guild.get_channel(channel_id)
            if channel:
                embed = discord.Embed(
                    title="👋 Καλωσόρισες!",
                    description=(
                        f"Καλωσόρισες στο **{cfg.get('server_name', member.guild.name)}**, {member.mention}!\n\n"
                        "📋 Δες τον κατάλογο μας με `/catalog`\n"
                        "🛒 Άνοιξε παραγγελία από το κανάλι παραγγελιών"
                    ),
                    color=discord.Color.green(),
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                await channel.send(embed=embed)

        # 3. Auto ping στα κανάλια ｜📦〃owner-restock και 📝〃feedback (διαγραφή σε 3 δευτερόλεπτα)
        target_channels = ["｜📦〃owner-restock", "📝〃feedback"]
        
        for name in target_channels:
            ch = discord.utils.get(member.guild.text_channels, name=name)
            if ch:
                await ch.send(
                    content=f"👋 Νέο μέλος: {member.mention}",
                    delete_after=3.0
                )


async def setup(bot: commands.Bot):
    await bot.add_cog(Welcome(bot))