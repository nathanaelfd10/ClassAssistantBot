import json
from datetime import datetime, timezone, timedelta

class ClassAssistantBot(object):

    def __init__(self):
        with open('schedule.json') as f:
            self.jadwal_json = json.load(f)
        self.day_list_english = ('Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday')
       
    def listToString(self, s): 
        str1 = ""
        for ele in s: 
            str1 += ele  
        return str1 

    def get_matkul_json(self):
        return self.jadwal_json

    def validate_day(self, day):
        
        if day in self.day_list_english:
            return True
        else:
            return False
    
    def get_matkul_schedule(self, day):
            timezone_offset = +7.0  # Asia/Jakarta (UTC+07:00)
            tzinfo = timezone(timedelta(hours=timezone_offset))
            now_tz_jkt = datetime.now(tzinfo)
            self.today = now_tz_jkt.strftime("%A")
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

    trigger_word = ["!ifbot", "kalbiser!"]

    response_words = [
        "Cheer up!",
        "Yo!"
    ]


    


