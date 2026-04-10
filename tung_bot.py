import discord
from discord.ext import commands
from datetime import datetime
import pytz
import asyncio
import os

TOKEN = os.environ["TOKEN"]
CANAL_GERAL_NOME = os.environ.get("CANAL_GERAL_NOME", "geral")
IMAGEM_TUNG = os.environ["IMAGEM_TUNG"]

intents = discord.Intents.default()
intents.members = True
intents.moderation = True

bot = commands.Bot(command_prefix="!", intents=intents)


def horario_brasilia() -> str:
    tz = pytz.timezone("America/Sao_Paulo")
    agora = datetime.now(tz)
    return agora.strftime("%d/%m/%Y às %H:%M:%S")


def get_canal_geral(guild: discord.Guild) -> discord.TextChannel | None:
    return discord.utils.get(guild.text_channels, name=CANAL_GERAL_NOME)


async def enviar_mensagem_tung(canal: discord.TextChannel, usuario: discord.User, tipo: str):
    avatar_url = usuario.display_avatar.url

    embed = discord.Embed(
        title=f"**{usuario.name} is with Tung now.**",
        color=0xF0E6C8,  # dourado suave, combina com a imagem
    )
    embed.set_image(url=IMAGEM_TUNG)           # imagem principal (Tung)
    embed.set_thumbnail(url=avatar_url)        # foto de perfil do banido/expulso/saiu
    embed.add_field(name="👤 Usuário", value=usuario.name, inline=True)
    embed.add_field(name="📋 Evento", value=tipo, inline=True)
    embed.add_field(name="🕐 Horário (Brasília)", value=horario_brasilia(), inline=False)
    embed.set_footer(text="See you on the other side 🪽")

    await canal.send(embeds=[embed])


# ----- BANIMENTO -----
@bot.event
async def on_member_ban(guild: discord.Guild, user: discord.User):
    canal = get_canal_geral(guild)
    if not canal:
        return
    await enviar_mensagem_tung(canal, user, "🔨 Banido")


# ----- EXPULSÃO (kick) — detectada via audit log -----
@bot.event
async def on_member_remove(member: discord.Member):
    guild = member.guild
    canal = get_canal_geral(guild)
    if not canal:
        return

    # Aguarda o audit log registrar a ação
    await asyncio.sleep(1.5)

    tipo = "🚪 Saiu do servidor"  # padrão: saída voluntária

    # Verifica se foi um kick no audit log
    if guild.me.guild_permissions.view_audit_log:
        async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.kick):
            if entry.target.id == member.id:
                # Considera kick se aconteceu nos últimos 5 segundos
                diff = (datetime.now(pytz.utc) - entry.created_at).total_seconds()
                if diff < 5:
                    tipo = "👢 Expulso (Kick)"
                break

    # Se foi banimento, o evento on_member_ban já cuida — evita duplicata
    try:
        await guild.fetch_ban(member)
        return  # era ban, ignora aqui
    except discord.NotFound:
        pass

    await enviar_mensagem_tung(canal, member, tipo)


@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user} (ID: {bot.user.id})")
    print("🪽 Aguardando eventos do servidor...")


bot.run(TOKEN)
