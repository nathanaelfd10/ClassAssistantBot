from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord.ext import commands
import discord
import os
from dotenv import load_dotenv
import requests
import json
from datetime import datetime, timedelta, date
import pytz
from ClassAssistant import ClassAssistantBot
from keep_alive import keep_alive

#INITIALIZE DISCORD BOT
load_dotenv('.env')
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.environ['CHANNEL_ID'])
client = discord.Client()
bot = commands.Bot(command_prefix="!")
# CHANNEL_ID = str(os.getenv("CHANNEL_ID")) #882920343440871444 #BETA Server

#INITIALIZE THE ACTUAL PROGRAM
IFBot = ClassAssistantBot()
tugas_schedule_list = IFBot.get_jadwal_json()

#INITIALIZE DATE TIME
now = datetime.now()
tz = pytz.timezone('Asia/Jakarta')
tz_jkt = now.replace(tzinfo=tz)
day_list = {'Minggu':'Sunday', 'Senin':'Monday', 'Selasa':'Tuesday', 'Rabu':'Wednesday', 'Kamis':'Thursday', 'Jumat':'Friday', 'Sabtu':'Saturday'}
deadline_format = "%d %B %Y %H:%M"

#INITIALIZE STRING
reminder_desc = "The following task is due:"

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

# @bot.command(name='task_new')
# async def new_task(ctx, matkul_name, tugas_name, desc, deadline):
#     tugas_schedule_list = IFBot.get_jadwal_json()
#     tugas_schedule_list['jadwal_tugas'].append(
#         {      
#             "matkul_name": str(matkul_name).capitalize(),
#             "tugas_name": str(tugas_name).capitalize(),
#             "desc": str(desc).capitalize(),
#             "date_end": str(deadline),
#             "day_end": datetime.strptime(deadline, deadline_format).strftime('%A')
#         }
#     )
#     IFBot.save_json(tugas_schedule_list)
#     await add_tugas_reminder(matkul_name, tugas_name, desc, deadline)

#     c = bot.get_channel(CHANNEL_ID)
#     await c.send("Task {} successfully created.".format(tugas_name))

@bot.command(name='reminder', aliases=['remindme', 'remind_new'])
async def new_task(ctx, reminder, deadline):
    try:
        tugas_schedule_list = IFBot.get_jadwal_json()
        tugas_schedule_list['reminder'].append(
            {      
                "reminder": str(reminder).capitalize(),
                "date_end": str(deadline),
                "day_end": datetime.strptime(deadline, deadline_format).strftime('%A')
            }
        )
        IFBot.save_json(tugas_schedule_list)
        await add_reminder(reminder, deadline)

        c = bot.get_channel(CHANNEL_ID)
        await c.send("""Reminder "{reminder}" successfully created and will be due at `{day}, {deadline}`""".format(reminder = reminder, day = await get_day(deadline, deadline_format), deadline = deadline))
    except:
        c = bot.get_channel(CHANNEL_ID)
        await c.send("""``Command usage:\n!remindme "<reminder>" "<date> <hour>"\nEx: !remindme "Pick up groceries" "12 December 2021 15:00"``""")

async def add_reminder(reminder, deadline):
    deadline_time = datetime.strptime(deadline, deadline_format)
    time_morning = deadline_time.replace(hour=10, minute=00)
    scheduler.add_job(send_reminder_embed, 'date', run_date=deadline_time, timezone=tz, 
    args=[reminder, deadline])
    
async def send_reminder_embed(reminder, deadline):
    embed=discord.Embed(title="Task Reminder", description="The following task is due", color=0x0091ff)
    embed.set_author(name="ClassAssistantBot", url="https://github.com/noxfl/ClassAssistantBot/", icon_url="https://avatars.githubusercontent.com/u/64892153?v=4")
    embed.add_field(name="{reminder}".format(reminder=reminder), value="{deadline} ({day_end})".format(
        reminder = reminder,
        deadline = deadline,
        day_end = await get_day(deadline, deadline_format)
    ), inline=False)
    c = bot.get_channel(CHANNEL_ID)
    await c.send(embed=embed)

# async def add_tugas_reminder(matkul_name, tugas_name, desc, deadline):
#     deadline_time = datetime.strptime(deadline, deadline_format)
#     time_morning = deadline_time.replace(hour=10, minute=00)
#     scheduler.add_job(send_tugas_embed, 'date', run_date=deadline_time, timezone=tz, 
#     args=[matkul_name, tugas_name, desc, deadline])

# async def send_tugas_embed(matkul_name, tugas_name, desc, deadline):
#     embed=discord.Embed(title="Task Reminder", description="The following task will be due in a few days:".format(tugas_name=tugas_name), color=0x0091ff)
#     embed.set_author(name="ClassAssistantBot", url="https://github.com/noxfl/ClassAssistantBot/", icon_url="https://avatars.githubusercontent.com/u/64892153?v=4")
#     embed.add_field(name="{matkul_name}".format(matkul_name=matkul_name), value="{tugas_name}: {desc}\n{deadline} ({day_end})".format(
#         tugas_name = tugas_name,
#         desc = desc,
#         deadline = deadline,
#         day_end = await get_day(deadline, deadline_format)
#     ), inline=False)
#     c = bot.get_channel(CHANNEL_ID)
#     await c.send(embed=embed)

async def get_day(date, deadline_format):
    return datetime.strptime(date, deadline_format).strftime('%A')

async def remove_all_scheduler():
    for job in scheduler.get_jobs():
        print(job)
        job.remove()

@bot.command(name='task_reload')
async def reload_scheduler(ctx):
    print('\n======== REMOVED ALL SCHEDULER ========')
    await remove_all_scheduler()
    
    print('\n======== LOADED MATKUL REMINDER ========')
    await populate_matkul_reminder()
    
    # print('\n======== LOADED TUGAS REMINDER ========')
    # # await populate_tugas_reminder()

    print('======== LOADED TASK REMINDER =======')
    await populate_task_reminder()
    
    c = bot.get_channel(CHANNEL_ID)
    await c.send("Tasks successfully reloaded.")
    
@bot.command(name='absen')
async def absensi2(ctx, i=0):
        count = 0
        today_jadwal = {}
        jadwal = tugas_schedule_list['jadwal_mobile']

        for x in jadwal:
            if x['day'] == IFBot.today:
                count += 1
                today_jadwal[count] = x
        await send_absen_embed(today_jadwal, i)

async def send_absen_embed(jadwal, i):
    c = bot.get_channel(CHANNEL_ID)
    try:
        embed=discord.Embed(title="{kode_matkul} {name} | {hour_begin} - {hour_end}.".format(
          kode_matkul = jadwal[i]['kode_matkul'],
          name = jadwal[i]['name'],
          hour_begin = jadwal[i]['hour_begin'],
          hour_end = jadwal[i]['hour_end'],
        ), description="desc", color=0x3dff54)
        embed.set_author(name="ClassAssistantBot", url="https://github.com/noxfl", icon_url="https://avatars.githubusercontent.com/u/64892153?v=4")
        embed.add_field(name="Be sure to login first before clicking any of the link below.", value="[Login](http://leaps.kalbis.ac.id/login)", inline=False)
        embed.add_field(name="Attendance", value="[Tap In/Tap Out]({tap_in_link})".format(tap_in_link = jadwal[i]['tap_in_link']), inline=True)
        embed.add_field(name="TLM", value="[Here]({learning_resource})".format(learning_resource = jadwal[i]['learning_resource']), inline=True)
        embed.add_field(name="Assignments", value="[Here]({assignment})".format(assignment = jadwal[i]['assignment']), inline=True)
        embed.set_footer(text="{lecturer}".format(lecturer=jadwal[i]['lecturer']))
        
        await c.send(embed=embed)
        print('Embed sent: {name}'.format(name=jadwal[i]['name']))
    except: 
        matkul_info_message = IFBot.matkul_data_to_message(IFBot.get_matkul_schedule('TODAY'), 'TODAY')
        await c.send(matkul_info_message)

# @bot.command(name='task', aliases=['tugas', 'deadline'])
# async def task_deadline(ctx, arg=None, matkul_name="", tugas_name="", desc="", deadline=""):
#     c = bot.get_channel(CHANNEL_ID)
#     if str(arg).upper() == 'NEW':
#         try:
#             deadline_dt = datetime.strptime(deadline, deadline_format)
#             deadline_jkt = deadline_dt.replace(tzinfo=tz)
#             # deadline = "21 June, 2021 - 10:00"
#             # deadline_dt = datetime.strptime(deadline, deadline_format)
#             # deadline_jkt = deadline_dt.replace(tzinfo=tz)
#             print(deadline_dt)
#             await c.send(deadline_jkt)
#         except:
#             await c.send("```Please enter a valid format\n!task <day|new> <matkul_name> <tugas_name> <desc> <deadline>```")
#     else:
#         arg_c1 = str(arg).capitalize()

#         if arg_c1 in day_list:
#             arg_c2 = str(day_list.get(arg_c1)).capitalize()
#             print('arg in list', arg_c2)
#         else: 
#             arg_c2 = str(arg).capitalize()

#         print('ARG_C: ', arg_c1)
#         print('INPUT 2: ', arg)

#         tugas_info_message = IFBot.tugas_data_to_message(IFBot.get_tugas_schedule(arg_c2), arg_c2)
#         await c.send(tugas_info_message)

@bot.command(name='uts', alises=['jadwal_uts'])
async def uts(ctx):
        jadwal_uts = """
                    ```Jadwal UTS
            Senin, 25 okt 2021
            14.00 - 16.00 Mobile Computing | Parallel Computation (T)
            16.30 - 18.10 Mobile Computing | Parallel Computation (P)

            Selasa, 26 okt 2021
            11.00 - 13.00 Computer Graphics (T)
            14.00 - 16.00 Computer Graphics (P)

            Rabu, 27 okt 2021
            08.30 - 10.00 Mandarin
            11.00 - 13.00 Research Methodology

            Kamis, 28 okt 2021
            14.00 - 16.00 Fundamentals of Data Analysis (T)
            16.30 - 18.30 Fundamentals of Data Analysis (P)

            Jumat, 29 okt 2021
            14.00 - 16.00 Artificial Intelligence (T)
            16.30 - 18.10 Artificial Intelligence (P)
            ```"""
        c = bot.get_channel(CHANNEL_ID)
        await c.send(jadwal_uts)


@bot.command(name='class', aliases=['kelas', 'cek', 'jadwal'])
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
        time_parsed = datetime.strptime(hour, '%H:%M') - timedelta(hours=0, minutes=15)
        # print('TIME SUBSTRACTED: {}'.format(time_parsed))
    elif mode.lower() == 'add':
        time_parsed = datetime.strptime(hour, '%H:%M') + timedelta(hours=0, minutes=5)
        # print('TIME ADDED: {}'.format(time_parsed))
    else:
        print('{function_name}: Invalid mode value has been entered'.format(function_name = modify_thirty_minutes.__name__))
        return hour
    time_converted = datetime.strftime(time_parsed, "%H:%M")
    return time_converted


# async def populate_tugas_reminder():
#     tugas_schedule_list = IFBot.get_jadwal_json()
#     tugas_set_count = 0
#     for tugas in tugas_schedule_list['jadwal_tugas']:
#         tugas_set_count += 1
#         print('Adding {name} to schedule..'.format(name=tugas['tugas_name']))
#         await add_tugas_reminder(tugas['matkul_name'], tugas['tugas_name'], tugas['desc'], tugas['date_end'])
#         # deadline_time = datetime.strptime(tugas['date_end'], deadline_format)
#         # time_morning = deadline_time.replace(hour=10, minute=00)
#         # time_h_min_tiga_morning = deadline_time.replace() #pokoknya mundur 3 hari lah dia
#         # scheduler.add_job(send_message, 'date', run_date=time_morning, timezone=tz, args=['text'])
        

#     print('Tugas set count:', tugas_set_count)

async def populate_task_reminder():
    task_schedule_list = IFBot.get_jadwal_json()
    task_set_count = 0
    for task in tugas_schedule_list['reminder']:
        task_set_count += 1
        print('Adding {name} to schedule..'.format(name=task['reminder']))
        await add_reminder(task['reminder'], task['date_end'])
        # deadline_time = datetime.strptime(tugas['date_end'], deadline_format)
        # time_morning = deadline_time.replace(hour=10, minute=00)
        # time_h_min_tiga_morning = deadline_time.replace() #pokoknya mundur 3 hari lah dia
        # scheduler.add_job(send_message, 'date', run_date=time_morning, timezone=tz, args=['text'])
    print('Task set count:', task_set_count)

async def show_scheduler():
    for job in scheduler.get_jobs():
        print(job.name, job.trigger, job.func)


async def populate_matkul_reminder():
    matkul_schedule_list = IFBot.get_jadwal_json()
    matkul_set_count = 0
    tap_in_message = "Tap in here"
    tap_out_message = "Tap out here"
    for num, matkul in enumerate(matkul_schedule_list['jadwal_mobile']):
        matkul_set_count += 1
        print('Adding {name} to scheduler..'.format(name=matkul['name']))
        matkul_start_reminder_message = "{} is about to start soon.\nMake sure to check attendance in by clicking the link above!\nGet ready for today's class, best of luck!".format(matkul['name'])
        # matkul_start_reminder_message = "{} is about to start soon.\nMake sure to check attendance in by clicking the link above!\nGet ready for today's class, best of luck!"
        matkul_end_reminder_message = "{} is about to end. Don't forget to check your attendance out!".format(matkul['name'])
        time_before_class = modify_thirty_minutes(matkul['hour_begin'], 'substract').split(":")
        time_after_class = modify_thirty_minutes(matkul['hour_end'], 'substract').split(":")
        day = matkul['day'][0:3]
        scheduler.add_job(send_embed, CronTrigger(day_of_week=day.lower(), hour=time_before_class[0], minute=time_before_class[1], timezone=tz), 
            args=[matkul['kode_matkul'], matkul['name'], matkul['hour_begin'], matkul['hour_end'],
                     tap_in_message, matkul_start_reminder_message, matkul['tap_in_link'], matkul['lecturer'], matkul['learning_resource'], matkul['assignment']])
        scheduler.add_job(send_embed, CronTrigger(day_of_week=day.lower(), hour=time_after_class[0], minute=time_after_class[1], timezone=tz), 
            args=[matkul['kode_matkul'], matkul['name'], matkul['hour_begin'], matkul['hour_end'], 
                   tap_out_message, matkul_end_reminder_message, matkul['tap_out_link'], matkul['lecturer'], matkul['learning_resource'], matkul['assignment']])
    print('Matkul set count:', matkul_set_count)

async def send_message(message):
    try:
        c = bot.get_channel(CHANNEL_ID)
        await c.send(message)
        print('Message sent: {}'.format(message))
    except:
        print('Message delivery failed')

#testing
async def func():
    c = client.get_channel(CHANNEL_ID)
    await c.send('from func()')

@bot.command()
async def ping(ctx):
	await ctx.channel.send("pong")

# @bot.command()
# async def here(ctx, given_name):
#     channel = discord.utils.get(ctx.guild.channels, name=given_name)
#     channel_id = channel.id
#     await ctx.channel.send("I will start sending messages here from now on!")

@bot.event
async def on_ready():
    print('Successfully logged in as {0.user}'.format(bot))
    print("Ready..")
    await populate_matkul_reminder()
    await populate_task_reminder()
    # await populate_tugas_reminder()
    # await send_message('Bot has come online')
    scheduler.start()
    
    
keep_alive()
bot.run(DISCORD_TOKEN)

