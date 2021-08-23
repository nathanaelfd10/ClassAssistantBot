from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord.ext import commands
import discord
import os
from dotenv import load_dotenv
import random
import requests
import json
import schedule
import time
import asyncio
from datetime import datetime, timedelta
import calendar
from ClassAssistant import ClassAssistantBot

load_dotenv('DISCORD_TOKEN.env')
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
client = discord.Client()
bot = commands.Bot(command_prefix="!class ")
IFBot = ClassAssistantBot()

def get_words():
    repsonse = requests.get("http://zenquotes.io/api/random")
    json_data = json.loads(repsonse.text)
    quote = json_data[0]['q'] + " -" + json_data[0]['a']
    return(quote)

scheduler = AsyncIOScheduler()

@bot.command()
async def today(ctx):
    matkul_info_message = IFBot.matkul_data_to_message(IFBot.get_matkul_schedule())
    c = bot.get_channel(878348575648665661)
    await c.send(matkul_info_message)

async def send_embed(kode_matkul, nama, hour_begin, hour_end, title_desc, desc, link):
    try:
        embed=discord.Embed(title="{kode_matkul} {nama} | {hour_begin} - {hour_end}. {title_desc}.".format(
            kode_matkul = kode_matkul,
            nama = nama, 
            hour_begin = hour_begin,
            hour_end = hour_end,
            title_desc = title_desc
        ), url="{link}".format(link = link), description="{desc}".format(nama = nama, desc = desc), color=0x00ff62)
        embed.set_author(name="ClassAssistantBot", url="https://github.com/noxfl/ClassAssistantBot/", icon_url="https://avatars.githubusercontent.com/u/64892153?v=4")
        c = bot.get_channel(878348575648665661)
        await c.send(embed=embed)
        print('Embed sent: {nama}'.format(nama=nama))
    except: 
        print('Embed delivery failed')
   

def modify_thirty_minutes(hour, mode):
    if mode.lower() == 'substract':
        time_parsed = datetime.strptime(hour, '%H:%M') - timedelta(hours=0, minutes=30)
        # print('TIME SUBSTRACTED: {}'.format(time_parsed))
    elif mode.lower() == 'add':
        time_parsed = datetime.strptime(hour, '%H:%M') + timedelta(hours=0, minutes=30)
        # print('TIME ADDED: {}'.format(time_parsed))
    else:
        print('{function_name}: Invalid mode value has been entered'.format(function_name = modify_thirty_minutes.__name__))
        return hour
    time_converted = datetime.strftime(time_parsed, "%H:%M")
    return time_converted

async def populate_matkul_reminder():
    matkul_schedule_list = IFBot.get_matkul_json()
    matkul_set_count = 0
    tap_in_message = "Tap in here"
    tap_out_message = "Tap out here"
    for num, matkul in enumerate(matkul_schedule_list['jadwal_mobile']):
        matkul_set_count += 1
        print('Adding {nama} to schedule..'.format(nama=matkul['nama']))
        matkul_start_reminder_message = "{} is about to start soon.\nMake sure to check attendance in by clicking the link above!\nGet ready for today's class, best of luck!".format(matkul['nama'])
        # matkul_start_reminder_message = "{} is about to start soon.\nMake sure to check attendance in by clicking the link above!\nGet ready for today's class, best of luck!"
        matkul_end_reminder_message = "{} has now ended. Don't forget to check your attendance out!".format(matkul['nama'])
        time_before_class = modify_thirty_minutes(matkul['hour_begin'], 'substract').split(":")
        time_after_class = modify_thirty_minutes(matkul['hour_end'], 'add').split(":")
        day = matkul['day'][0:3]
        print("Time before class: {a} + {b}".format(a=time_before_class[0], b=time_before_class[1]))
        print("Time after class: {a} + {b}".format(a=time_after_class[0], b=time_after_class[1]))
        scheduler.add_job(send_embed, CronTrigger(day_of_week=day.lower(), hour=time_before_class[0], minute=time_before_class[1]), args=[matkul['kode_matkul'], matkul['nama'], matkul['hour_begin'], matkul['hour_end'], tap_in_message, matkul_start_reminder_message, 'http://leaps.kalbis.ac.id/'])
        # scheduler.add_job(send_embed, CronTrigger(day_of_week='mon', second="5, 15, 25, 35, 45, 55"), args=[matkul_end_reminder_message])
        scheduler.add_job(send_embed, CronTrigger(day_of_week=day.lower(), hour=time_after_class[0], minute=time_after_class[1]), args=[matkul['kode_matkul'], matkul['nama'], matkul['hour_begin'], matkul['hour_end'], tap_out_message, matkul_end_reminder_message, 'http://leaps.kalbis.ac.id/'])
        # scheduler.add_job(send_matkul_reminder, CronTrigger(day_of_week='mon', second="0, 10, 20, 30, 40, 50"), args=[matkul_start_reminder_message])
        # scheduler.add_job(send_matkul_reminder, CronTrigger(day_of_week='mon', second="5, 15, 25, 35, 45, 55"), args=[matkul_end_reminder_message])
    print('Matkul set count:', matkul_set_count)
    for job in scheduler.get_jobs():
        print(job.name, job.trigger, job.func)



async def send_matkul_reminder(matkul):
    try:
        c = bot.get_channel(878348575648665661)
        await c.send(matkul)
        print('Message sent: {}'.format(matkul))
    except:
        print('Message delivery failed')

#testing
async def func():
    c = client.get_channel(878348575648665661)
    await c.send('from func()')

@bot.command()
async def ping(ctx):
	await ctx.channel.send("pong")

@bot.command()
async def here(ctx, given_name):
    channel = discord.utils.get(ctx.guild.channels, name=given_name)
    channel_id = channel.id
    await ctx.channel.send("I will start sending messages here from now on!")

@bot.event
async def on_ready():
    print('Successfully logged in as {0.user}'.format(bot))
    print("Ready..")
    await populate_matkul_reminder()
    await send_matkul_reminder('Raiden Shogun pulang 2.1')
    scheduler.start()


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content

    if msg.startswith('$hello'):
        quote = get_words()
        await message.channel.send(quote)

    if msg.startswith('!absen'):
        matkul_today = IFBot.matkul_data_to_message(IFBot.get_matkul_schedule())
        await message.channel.send(matkul_today)

    if msg.startswith('!class'):
        await message.channel.send('Coming soon!')

    if any(word in msg for word in trigger_word):
        await message.channel.send(random.choice(response_words))

trigger_word = ["!ifbot", "kalbiser!"]

response_words = [
    "Cheer up!",
    "Yo!"
]

bot.run(DISCORD_TOKEN)

