import os

from client import MyClient

if __name__ == '__main__':
    bot = 'vidtract'
    print('start', bot)
    # this is a application token
    token = os.environ.get(bot)

    # pass unique str
    client = MyClient(bot)
    client.post_works.start(21, 0)
    print('end', bot)
    client.run(token)