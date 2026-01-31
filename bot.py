import discord
from discord.ext import commands
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
SHEET_NAME = os.getenv("SHEET_NAME")

ABSENCE_CHANNEL = "absences"

# ---- Google Sheets setup ----
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

# creds = ServiceAccountCredentials.from_json_keyfile_name(
#     "credentials.json", scope
# )
import json

creds_dict = json.loads(os.environ["GOOGLE_CREDS_JSON"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(
    creds_dict, scope
)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1

# ---- Discord setup ----
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.channel.name != ABSENCE_CHANNEL:
        return

    content = message.content.strip().split()

    # Expected:
    # !absence first_name absent 2/4 sick
    if len(content) < 5 or content[0] not in {"!attendance"}:
        await message.reply(
            "❌ Format: `!attendance first_name absent/late date reason`"
        )
        return

    STATUS_MAP = {
        "late": "Will Be Late",
        "absent": "Must Send Recording",
    }
    
    _, first_name, status, date, *reason = content
    reason = " ".join(reason)

    status_key = status.lower()

    if status_key not in STATUS_MAP:
        await message.channel.send(
            "❌ Status must be `late` or `absent`."
        )
        return

    sheet_value = STATUS_MAP[status_key] # Absent / Late
    name = first_name.capitalize()

    # ---- Find student row ----
    try:
        names = sheet.col_values(1)
        row = names.index(name) + 1
    except ValueError:
        await message.reply(
            f"❌ Could not find `{name}` in the sheet."
        )
        return

    # ---- Find date column ----
    headers = sheet.row_values(1)
    if date not in headers:
        await message.reply(
            f"❌ Date `{date}` not found in sheet."
        )
        return

    col = headers.index(date) + 1

    # ---- Update sheet ----
    sheet.update_cell(row, col, sheet_value)

    await message.add_reaction("✅")

    response = (
        f"Marked **{name}** as **{sheet_value}** on **{date}**.\n"
        f"Reason: {reason}"
    )

    # Extra reminder for absences
    if status_key == "absent":
        response += (
            "\n\n❗ **Please make sure to send your recordings "
            "to make up this absence.**"
        )

    await message.reply(response)


bot.run(DISCORD_TOKEN)
