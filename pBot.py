# bot.py
# Discord.py 2.x public-ready bot:
# - No hardcoded IDs; per-guild config in bot_config.json
# - /start setup wizard (admin-only) to configure:
#     • Bot Logs Channel
#     • Archive Category
#     • Verification Channel  (+ auto post verify message + reaction)
#     • Verification Role     (mention/ID, create, or none)
#     • Ticket Recipient      (Server Owner or specific User_ID)
# - Verification reaction gives configured role
# - Ticket system with modal + per-user cooldown (10 min), sends to configured recipient
# - Role utilities: /giverole, /removerole, /userroles, /viewroles
# - Simple command logging to bot-logs channel

import os
import json
import asyncio
import time
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

CONFIG_FILE = "bot_config.json"

# ---------- Config helpers ----------
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_config(data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def guild_cfg(guild_id: int) -> dict:
    cfg = load_config()
    gid = str(guild_id)
    if gid not in cfg:
        cfg[gid] = {}
        save_config(cfg)
    return cfg[gid]

def update_guild_cfg(guild_id: int, key: str, value):
    cfg = load_config()
    gid = str(guild_id)
    if gid not in cfg:
        cfg[gid] = {}
    cfg[gid][key] = value
    save_config(cfg)

# ---------- Bot / Intents ----------
intents = discord.Intents.default()
intents.guilds = True
intents.members = True   # needed to add roles on verify & use Member converter in slash cmds
intents.message_content = False  # not required here

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# ---------- Utilities ----------
async def log_to_channel(guild: discord.Guild, *, content: Optional[str] = None, embed: Optional[discord.Embed] = None):
    cfg = guild_cfg(guild.id)
    ch_id = cfg.get("bot_logs")
    if not ch_id:
        return
    ch = guild.get_channel(ch_id)
    if ch:
        try:
            await ch.send(content=content, embed=embed)
        except discord.Forbidden:
            pass

def parse_channel_id(s: str) -> Optional[int]:
    s = s.strip().replace(" ", "")
    # Accept raw ID or <#123>
    if s.startswith("<#") and s.endswith(">"):
        s = s[2:-1]
    try:
        return int(s)
    except ValueError:
        return None

def parse_role_id(s: str) -> Optional[int]:
    s = s.strip().replace(" ", "")
    # Accept raw ID or <@&123>
    if s.startswith("<@&") and s.endswith(">"):
        s = s[3:-1]
    try:
        return int(s)
    except ValueError:
        return None

def parse_user_id(s: str) -> Optional[int]:
    s = s.strip().replace(" ", "")
    # Accept raw ID or <@123> or <@!123>
    if s.startswith("<@") and s.endswith(">"):
        core = s[2:-1]
        if core.startswith("!"):
            core = core[1:]
        s = core
    try:
        return int(s)
    except ValueError:
        return None

# ask a question in the same channel; wait for the admin's reply
async def ask_channel_question(interaction: discord.Interaction, question: str, timeout: int = 180) -> Optional[discord.Message]:
    await interaction.channel.send(question)
    def check(m: discord.Message):
        return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id
    try:
        msg = await bot.wait_for("message", check=check, timeout=timeout)
        if msg.content.lower() == "cancel":
            await interaction.channel.send("❌ Setup cancelled.")
            return None
        return msg
    except asyncio.TimeoutError:
        await interaction.channel.send("⏳ Setup timed out. Please run `/start` again.")
        return None

# Decorator to require setup for some commands
def require_setup(keys: list[str]):
    async def predicate(inter: discord.Interaction):
        cfg = guild_cfg(inter.guild.id)
        missing = [k for k in keys if not cfg.get(k)]
        if missing:
            await inter.response.send_message(
                f"⚠️ This server hasn't finished setup. An admin should run `/start` first (missing: {', '.join(missing)}).",
                ephemeral=True
            )
            return False
        return True
    return app_commands.check(predicate)

# ---------- Verification: reaction handler ----------
@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    if payload.guild_id is None or str(payload.emoji) != "✅":
        return
    guild = bot.get_guild(payload.guild_id)
    if not guild:
        return
    if payload.user_id == bot.user.id:
        return

    cfg = guild_cfg(guild.id)
    verify_channel_id = cfg.get("verification_channel")
    verify_msg_id = cfg.get("verification_message_id")
    verify_role_id = cfg.get("verification_role_id")

    if not (verify_channel_id and verify_msg_id and verify_role_id):
        return
    if payload.channel_id != verify_channel_id or payload.message_id != verify_msg_id:
        return

    member = guild.get_member(payload.user_id)
    role = guild.get_role(verify_role_id)
    if not member or not role:
        return
    try:
        await member.add_roles(role, reason="User verified via reaction")
        try:
            await member.send(f"✅ You have been verified in **{guild.name}**.")
        except discord.Forbidden:
            pass
        await log_to_channel(guild, embed=discord.Embed(
            title="✅ User Verified",
            description=f"{member.mention} received {role.mention}",
            color=discord.Color.green()
        ))
    except discord.Forbidden:
        await log_to_channel(guild, content=f"⚠️ Missing permissions to add {role} to {member}.")

# ---------- Ticket system ----------
cooldowns = {}  # {user_id: last_timestamp}

class TicketModal(discord.ui.Modal, title="Create Ticket 📨"):
    reason_field = discord.ui.TextInput(
        label="Reason",
        placeholder="Provide details about the issue or suggestion",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=4000,
    )

    def __init__(self, recipient: discord.Member):
        super().__init__()
        self.recipient = recipient

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📩 New Ticket Submitted",
            color=discord.Color.blurple(),
        )
        embed.add_field(name="From", value=f"{interaction.user} ({interaction.user.id})", inline=False)
        embed.add_field(name="Reason", value=self.reason_field.value, inline=False)
        embed.timestamp = discord.utils.utcnow()

        try:
            await self.recipient.send(embed=embed)
            await interaction.response.send_message("✅ Your ticket has been submitted.", ephemeral=True)
            await log_to_channel(interaction.guild, embed=discord.Embed(
                title="📝 Ticket Created",
                description=f"From {interaction.user.mention} sent to {self.recipient.mention}",
                color=discord.Color.blurple()
            ))
        except discord.Forbidden:
            await interaction.response.send_message("⚠️ Could not DM the ticket recipient.", ephemeral=True)

class TicketButton(discord.ui.View):
    def __init__(self, recipient: discord.Member):
        super().__init__(timeout=None)
        self.recipient = recipient

    @discord.ui.button(label="Create Ticket", style=discord.ButtonStyle.blurple, custom_id="ticket:create")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        now = time.time()
        last = cooldowns.get(interaction.user.id, 0)
        if now - last < 600:
            remaining = int(600 - (now - last))
            return await interaction.response.send_message(
                f"⏳ You must wait {remaining} seconds before creating another ticket.",
                ephemeral=True
            )
        cooldowns[interaction.user.id] = now
        await interaction.response.send_modal(TicketModal(self.recipient))

# ---------- Commands ----------
@tree.command(name="start", description="Run the setup wizard (Admin only)")
@app_commands.checks.has_permissions(administrator=True)
async def start(interaction: discord.Interaction):
    # Acknowledge so we can send multiple messages in channel
    await interaction.response.defer(thinking=False)
    await interaction.channel.send("⚙️ Setup started! Type `cancel` anytime to stop.")

    cfg = guild_cfg(interaction.guild.id)

    # 1) Bot Logs Channel
    msg = await ask_channel_question(
        interaction,
        "📜 What is the **Channel ID** for bot-logs?\nType an ID / mention, `none`, or `create`."
    )
    if msg is None: return

    log_channel = None
    if msg.content.lower() == "none":
        update_guild_cfg(interaction.guild.id, "bot_logs", None)
        log_channel = interaction.channel
    elif msg.content.lower() == "create":
        ch = await interaction.guild.create_text_channel("bot-logs")
        update_guild_cfg(interaction.guild.id, "bot_logs", ch.id)
        log_channel = ch
    else:
        ch_id = parse_channel_id(msg.content)
        ch = interaction.guild.get_channel(ch_id) if ch_id else None
        if ch:
            update_guild_cfg(interaction.guild.id, "bot_logs", ch.id)
            log_channel = ch
        else:
            await interaction.channel.send("⚠️ Channel not found. Defaulting to this channel.")
            update_guild_cfg(interaction.guild.id, "bot_logs", interaction.channel.id)
            log_channel = interaction.channel

    # 2) Verification Channel
    msg = await ask_channel_question(
        interaction,
        "✅ What is your **verification channel**?\nOptions: channel ID/mention, `create`, or `none`."
    )
    if msg is None: return

    verification_channel = None
    if msg.content.lower() == "none":
        update_guild_cfg(interaction.guild.id, "verification_channel", None)
    elif msg.content.lower() == "create":
        verification_channel = await interaction.guild.create_text_channel("verification")
        update_guild_cfg(interaction.guild.id, "verification_channel", verification_channel.id)
    else:
        ch_id = parse_channel_id(msg.content)
        ch = interaction.guild.get_channel(ch_id) if ch_id else None
        if ch:
            verification_channel = ch
            update_guild_cfg(interaction.guild.id, "verification_channel", ch.id)
        else:
            await interaction.channel.send("⚠️ Channel not found. Setting to None.")
            update_guild_cfg(interaction.guild.id, "verification_channel", None)

    # 3) Verification Role
    msg = await ask_channel_question(
        interaction,
        "🧾 Which **role** should be granted when users verify?\nOptions: role ID/mention, `create` (make 'Verified'), or `none`."
    )
    if msg is None: return

    verify_role_id = None
    if msg.content.lower() == "none":
        update_guild_cfg(interaction.guild.id, "verification_role_id", None)
    elif msg.content.lower() == "create":
        role = await interaction.guild.create_role(name="Verified", reason="Verification system setup")
        verify_role_id = role.id
        update_guild_cfg(interaction.guild.id, "verification_role_id", verify_role_id)
    else:
        rid = parse_role_id(msg.content)
        role = interaction.guild.get_role(rid) if rid else None
        if role:
            verify_role_id = role.id
            update_guild_cfg(interaction.guild.id, "verification_role_id", verify_role_id)
        else:
            await interaction.channel.send("⚠️ Role not found. Setting to None.")
            update_guild_cfg(interaction.guild.id, "verification_role_id", None)

    # 4) Ticket Recipient
    msg = await ask_channel_question(
        interaction,
        "📨 Who should the tickets (use `/ticket`) be sent to?\nOptions: `Server Owner` or a specific `User_ID`."
    )
    if msg is None: return

    if msg.content.lower() == "server owner":
        update_guild_cfg(interaction.guild.id, "ticket_recipient", interaction.guild.owner_id)
    else:
        uid = parse_user_id(msg.content)
        member = interaction.guild.get_member(uid) if uid else None
        if member:
            update_guild_cfg(interaction.guild.id, "ticket_recipient", member.id)
        else:
            await interaction.channel.send("⚠️ User not found. Defaulting to server owner.")
            update_guild_cfg(interaction.guild.id, "ticket_recipient", interaction.guild.owner_id)

    # 5) Archive Category
    msg = await ask_channel_question(
        interaction,
        "📦 What is the **Category ID** for archived channels?\nType an ID, `none`, or `create` to let the bot make one."
    )
    if msg is None: return

    if msg.content.lower() == "none":
        update_guild_cfg(interaction.guild.id, "archive_category", None)
    elif msg.content.lower() == "create":
        category = await interaction.guild.create_category("Archived Channels")
        update_guild_cfg(interaction.guild.id, "archive_category", category.id)
    else:
        try:
            cat_id = int(msg.content)
            category = interaction.guild.get_channel(cat_id)
            if isinstance(category, discord.CategoryChannel):
                update_guild_cfg(interaction.guild.id, "archive_category", category.id)
            else:
                await interaction.channel.send("⚠️ That ID doesn’t belong to a category. Setting to None.")
                update_guild_cfg(interaction.guild.id, "archive_category", None)
        except ValueError:
            await interaction.channel.send("⚠️ Invalid ID. Setting to None.")
            update_guild_cfg(interaction.guild.id, "archive_category", None)

    # Save once more to be safe
    cfg = guild_cfg(interaction.guild.id)

    # Post Setup Complete
    embed = discord.Embed(
        title="✅ Setup Complete",
        description=(
            f"**Bot Logs Channel:** {f'<#{cfg.get(\"bot_logs\")}>' if cfg.get('bot_logs') else 'None'}\n"
            f"**Verification Channel:** {f'<#{cfg.get(\"verification_channel\")}>' if cfg.get('verification_channel') else 'None'}\n"
            f"**Verification Role:** {f'<@&{cfg.get(\"verification_role_id\")}>' if cfg.get('verification_role_id') else 'None'}\n"
            f"**Ticket Recipient:** {f'<@{cfg.get(\"ticket_recipient\")}>' if cfg.get('ticket_recipient') else 'None'}\n"
            f"**Archive Category:** {cfg.get('archive_category') or 'None'}"
        ),
        color=discord.Color.green()
    )
    await log_channel.send(embed=embed)

    # If verification channel and role exist, post the verify message w/ reaction
    if cfg.get("verification_channel") and cfg.get("verification_role_id"):
        verify_channel = interaction.guild.get_channel(cfg["verification_channel"])
        if verify_channel:
            try:
                verify_msg = await verify_channel.send(
                    "👋 **Welcome!** Please react with ✅ if you agree to all of the above rules "
                    "to verify and gain access to the server."
                )
                await verify_msg.add_reaction("✅")
                update_guild_cfg(interaction.guild.id, "verification_message_id", verify_msg.id)
            except discord.Forbidden:
                await interaction.channel.send(
                    f"⚠️ I couldn't send a verification message in {verify_channel.mention} (missing permissions)."
                )

@tree.command(name="ticket", description="Post the ticket panel (Admin only)")
@app_commands.checks.has_permissions(administrator=True)
@require_setup(["ticket_recipient"])
async def ticket(interaction: discord.Interaction):
    cfg = guild_cfg(interaction.guild.id)
    recipient_id = cfg.get("ticket_recipient") or interaction.guild.owner_id
    recipient = interaction.guild.get_member(recipient_id) or interaction.guild.owner

    embed = discord.Embed(
        title="🎟 Ticket Support System",
        description=(
            "Need **help**, have **an issue**, or just a **suggestion**?\n\n"
            "Click the **Create Ticket** button below to send a message directly to the staff recipient.\n"
            "Please provide as much detail as possible."
        ),
        color=discord.Color.blurple()
    )
    embed.set_footer(text="You can submit one ticket every 10 minutes.")
    embed.timestamp = discord.utils.utcnow()

    await interaction.response.send_message(embed=embed, view=TicketButton(recipient), ephemeral=False)
    await log_to_channel(interaction.guild, embed=discord.Embed(
        title="📌 Ticket Panel Posted",
        description=f"By {interaction.user.mention} in {interaction.channel.mention}",
        color=discord.Color.blurple()
    ))

# ----- Role utilities -----
@tree.command(name="giverole", description="Give a role to a user (Admin only)")
@app_commands.describe(user="The user to give the role to", role="The role to give")
@app_commands.checks.has_permissions(administrator=True)
async def giverole(interaction: discord.Interaction, user: discord.Member, role: discord.Role):
    try:
        await user.add_roles(role, reason=f"giverole by {interaction.user}")
        await interaction.response.send_message(
            embed=discord.Embed(
                title="✅ Role Added",
                description=f"{role.mention} has been given to {user.mention}.",
                color=discord.Color.green()
            )
        )
        await log_to_channel(interaction.guild, embed=discord.Embed(
            title="🔧 Role Given",
            description=f"{role.mention} → {user.mention} (by {interaction.user.mention})",
            color=discord.Color.green()
        ))
    except discord.Forbidden:
        await interaction.response.send_message("⚠️ I do not have permission to give that role.", ephemeral=True)

@tree.command(name="removerole", description="Remove a role from a user (Admin only)")
@app_commands.describe(user="The user to remove the role from", role="The role to remove")
@app_commands.checks.has_permissions(administrator=True)
async def removerole(interaction: discord.Interaction, user: discord.Member, role: discord.Role):
    try:
        await user.remove_roles(role, reason=f"removerole by {interaction.user}")
        await interaction.response.send_message(
            embed=discord.Embed(
                title="🗑️ Role Removed",
                description=f"{role.mention} has been removed from {user.mention}.",
                color=discord.Color.red()
            )
        )
        await log_to_channel(interaction.guild, embed=discord.Embed(
            title="🧹 Role Removed",
            description=f"{role.mention} × {user.mention} (by {interaction.user.mention})",
            color=discord.Color.red()
        ))
    except discord.Forbidden:
        await interaction.response.send_message("⚠️ I do not have permission to remove that role.", ephemeral=True)

@tree.command(name="userroles", description="View all roles of a user")
@app_commands.describe(user="The user whose roles you want to view")
async def userroles(interaction: discord.Interaction, user: discord.Member):
    roles = [r for r in user.roles if r != interaction.guild.default_role]
    roles_str = ", ".join(r.mention for r in roles) if roles else "No roles"
    embed = discord.Embed(
        title=f"Roles for {user}",
        description=roles_str,
        color=discord.Color.blurple()
    )
    embed.set_footer(text=f"Total Roles: {len(roles)}")
    await interaction.response.send_message(embed=embed)
    await log_to_channel(interaction.guild, embed=discord.Embed(
        title="ℹ️ Viewed User Roles",
        description=f"{interaction.user.mention} viewed roles for {user.mention}",
        color=discord.Color.blurple()
    ))

@tree.command(name="viewroles", description="View all roles in the server")
async def viewroles(interaction: discord.Interaction):
    roles = [r for r in interaction.guild.roles if r != interaction.guild.default_role]
    roles = list(reversed(roles))  # highest first
    roles_str = ", ".join(r.mention for r in roles) if roles else "No roles found."
    embed = discord.Embed(
        title=f"Roles in {interaction.guild.name}",
        description=roles_str,
        color=discord.Color.blurple()
    )
    embed.set_footer(text=f"Total Roles: {len(roles)}")
    await interaction.response.send_message(embed=embed)

# ---------- Errors ----------
@giverole.error
@removerole.error
@ticket.error
async def admin_cmd_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ You must be an administrator to use this command.", ephemeral=True)

# ---------- Startup ----------
@bot.event
async def on_ready():
    # Sync application commands
    try:
        await tree.sync()
    except Exception as e:
        print("Command sync failed:", e)
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

# ---------- Run ----------
if __name__ == "__main__":
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise SystemExit("Please set BOT_TOKEN environment variable.")
    bot.run(token)
