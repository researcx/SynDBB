# credits to Anarov for improved example
from __future__ import print_function
from bs4 import BeautifulSoup
import requests
import random
import time
import basc_py4chan
import sys
print("Starting...")

#usage: 4chan-poster.py <board> <first/random/all>

def checkIfAny(mainStr, listOfStr):
   for subStr in listOfStr:
       if subStr in mainStr.lower():
           return (True, subStr)
   return (False, "")

def main():
    username = str(sys.argv[5])
    query_url = str(sys.argv[4])
    chboard = str(sys.argv[1])
    post_into = str(sys.argv[2])
    mode = str(sys.argv[3])
    board = basc_py4chan.Board(chboard)
    threads = board.get_threads()
    print("Got %i threads" % len(threads))

    print("Board: " + chboard + " - Posting into: " + post_into + " - Mode: " + mode)

    if mode == "first":
        thread_check = threads[0]
        print("Checking by last active")
    if mode == "random": 
        thread_check = random.choice(threads)
        print("Checking at random")

    is_first_post = 1
    replyToThread = 0
    replyToPost = 0
    ignore = 0
    running = 0


    thread = []
    thread_icons = ['art', 'attention', 'link', 'news', 'rant', 'release', 'repeat', 'serious', 'stupid', 'unfunny', 'weird']
    allowed_threads = ['futa', 'foot', 'feet', 'futa', 'female', 'fellatio', 'caught', 'romantic', 'blowjob', 'kitsune', 'corrupt', 'poke', 'catgirl', 'slut', 'gif', 'bunny', 'konosuba', 'megumin', 'magical', 'bdsm', 'bondage', 'military', 'uniform', 'nurse', 'medic', 'mom', 'mother', 'panties', 'trap', 'trans', 'cunt', 'boy', 'fem', 'blush', 'horny', 'smell', 'scent', 'robot', 'cyborg', 'android', 'latex', 'rubber', 'doll', 'girl', 'hairy', 'armpit', 'butt', 'shemale', 'shiny', 'hypno', 'contortion', 'predicament', 'heel', 'nylon', 'leg', 'stocking', 'sock', 'horny', 'encase', 'chubby', 'bbw', 'sissy', 'cow', 'anal', 'tomboy', 'touhou', 'witch', 'throat', 'boob', 'breast', 'tit']
    disallowed_threads = ['vore', 'bomb', 'giant', 'rape', 'sbbw', 'bedbound', 'gore', 'guro', 'rules']

    # for current_thread in thread_check:
    # print("Waiting...")
    # time.sleep(1)
    for post in thread_check.all_posts:
        if post.has_file:
            post_number = "[feed-id]"+str(post.post_number)+"[/feed-id]"
            
            if post.comment:
                message = BeautifulSoup(post.comment).get_text('\n')
            else:
                message = ""
            if post.file.filename:
                file_url = "[ct]https://i.4cdn.org/"+ chboard +"/" + post.file.filename+"[/ct]"
            else:
                file_url = ""
            post_url = post.url

            #print('ID: #', post_number)
            #print('Message:', message)
            #print('File:', post_url)

            if is_first_post and post.subject:
                print("Checking if OP...")
                time.sleep(1)
                subject = post.subject
                print('Subject:', subject)
                allowed = checkIfAny(post.subject, allowed_threads)
                disallowed = checkIfAny(post.subject, disallowed_threads)
                if disallowed[0]:
                    print('Avoiding: ', disallowed[1])
                if allowed[0] and not disallowed[0]:
                    print('Found: ', allowed[1])
                    print("Creating new thread...")
                    running = 1
                    query_data = {"api": "INVALID_API",\
                            "create_thread": "true",\
                            "username": username,\
                            "category": post_into,\
                            "content": post_number + '\n'+ file_url + '\n\n' + message + "\n\n" + post_url,\
                            "title": subject,\
                            "icon": random.choice(thread_icons),\
                            "anon": "1"}
                    r = requests.post(query_url, query_data)
                    replyToThread = r.text
                    is_first_post = 0
                else:
                    print("Ignoring...")
                    ignore = 1
            else:
                if running and not ignore:
                    print("Checking if new replies...")
                    time.sleep(1)
                    if replyToThread != 0:
                        print("Replying to " + str(replyToThread))
                        query_data2 = {"api": "INVALID_API",\
                                "create_post": "true",\
                                "username": username,\
                                "content": post_number + '\n'+ file_url + '\n\n' + message + "\n\n" + post_url,\
                                "reply_to_thread": str(replyToThread),\
                                "reply_to_post": str(replyToPost),\
                                "anon": "1"}
                        #print(query_data2)
                        r2 = requests.post(query_url, query_data2)
                        print(r2.text)
                    ignore = 0

if __name__ == "__main__":
    main()
