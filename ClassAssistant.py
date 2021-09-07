import json
from datetime import datetime, timezone, timedelta
import pytz

class ClassAssistantBot(object):

    def __init__(self):
        self.jadwal_json = self.load_json()
        self.day_list_english = ('Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday')
        # self.prune_json()
        #DATE TIME
        timezone_offset = +7.0  # Asia/Jakarta (UTC+07:00)
        tzinfo = timezone(timedelta(hours=timezone_offset))
        now_tz_jkt = datetime.now(tzinfo)
        self.today = now_tz_jkt.strftime("%A")
        self.schedule_json = 'schedule.json'
        
       
    def listToString(self, s): 
        str1 = ""
        for ele in s: 
            str1 += ele  
        return str1 

    def get_jadwal_json(self):
        self.jadwal_json = self.load_json()
        return self.jadwal_json
    
    def save_json(self, dict):
        with open(self.schedule_json, 'w') as json_file:
            json.dump(dict, json_file)

    def load_json(self):
        with open('schedule.json') as f:
            return json.load(f)

    def prune_json(self):
        tz = pytz.timezone('Asia/Jakarta')
        with open('schedule2.json', "a") as json_file:
            data = json.load(json_file)
            
            for x in data['jadwal_tugas']:
                now = datetime.now()
                now_jkt = now.replace(tzinfo=tz)
                date_parse = datetime.strptime(x['date_end'], "%d %B, %Y - %H:%M")
                date_parse_tz = date_parse.replace(tzinfo=tz)
                if date_parse_tz < now_jkt:
                    del x
        
            json.dump(data, 'schedule2.json')

    def validate_day(self, day):
        if day in self.day_list_english:
            return True
        else:
            return False

    def get_tugas_schedule(self, day):
        self.jadwal_json = self.load_json()
        tugas_list = []
        show_all_template = "{no}. {matkul_name} — {day_end} - {tugas_name}"
        list_content_template = "{no}. {matkul_name} — {tugas_name} - {day_end} - {date_end} | {desc}"
        list_counter = 0
        for tugas in self.jadwal_json['jadwal_tugas']:
            if str(tugas['day_end']).upper() == str(day).upper():
                list_counter += 1
                tugas_list.append(list_content_template.format(
                    no = list_counter,
                    matkul_name = tugas['matkul_name'],
                    tugas_name = tugas['tugas_name'],
                    date_end = tugas['date_end'],
                    day_end = tugas['day_end'],
                    desc = tugas['desc']
                ))
        return tugas_list
    
    def get_matkul_schedule(self, day):
            self.jadwal_json = self.load_json()
            matkul_list = []
            show_all_template = "{no}. {day} — {name} - {hour_begin}-{hour_end}"
            list_content_template = "{no}. {kode_matkul} — {name} - {hour_begin}-{hour_end}"
            list_counter = 0

            if str(day).upper() == 'TODAY':
                for matkul in self.jadwal_json['jadwal_mobile']:
                    if str(matkul['day']).upper() == str(self.today).upper():
                        list_counter += 1
                        matkul_list.append(list_content_template.format(
                        no = list_counter,
                        day = matkul['day'],
                        kode_matkul = matkul['kode_matkul'], 
                        name = matkul['name'], 
                        lecturer = matkul['lecturer'],
                        hour_begin = matkul['hour_begin'], 
                        hour_end = matkul['hour_end']
                        ))
                print("Output from get_matkul_schedule():\n", matkul_list)
                return matkul_list
            elif str(day).upper() == 'LIST':
                sorted_matkul_list = sorted(self.jadwal_json['jadwal_mobile'], key=lambda x: self.day_list_english.index(x['day']))
                for matkul in sorted_matkul_list:
                        list_counter += 1
                        matkul_list.append(show_all_template.format(
                        no = list_counter,
                        day = matkul['day'],
                        kode_matkul = matkul['kode_matkul'], 
                        name = matkul['name'], 
                        lecturer = matkul['lecturer'],
                        hour_begin = matkul['hour_begin'], 
                        hour_end = matkul['hour_end']
                        ))
                print("Output from get_matkul_schedule():\n", matkul_list)
                return matkul_list
            else:
                if self.validate_day(day):
                    for matkul in self.jadwal_json['jadwal_mobile']:
                        if str(matkul['day']).upper() == str(day).upper():
                                list_counter += 1
                                matkul_list.append(list_content_template.format(
                                no = list_counter,
                                day = day,
                                kode_matkul = matkul['kode_matkul'], 
                                name = matkul['name'], 
                                lecturer = matkul['lecturer'],
                                hour_begin = matkul['hour_begin'], 
                                hour_end = matkul['hour_end']
                                ))
                else:
                    pass
                print("Output from get_matkul_schedule():\n", matkul_list)
                return matkul_list

    def tugas_data_to_message(self, tugas_list, day):
        tugas_greetings_template = "======== {}'s Tasks ========\n"
        if str(day).upper() == 'TODAY':
            tugas_greetings = tugas_greetings_template.format(self.today)
        elif self.validate_day(day):
            tugas_greetings = tugas_greetings_template.format(day)
        elif str(day).upper() == 'LIST':
            tugas_greetings = "======== Showing All Tasks ========\n"
        else:
            tugas_greetings = "```{} is not a valid day of week name.\nPlease enter a valid day of week in English/Indonesian\n(e.g. Monday or Senin)```".format(day)
            return tugas_greetings

        tugas_message = []
        tugas_message.append(tugas_greetings)
        if len(tugas_list) == 0:
            tugas_message.append("No tasks for {} of this week, rest easy!".format(day))
        else:
            for tugas in tugas_list:
                tugas_message.append(str(tugas+"\n"))
        print("From get_tugas_list_message:\n", self.listToString(tugas_message))
        tugas_message_string = "```{}```".format(self.listToString(tugas_message))
        return tugas_message_string


    def matkul_data_to_message(self, matkul_list, day):
        matkul_greetings_template = "======== {}'s Classes ========\n"
        if str(day).upper() == 'TODAY':
            matkul_greetings = matkul_greetings_template.format(self.today)
        elif self.validate_day(day):
            matkul_greetings = matkul_greetings_template.format(day)
        elif str(day).upper() == 'LIST':
            matkul_greetings = "======== Showing All Classes ========\n"
        else:
            matkul_greetings = "```{} is not a valid day of week name.\nPlease enter a valid day of week in English/Indonesian\n(e.g. Monday or Senin)```".format(day)
            return matkul_greetings

        matkul_message = []
        matkul_message.append(matkul_greetings)
        if len(matkul_list) == 0:
            matkul_message.append("No class for {}, rest easy!".format(day))
        else:
            for matkul in matkul_list:
                matkul_message.append(str(matkul+"\n"))
        print("From get_matkul_list_message:\n", self.listToString(matkul_message))
        matkul_message_string = "```{}```".format(self.listToString(matkul_message))
        return matkul_message_string


    


