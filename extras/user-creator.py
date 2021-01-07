# credits to Anarov for improved example
from __future__ import print_function
from bs4 import BeautifulSoup
import requests
import random
import time
import sys

def main():
    username = str(sys.argv[1])
    password = str(sys.argv[2])
    rank = str(sys.argv[3])
    query_url = "http://127.0.0.1:5000/api/site/"

    if username == "random":
        from random_username.generate import generate_username
        username = generate_username(1)[0]

    query_data = {"api": "INVALID_API",\
            "create_user": "true",\
            "username": username,\
            "password": password,\
            "rank": rank}
    r = requests.post(query_url, query_data)
    print(r.text)

if __name__ == "__main__":
    main()
