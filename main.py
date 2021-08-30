from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord.ext import commands
import discord
import os
from dotenv import load_dotenv
import random
import requests
import json
from datetime import datetime, timedelta
import pytz
from ClassAssistant import ClassAssistantBot

#INITIALIZE DISCORD BOT
load_dotenv('.env')
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
client = discord.Client()
bot = commands.Bot(command_prefix="!")
CHANNEL_ID = 879663995852849193 #DEV Server

#INITIALIZE THE ACTUAL PROGRAM
IFBot = ClassAssistantBot()

#INITIALIZE DATE TIME
now = datetime.now()
tz = pytz.timezone('Asia/Jakarta')
tz_jkt = now.replace(tzinfo=tz)
day_list = {'Minggu':'Sunday', 'Senin':'Monday', 'Selasa':'Tuesday', 'Rabu':'Wednesday', 'Kamis':'Thursday', 'Jumat':'Friday', 'Sabtu':'Saturday'}

print(tz_jkt)

def get_words():
    repsonse = requests.get("http://zenquotes.io/api/random")
    json_data = json.loads(repsonse.text)
    quote = json_data[0]['q'] + " -" + json_data[0]['a']
    return(quote)

scheduler = AsyncIOScheduler({'apscheduler.timezone': 'UTC'})

@bot.command()
async def today(ctx):
    matkul_info_message = IFBot.matkul_data_to_message(IFBot.get_matkul_schedule(), "Today")
    c = bot.get_channel(CHANNEL_ID)
    await c.send(matkul_info_message)

@bot.command(name='class')
async def day(ctx, arg):

    #Checks if user asks for HELP, else run program
    if str(arg).upper() == 'HELP':
        help_info_message = "```Command usage:\n!class <day> | Shows class schedule according to day requested\n!class list | Shows list of classes in current semester\n!class today | Shows today's class list\n!class help | This menu```"
        c = bot.get_channel(CHANNEL_ID)
        await c.send(help_info_message)
    else:
        arg_c1 = str(arg).capitalize()

        if arg_c1 in day_list:
            arg_c2 = str(day_list.get(arg_c1)).capitalize()
            print('arg in list', arg_c2)
        else: 
            arg_c2 = str(arg).capitalize()

        print('ARG_C: ', arg_c1)
        print('INPUT 2: ', arg)
        matkul_info_message = IFBot.matkul_data_to_message(IFBot.get_matkul_schedule(arg_c2), arg_c2)
        c = bot.get_channel(CHANNEL_ID)
        await c.send(matkul_info_message)

async def send_embed(kode_matkul, name, hour_begin, hour_end, title_desc, desc, link, lecturer, learning_resource, assignment):
    try:
        embed=discord.Embed(title="{kode_matkul} {name} | {hour_begin} - {hour_end}. {title_desc}.".format(
          kode_matkul = kode_matkul,
          name = name,
          hour_begin = hour_begin,
          hour_end = hour_end,
          title_desc = title_desc
        ), description="{desc}".format(desc = desc), color=0x3dff54)
        embed.set_author(name="ClassAssistantBot", url="https://github.com/noxfl", icon_url="https://avatars.githubusercontent.com/u/64892153?v=4")
        embed.add_field(name="Be sure to login first before clicking any of the link below.", value="[Login](http://leaps.kalbis.ac.id/login)", inline=False)
        embed.add_field(name="Attendance", value="[Tap In/Tap Out]({tap_in_link})".format(tap_in_link = link), inline=True)
        embed.add_field(name="TLM", value="[Here]({learning_resource})".format(learning_resource = learning_resource), inline=True)
        embed.add_field(name="Assignments", value="[Here]({assignment})".format(assignment = assignment), inline=True)
        embed.set_footer(text="{lecturer}".format(lecturer=lecturer))
        c = bot.get_channel(CHANNEL_ID)
        await c.send(embed=embed)
        print('Embed sent: {name}'.format(name=name))
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
        print('Adding {name} to schedule..'.format(name=matkul['name']))
        matkul_start_reminder_message = "{} is about to start soon.\nMake sure to check attendance in by clicking the link above!\nGet ready for today's class, best of luck!".format(matkul['name'])
        # matkul_start_reminder_message = "{} is about to start soon.\nMake sure to check attendance in by clicking the link above!\nGet ready for today's class, best of luck!"
        matkul_end_reminder_message = "{} has now ended. Don't forget to check your attendance out!".format(matkul['name'])
        time_before_class = modify_thirty_minutes(matkul['hour_begin'], 'substract').split(":")
        time_after_class = modify_thirty_minutes(matkul['hour_end'], 'add').split(":")
        day = matkul['day'][0:3]
        scheduler.add_job(send_embed, CronTrigger(day_of_week=day.lower(), hour=time_before_class[0], minute=time_before_class[1], timezone=tz), 
            args=[matkul['kode_matkul'], matkul['name'], matkul['hour_begin'], matkul['hour_end'],
                     tap_in_message, matkul_start_reminder_message, matkul['tap_in_link'], matkul['lecturer'], matkul['learning_resource'], matkul['assignment']])
        scheduler.add_job(send_embed, CronTrigger(day_of_week=day.lower(), hour=time_after_class[0], minute=time_after_class[1], timezone=tz), 
            args=[matkul['kode_matkul'], matkul['name'], matkul['hour_begin'], matkul['hour_end'], 
                   tap_out_message, matkul_end_reminder_message, matkul['tap_out_link'], matkul['lecturer'], matkul['learning_resource'], matkul['assignment']])
    print('Matkul set count:', matkul_set_count)
    for job in scheduler.get_jobs():
        print(job.name, job.trigger, job.func)

async def send_matkul_reminder(matkul):
    try:
        c = bot.get_channel(CHANNEL_ID)
        await c.send(matkul)
        print('Message sent: {}'.format(matkul))
    except:
        print('Message delivery failed')

#testing
async def func():
    c = client.get_channel(CHANNEL_ID)
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
    # await send_matkul_reminder('Bot has come online')
    scheduler.start()
    

bot.run(DISCORD_TOKEN)

