import tkinter
import re
import sqlite3
import warnings
from tkinter import filedialog
warnings.filterwarnings('ignore')

con = sqlite3.connect('loot.db')
cur = con.cursor()
all_the_shit = []
loot_names = []
loot_quantity = []

cur.execute("DROP TABLE IF EXISTS loot") # this clears previous data, to not mix things up. in future I intend to make an extension to this script that saves grand totals, for somewhat of a monthly total thing
cur.execute("CREATE TABLE loot (user VARCHAR(255), item VARCHAR(255), qty int)") # table is created fresh each run, so data doesn't persist between files
con.commit()

tkinter.Tk().withdraw() # not sure why this is here, should've commented it last night, but it doesn't work without it

file_path = filedialog.askopenfilename() # request user open file

# this module reads the file, formats, and exports into sql to be read later
with open(file_path, 'r') as file:
    for line in file:
        line = line.strip().split('\t')
        if line != ['']:
            line.pop(4)
            line.pop(0)
            all_the_shit.append(line)
            cur.execute("INSERT INTO loot VALUES(?, ?, ?)", line)
            con.commit()

all_the_shit.pop(0) # removes the first line "Time  Character   such-and-such" from the file, so it doesn't break selection statements

# this module adds all unique items to the loot_names array
for i in all_the_shit: 
    if i[1] not in loot_names:
        loot_names.append(i[1])

# this module finds total quantity of each unique item and adds it to the loot_quantity array
for i in loot_names:
    for row in cur.execute("SELECT SUM(qty) FROM loot WHERE item=?", (i,)):
        response = str(row)
        response = re.sub('\(', '', response)
        response = re.sub('\,\)', '', response)
        response = int(response)
    loot_quantity.append(response)

print('\n\n')
sentinel = 0
for i in loot_names:
    name = loot_names[sentinel]
    qty = loot_quantity[sentinel]
    print(name + " " + str(qty))
    sentinel = sentinel + 1
print('\n\n')

con.close() # THIS LINE ABSOLUTELY MUST GO LAST

