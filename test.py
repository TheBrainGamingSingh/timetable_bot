from bs4 import BeautifulSoup
import requests
import ssl
import re
from ssl_type import SSLAdapter
import config
import pymongo
import os
from telegram import chat
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
import datetime
import calendar
import messages
TELENAME = ""
TOKEN = ""
PORT = int(os.environ.get('', ''))
NAME = ''
updater = Updater(TOKEN)
updater.start_webhook(listen="0.0.0.0",
                      port=PORT,
                      url_path=TOKEN)
updater.start_webhook(listen="0.0.0.0",port=int(PORT),url_path=TOKEN)
updater.bot.setWebhook("https://{}.herokuapp.com/{}".format(NAME, TOKEN))
dispatcher = updater.dispatcher

client = pymongo.MongoClient("")

user_db = client[""]
user_list = user_db[""]

def start(bot, update):
    welcome_string = "".join(messages.welcome_text)
    bot.send_message(chat_id=update.message.chat_id, text=welcome_string)
    if (user_list.count_documents({"userid": str(update.message.chat_id)})==1):
        for x in user_list.find({"userid": str(update.message.chat_id)},{ "_id": 0,"userkey": 1 }):
            name = x[""]
            db = client[""]
            global timetable
            timetable = db[name]
        bot.send_message(chat_id=update.message.chat_id, text=("Welcome back, " + name.title()))
    else:
        bot.send_message(chat_id=update.message.chat_id, text=("You seem to be new, please type /create (your single-worded name) to register. The bot will not function until registration is done."))

dispatcher.add_handler(CommandHandler('start', start))


job = updater.job_queue
def create_db(bot, update, args):   
    if (len(args)==0):
        bot.send_message(chat_id=update.message.chat_id, text="🧒 Please enter a single-worded name")
        return
    if (len(args)>1):
        bot.send_message(chat_id=update.message.chat_id, text="🧒 Please enter a single-worded name")
        return
    global db
    name = args[0]
    db = client["timetableapp"]
    global timetable
    timetable = db[name]
    user_entry = { "userid": str(update.message.chat_id), "userkey": name }
    user_list.insert_one(user_entry)
    bot.send_message(chat_id=update.message.chat_id, text="Name added to database! Please call /addmodules to add your modules! See /help for an example of how to add them!")
    
dispatcher.add_handler(CommandHandler('create', create_db, pass_args=True))

def fetch_schedule(courseCode):
        message = "OK"
        url = \
            "https://wish.wis.ntu.edu.sg/webexe/owa/AUS_SCHEDULE" + \
            ".main_display1?acadsem=" + config.ACADYEAR + ";" + config.ACADSEM + \
            "&r_search_type=F&r_subj_code=" + courseCode.upper() + \
            "&boption=Search&staff_access=false&acadsem=" + config.ACADYEAR + \
            ";" + config.ACADSEM + "&r_course_yr="
        try:
            s = requests.Session()
            s.mount("https://", SSLAdapter(ssl.PROTOCOL_TLSv1))
            r = s.post(url)
        except requests.exceptions.ConnectionError:
            message = "Connection error. Cannot connect to NTU server."
            exit(-1)
        soup = BeautifulSoup(r.text, features="html.parser")
        try:
            name_table = schedule = soup.find_all("table")[0].find_all("td")
            schedule = soup.find_all("table")[1].find_all("td")
        except IndexError:
            message = "The course code does not exist in NTU database for this semester."
            exit(-1)
        return schedule, name_table, message

def course_entry_into_database(course_code, index):
    if re.search(r"^\w{2}\d{4}$", course_code) == None:
        return("invalid course code format (not xxYYYY)")
    schedule, name_table, message = fetch_schedule(course_code)
    if message != "OK":
        return(message)
    course_name = str(name_table[1])[41:-16]
    _dict = {}
    for i in range(len(schedule)):
        result = re.search(r"\d{5}", str(schedule[i]))
        if result != None:
            _dict[result.group(0)]=i
    if index not in _dict:
        return("index wrong")
    else:
        if len(_dict) != 1:
            number_per_index = list(_dict.values())[1]-list(_dict.values())[0]
            index_full = schedule[_dict[index]:_dict[index]+number_per_index]
        elif len(_dict) == 1:
            index_full = schedule[:]
        number_of_classes = (len(index_full)//7)
        print(number_of_classes)
        for j in range(number_of_classes):
            if (timetable.count_documents({ "course_name": course_name, "course_code": course_code, "type": str(index_full[j*7+1])[7:-9], "day": str(index_full[j*7+3])[7:-9], "time": str(index_full[j*7+4])[7:-9], "location": str(index_full[j*7+5])[7:-9], "index": index, "acadyear": config.ACADYEAR, "acadsem": config.ACADSEM}) == 0):
                class_entry = {"course_name": course_name, "course_code": course_code, "type": str(index_full[j*7+1])[7:-9], "day": str(index_full[j*7+3])[7:-9], "time": str(index_full[j*7+4])[7:-9], "location": str(index_full[j*7+5])[7:-9], "index": index, "acadyear": config.ACADYEAR, "acadsem": config.ACADSEM}
                timetable.insert_one(class_entry)
                
                #return("info added")
            else:
                pass
                #return("info already inside")
        return(course_code + " added!")

def get_course_list(bot,update,args):
    course_dict = {}
    if (len(args)%2!=0):
        bot.send_message(chat_id=update.message.chat_id, text="Invalid entry format. Please enter\n/add \n(course code) (index)\n(course code) (index)\n for the modules in your timetable")
        return
    else:
        for x in range(len(args)//2):
            reply = course_entry_into_database(args[2*x],args[2*x+1])
            bot.send_message(chat_id=update.message.chat_id, text=reply)
        
dispatcher.add_handler(CommandHandler('addmodules', get_course_list, pass_args=True))
       
def tomorrow(bot,update):
    tomorrow_day = (datetime.datetime.today()+ datetime.timedelta(days=1)).strftime('%a')
    tomorrow_longday = (datetime.datetime.today()+ datetime.timedelta(days=1)).strftime('%A')
    daily = ""
    daily += "📝 Here's your timetable for tomorrow!\n"
    daily += "====================\n"
    daily += (tomorrow_longday + "'s timetable!\n")
    # if (tomorrow_day == "Saturday" or tomorrow_day == "Sunday"):
    #     bot.send_message(chat_id=update.message.chat_id, text="It's a weekend tomorrow!")
    #     return
    query ={"day": tomorrow_day.upper()}
    for x in timetable.find(query,{ "_id": 0,"course_name": 1, "course_code": 1, "type":1, "time":1, "location":1, "index":1}).sort("time"):
        name = x["course_name"].title()
        print(name)
        if (name[-1] == "*" or name[-1] == "#" or name[-1] == "^"):
            name = name[:-1]
            if (name[-1] == "*" or name[-1] == "#" or name[-1] == "^"):
                name = name[:-1]
                if (name[-1] == "*" or name[-1] == "#" or name[-1] == "^"):
                    name = name[:-1]
        name = re.sub('Amp;', '', name)
        daily += ("====================\n")
        daily += ("📌 " + x["course_code"].upper() + " " + name.title() + "\n")
        daily += ("Type: " + x["type"].title() + "\n")
        daily += ("⌛ " + x["time"] + "\n")
        #daily += ("Index: " + x["index"] + "\n")
        daily += ("📍 " + x["location"].upper() + "\n")
    if (daily[-6:-1]=="able!"):
        daily += "You have no lessons tomorrow!"
    bot.send_message(chat_id=update.message.chat_id, text=daily)

dispatcher.add_handler(CommandHandler('tomorrow', tomorrow))

def today(bot,update):
    today_day = (datetime.datetime.today().strftime('%a'))
    today_longday = (datetime.datetime.today().strftime('%A'))
    daily = ""
    daily += "📝 Here's your timetable for today!\n"
    daily += "====================\n"
    daily += (today_day + "'s timetable!\n")
    query ={"day": today_day.upper()}
    for x in timetable.find(query,{ "_id": 0,"course_name": 1, "course_code": 1, "type":1, "time":1, "location":1}).sort("time"):
        name = x["course_name"].title()
        if (name[-1] == "*" or name[-1] == "#" or name[-1] == "^"):
            name = name[:-1]
            if (name[-1] == "*" or name[-1] == "#" or name[-1] == "^"):
                name = name[:-1]
                if (name[-1] == "*" or name[-1] == "#" or name[-1] == "^"):
                    name = name[:-1]
        name = re.sub('Amp;', '', name)
        daily += ("====================\n")
        daily += ("📌 " + x["course_code"].upper() + " " + name.title() + "\n")
        daily += ("Type: " + x["type"].title() + "\n")
        daily += ("⌛ " + x["time"] + "\n")
        daily += ("📍 " + x["location"].upper() + "\n")
    if (daily[-6:-1]=="able!"):
        daily += "You have no lessons today!"
    bot.send_message(chat_id=update.message.chat_id, text=daily)

dispatcher.add_handler(CommandHandler('today', today))

def timetable1(bot,update):
    days_of_week=['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
    days_short_week=["MON","TUE","WED","THU","FRI","SAT","SUN"]
    weekly = ""
    weekly += "📝 Here's your weekly timetable!\n"
    weekly += ("====================\n")
    for x in range(len(days_of_week)):
        day_classes = timetable.find({"day": days_short_week[x]},{ "_id": 0,"course_name": 1, "course_code":1, "type":1, "time":1, "location":1, "day":1, "day":1}).sort([("day", 1), ("time", 1)])
        weekly += ("🗓 " + days_of_week[x].title() + "\n")
        for y in day_classes:
            name = y["course_name"].title()
            if (name[-1] == "*" or name[-1] == "#" or name[-1] == "^"):
                name = name[:-1]
                if (name[-1] == "*" or name[-1] == "#" or name[-1] == "^"):
                    name = name[:-1]
                    if (name[-1] == "*" or name[-1] == "#" or name[-1] == "^"):
                        name = name[:-1]
            name = re.sub('Amp;', '', name)
            weekly += ("---------------------\n")
            weekly += ("📌 " + y["course_code"].upper() + " " + name.title() + "\n")
            weekly += ("Type: " + y["type"].title() + "\n")
            weekly += ("⌛ " + y["time"] + "\n")
            weekly += ("📍 " + y["location"].upper() + "\n")
        if (weekly[-4:-1]=="day"):
            weekly += ("You have no lessons on this day!\n")
        weekly += ("====================\n")
    
    bot.send_message(chat_id=update.message.chat_id, text=weekly)

dispatcher.add_handler(CommandHandler('timetable', timetable1))

def tomorrow1(bot,job):
    print("1")
    tomorrow_day = (datetime.datetime.today()+ datetime.timedelta(days=1)).strftime('%a')
    tomorrow_longday = (datetime.datetime.today()+ datetime.timedelta(days=1)).strftime('%A')
    daily = ""
    daily += "📝 Here's your timetable for tomorrow!\n"
    daily += "====================\n"
    daily += (tomorrow_longday + "'s timetable!\n")
    query ={"day": tomorrow_day.upper()}
    for x in timetable.find(query,{ "_id": 0,"course_name": 1, "course_code": 1, "type":1, "time":1, "location":1, "index":1}).sort("time"):
        name = x["course_name"].title()
        print(name)
        if (name[-1] == "*" or name[-1] == "#" or name[-1] == "^"):
            name = name[:-1]
            if (name[-1] == "*" or name[-1] == "#" or name[-1] == "^"):
                name = name[:-1]
                if (name[-1] == "*" or name[-1] == "#" or name[-1] == "^"):
                    name = name[:-1]
        name = re.sub('Amp;', '', name)
        daily += ("====================\n")
        daily += ("📌 " + x["course_code"].upper() + " " + name.title() + "\n")
        daily += ("Type: " + x["type"].title() + "\n")
        daily += ("⌛ " + x["time"] + "\n")
        daily += ("📍 " + x["location"].upper() + "\n")
    if (daily[-6:-1]=="able!"):
        daily += "You have no lessons tomorrow!"
    bot.send_message(chat_id=job.context, text=daily)


def start_reminders(bot,update,job_queue):
    bot.send_message(chat_id=update.message.chat_id, text = 'Starting daily reminders!')
    job.run_daily(tomorrow1,datetime.time(hour=22, minute=30, second=0),days=(0,1,2,3,4,5,6), context = update.message.chat_id)

dispatcher.add_handler(CommandHandler('reminders', start_reminders, pass_job_queue=True))

def help1(bot,update):
    help_string = "".join(messages.help_text)
    bot.send_message(chat_id=update.message.chat_id, text=help_string)
    bot.send_message(chat_id=update.message.chat_id, text=daily)

dispatcher.add_handler(CommandHandler('help', help1))

def unknown(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text="😞 Sorry, I didn't understand that command.")
dispatcher.add_handler(MessageHandler(Filters.command, unknown))

updater.idle()
