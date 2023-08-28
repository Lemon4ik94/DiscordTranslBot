from cfg import *
import discord
from database import Database
from discord import Webhook
from discord import app_commands
from discord.ext import commands
from deep_translator import GoogleTranslator

intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix='>', intents=intents)
db = Database("webhook.db")


@bot.event
async def on_webhooks_update(channel):
    dbwebhooks = db.get_webhooks(channel.id)
    webhooks = await channel.webhooks()
    for dbwebhook in dbwebhooks:
        if dbwebhook in webhooks:
            pass
        else:
            db.delete_webhook(dbwebhook)


@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)


@bot.tree.command(name='test')
async def test(interaction):
    await interaction.response.send_message(interaction.channel, ephemeral=True)


@bot.tree.command(name='create-webhook', description='Creates webhook for translation')
@app_commands.describe(fromchannel='From Channel')
@app_commands.choices(tolanguage=[
    app_commands.Choice(name="English", value="en"),
    app_commands.Choice(name="Ukrainian", value="uk"),
    app_commands.Choice(name="Russian", value="ru")
])
async def create(interaction, fromchannel: discord.TextChannel, tolanguage: app_commands.Choice[str]):
    await interaction.response.send_message(f"from <#{fromchannel.id}> to <#{interaction.channel.id}> to {tolanguage.name}", ephemeral=True)
    webhook = await interaction.channel.create_webhook(name=f"TranslateTo{tolanguage.name}")
    db.create_webhook(interaction.channel.id, fromchannel.id, webhook.id, webhook.url, tolanguage.value)


@bot.tree.context_menu(name="Translate to English")
async def translate(interaction, message: discord.Message):
    content = message.content
    username = message.author.display_name

    translated_content = GoogleTranslator(source='auto', target='en').translate(content)
    await interaction.response.send_message(f"{username} said:\n{translated_content}", ephemeral=True)


@bot.tree.context_menu(name="Перекласти на Українську")
async def translate_toua(interaction, message: discord.Message):
    content = message.content
    username = message.author.display_name

    translated_content = GoogleTranslator(source='auto', target='uk').translate(content)
    await interaction.response.send_message(f"{username} said:\n{translated_content}", ephemeral=True)


@bot.tree.context_menu(name="Перевести на Русский")
async def translate_toru(interaction, message: discord.Message):
    content = message.content
    username = message.author.display_name

    translated_content = GoogleTranslator(source='auto', target='ru').translate(content)
    await interaction.response.send_message(f"{username} said:\n{translated_content}", ephemeral=True)


@bot.event
async def on_message(message):
    msg = ''
    if message.author == bot.user or message.author.bot:
        return

    content = message.content
    username = message.author.display_name
    avatar_url = message.author.display_avatar

    if db.get_webhookurl(message.channel.id) is not None:
        webhook_url = db.get_webhookurl(message.channel.id)
        translated_content = GoogleTranslator(source='auto', target=webhook_url[1]).translate(content)
    else:
        return

    if message.attachments:
        msg = message.attachments[0].url

    webhook = Webhook.from_url(webhook_url[0], client=bot)
    await webhook.send(f"{str(translated_content)}\n{msg}", username=username, avatar_url=avatar_url)


bot.run(token)
