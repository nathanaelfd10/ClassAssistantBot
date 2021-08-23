from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord.ext import commands
import discord
import os
import random
import requests
import json
import schedule
import asyncio
import time
import threading
from datetime import date
import calendar

class ClassAssistantBot(object):

    def __init__(self):
        self.jadwal_mobile = """{"jadwal_mobile" : [
        {
            "kode_matkul": "TI2104",
            "classroom": "AR407",
            "nama": "Computer Graphics",
            "dosen": "Yulia Ery Kurniawati",
            "day": "Monday",
            "hour_begin": "11:00",
            "hour_end": "13:30",
            "student_count": 36
        },
        {
            "kode_matkul": "TI3054",
            "classroom": "AR306",
            "nama": "Mobile Computing",
            "dosen": "Alfa",
            "day": "Sunday",
            "hour_begin": "15:00",
            "hour_end": "17:30",
            "student_count": 21
        },
             {
            "kode_matkul": "TI3054",
            "classroom": "AR306",
            "nama": "Research and stuffs",
            "dosen": "Alfa",
            "day": "Sunday",
            "hour_begin": "21:23",
            "hour_end": "23:30",
            "student_count": 21
        }
        ]
        }"""

        my_date = date.today()
        self.today = calendar.day_name[my_date.weekday()]
        self.jadwal_json = json.loads(self.jadwal_mobile)

    def job(self):
        print("Running")

    def helloworld(self):
        print("I'm running!!!")

    def run_threaded(self, job_func):
        job_thread = threading.Thread(target=job_func)
        job_thread.start()

    def get_words(self):
        repsonse = requests.get("http://zenquotes.io/api/random")
        json_data = json.loads(repsonse.text)
        quote = json_data[0]['q'] + " -" + json_data[0]['a']
        return(quote)

    def translate_day_to_indo(self, day):
        try:
            if day == 'Saturday':
                return 'Sabtu'
        except:
            return 'Invalid day'

    def listToString(self, s): 
        str1 = ""
        for ele in s: 
            str1 += ele  
        
        return str1 

    def get_matkul_json(self):
        jadwal_json = json.loads(self.jadwal_mobile)
        return jadwal_json

    def get_matkul_schedule(self):
        jadwal_json = self.get_matkul_json()
        matkul_list = []
        for num, matkul in enumerate(jadwal_json['jadwal_mobile']):
            if str(matkul['day']).lower() == self.today.lower():
                matkul_list.append("{num}. {kode_matkul} - {nama} - {hour_begin}-{hour_end}".format(
                    num = num+1,
                    day = self.today,
                    kode_matkul = matkul['kode_matkul'], 
                    nama = matkul['nama'], 
                    dosen = matkul['dosen'],
                    hour_begin = matkul['hour_begin'], 
                    hour_end = matkul['hour_end']
                    ))
        print("From get_matkul():\n", matkul_list)

        return matkul_list


    def matkul_data_to_message(self, matkul_list):
        matkul_greetings = "======== {}'s Classes ========\n".format(self.today)
        matkul_message = []

        matkul_message.append(matkul_greetings)
        for matkul in matkul_list:
            matkul_message.append(str(matkul+"\n"))
        print("From get_matkul_list_message:\n", self.listToString(matkul_message))
        matkul_message_string = "```{}```".format(self.listToString(matkul_message))
        return matkul_message_string

    trigger_word = ["!ifbot", "kalbiser!"]

    response_words = [
        "Cheer up!",
        "Yo!"
    ]


    


