import discord
from discord.ext import commands
from datetime import datetime
import pytz
import asyncio
import os
import random

TOKEN = os.environ["TOKEN"]
CANAL_GERAL_NOME = os.environ.get("CANAL_GERAL_NOME", "geral")
IMAGEM_TUNG = os.environ["IMAGEM_TUNG"]
IMAGEM_TUNG_DARK = "https://i.imgur.com/p4PNbgT.jpg"  # variação sinistra

intents = discord.Intents.default()
intents.members = True
intents.moderation = True
intents.message_content = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Guarda IDs de quem já baniu/expulsou alguém nesta sessão
executores_punicao: set[int] = set()


def horario_brasilia() -> str:
    tz = pytz.timezone("America/Sao_Paulo")
    agora = datetime.now(tz)
    return agora.strftime("%d/%m/%Y às %H:%M:%S")


def get_canal_geral(guild: discord.Guild) -> discord.TextChannel | None:
    return discord.utils.get(guild.text_channels, name=CANAL_GERAL_NOME)


async def enviar_mensagem_tung(canal: discord.TextChannel, usuario: discord.User, tipo: str):
    """Embed padrão — dourado, angelical."""
    avatar_url = usuario.display_avatar.url

    embed = discord.Embed(
        title=f"**{usuario.name} is with Tung now.**",
        color=0xF0E6C8,
    )
    embed.set_image(url=IMAGEM_TUNG)
    embed.set_thumbnail(url=avatar_url)
    embed.add_field(name="👤 Usuário", value=usuario.name, inline=True)
    embed.add_field(name="📋 Evento", value=tipo, inline=True)
    embed.add_field(name="🕐 Horário (Brasília)", value=horario_brasilia(), inline=False)
    embed.set_footer(text="See you on the other side 🪽")

    await canal.send(embeds=[embed])


async def enviar_mensagem_tung_dark(canal: discord.TextChannel, usuario: discord.User, tipo: str):
    """Embed sinistra — vermelha, para quem já puniu outros."""
    avatar_url = usuario.display_avatar.url

    embed = discord.Embed(
        title=f"**{usuario.name} iS wITh tUng nOW.**",
        color=0x8B0000,  # vermelho sangue
    )
    embed.set_image(url=IMAGEM_TUNG_DARK)
    embed.set_thumbnail(url=avatar_url)
    embed.add_field(name="😈 Usuário", value=usuario.name, inline=True)
    embed.add_field(name="🩸 Evento", value=tipo, inline=True)
    embed.add_field(
        name="🕯️ Horário (Brasília)",
        value=horario_brasilia(),
        inline=False,
    )
    embed.set_footer(text="We'll meet where the light doesn't reach. 🔥")

    await canal.send(embeds=[embed])


async def ja_puniu_alguem(guild: discord.Guild, user_id: int) -> bool:
    """Verifica no audit log se o usuário já baniu ou expulsou alguém."""
    if not guild.me.guild_permissions.view_audit_log:
        return user_id in executores_punicao

    acoes = [discord.AuditLogAction.ban, discord.AuditLogAction.kick]
    for acao in acoes:
        async for entry in guild.audit_logs(limit=100, action=acao):
            if entry.user and entry.user.id == user_id:
                return True

    return user_id in executores_punicao


async def processar_saida(guild: discord.Guild, usuario: discord.User, tipo: str):
    canal = get_canal_geral(guild)
    if not canal:
        return

    if await ja_puniu_alguem(guild, usuario.id):
        await enviar_mensagem_tung_dark(canal, usuario, tipo)
    else:
        await enviar_mensagem_tung(canal, usuario, tipo)


# ----- BANIMENTO -----
@bot.event
async def on_member_ban(guild: discord.Guild, user: discord.User):
    await asyncio.sleep(1.5)

    # Registra quem aplicou o ban
    if guild.me.guild_permissions.view_audit_log:
        async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.ban):
            if entry.target and entry.target.id == user.id:
                if entry.user:
                    executores_punicao.add(entry.user.id)
                break

    await processar_saida(guild, user, "🔨 Banido")


# ----- EXPULSÃO (kick) — detectada via audit log -----
@bot.event
async def on_member_remove(member: discord.Member):
    guild = member.guild

    await asyncio.sleep(1.5)

    tipo = "🚪 Saiu do servidor"

    if guild.me.guild_permissions.view_audit_log:
        async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.kick):
            if entry.target and entry.target.id == member.id:
                diff = (datetime.now(pytz.utc) - entry.created_at).total_seconds()
                if diff < 5:
                    tipo = "👢 Expulso (Kick)"
                    if entry.user:
                        executores_punicao.add(entry.user.id)
                break

    # Evita duplicata com on_member_ban
    try:
        await guild.fetch_ban(member)
        return
    except discord.NotFound:
        pass

    await processar_saida(guild, member, tipo)


# ----- MENÇÃO AO BOT -----
FRASES_TUNG = [
    "**Você me chamou… e agora eu vejo você também.**",
    "**Eu sempre estive aqui… você só começou a perceber agora.**",
    "**Você não me invocou… apenas abriu os olhos para mim.**",
    "**Entre a luz e o silêncio… eu esperei por você.**",
    "**Ele está com Tung agora!**",
]

@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return

    if bot.user in message.mentions:
        await message.channel.send(random.choice(FRASES_TUNG))

    await bot.process_commands(message)


@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user} (ID: {bot.user.id})")
    print("🪽 Aguardando eventos do servidor...")


bot.run(TOKEN)
