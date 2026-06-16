import sqlite3

# Data store karne ke liye Sqlite3 ka connection banaya gaya hai.
con = sqlite3.connect("heybuddy.db")
cursor = con.cursor()

# Ek nayi table 'sys_command' banate hai. Agar pehle se bani hai to error na de (IF NOT EXISTS).
cursor.execute("""
CREATE TABLE IF NOT EXISTS sys_command(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    path TEXT
)
""")

# Purane code mein path "C:\Users\Dipes\..." fix tha, jo uske computer mein tha but humare paas fail ho sakta tha.
# Yaha ab basic example set kar diya jisko aap change kar sakte ho further.
# (agar duplicate row ka error aaye baar baar chalane se, toh use handle karna sikhna padega aage chalkar)
cursor.execute(
    "INSERT INTO sys_command (name, path) VALUES (?, ?)",
    ("notepad", r"C:\Windows\System32\notepad.exe")
)

con.commit()
con.close()
