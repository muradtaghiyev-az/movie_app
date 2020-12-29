import requests
from bs4 import BeautifulSoup

class Movie:
    LINK = "https://www.whatismymovie.com/results?text="
    def __init__(self, login):
        self.login = login
    
    @classmethod
    def get_link(cls, search_text):
        text = search_text.split()
        link_text = "+".join(text)
        link = cls.LINK + link_text
        return link
    
    def find_movie(self, search_text, max_ = 5):
        link = self.get_link(search_text)
        r = requests.get(link)
        soup = BeautifulSoup(r.content, "html.parser")
        names = soup.find_all("h3", class_="panel-title")
        print(f"{self.login} we find for you {max_} movies: ")
        print()
        for name in names[:max_*2]:
            if "More like this" not in str(name):
                print(name.text)
                print()

username = input("Username: ")
movie1 = Movie(username)
search = input("Search movies: ")
movie1.find_movie(search)
