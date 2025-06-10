# WeCantTalk.py
# Make sure to install required packages in your virtual environment:
# pip install discord.py requests python-dotenv

import os
import discord
from discord.ext import commands
import requests
from dotenv import load_dotenv
import threading
import asyncio

load_dotenv()

# Load environment variables
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
KOKORO_API_URL = os.getenv('KOKORO_API_URL')
DEFAULT_VOICE_ID = os.getenv('VOICE_ID')
MODEL_ID = os.getenv('MODEL_ID')

# Runtime-configurable language code
current_lang_code = None

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot connected as {bot.user}')

def sanitize_mentions(ctx, text):
    for user in ctx.message.mentions:
        text = text.replace(f'<@{user.id}>', user.display_name)
        text = text.replace(f'<@!{user.id}>', user.display_name)
    return text

def make_payload(model, voice, message):
    return {
        "model": model,
        "input": message,
        "voice": voice,
        "response_format": "mp3",
        "download_format": "mp3",
        "speed": 1,
        "stream": False,
        "return_download_link": False,
        "lang_code": current_lang_code,
        "normalization_options": {
            "normalize": True,
            "unit_normalization": False,
            "url_normalization": True,
            "email_normalization": True,
            "optional_pluralization_normalization": True,
            "phone_normalization": True
        }
    }

async def handle_speech(ctx, model, voice, message):
    if ctx.author.voice is None:
        await ctx.send("You must be in a voice channel to use this command.")
        return

    voice_channel = ctx.author.voice.channel
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not voice_client or not voice_client.is_connected():
        voice_client = await voice_channel.connect()
    elif voice_client.channel != voice_channel:
        await voice_client.move_to(voice_channel)

    message = sanitize_mentions(ctx, message)

    try:
        payload = make_payload(model, voice, message)
        headers = {'Accept': 'audio/mpeg'}
        response = requests.post(KOKORO_API_URL, json=payload, headers=headers, timeout=10)
        print("Status:", response.status_code)
        print("Content-Type:", response.headers.get("Content-Type"))
        print("Content Length:", len(response.content))

        if response.status_code != 200 or not response.content or "audio" not in response.headers.get("Content-Type", ""):
            await ctx.send(f"Failed to get TTS audio. Status: {response.status_code}")
            return

        audio_filename = f"tts_output_{ctx.message.id}.mp3"
        with open(audio_filename, "wb") as f:
            f.write(response.content)

        source = discord.FFmpegPCMAudio(audio_filename)
        voice_client.play(source)

        lang_note = f" (lang: `{current_lang_code}`)" if current_lang_code else ""
        await ctx.send(f"Playing your message with voice `{voice}`{lang_note}!")

    except Exception as e:
        print("Unexpected error:", e)
        await ctx.send("An unexpected error occurred.")

@bot.command()
async def speak(ctx, *, message: str):
    await handle_speech(ctx, MODEL_ID, DEFAULT_VOICE_ID, message)

@bot.command()
async def speakwith(ctx, voice: str, *, message: str):
    await handle_speech(ctx, MODEL_ID, voice, message)

@bot.command()
async def listvoices(ctx):
    try:
        response = requests.get(KOKORO_API_URL.replace("/v1/audio/speech", "/v1/audio/voices"), timeout=10)
        if response.status_code == 200:
            voices = response.json().get("voices", [])
            voice_list = ", ".join(voices)
            await ctx.send(f"Available voices: {voice_list}")
        else:
            await ctx.send(f"Failed to fetch voice list. Status: {response.status_code}")
    except Exception as e:
        print("Error fetching voice list:", e)
        await ctx.send("Could not retrieve voice list.")

@bot.command()
async def setlang(ctx, lang: str):
    global current_lang_code
    if lang.lower() in ["none", "reset", "clear"]:
        current_lang_code = None
        await ctx.send("Language setting cleared. Now using default language behavior.")
    else:
        current_lang_code = lang
        await ctx.send(f"Language code set to `{lang}`.")

@bot.command()
async def stop(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await ctx.send("Playback stopped.")
    else:
        await ctx.send("Nothing is playing right now.")

@bot.command()
async def raid(ctx, channel_id: int, *, message: str):
    channel = discord.utils.get(ctx.guild.voice_channels, id=channel_id)
    if not channel:
        await ctx.send("Voice channel not found.")
        return
    try:
        voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if not voice_client or not voice_client.is_connected():
            voice_client = await channel.connect()
        else:
            await voice_client.move_to(channel)

        payload = make_payload(MODEL_ID, DEFAULT_VOICE_ID, message)
        headers = {'Accept': 'audio/mpeg'}
        response = requests.post(KOKORO_API_URL, json=payload, headers=headers, timeout=10)

        if response.status_code != 200 or not response.content or "audio" not in response.headers.get("Content-Type", ""):
            await ctx.send(f"Failed to get TTS audio. Status: {response.status_code}")
            return

        audio_filename = f"tts_raid_{ctx.message.id}.mp3"
        with open(audio_filename, "wb") as f:
            f.write(response.content)

        source = discord.FFmpegPCMAudio(audio_filename)
        voice_client.play(source)
        lang_note = f" (lang: `{current_lang_code}`)" if current_lang_code else ""
        await ctx.send(f"Raided <#{channel_id}> with: `{message}`{lang_note}")
    except Exception as e:
        print("Raid error:", e)
        await ctx.send("Something went wrong during the raid.")

@bot.command(name="WeCantTalk")
async def wecanttalk(ctx):
    commands_info = [
        "**!speak [message]** – Speak a message using the default voice.",
        "**!speakwith [voice] [message]** – Use a specific voice to speak.",
        "**!listvoices** – Show available voices from the API.",
        "**!stop** – Stop the current playback in voice chat.",
        "**!raid [channel_id] [message]** – Speak a message in a specific voice channel by ID.",
        "**!setlang [lang_code|none]** – Set or reset the language for speech generation."
    ]
    help_text = "\n".join(commands_info)
    current_lang = f"Current language: `{current_lang_code}`" if current_lang_code else "Language: Default"
    await ctx.send(f"**WeCantTalk Bot Commands:**\n{help_text}\n\n{current_lang}")

# Console interaction support (Windows-friendly)
def console_input_loop():
    def _run():
        while True:
            try:
                raw = input("Console> ").strip()
                if not raw:
                    continue
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                if raw.startswith("speakwith"):
                    _, voice, *msg = raw.split()
                    message = " ".join(msg)
                    loop.run_until_complete(console_speak(voice, message))
                else:
                    loop.run_until_complete(console_speak(DEFAULT_VOICE_ID, raw))
            except Exception as e:
                print("Console input error:", e)
    threading.Thread(target=_run, daemon=True).start()

async def console_speak(voice, message):
    for vc in bot.voice_clients:
        if vc.is_connected():
            try:
                print(f"Console speaking: '{message}' with voice '{voice}' lang='{current_lang_code}'")
                payload = make_payload(MODEL_ID, voice, message)
                headers = {'Accept': 'audio/mpeg'}
                response = requests.post(KOKORO_API_URL, json=payload, headers=headers, timeout=10)
                print("Status:", response.status_code)
                print("Content-Type:", response.headers.get("Content-Type"))
                print("Content Length:", len(response.content))

                if response.status_code != 200 or not response.content or "audio" not in response.headers.get("Content-Type", ""):
                    print("Failed to get TTS audio.")
                    return

                audio_filename = f"tts_console.mp3"
                with open(audio_filename, "wb") as f:
                    f.write(response.content)

                if not vc.is_playing():
                    vc.play(discord.FFmpegPCMAudio(audio_filename))
                else:
                    print("Voice channel is already playing audio.")
            except Exception as e:
                print("Error in console speak:", e)
            return
    print("No active voice connection. Join a channel first.")

console_input_loop()

bot.run(DISCORD_TOKEN)
