import discord
from discord import app_commands
from discord.ext import commands


def get_dot_role(guild: discord.Guild):
    return discord.utils.get(guild.roles, name=".")


def get_owner_role(guild: discord.Guild):
    return discord.utils.get(guild.roles, name=".Owner")


def get_customer_role(guild: discord.Guild):
    return discord.utils.get(guild.roles, name=".Customer")


def has_exclusion_permission(guild: discord.Guild, user: discord.Member):
    """Ελέγχει αν ο χρήστης εξαιρείται από το Customer role (δηλ. είναι Admin, '.' ή '.Owner')."""
    if user.guild_permissions.administrator:
        return True
    dot_role = get_dot_role(guild)
    owner_role = get_owner_role(guild)
    if dot_role and dot_role in user.roles:
        return True
    if owner_role and owner_role in user.roles:
        return True
    return False


class UnifiedTicketPanelView(discord.ui.View):
    """Persistent view με τα κουμπιά Purchase, Support και Replace."""

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="🛒 Purchase",
        style=discord.ButtonStyle.green,
        custom_id="ticket:purchase",
        row=0
    )
    async def purchase_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        cog: "Tickets" = interaction.client.get_cog("Tickets")
        await cog.create_ticket(interaction, "purchase")

    @discord.ui.button(
        label="🛠️ Support",
        style=discord.ButtonStyle.blurple,
        custom_id="ticket:support",
        row=0
    )
    async def support_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        cog: "Tickets" = interaction.client.get_cog("Tickets")
        await cog.create_ticket(interaction, "support")

    @discord.ui.button(
        label="🔄 Replace",
        style=discord.ButtonStyle.grey,
        custom_id="ticket:replace",
        row=0
    )
    async def replace_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        cog: "Tickets" = interaction.client.get_cog("Tickets")
        await cog.create_ticket(interaction, "replace")


class TicketControlView(discord.ui.View):
    """Κουμπιά μέσα στο ticket: Επιβεβαίωση Πληρωμής / Κλείσιμο."""

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="✅ Επιβεβαίωση Πληρωμής / Mark Paid",
        style=discord.ButtonStyle.success,
        custom_id="ticket:mark_paid",
    )
    async def mark_paid(self, interaction: discord.Interaction, button: discord.ui.Button):
        cog: "Tickets" = interaction.client.get_cog("Tickets")
        await cog.mark_paid(interaction)

    @discord.ui.button(
        label="🔒 Κλείσιμο Ticket / Close",
        style=discord.ButtonStyle.danger,
        custom_id="ticket:close",
    )
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        cog: "Tickets" = interaction.client.get_cog("Tickets")
        await cog.close_ticket(interaction)


class Tickets(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        self.bot.add_view(UnifiedTicketPanelView())
        self.bot.add_view(TicketControlView())

    # ---------- Ενιαίο Slash Command για το Panel ----------
    @app_commands.command(name="ticket-panel", description="Στέλνει το ενιαίο panel δημιουργίας ticket (μόνο staff).")
    async def ticket_panel(self, interaction: discord.Interaction):
        if not has_exclusion_permission(interaction.guild, interaction.user):
            await interaction.response.send_message("❌ Δεν έχεις δικαίωμα για αυτή την εντολή. / You don't have permission.", ephemeral=True)
            return

        cfg = self.bot.config
        embed = discord.Embed(
            title=f"🎫 {cfg.get('server_name', 'Shop')} - Ticket System",
            description=(
                "🇬🇷 Χρειάζεσαι βοήθεια, θέλεις να κάνεις μια αγορά ή αντικατάσταση;\n"
                "Πάτησε το αντίστοιχo κουμπί παρακάτω:\n"
                "• **Purchase** - Για αγορές (δες `/catalog`)\n"
                "• **Support** - Για υποστήριξη & προβλήματα\n"
                "• **Replace** - Για αντικατάσταση προϊόντος\n\n"
                "🇺🇸 Need help, want to purchase or replace?\n"
                "Click the corresponding button below:\n"
                "• **Purchase** - For orders (see `/catalog`)\n"
                "• **Support** - For support & issues\n"
                "• **Replace** - For product replacement"
            ),
            color=discord.Color.blurple(),
        )
        embed.set_footer(text="Επιλέξτε μια κατηγορία / Select a category 👇")
        
        await interaction.channel.send(embed=embed, view=UnifiedTicketPanelView())
        await interaction.response.send_message("✅ Το panel στάλθηκε επιτυχώς. / Panel sent successfully.", ephemeral=True)

    # ---------- Δημιουργία ticket ανάλογα με την επιλογή ----------
    async def create_ticket(self, interaction: discord.Interaction, ticket_type: str):
        guild = interaction.guild
        cfg = self.bot.config
        user = interaction.user

        # Αυτόματη προσθήκη του ρόλου .Customer σε οποιονδήποτε ΔΕΝ έχει '.' ή '.Owner'
        if not has_exclusion_permission(guild, user):
            customer_role = get_customer_role(guild)
            if customer_role:
                if customer_role not in user.roles:
                    try:
                        await user.add_roles(customer_role, reason="Auto-assign Customer role on ticket creation")
                    except discord.Forbidden:
                        print("⚠️ Σφάλμα: Το bot δεν έχει δικαιώματα (Manage Roles) ή ο ρόλος .Customer είναι πάνω από το bot!")
                    except Exception as e:
                        print(f"⚠️ Σφάλμα κατά την προσθήκη ρόλου Customer: {e}")

        category = None
        if cfg.get("ticket_category_id"):
            category = guild.get_channel(cfg["ticket_category_id"])

        channel_name = f"{ticket_type}-{user.name}".lower()

        existing = discord.utils.get(guild.text_channels, name=channel_name)
        if existing:
            await interaction.response.send_message(
                f"⚠️ Έχεις ήδη ανοιχτό ticket / You already have an open ticket: {existing.mention}", ephemeral=True
            )
            return

        dot_role = get_dot_role(guild)
        owner_role = get_owner_role(guild)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        }
        
        if dot_role:
            overwrites[dot_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)
        if owner_role:
            overwrites[owner_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites,
            topic=f"Ticket ({ticket_type.upper()}) για {user} (ID: {user.id})",
        )

        # Δίγλωσση διαμόρφωση μηνύματος ανάλογα με τον τύπο του ticket
        if ticket_type == "purchase":
            embed = discord.Embed(
                title="🛒 Νέα Παραγγελία / New Purchase",
                description=(
                    f"🇬🇷 Καλωσόρισες {user.mention}!\n"
                    "Γράψε μας ποια/ποιες υπηρεσίες θέλεις να παραγγείλεις (δες `/catalog`).\n"
                    f"**Τρόποι πληρωμής / Payment methods:** {', '.join(cfg.get('payment_methods', []))}\n"
                    "Όταν ολοκληρωθεί η πληρωμή, το staff θα πατήσει **✅ Επιβεβαίωση Πληρωμής**.\n\n"
                    f"🇺🇸 Welcome {user.mention}!\n"
                    "Let us know which services you want to order (see `/catalog`).\n"
                    "Once payment is complete, staff will click **Mark Paid**."
                ),
                color=discord.Color.green(),
            )
        elif ticket_type == "support":
            embed = discord.Embed(
                title="🛠️ Τμήμα Υποστήριξης / Support",
                description=(
                    f"🇬🇷 Γεια σου {user.mention}!\n"
                    "Περιέγραψε αναλυτικά το πρόβλημα ή την ερώτησή σου και κάποιος από το staff θα σε εξυπηρετήσει σύντομα.\n\n"
                    f"🇺🇸 Hello {user.mention}!\n"
                    "Describe your issue or question in detail and a staff member will assist you soon."
                ),
                color=discord.Color.blurple(),
            )
        else:  # replace
            embed = discord.Embed(
                title="🔄 Αίτημα Αντικατάστασης / Replacement",
                description=(
                    f"🇬🇷 Γεια σου {user.mention}!\n"
                    "Γράψε μας ποιο προϊόν/λογαριασμό αντιμετωπίζει πρόβλημα και στείλε τα απαραίτητα αποδεικτικά (π.χ. screenshot).\n\n"
                    f"🇺🇸 Hello {user.mention}!\n"
                    "Let us know which product/account is facing an issue and send necessary proof (e.g. screenshot)."
                ),
                color=discord.Color.orange(),
            )

        # Mentions: User, .Owner, .
        mentions = [user.mention]
        if owner_role:
            mentions.append(owner_role.mention)
        if dot_role:
            mentions.append(dot_role.mention)
        
        content_mentions = " ".join(mentions)

        await channel.send(content=content_mentions, embed=embed, view=TicketControlView())

        await interaction.response.send_message(f"✅ Το ticket δημιουργήθηκε / Created: {channel.mention}", ephemeral=True)
        await self._log(guild, f"🎫 Νέο ticket ({ticket_type}) από {user.mention}: {channel.mention}")

    # ---------- Επιβεβαίωση πληρωμής ----------
    async def mark_paid(self, interaction: discord.Interaction):
        if not has_exclusion_permission(interaction.guild, interaction.user):
            await interaction.response.send_message("❌ Μόνο το staff/owner μπορεί να επιβεβαιώσει πληρωμή.", ephemeral=True)
            return

        embed = discord.Embed(
            description=f"✅ Η πληρωμή επιβεβαιώθηκε από {interaction.user.mention} / Payment confirmed by {interaction.user.mention}. Ευχαριστούμε!",
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed)
        try:
            await interaction.channel.edit(name=f"✅-{interaction.channel.name}")
        except discord.HTTPException:
            pass
        await self._log(interaction.guild, f"✅ Πληρωμή επιβεβαιώθηκε στο {interaction.channel.mention} από {interaction.user.mention}")

    # ---------- Κλείσιμο ticket ----------
    async def close_ticket(self, interaction: discord.Interaction):
        if not has_exclusion_permission(interaction.guild, interaction.user):
            await interaction.response.send_message("❌ Μόνο το staff/owner μπορεί να κλείσει το ticket.", ephemeral=True)
            return

        await interaction.response.send_message("🔒 Το ticket κλείνει σε 5 δευτερόλεπτα / Closing in 5 seconds...")
        await self._log(interaction.guild, f"🔒 Το ticket {interaction.channel.name} έκλεισε από {interaction.user.mention}")
        await discord.utils.sleep_until(discord.utils.utcnow() + __import__("datetime").timedelta(seconds=5))
        await interaction.channel.delete()

    async def _log(self, guild: discord.Guild, message: str):
        log_id = self.bot.config.get("ticket_log_channel_id")
        if not log_id:
            return
        channel = guild.get_channel(log_id)
        if channel:
            await channel.send(message)


async def setup(bot: commands.Bot):
    await bot.add_cog(Tickets(bot))