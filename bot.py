from discord.ext import tasks
from datetime import datetime
from zoneinfo import ZoneInfo
import discord
from discord.ext import commands
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
SHEET_NAME = os.getenv("SHEET_NAME")

LOG_ABSENCE_CHANNEL = "log-absences"
TWIG_ABSENCE_CHANNEL = "twig-absences"

# ---- Google Sheets setup ----
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

# creds = ServiceAccountCredentials.from_json_keyfile_name(
#     "credentials.json", scope
# )
import json

STATUS_MAP = {
    "attendance": "In Attendance",
    "late": "Will Be Late",
    "makeup": "Must Send Recording",
    "leavingearly": "Leaving Early",

    # officer-only statuses
    "excused": "Excused (Sent)",
    "latesent": "Will Send LATE",
    "neversent": "Never Sent Recording",

    # alias
    "absent": "Must Send Recording",
}

OFFICER_ONLY_STATUSES = {
    "excused",
    "latesent",
    "neversent",
}

# PRIVATE CHANNEL IDS
PRIVATE_CHANNELS = {
    "Cat": 1500892813007523860,
    "Alex": 1462123093156958320,
}

# DIRECTOR PREZ
AUTHORIZED_MAKEUP_USERS = {
    364035221458255873,  # AL
    643833470329552896,  # CT
}

USER_IDS = {
    "Cat": 643833470329552896,
    "Alex": 364035221458255873,
}

REHEARSAL_SCHEDULE = [
    {"weekday": 2, "hour": 19, "minute": 0},  # Wednesday 7:00 PM
    {"weekday": 4, "hour": 18, "minute": 0},  # Friday 6:00 PM
    {"weekday": 6, "hour": 17, "minute": 0},  # Sunday 5:00 PM
]

# creds_dict = json.loads(os.environ["GOOGLE_CREDS_JSON"])
# creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
creds = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json", scope
)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1

# ---- Discord setup ----
intents = discord.Intents.default()
intents.message_content = True


@bot.event
async def on_ready():

    print(f"Logged in as {bot.user}")

    bot.startup_time = datetime.now(
        ZoneInfo("America/New_York")
    )

    if not rehearsal_check_loop.is_running():
        rehearsal_check_loop.start()

LAST_REMINDER_DATE = None
LAST_REHEARSAL_SENT = set() # store (year, week, weekday, hour)

# TEST_REMINDER_SENT = False

def get_week_id(now):
    return now.isocalendar().week

@tasks.loop(seconds=30)
async def rehearsal_check_loop():

    now = datetime.now(ZoneInfo("America/New_York"))

    year = now.isocalendar().year
    week = now.isocalendar().week
    weekday = now.weekday()
    hour = now.hour
    minute = now.minute

    global LAST_REHEARSAL_SENT

    for rehearsal in REHEARSAL_SCHEDULE:

        if (
            weekday == rehearsal["weekday"]
            and hour == rehearsal["hour"]
            and minute >= rehearsal["minute"]
        ):

            key = (year, week, weekday, rehearsal["hour"], rehearsal["minute"])

            if key in LAST_REHEARSAL_SENT:
                continue

            LAST_REHEARSAL_SENT.add(key)

            print("REHEARSAL TRIGGER:", key)

            today = f"{now.month}/{now.day}"
            await send_makeup_reminders(today)


async def send_makeup_reminders(date):

    print(f"Checking reminders for date: {date}")

    headers = sheet.row_values(1)

    print("HEADERS:")
    print(headers)

    if date not in headers:
        print(f"❌ DATE '{date}' NOT FOUND IN HEADERS")
        return

    col = headers.index(date) + 1

    print(f"✅ USING COLUMN: {col}")

    names = sheet.col_values(1)
    attendance = sheet.col_values(col)

    print("\nNAMES:")
    print(names)

    print("\nATTENDANCE:")
    print(attendance)

    reminder_statuses = {
        "Must Send Recording",
        "Will Send LATE",
    }

    for i in range(1, len(names)):

        if i >= len(attendance):
            print(f"Skipping row {i}: no attendance value")
            continue

        student_name = names[i].strip()
        status = attendance[i].strip()

        print(
            f"\nChecking student: '{student_name}'"
        )

        print(
            f"Status found: '{status}'"
        )

        if status not in reminder_statuses:
            print("❌ Status mismatch")
            continue

        if student_name not in PRIVATE_CHANNELS:
            print(
                f"❌ No private channel mapping for '{student_name}'"
            )
            continue

        channel_id = PRIVATE_CHANNELS[student_name]

        print(f"✅ CHANNEL ID: {channel_id}")

        try:

            channel = await bot.fetch_channel(channel_id)

            print(
                f"✅ CHANNEL FOUND: {channel.name}"
            )

        except Exception as e:

            print(
                f"❌ CHANNEL FETCH ERROR: {e}"
            )

            continue

        try:

            user_id = USER_IDS.get(student_name)

            mention = ""

            if user_id:
                member = await bot.fetch_user(user_id)
                mention = member.mention

            await channel.send(
                f"{mention} ❗\n\n"
                f"You currently have status:\n"
                f"**{status}** for rehearsal **{date}**.\n\n"
                f"Please submit attendance credit within "
                f"**3 days**."
            )

            print(
                f"✅ SUCCESSFULLY SENT TO {student_name}"
            )

        except Exception as e:

            print(
                f"❌ SEND ERROR: {e}"
            )

@bot.command(name="testreminders")
async def testreminders(ctx):

    today = f"{datetime.now().month}/{datetime.now().day}"

    print("MANUAL TEST COMMAND TRIGGERED")

    await send_makeup_reminders(today)

    await ctx.reply("Ran reminder test.")


@bot.command(name="madeup")
async def madeup(ctx, first_name=None, date=None):

    if ctx.author.id not in AUTHORIZED_MAKEUP_USERS:
        await ctx.reply(
            "❌ You are not authorized to use this command."
        )
        return

    if not all([first_name, date]):
        await ctx.reply(
            "❌ Usage:\n"
            "`!madeup name date`"
        )
        return

    name = first_name.capitalize()

    headers = sheet.row_values(1)

    if date not in headers:
        await ctx.reply(f"❌ Date `{date}` not found.")
        return

    col = headers.index(date) + 1

    names = sheet.col_values(1)

    try:
        row = names.index(name) + 1
    except ValueError:
        await ctx.reply(f"❌ Could not find `{name}`.")
        return

    current_status = sheet.cell(row, col).value

    valid_makeup_statuses = {
        "Must Send Recording",
        "Will Send LATE",
    }

    if current_status not in valid_makeup_statuses:
        await ctx.reply(
            f"❌ `{name}` does not currently "
            f"need makeup credit."
        )
        return

    sheet.update_cell(
        row,
        col,
        "Excused (Sent)"
    )

    await ctx.message.add_reaction("✅")

    await ctx.reply(
        f"Marked **{name}** as "
        f"**Excused (Sent)** for **{date}**."
    )


@bot.command(name="attendance")
async def attendance(
    ctx,
    first_name: str = None,
    status: str = None,
    date: str = None,
    *,
    reason: str = None,
):

    if not all([first_name, status, date]):
        await ctx.reply(
            "❌ Format:\n"
            "`!attendance name status date reason`"
        )
        return

    status_key = status.lower()

    if status_key not in STATUS_MAP:
        await ctx.reply(
            "❌ Invalid status.\n\n"
            "Options:\n"
            f"{', '.join(STATUS_MAP.keys())}"
        )
        return

    # -------------------------
    # OFFICER PERMISSION CHECK
    # -------------------------

    if (
        status_key in OFFICER_ONLY_STATUSES
        and ctx.author.id not in AUTHORIZED_MAKEUP_USERS
    ):
        await ctx.reply(
            "❌ Only authorized attendance managers "
            "can use that status."
        )
        return

    sheet_value = STATUS_MAP[status_key]

    name = first_name.capitalize()

    # -------------------------
    # FIND STUDENT ROW
    # -------------------------

    try:
        names = sheet.col_values(1)
        row = names.index(name) + 1

    except ValueError:
        await ctx.reply(
            f"❌ Could not find `{name}`."
        )
        return

    # -------------------------
    # FIND DATE COLUMN
    # -------------------------

    headers = sheet.row_values(1)

    if date not in headers:
        await ctx.reply(
            f"❌ Date `{date}` not found."
        )
        return

    col = headers.index(date) + 1

    # -------------------------
    # UPDATE SHEET
    # -------------------------

    sheet.update_cell(row, col, sheet_value)

    await ctx.message.add_reaction("✅")

    response = (
        f"Marked **{name}** as "
        f"**{sheet_value}** on **{date}**."
    )

    if reason:
        response += f"\nReason: {reason}"

    # -------------------------
    # AUTO REMINDER NOTE
    # -------------------------

    if sheet_value in {
        "Must Send Recording",
        "Will Send LATE",
    }:
        response += (
            "\n\n❗ Makeup recording required "
            "within **3 days**."
        )

    await ctx.reply(response)


@bot.command(name="clearattendance")
async def clearattendance(ctx, first_name=None, date=None):

    if not all([first_name, date]):
        await ctx.reply(
            "❌ Usage:\n"
            "`!clearattendance name date`"
        )
        return

    name = first_name.capitalize()

    try:
        names = sheet.col_values(1)
        row = names.index(name) + 1
    except ValueError:
        await ctx.reply(f"❌ Could not find `{name}`.")
        return

    headers = sheet.row_values(1)

    if date not in headers:
        await ctx.reply(f"❌ Date `{date}` not found.")
        return

    col = headers.index(date) + 1

    sheet.update_cell(row, col, "")

    await ctx.message.add_reaction("✅")

    await ctx.reply(
        f"Cleared attendance for **{name}** on **{date}**."
    )


from flask import Flask
from threading import Thread
import os

app = Flask("")


@app.route("/")
def home():
    return "Bot is running!"


def run():
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)


Thread(target=run).start()

bot.run(DISCORD_TOKEN)
