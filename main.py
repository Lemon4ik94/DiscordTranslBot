from cfg import *
import discord
from database import Database
from discord import Webhook
from discord import app_commands
from discord.ext import commands
from deep_translator import GoogleTranslator

intents = discord.Intents.default()
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
@app_commands.describe(channelfrom='Channel from')
async def create(interaction, channelfrom: discord.TextChannel):
    await interaction.response.send_message(f"from {channelfrom} to {interaction.channel}", ephemeral=True)
    webhook = await interaction.channel.create_webhook(name="Translate")
    db.create_webhook(interaction.channel.id, channelfrom.id, webhook.id, webhook.url)\



@bot.event
async def on_message(message):
    msg = ''
    if message.author == bot.user or message.author.bot:
        return

    content = message.content
    username = message.author.display_name
    avatar_url = message.author.display_avatar

    if db.get_webhookurl(message.channel.id) is not None:
        translated_content = GoogleTranslator(source='auto', target='en').translate(content)
        webhook_url = db.get_webhookurl(message.channel.id)[0]
    else:
        return

    if message.attachments:
        msg = message.attachments[0].url

    webhook = Webhook.from_url(webhook_url, client=bot)
    await webhook.send(f"{str(translated_content)}\n{msg}", username=username, avatar_url=avatar_url)


bot.run(token)
