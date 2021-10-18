import discord
import copy
import datetime
import os
from dotenv import load_dotenv
from discord.ext import tasks, commands
import asyncio
import json

from my_work import MyWork
load_dotenv()


class MyClient(discord.Client):
    def __init__(self, unique, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.all_users_path = './db/'+str(unique) + '_users.txt'
        self.works_path = './db/'+str(unique) + '_works.txt'
        self.work = MyWork(self.works_path)
        self.all_users = self.get_all_users()
        self.alarm_active = False
        # self.ch = self.get_all_channels()
        self.all_cmds = '''

All Command...

### Work
. to @someone <title> <description>
. w <work_id> del 
. w <work_id> done 
. w <work_id> status <status> 

### show all commands you can use
. show cmd

### about user
. del user @someone
. show user

### variation
you can type these all to exec a command
. .    # show all works
. w @someone <title> <description>
. del <work_id>
. add work to @someone <title> <description>
. add to @someone <title> <description>
. addwork @someone <title> <description>
. addwork to @someone <title> <description>

. deluser @someone
. showuser
.....

                '''

    async def on_ready(self):
        print('Logged on as', self.user)

    def is_activate_command(self):
        if self.msg.startswith('. ') and len(self.msg) >= 4:
            return True
    def get_command(self):
        args = self.msg[2:].split(' ')
        return len(args), args
    def get_all_users(self):
        # read file
        path = self.all_users_path
        if not os.path.exists(path):
            with open(path, 'w') as f:
                json.dump([],f)

        with open(path, 'r') as f:
            dat = json.load(f)
        return dat
    def get_all_users_id(self, all_users):
        ans = []
        for user in all_users:
            ans.append(user['id'])
        return ans
    def add_user(self,user):
        user_id = str(user.id)
        user_name = str(user)
        all_users_id = self.get_all_users_id(self.all_users)

        
        
        if user_id not in all_users_id:
            self.all_users.append({
                'id':user_id,
                'name': user_name,
            })
            with open(self.all_users_path, 'w') as f:
                json.dump(self.all_users,f)
            return True
    def del_user(self, user_id):

        remove_ind = None
        for i, user in enumerate(self.all_users):
            if user['id'] == user_id:
                remove_ind = i
                break
        if remove_ind != None:
            self.all_users.remove(self.all_users[i])
            with open(self.all_users_path, 'w') as f:
                json.dump(self.all_users,f)
            return True

    def seconds_until(self, hours, minutes):
        given_time = datetime.time(hours, minutes)
        now = datetime.datetime.now()
        future_exec = datetime.datetime.combine(now, given_time)
        if (future_exec - now).days < 0:  # If we are past the execution, it will take place tomorrow
            future_exec = datetime.datetime.combine(now + datetime.timedelta(days=1), given_time) # days always >= 0

        return (future_exec - now).total_seconds()
    

    @tasks.loop(hours=24)
    async def post_sleep(self, hour, min):
        await asyncio.sleep(self.seconds_until(hour,min))
        await self.send('sleep now!')
        await asyncio.sleep(2)
        
        # loop until on online
        self.alarm_active = True
        for i in range(20):
            await self.send('\n\n'+('.'*i)+'\nSLEEP NOW!\nSLEEP NOW!\nSLEEP NOW!\n')
            await asyncio.sleep(3)
            if self.alarm_active == False:
                await self.send('alarm off')
                break
            if i == 19:
                await self.send('alarm off')


    @tasks.loop(hours=24)
    async def post_works(self, hour, min):
        await asyncio.sleep(self.seconds_until(hour,min))
        await self.show_all_works()
    
    async def after(self, sec):
        await asyncio.sleep(sec)
        await self.send('done')
    
    async def send(self,*msg):
        text = '-> '
        for _ in msg:
            text += _ + ' '

        await self.ch.send(text)
    def extract_user_id(self, user_id_text):
        user_id = user_id_text.replace('<@!', '')[:-1]
        return user_id
    
    async def show_all_works(self, is_done=None,q_status=None):
        works = self.work.get_works()

        text = ''
        for work in works:
            status = work['status']
            if is_done == True:
                if status == 'done':
                    pass
                else:
                    continue
            elif is_done == False:
                if status == 'done':
                    continue
                else:
                    pass
            if q_status is not None:
                if status == q_status:
                    pass
                else:
                    continue

            id = work['id']
            date = work['date'][:-7]
            assigned_by = work['assigned_by']
            assigned_to = work['assigned_to']
            assigned_by = self.get_name_from_id(assigned_by)[:-5]
            assigned_to = assigned_to
            title = work['title']
            description = work['description']

            text += '\n"%s" -%s-\nstatus: %s\n%s --> <@!%s>\n%s\n%s\n'%(title,id, status,assigned_by, assigned_to,date, description)
        await self.send(text)
    def get_name_from_id(self, user_id):
        user_id = str(user_id)
        for user in self.all_users:
            if user['id'] == user_id:
                return user['name']
        return 'xxxxxxxxx'

    async def on_message(self, message):
        
        # don't respond to ourselves
        if message.author == self.user:
            return
        print('from', message.author, '->',message.content)
        self.alarm_active = False
        add_user_res = self.add_user(message.author)

        # do command
        self.msg = message.content
        self.ch = message.channel
        user = message.author


        # print if add new user
        if add_user_res:
            await self.send('Hello, '+ str(user)[:-5]+'.\nYour name is added to my brain.')
        
        if self.msg.startswith('.') and len(self.msg) < 5 and ' ' not in self.msg:
            await self.send(self.all_cmds)
            return
        if self.msg in ['. .','. w','. a','. work','. works','. all','. w all', '. workall','. w a', '. work all', '. all work', '. show work', '. show works', '. shows work']:
            await self.show_all_works()
            return
        
        # all commands
        if self.is_activate_command():
            n_arg, args  = self.get_command()

            # test
            cmd = n_arg == 1 and args[0] == 'test'
            if cmd:
                await self.send('test na krub')
                return
            
            # delete user
            cmd1 =n_arg == 2 and 'd' in args[0] and 'user' in args[0] 
            cmd2 = n_arg ==3 and 'd' in args[0] and 'u' in args[1]
            if cmd1 or cmd2:
                user_id = self.extract_user_id(args[1])
                res = self.del_user(user_id)
                if res:
                    await self.send('success, delete '+user_id)
                else:
                    await self.send('fail')
            
            # show all users
            cmd1 = n_arg == 2 and args[0] == 'show'  and (args[1]=='user' or args[1]=='users')
            cmd2 = n_arg == 1 and  'showuser' in args[0] and n_arg < 12
            cmd3 = n_arg == 1 and 'user' in args[0] and n_arg<10
            if cmd1 or cmd2 or cmd3:
                all_users = self.get_all_users()
                text = 'All User in My Brain...\n'
                for i,user in enumerate(all_users):
                    text += str(i+1)+' -> '+ user['name'] + '\n'
                await self.send(text)
            


            # show all commands
            cmd1 = n_arg == 2 and args[0] == 'show' and (args[1] == 'command' or args[1] == 'cmd')
            if cmd1:
                await self.send(self.all_cmds)
            
            # show all work with query
            cmd1 = n_arg == 2 and 'w' in args[0]
            cmd2 = n_arg == 2 and 'a' in args[0]
            if cmd1 or cmd2 or cmd3:
                if 'd' == args[1] or 'done' == args[1]:
                    await self.show_all_works(is_done=True)
                else:
                    q_status = args[1]
                    await self.show_all_works(q_status=q_status)
                return
            # show all works
            cmd1= n_arg == 1 and 'work' in args[0]
            cmd2= n_arg == 1 and args[0] == 'works'
            cmd3= n_arg == 2 and args[0:2] == ['show', 'work']
            cmd4= n_arg == 2 and args[0:2] == ['show', 'works']
            cmd5 = n_arg == 1 and ('w' in args[0] or 'a' in args[0] or 's' in args[0])
            if cmd1 or cmd2 or cmd3 or cmd4 or cmd5:
                await self.show_all_works()
                return
            
            ## del work
            cmd1 = n_arg == 3 and 'w' in args[0]  and 'del' in args[2] 
            cmd2 = n_arg == 2 and 'del' in args[0]
            if cmd1 or cmd2:
                wid = args[1]
                res = self.work.del_works(wid)
                if res:
                    await self.send('success')
                else:
                    await self.send('fail')
                return
            
            ## done work
            cmd1 = n_arg == 3 and 'w' in args[0] and args[2] == 'done'
            if cmd1:
                wid = args[1]
                status = 'done'
                res = self.work.update_status_work(wid, status)
                if res:
                    await self.send('success')
                else:
                    await self.send('fail')
                return

            ## update status
            cmd1 = n_arg == 4 and 'w' in args[0]  and 's' in args[2]
            if cmd1:
                wid = args[1]
                status = args[3]
                res = self.work.update_status_work(wid, status)
                if res:
                    await self.send('success')
                else:
                    await self.send('fail')
                return

            # # add work
            cmd1 = n_arg >=4 and args[0] == 'to'
            cmd2 = n_arg >= 6 and args[0:3] == ['add','work','to']
            cmd3 = n_arg >= 4 and ('a' in args[0] or 'w' in args[0])
            cmd4 = n_arg >= 5 and ('a' in args[0] or 'w' in args[0]) and args[1] == 'to'
            cmd5 = n_arg >= 4 and 'w' in args[0]

            found = 0
            if cmd1 :
                someone = args[1]
                title = args[2]
                des = args[3:]
                found = 1
            elif cmd2:
                someone = args[3]
                title = args[4]
                des = args[5:]
                found = 1
            elif cmd3:
                someone = args[1]
                title = args[2]
                des = args[3:]
                found = 1
            elif cmd4:
                someone = args[2]
                title = args[3]
                des = args[4:]
                found = 1
            elif cmd5:
                someone = args[1]
                title = args[2]
                des = args[3:]
                found = 1
            
            if found == 1:
                someone_id = self.extract_user_id(someone)
                self.work.add_works(user.id,someone_id, title, *des)
                await self.send('Added', title)
                return


# def t2():
#         print('start t2')
#         token = os.environ.get('p_save_token')
#         client2 = MyClient(2)
#         client2.post_works.start()
#         print('end t2')
#         client2.run(token)
# def t1():

if __name__ == '__main__':
    # you have to create .env file on the same dir
    # and define bot_token = 'your token'

    # to get create a discord bot
    # https://discord.com/developers/applications/

    # to invite a bot to a server
    # https://discordapi.com/permissions.html

    print('start t1')
    # this is a application token
    token = os.environ.get('bot_token')

    # pass unique str
    client = MyClient('staria')
    client.post_works.start(19, 30)
    client.post_sleep.start(21, 30)
    print('end t1')
    client.run(token)


# print('start')
# t1()
# t2()
# print('end')
# x = threading.Thread(target= asyncio.run(t1()))
# x.start()
# x = threading.Thread(target= asyncio.run(t2()))
# x.start()
# print('end all')
# print('start all')
### get all connected text channel 
# text_channel_list = []
# for server in discord.Client.guilds:
#     for channel in server.channels:
#         if str(channel.type) == 'text':
#             text_channel_list.append(channel)
# self.ch= text_channel_list