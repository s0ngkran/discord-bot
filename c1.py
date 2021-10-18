import os

from client import MyClient

if __name__ == '__main__':
    bot = 'staria'
    print('start', bot)
    # this is a application token
    token = os.environ.get(bot)

    # pass unique str
    client = MyClient(bot)
    client.post_works.start(19, 30)
    client.post_sleep.start(21, 30)
    print('end', bot)
    client.run(token)