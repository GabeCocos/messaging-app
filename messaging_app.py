import sqlite3
from datetime import datetime

# --- SETUP DATABASE ---
conn = sqlite3.connect("messaging_app.db")
cursor = conn.cursor()

# Create users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL
);
""")

# Create followers table (many-to-many relationship)
cursor.execute("""
CREATE TABLE IF NOT EXISTS followers (
    follower_id INTEGER,
    following_id INTEGER,
    FOREIGN KEY(follower_id) REFERENCES users(id),
    FOREIGN KEY(following_id) REFERENCES users(id)
);
""")

# Create status updates
cursor.execute("""
CREATE TABLE IF NOT EXISTS statuses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    content TEXT,
    created_at TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
""")

# Create messages table
cursor.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER,
    receiver_id INTEGER,
    content TEXT,
    timestamp TEXT,
    FOREIGN KEY(sender_id) REFERENCES users(id),
    FOREIGN KEY(receiver_id) REFERENCES users(id)
);
""")

conn.commit()

# --- FUNCTIONS ---

def register_user(username):
    try:
        cursor.execute("INSERT INTO users (username) VALUES (?)", (username,))
        conn.commit()
        print(f"✅ User '{username}' registered successfully!")
    except sqlite3.IntegrityError:
        print("⚠️ Username already exists.")

def get_user_id(username):
    cursor.execute("SELECT id FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    return result[0] if result else None

def follow(follower, following):
    follower_id = get_user_id(follower)
    following_id = get_user_id(following)

    if not follower_id or not following_id:
        print("⚠️ One or both users do not exist.")
        return

    cursor.execute("INSERT INTO followers (follower_id, following_id) VALUES (?, ?)", 
                   (follower_id, following_id))
    conn.commit()
    print(f"👤 {follower} is now following {following}")

def show_followers(username):
    user_id = get_user_id(username)
    cursor.execute("""
        SELECT u.username FROM followers f
        JOIN users u ON f.follower_id = u.id
        WHERE f.following_id = ?
    """, (user_id,))
    followers = [row[0] for row in cursor.fetchall()]
    print(f"👥 {username}'s followers ({len(followers)}): {followers}")

def show_following(username):
    user_id = get_user_id(username)
    cursor.execute("""
        SELECT u.username FROM followers f
        JOIN users u ON f.following_id = u.id
        WHERE f.follower_id = ?
    """, (user_id,))
    following = [row[0] for row in cursor.fetchall()]
    print(f"➡️ {username} is following ({len(following)}): {following}")

def post_status(username, content):
    user_id = get_user_id(username)
    cursor.execute("INSERT INTO statuses (user_id, content, created_at) VALUES (?, ?, ?)", 
                   (user_id, content, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    print(f"📝 {username} posted a new status!")

def show_statuses(username):
    user_id = get_user_id(username)
    cursor.execute("""
        SELECT content, created_at FROM statuses 
        WHERE user_id = ? ORDER BY created_at DESC
    """, (user_id,))
    posts = cursor.fetchall()
    print(f"\n📢 {username}'s Status Updates:")
    for post in posts:
        print(f"- {post[0]} ({post[1]})")

def send_message(sender, receiver, content):
    sender_id = get_user_id(sender)
    receiver_id = get_user_id(receiver)
    if not sender_id or not receiver_id:
        print("⚠️ Invalid users.")
        return

    cursor.execute("""
        INSERT INTO messages (sender_id, receiver_id, content, timestamp)
        VALUES (?, ?, ?, ?)
    """, (sender_id, receiver_id, content, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    print(f"💬 Message sent from {sender} to {receiver}!")

def view_inbox(username):
    user_id = get_user_id(username)
    cursor.execute("""
        SELECT u.username, m.content, m.timestamp
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        WHERE m.receiver_id = ?
        ORDER BY m.timestamp DESC
    """, (user_id,))
    messages = cursor.fetchall()
    print(f"\n📨 Inbox for {username}:")
    for msg in messages:
        print(f"From {msg[0]}: {msg[1]} ({msg[2]})")

# --- DEMO USAGE ---

if __name__ == "__main__":
    # Register users
    register_user("luke")
    register_user("leia")
    register_user("han")

    # Follow actions
    follow("luke", "leia")
    follow("leia", "han")
    follow("han", "luke")

    # Show relationships
    show_followers("luke")
    show_following("leia")

    # Status updates
    post_status("luke", "May the Force be with you.")
    post_status("leia", "Hope will never die.")
    post_status("han", "Never tell me the odds.")

    show_statuses("leia")

    # Messaging
    send_message("luke", "leia", "Hey, how’s the rebellion?")
    send_message("leia", "luke", "Still fighting. You?")
    send_message("han", "luke", "You owe me a drink.")

    view_inbox("luke")
