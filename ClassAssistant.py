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
            "kode_matkul": "MA5004",
            "classroom": "AR306",
            "name": "Fundamentals of Data Analysis - Theory",
            "lecturer": "Novi Patricia S.Kom., M.Sc.",
            "day": "Thursday",
            "hour_begin": "13:00",
            "hour_end": "15:30",
            "student_count": 34, 
            "tap_in_link": "http://leaps.kalbis.ac.id/LMS/lectures/detail/8394/attendance",
            "tap_out_link": "http://leaps.kalbis.ac.id/LMS/lectures/detail/8394/attendance",
            "learning_resource": "http://leaps.kalbis.ac.id/LMS/lectures/detail/8394/teaching-learning-materials",
            "assignment": "http://leaps.kalbis.ac.id/LMS/lectures/detail/8394/assignments",
            "unit_credit": 3 
        },
{
            "kode_matkul": "MA5004",
            "classroom": "AR306",
            "name": "Fundamentals of Data Analysis - Practicum",
            "lecturer": "Novi Patricia S.Kom., M.Sc.",
            "day": "Thursday",
            "hour_begin": "16:00",
            "hour_end": "17:40",
            "student_count": 34, 
            "tap_in_link": "http://leaps.kalbis.ac.id/LMS/lectures/detail/8395/attendance",
            "tap_out_link": "http://leaps.kalbis.ac.id/LMS/lectures/detail/8395/attendance",
            "learning_resource": "http://leaps.kalbis.ac.id/LMS/lectures/detail/8395/teaching-learning-materials",
            "assignment": "http://leaps.kalbis.ac.id/LMS/lectures/detail/8395/assignments",
            "unit_credit": 1 
        },
        {
            "kode_matkul": "TI2104",
            "classroom": "AR407",
            "name": "Computer Graphics - Theory",
            "lecturer": "Yulia Ery Kurniawati S.Kom., M.Eng.",
            "day": "Tuesday",
            "hour_begin": "11:00",
            "hour_end": "13:30",
            "student_count": 36, 
            "tap_in_link": "http://leaps.kalbis.ac.id/LMS/lectures/detail/8396/attendance",
            "tap_out_link": "http://leaps.kalbis.ac.id/LMS/lectures/detail/8396/attendance",
            "learning_resource": "http://leaps.kalbis.ac.id/LMS/lectures/detail/8396/teaching-learning-materials",
            "assignment": "http://leaps.kalbis.ac.id/LMS/lectures/detail/8396/assignments",
            "unit_credit": 3
        },
        {
            "kode_matkul": "TI2104",
            "classroom": "AR407",
            "name": "Computer Graphics - Practicum",
            "lecturer": "Yulia Ery Kurniawati S.Kom., M.Eng.",
            "day": "Tuesday",
            "hour_begin": "14:00",
            "hour_end": "15:40",
            "student_count": 36, 
            "tap_in_link": "http://leaps.kalbis.ac.id/LMS/lectures/detail/8397/attendance",
            "tap_out_link": "http://leaps.kalbis.ac.id/LMS/lectures/detail/8397/attendance",
            "learning_resource": "http://leaps.kalbis.ac.id/LMS/lectures/detail/8397/teaching-learning-materials",
            "assignment": "http://leaps.kalbis.ac.id/LMS/lectures/detail/8397/assignments",
            "unit_credit": 1
        },
        {
            "kode_matkul": "TI3054",
            "classroom": "AR306",
            "name": "Mobile Computing - Theory",
            "lecturer": "Alfa Ryano Yohannis S.T., M.T.",
            "day": "Monday",
            "hour_begin": "13:00",
            "hour_end": "15:30",
            "student_count": 21, 
            "tap_in_link": "http://leaps.kalbis.ac.id/LMS/lectures/detail/8402/attendance",
            "tap_out_link": "http://leaps.kalbis.ac.id/LMS/lectures/detail/8402/attendance",
            "learning_resource": "http://leaps.kalbis.ac.id/LMS/lectures/detail/8402/teaching-learning-materials",
            "assignment": "http://leaps.kalbis.ac.id/LMS/lectures/detail/8402/assignments",
            "unit_credit": 3
        },
{
            "kode_matkul": "TI3054",
            "classroom": "AR306",
            "name": "Mobile Computing - Practicum",
            "lecturer": "Alfa Ryano Yohannis S.T., M.T.",
            "day": "Monday",
            "hour_begin": "16:00",
            "hour_end": "17:40",
            "student_count": 21, 
            "tap_in_link": "http://leaps.kalbis.ac.id/LMS/lectures/detail/8403/attendance",
            "tap_out_link": "http://leaps.kalbis.ac.id/LMS/lectures/detail/8403/attendance",
            "learning_resource": "http://leaps.kalbis.ac.id/LMS/lectures/detail/8403/teaching-learning-materials",
            "assignment": "http://leaps.kalbis.ac.id/LMS/lectures/detail/8403/assignments",
            "unit_credit": 1
        },
{
            "kode_matkul": "TI4064",
            "classroom": "AR308",
            "name": "Artificial Intelligence - Theory",
            "lecturer": "Yulius Denny Prabowo S.T., M.T.I.",
            "day": "Friday",
            "hour_begin": "13:00",
            "hour_end": "15:30",
            "student_count": 31, 
            "tap_in_link": "http://leaps.kalbis.ac.id/LMS/lectures/detail/8398/attendance",
            "tap_out_link": "http://leaps.kalbis.ac.id/LMS/lectures/detail/8398/attendance",
            "learning_resource": "http://leaps.kalbis.ac.id/LMS/lectures/detail/8398/teaching-learning-materials",
            "assignment": "http://leaps.kalbis.ac.id/LMS/lectures/detail/8398/assignments",
            "unit_credit": 3
        },
{
            "kode_matkul": "TI4064",
            "classroom": "AR308",
            "name": "Artificial Intelligence - Practicum",
            "lecturer": "Yulius Denny Prabowo S.T., M.T.I.",
            "day": "Friday",
            "hour_begin": "16:00",
            "hour_end": "17:40",
            "student_count": 31, 
            "tap_in_link": "http://leaps.kalbis.ac.id/LMS/lectures/detail/8399/attendance",
            "tap_out_link": "http://leaps.kalbis.ac.id/LMS/lectures/detail/8399/attendance",
            "learning_resource": "http://leaps.kalbis.ac.id/LMS/lectures/detail/8399/teaching-learning-materials",
            "assignment": "http://leaps.kalbis.ac.id/LMS/lectures/detail/8399/assignments",
            "unit_credit": 1
        },
{
            "kode_matkul": "UM0062",
            "classroom": "AR301",
            "name": "Introduction to Mandarin",
            "lecturer": "Yohanes Putut Wibhisana S.S., M.Kesos.",
            "day": "Wednesday",
            "hour_begin": "09:00",
            "hour_end": "10:40",
            "student_count": 50, 
            "tap_in_link": "http://leaps.kalbis.ac.id/LMS/lectures/detail/8535/attendance",
            "tap_out_link": "http://leaps.kalbis.ac.id/LMS/lectures/detail/8535/attendance",
            "learning_resource": "http://leaps.kalbis.ac.id/LMS/lectures/detail/8535/teaching-learning-materials",
            "assignment": "http://leaps.kalbis.ac.id/LMS/lectures/detail/8535/assignments",
            "unit_credit": 2
        },
        {
            "kode_matkul": "UM3033",
            "classroom": "AR407",
            "name": "Research Methodology for IT or IS",
            "lecturer": "Drs. Muhammad Rusli M.M.",
            "day": "Wednesday",
            "hour_begin": "11:00",
            "hour_end": "13:30",
            "student_count": 89, 
            "tap_in_link": "http://leaps.kalbis.ac.id/LMS/lectures/detail/8393/attendance",
            "tap_out_link": "http://leaps.kalbis.ac.id/LMS/lectures/detail/8393/attendance",
            "learning_resource": "http://leaps.kalbis.ac.id/LMS/lectures/detail/8393/teaching-learning-materials",
            "assignment": "http://leaps.kalbis.ac.id/LMS/lectures/detail/8393/assignments",
            "unit_credit": 2
        },
                {
            "kode_matkul": "UM3033",
            "classroom": "AR407",
            "name": "MATKUL BOONG BOONGAN",
            "lecturer": "Drs. Muhammad Rusli M.M.",
            "day": "Wednesday",
            "hour_begin": "20:32",
            "hour_end": "19:33",
            "student_count": 89, 
            "tap_in_link": "http://leaps.kalbis.ac.id/LMS/lectures/detail/8393/attendance",
            "tap_out_link": "http://leaps.kalbis.ac.id/LMS/lectures/detail/8393/attendance",
            "learning_resource": "http://leaps.kalbis.ac.id/LMS/lectures/detail/8393/teaching-learning-materials",
            "assignment": "http://leaps.kalbis.ac.id/LMS/lectures/detail/8393/assignments",
            "unit_credit": 2
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
                matkul_list.append("{num}. {kode_matkul} - {name} - {hour_begin}-{hour_end}".format(
                    num = num+1,
                    day = self.today,
                    kode_matkul = matkul['kode_matkul'], 
                    name = matkul['name'], 
                    lecturer = matkul['lecturer'],
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


    


