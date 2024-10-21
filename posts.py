import sqlite3
import requests
import json

def create_database():
    conn = sqlite3.connect('posts.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            title TEXT,
            body TEXT
        )
    ''')
    conn.commit()
    conn.close()

def fetch_posts():
    response = requests.get('https://jsonplaceholder.typicode.com/posts')
    return response.json()

def save_posts_to_db(posts):
    conn = sqlite3.connect('posts.db')
    cursor = conn.cursor()
    
    for post in posts:
        cursor.execute('''
            INSERT OR REPLACE INTO posts (id, user_id, title, body) VALUES (?, ?, ?, ?)
        ''', (post['id'], post['userId'], post['title'], post['body']))
    
    conn.commit()
    conn.close()

#чтение всех записей
def get_all_posts():
    conn = sqlite3.connect('posts.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM posts')
    all_posts = cursor.fetchall()
    
    conn.close()
    return all_posts

#чтение по пользователям
def get_posts_by_user(user_id):
    conn = sqlite3.connect('posts.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM posts WHERE user_id = ?', (user_id,))
    posts = cursor.fetchall()
    
    conn.close()
    return posts

if __name__ == '__main__':
    create_database()               
    posts = fetch_posts()            
    save_posts_to_db(posts)        

    all_posts = get_all_posts()
    for post in all_posts:
        print(post)

   
    user_posts = get_posts_by_user(1)
    for post in user_posts:
        print(post)
