<h1 align="center">Timetable Bot for NTU Beta 0.1.0</h1> 

<hr>

A Telegram chatbot that acquires timetable data from NTU's class schedule portal, generates a timetable in app and sends daily reminders. 

<hr>

### Usecase

* **Individuals** can use it to easily acquire and reference their own timetable, with also the ability to enable reminders to be sent daily.

<hr>

### Commands

* **/start**
>  Starts the bot

* **/create**

>  One time registration of your name (single word) so that a database that has your timetable can be initialised. For example: /create Student 

* **/addmodules**

>  Add your modules to generate the timetable.

Example:

/addmodules 

CZ0001 10078 

CZ1005 13804 

CZ1006 10101 

CZ1007 10114 

CZ1011 10126 

* **/today**

>  Sends the timetable and events for today

* **/tomorrow**

>  Sends the timetable and events for tomorrow

* **/timetable**

>  Sends the timetable for the week

* **/reminders**

>  Enables daily reminders of the next day's timetable to be sent. For now it is set at 10:30pm. Next version of the bot will improve upon this.

* **/help**

>  Sends the full list of commands available, with examples provided.

### Running your own instance

* Obtain bot token from @BotFather on Telegram
* Set up MongoDB cluster
* Host on suitable platform. Current source code is written to be [deployed on Heroku](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Where-to-host-Telegram-Bots). However, as the hosting is free, one gets the reliability and uptime one pays for. 

<hr>

### Future Work

* Make UX more friendly and smooth, by adding in conversation handlers instead of the bot just responding to commands
* Add in customisable reminders, so that users can set time they want the reminders at, and maybe a custom message attached to it.

<hr>

### Credits

Authors of all libraries / modules used in the inspiration for and development of this bot, in no particular order:
* [Python Telegram Bot](https://github.com/python-telegram-bot/python-telegram-bot) - the most functional Python wrapper for the telegram bot API.
* [PyMongo](https://github.com/mongodb/mongo-python-driver) - PyMongo is objectively the best raw mongo connector for Python, coming with a default connection pool enabled by default. 
* [MongoDB](https://www.mongodb.com/) - mongoDB is used as the database for this bot, with it being noSQL allows for easy information storage.
* [SIM-UoW Timetable Bot](https://github.com/xlanor/SIM-UoW-Timetable-bot) - Took inspiration from this amazing bot in crafting the functions and presentation for this bot.
* [NTU Course Planner](https://github.com/koallen/ntu-course-planner-cli) - Learnt web scrapping and HTML parsing from reading through and using the code in this application
