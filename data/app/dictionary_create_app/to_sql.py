import json
import sqlite3
import os
import time
import sys


def _create_db():
    if os.path.isfile("dictionary.db"):
        os.remove("dictionary.db")

    print ("Creating database ... ", end="")

    sql_create = """
    CREATE TABLE lang (id INTEGER NOT NULL UNIQUE PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL);
    CREATE TABLE word (id INTEGER NOT NULL UNIQUE PRIMARY KEY AUTOINCREMENT, word TEXT NOT NULL, word_alt TEXT NOT NULL, lang_id INTEGER NOT NULL);
    CREATE TABLE dict (id INTEGER NOT NULL UNIQUE PRIMARY KEY AUTOINCREMENT, lang_id INTEGER NOT NULL, name TEXT NOT NULL, name_desc TEXT NOT NULL, desc TEXT NOT NULL, search_string TEXT NOT NULL);
    CREATE TABLE item (id INTEGER NOT NULL UNIQUE PRIMARY KEY AUTOINCREMENT, dict_id INTEGER NOT NULL, name TEXT NOT NULL, desc TEXT NOT NULL);
    CREATE TABLE link (id INTEGER NOT NULL UNIQUE PRIMARY KEY AUTOINCREMENT, item_id INTEGER NOT NULL, name TEXT NOT NULL, refers TEXT NOT NULL);
    INSERT INTO lang (name) VALUES ('serbian');
    """

    conn = sqlite3.connect("dictionary.db")

    cur = conn.cursor()

    sql_commands = [x for x in sql_create.split("\n") if x.strip() != ""]

    for sql_command in sql_commands:
        cur.execute(sql_command)
        conn.commit()

    print ("done.")

    conn.close()

def _words():
    print ()
    print ("WORD: Preparing list ... ", end="")

    word_set = set()
    sql_command = ""
    for i in range(len(d["serbian"]["latin"]["abc+"])):
        if STOP_AFTER:
            if STOP_AFTER == i:
                break

        
        w = d["serbian"]["latin"]["abc+"][i]
        w = _remove_chars(w)
        if not w:
            continue

        w_a = d["serbian"]["latin"]["abc"][i]
        w_a = _remove_chars(w_a)

        word_set.add(f"{w}\n{w_a}")


    print (" Sorting...", end="")

    word_list = list(word_set)
    word_list.sort()

    print (" Adding to command ...")
    step = int(len(word_list) / 100)
    for idx, i in enumerate(word_list):
        i = i.split("\n")
        sql_command += f"INSERT INTO word (word, word_alt, lang_id) VALUES ('{i[0].strip()}', '{i[1].strip()}', 1); \n"
        if idx % step == 0 or idx > len(word_list) - 10:
            print (f"{idx}/{len(word_list)} words ... executing ... ", end="")
            for j in sql_command.split("\n"):
                cur.execute(j)
            print ("commiting ... ", end="")
            conn.commit()
            print ("Done.")
            sql_command = ""




REMOVE_CHARS = "0123456789,.()[]{}+=\"';:<>/?!@#$%^&*_"
STOP_AFTER = None
MAX_NUMBER_OF_ROWS_WITHOUT_COMMIT = 250

def _remove_chars(text: str) -> str:
    for i in REMOVE_CHARS:
        text = text.replace(i, "")
    text = text.strip()
    if text.find("-") == 0 or text.find("-") == len(text) - 1:
        text = text.replace("-", "")
    return text


total_t_start = time.perf_counter()
with open("dictionary.json", "r", encoding="utf-8") as file:
    d = json.load(file)


print(f"You have {len(d['serbian']['dicts'])} new dictionaries to add.")
print(f"Database exist: {os.path.isfile('dictionary.db')}")
print()
print ("Do you want to append to existing, or create new database ?")
result = input("(A)ppend, (N)ew, (Q)uit  : ").lower()

create_new = None

if result == "a":
    create_new = False
elif result == "n":
    create_new = True

if create_new is None:
    sys.exit()

# Create DataBase
if create_new:
    _create_db()


conn = sqlite3.connect("dictionary.db")
cur = conn.cursor()


# Words
if create_new:
    _words()

# Dictionaries
counter = 0
for dict_name in d["serbian"]["dicts"]:
    dict_t = time.perf_counter()
    sql_command = f"INSERT INTO dict (lang_id, name, name_desc, desc, search_string) VALUES (1, '{dict_name}', ?, ?, ?) ;"
    dict_describe_name = d["serbian"]["dicts"][dict_name]["@name"]
    dict_describe_desc = d["serbian"]["dicts"][dict_name]["@desc"]
    dict_describe_search_string = d["serbian"]["dicts"][dict_name]["@search_string"]
    cur.execute(sql_command, (dict_describe_name, dict_describe_desc, dict_describe_search_string))
    conn.commit()
    dict_id = cur.lastrowid

    d["serbian"]["dicts"][dict_name].pop("@name")
    d["serbian"]["dicts"][dict_name].pop("@desc")
    d["serbian"]["dicts"][dict_name].pop("@search_string")

    print ()
    print (f"Started dict: ({dict_id}) {dict_name} ")

    count = 0
    printed_percent = 0
    for item in d["serbian"]["dicts"][dict_name]:
        percent = int(count / len(d["serbian"]["dicts"][dict_name]) * 100)
        if percent and percent % 3 == 0 and percent != printed_percent:
            printed_percent = percent
            print (f"{percent}% ", end="", flush=True)

        count += 1
        if STOP_AFTER:
            if count == STOP_AFTER:
                break
        item_text = d["serbian"]["dicts"][dict_name][item]["text"]
        item_links = d["serbian"]["dicts"][dict_name][item]["links"]

        sql_command = f"INSERT INTO item (dict_id, name, desc) VALUES ({dict_id}, ?, ?);"
        cur.execute(sql_command, (item, item_text))
        counter += 1
        
        if not item_links and counter <= MAX_NUMBER_OF_ROWS_WITHOUT_COMMIT:
            if count < len(d["serbian"]["dicts"][dict_name]) - 20:
                continue
        counter = 0
        conn.commit()
        item_id = cur.lastrowid

        for link in item_links:
            if len(link[0]) < 3:
                continue
            sql_command = f"INSERT INTO link (item_id, name, refers) VALUES ({item_id}, ?, ?);"
            cur.execute(sql_command, (link[0], link[1]))
        conn.commit()
    
    print (f"  100% Done.  TIME: {(time.perf_counter() - dict_t)/60: ,.2f} min")

total_t_start = int((time.perf_counter() - total_t_start))
print ()
print (print (f"  All Done.  TIME: {int(total_t_start/3600):02d}:{int(total_t_start/60)%60:02d}:{total_t_start%60:02d}"))

