import os
import discord
from discord.ext import commands
import json
import pandas as pd

# Google sheet länk
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS1RCP3YasIrjwxp8oGOVruwDQxSS_fKL3hImTeQTZNTUYnb0bK6VKS23lOhCs5cfU82kMlMDJw3SGQ/pub?output=csv"  # Replace this with your public Google Sheet CSV link

# STARTA
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# LADDA SHEETET
def load_google_sheet():
    try:
        # Skip the first row (day names) and use the second row as headers
        sheet = pd.read_csv(CSV_URL, header=1, dtype=str)
        sheet.columns = sheet.columns.str.strip()  # Clean column names
        return sheet
    except Exception as e:
        print(f"Error fetching Google Sheet: {e}")
        return None

# LADDA FUNktion
def load_google_sheet():
    try:
        # Skip the first row (day names) and use the second row as headers
        sheet = pd.read_csv(CSV_URL, header=1, dtype=str)
        sheet.columns = sheet.columns.str.strip()  # Clean column names
        return sheet
    except Exception as e:
        print(f"Error fetching Google Sheet: {e}")
        return None


# Bot commando kalsong
@bot.command(name="check")
async def check_availability(ctx, date: str):
    """
    Check availability of players by class for a specific date.
    Usage: !check 22/12/2024
    """
    sheet = load_google_sheet()
    if sheet is None:
        await ctx.send("Error: Could not fetch the Google Sheet. Please try again later.")
        return

    # om inte error dåligt
    if date not in sheet.columns:
        await ctx.send(f"Error: Date '{date}' is not in the Google Sheet.")
        return

    # Filtrera players
    available_players = sheet[sheet[date].str.lower() == "yes"]

    tentative_players = sheet[sheet[date].str.lower() == "tentative"]

    if available_players.empty and tentative_players.empty:
        await ctx.send(f"No players are available or tentative on {date}.")
        return

    # Räkna 
    total_players = len(available_players)

    # Gruppera
    grouped = available_players.groupby("Class")["Raider"].apply(list)

    grouped_tentative = tentative_players.groupby("Class")["Raider"].apply(list)

    # Formatera 
    response = f"**Total Players Available On {date}: {total_players} Raiders**\n\n"

    for player_class, players in grouped.items():
        response += f"**{player_class}** ({len(players)} player(s)):\n"
        for player in players:
            response += f"- {player}\n"
        response += "\n"
    
    # Tentative
    if not tentative_players.empty:
        response += f"**Tentative Players On {date}: {len(tentative_players)} Raiders**\n\n"
        for player_class, players in grouped_tentative.items():
            response += f"**{player_class}** ({len(players)} player(s)):\n"
            for player in players:
                response += f"- {player}\n"
            response += "\n"

    # Formatterad repsones eee
    await ctx.send(response)

    # TXT FIL COOl
    file_path = f"availability_{date.replace('/', '-')}.txt"
    with open(file_path, "w") as file:
        file.write(response)

    
    with open(file_path, "rb") as file:
        await ctx.send(file=discord.File(file, filename=os.path.basename(file_path)))

    # Rensa för jag vill inte ha 100000 filer tack
    os.remove(file_path)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")

# KÖR
bot.run(TOKEN)


