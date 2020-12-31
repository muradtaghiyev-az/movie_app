import requests
from bs4 import BeautifulSoup
import bcrypt
import sqlite3


class Movie:
    LINK = "https://www.whatismymovie.com/results?text="

    def __init__(self):
        choice = input("1. Login\n2. Register\nPlease choose one: ")

        self.username = input("Please enter your username: ")
        self.password = input("Please enter your password: ")
        self.conn = self.database()
        self.login_ok = False

        if choice == "1":
           self.login()

        elif choice == "2":
            self.register()

        if self.login_ok:
            while True:
                print()
                print("1. Search")
                print("2. Last 3 search results")
                print("3. Last search results")
                print("4. Stop program")
                print()
                choice = int(input("Enter your choice: "))

                if choice == 1:
                    self.search()

                elif choice == 2:
                    self.last_3_search()

                elif choice == 3:
                    self.last_search()

                elif choice == 4:
                    print("Program finished!")
                    break

        else:
            print("Your information is not available")

    def register(self):
            pwd_conf = input("Please confirm your password: ")
            while pwd_conf != self.password:
                pwd_conf = input("Passwords are not equal, try again: ")
            else:
                salt = bcrypt.gensalt()
                hashed_password = bcrypt.hashpw(self.password.encode(), salt)

                self.conn.execute(f"""
                    INSERT INTO users (USERNAME, PASSWORD)
                    VALUES ('{self.username}','{hashed_password.decode("utf-8")}');
                """)

                self.conn.execute(f"""
                    INSERT INTO search_options (USERNAME)
                    VALUES ('{self.username}');
                """)

                self.conn.commit()
                self.login_ok = True

    def login(self):
        result = list(self.conn.execute(f"""
            SELECT * FROM users WHERE username = '{self.username}';
        """))

        if len(result) == 0:
            print("No user found")
        else:
            pwd = result[0][1]
            if bcrypt.checkpw(self.password.encode(), pwd.encode()):
                self.login_ok = True

    def database(self):
        conn = sqlite3.connect("movie.db")

        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                USERNAME TEXT PRIMARY KEY,
                PASSWORD TEXT NOT NULL);
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS search_options (
                USERNAME TEXT PRIMARY KEY,
                SEARCH1 TEXT,
                SEARCH2 TEXT,
                SEARCH3 TEXT);
        """)

        return conn

    def cut_connection(self):
        self.conn.commit()
        self.conn.close()

    @classmethod
    def get_link(cls, search_text):
        text = search_text.split()
        link_text = "+".join(text)
        link = cls.LINK + link_text
        return link

    def find_movie(self, search_text, max_=3):
        print()
        link = self.get_link(search_text)
        r = requests.get(link)
        soup = BeautifulSoup(r.text, "html.parser")
        names = soup.find_all("h3", class_="panel-title")
        print(f"{self.username} we find for you {max_} movies: ")
        print()
        for name in names[:max_*2]:
            if "More like this" not in str(name):
                print(name.text)
                print()

        self.update_results(search_text)

    def search(self):
        movie_text = input("Which movie do you want to search: ")
        movie_num = int(input("Number of movies: "))
        self.find_movie(movie_text, movie_num)

    def update_results(self, last_result):
        result = list(self.conn.execute(f"""
            SELECT SEARCH1, SEARCH2, SEARCH3 FROM search_options WHERE USERNAME = '{self.username}';
        """))[0]

        self.conn.execute(f"""
            UPDATE search_options SET SEARCH3 = '{result[1]}' WHERE USERNAME = '{self.username}';
        """)

        self.conn.execute(f"""
            UPDATE search_options SET SEARCH2 = '{result[0]}' WHERE USERNAME = '{self.username}';
        """)

        self.conn.execute(f"""
            UPDATE search_options SET SEARCH1 = '{last_result}' WHERE USERNAME = '{self.username}';
        """)

        self.conn.commit()

    def last_3_search(self):
        result = list(self.conn.execute(f"""
            SELECT SEARCH1, SEARCH2, SEARCH3 FROM search_options WHERE USERNAME = '{self.username}';
        """))[0]

        for search in result[::-1]:
            self.find_movie(search)

    def last_search(self):
        result = list(self.conn.execute(f"""
            SELECT SEARCH1, SEARCH2, SEARCH3 FROM search_options WHERE USERNAME = '{self.username}';
        """))[0][0]
        self.find_movie(result)


if __name__ == "__main__":
    movie1 = Movie()
    movie1.cut_connection()
