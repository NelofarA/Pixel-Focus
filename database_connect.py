import sqlite3
import os

conn = sqlite3.connect("database.db")
cursor = conn.cursor()


#Users Table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        uid INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        salt TEXT NOT NULL,
        level INTEGER DEFAULT 0,
        xp INTEGER DEFAULT 0
    )
""")

#Skills Table
#there should be a max of 5 skill sets
cursor.execute("""
    CREATE TABLE IF NOT EXISTS skills (
        skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        time_spent INT NOT NULL DEFAULT 0,
        flashcard_count INTEGER DEFAULT 0,
        quiz_avg  REAL DEFAULT -1,
        total_quizzes_taken INTEGER DEFAULT 0,
        FOREIGN KEY(user_id) REFERENCES users(uid)
    )
""")

#Flashcards Table

#the back of the flashcard shouldnt be more than 5 words.
#there should be only one flashcard set per skill set
cursor.execute("""
    CREATE TABLE IF NOT EXISTS flashcards (
        flashcard_id INTEGER PRIMARY KEY AUTOINCREMENT,
        skill_id INTEGER NOT NULL,
        front TEXT NOT NULL,
        back TEXT NOT NULL,
        FOREIGN KEY(skill_id) REFERENCES skills(skill_id)
    )
""")




conn.commit()
conn.close()
print("tables created")