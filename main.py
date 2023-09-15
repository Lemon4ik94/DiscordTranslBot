from cfg import *
import re
import discord
from database import Database
from discord import Webhook
from discord import app_commands
from discord.ext import commands
import deepl

translator = deepl.Translator(auth_key)
intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix='>', intents=intents)
db = Database("webhook.db")


@bot.event
async def on_webhooks_update(channel):
    dbwebhooks = db.get_webhooks(channel.id)
    webhooks = await channel.webhooks()

    for dbwebhook in dbwebhooks:
        if dbwebhook in [e.id for e in webhooks]:
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


@bot.tree.command(name='create-webhook', description='Creates webhook for translation')
@app_commands.describe(fromchannel='From Channel')
@app_commands.choices(tolanguage=[
    app_commands.Choice(name="English", value="EN-US"),
    app_commands.Choice(name="Ukrainian", value="UK"),
    app_commands.Choice(name="Russian", value="RU")
])
async def create(interaction, fromchannel: discord.TextChannel, tolanguage: app_commands.Choice[str]):
    await interaction.response.send_message(f"from <#{fromchannel.id}> to <#{interaction.channel.id}> to {tolanguage.name}", ephemeral=True)
    webhook = await interaction.channel.create_webhook(name=f"TranslateTo{tolanguage.name}")
    db.create_webhook(webhook.id, interaction.channel.id, fromchannel.id, webhook.url, tolanguage.value)


@bot.tree.context_menu(name="Translate to English")
async def translate(interaction, message: discord.Message):
    content = message.content
    username = message.author.display_name

    translated_content = translator.translate_text(content, target_lang="EN-US")
    await interaction.response.send_message(f"{username} said:\n{translated_content}", ephemeral=True)


@bot.tree.context_menu(name="Перекласти на Українську")
async def translate_toua(interaction, message: discord.Message):
    content = message.content
    username = message.author.display_name

    translated_content = translator.translate_text(content, target_lang="UK")
    await interaction.response.send_message(f"{username} said:\n{translated_content}", ephemeral=True)


@bot.tree.context_menu(name="Перевести на Русский")
async def translate_toru(interaction, message: discord.Message):
    content = message.content
    username = message.author.display_name

    translated_content = translator.translate_text(content, target_lang="RU")
    await interaction.response.send_message(f"{username} said:\n{translated_content}", ephemeral=True)


def user_ping(word):
    if "<@" in word:
        word = re.split(r"<@([\d_ ]+)>", word)
        word[1] = f"@{bot.get_user(int(word[1])).global_name}"

        return " ".join(word)
    else:
        return word


@bot.event
async def on_message(message):
    picurl = ''
    if message.author == bot.user or message.author.bot:
        return

    content = message.content
    username = message.author.display_name
    avatar_url = message.author.display_avatar

    content = " ".join(list(map(user_ping, content.split(" "))))

    if db.get_webhookurl(message.channel.id) is not None:
        webhook_url = db.get_webhookurl(message.channel.id)
    else:
        return

    for element in webhook_url:

        if content:
            translated_content = translator.translate_text(str(content), target_lang=element[1])
        else:
            translated_content = ""

        if translated_content is not None:
            content = translated_content

        if message.attachments:
            for pic in message.attachments:
                if pic.is_spoiler():
                    picurl += f"||{pic.url}||\n"
                else:
                    picurl += pic.url + "\n"

        webhook = Webhook.from_url(element[0], client=bot)
        try:
            await webhook.send(f"{content}\n\n{picurl}", username=username, avatar_url=avatar_url)
        except discord.errors.NotFound:
            print(f"Webhook {webhook.id} was not found on the server. Deleting it from db...")
            db.delete_webhook(webhook.id)


bot.run(token)
