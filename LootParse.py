#############################
#         Carl Castle       #
#           5-08-25         #
#        Final Project      #
#############################

# This program parses Fleet Log outputs from Eve Online. The outputs are standardized, and have had the same format for 19 years.
# To help you from having to search for them, there are no images. The reason is further explained at the end of the file. I expect no points.

# Import libraries
import os, re, sqlite3
import tkinter as tk
from tkinter import filedialog
from pathlib import Path

# Handle the sqlite connection
directory = os.path.dirname(__file__) # Get the path to the current folder. This will be useful later
con = sqlite3.connect(directory + 'loot.db') # Create connection to the sqlite file, in the current folder.
cur = con.cursor() # Define the cursor

# Initialize the lists to be used later
item_list = []
loot_names = []
loot_quantity = []

# This was useful during testing, in case the program crashed partway through. I decided to leave it in case I expand on this project later.
cur.execute("DROP TABLE IF EXISTS loot") # This clear previous data
cur.execute("CREATE TABLE loot (user VARCHAR(255), item VARCHAR(255), qty int)") # Create a fresh table to work in
con.commit() # Commit changes. Without this statement, changes are stored in memory, and can't be read by other commands



# this module reads the file, formats, and exports into sql to be read later
def parse_file(file_path):
    with open(file_path, 'r') as file: # Open file in read-only
        for line in file:
            line = line.strip().split('\t') # Strip each line into ['Time', 'Character', 'Item Type', 'Quantity', 'Item Group']
            if line != ['']: # Check if the line is empty. Sometimes if someone disconnects before the fleet is updated, a blank line is inserted instead of data
                line.pop(4) # Remove the 'Item Group' value from the line list
                line.pop(0) # Remove the 'Time' value from the line list
                item_list.append(line) # Add the line, whose value is now ['Character', 'Item Type', 'Quantity'] to the item_list
                cur.execute("INSERT INTO loot VALUES(?, ?, ?)", line) # Insert the line into sqlite
                con.commit() # Commit changes
    item_list.pop(0) # The first line in the Eve Fleet Log output currently has, literally, ['Character', 'Item Type', 'Quantity'], and needs to be removed.



# this module adds all unique items to the loot_names list
def get_item_names():
    for i in item_list: 
        if i[1] not in loot_names: # Check if item is NOT in the list. If it is not present, add it
            loot_names.append(i[1]) # [1] to refer to the ['Item Type'] field



# this module finds total quantity of each unique item and adds it to the loot_quantity array
def get_item_quantity():
    for i in loot_names: # Runs for each item in the list
        for row in cur.execute("SELECT SUM(qty) FROM loot WHERE item=?", (i,)): # Grabs the total sum of all entries where the Item Type matches the request
            response = str(row) # Turns the response list (containing one entry) into a string
            response = re.sub(r'\(', '', response) # Trims the start of the response
            response = re.sub(r'\,\)', '', response) # Trims the end of the response
            response = float(response) # Converts the trimmed string into a float, in case of partial drops (this is a possibility)
        loot_quantity.append(response) # Append the result to the loot_quantity list. The indexes between names/quantity will match


# This module is where the magic happens, most of the processing is in here.
# This is my solution to tkinter needing all of the data upfront in the form of labels.
# Without knowing exactly how many lines will be in a fleet log, I couldn't hard-code any amount of labels
def join_list_to_string():
    placeholder_list = [] # This is meant to hold the strings to be joined
    global loot_names, loot_quantity, item_list # This is so that the lists can be emptied after processing.
    # Continuing the comment from above. If this is not done, calling this function repeatedly (which is aviailable) will pack the lists full of data from
    # different files, giving inaccurate data in the printout
    output_string = '' # Init string to be used later
    sentinel = 0 # Instead of the usual 'for i in xyz' I had to use a sentinel, because 'i' in this case is a string instead of an index, and is not iterable
    for i in loot_names:

        # These two lines grab the name and quantity
        name = loot_names[sentinel]
        qty = loot_quantity[sentinel]

        # These three lines make a string out of the name and quantity values, and append it with a newline into the output_string. The output_string becomes quite long.
        placeholder_string = f"{name}   {qty}" # Create string with the name/quantity
        placeholder_list.append(placeholder_string) # Add that string into the placeholder_list
        output_string = '\n'.join(placeholder_list) # Append the string from the sentinel index into the output_string

        # We all know what this one does
        sentinel += 1
    
    # These 3 lines reset the lists, so multiple files can be parsed without mixing data
    loot_names = []
    loot_quantity = []
    item_list = []

    if output_string == '': output_string = 'Nothing to see here!' # In case the fleet log is empty, like Data 4
    return output_string # Return the completed output_string, with all of the line breaks, to be used as a label.


# This creates the new windows with data in them
def open_output_window(path):
    label_text = join_list_to_string() # Run the above function to get the label text
    new_window = tk.Toplevel(root) # Create the new window
    new_window.title(Path(path).stem) # Set a title based on what file the user chose
    new_window.geometry('320x900') # This seemed like a healthy size
    label = tk.Label(new_window, text=label_text) # Create the label
    label.pack(pady=20) # Add the label into the window



# I'll be entirely transparent, I don't understand classes well at all. I attempted to do everything I could outside of them.
# This is the bare minimum I could get away with, without sacrificing functionality, most of this is repurposed from previous assignments.
class loot_parse:

    def __init__(self, root):

        # Create the window
        self.root = root
        self.root.title("Eve Loot Parser")
        self.root.geometry("300x150")

        # Set the header
        self.label = tk.Label(root, text="Select the Fleet Log you wish to parse")
        self.label.pack(pady=20)

        # Set a button frame, so they're all in line
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady=10)

        # Create the buttons
        self.show_example_button = tk.Button(self.button_frame, text="Show Example", command=self.show_example)
        self.run_parse_button = tk.Button(self.button_frame, text="Choose File", command = self.run_parse)
        self.exit_button = tk.Button(self.button_frame, text="Exit", command = self.exit)

        # Align the buttons in the frame
        self.show_example_button.grid(row = 0, column = 0, padx = 5)
        self.run_parse_button.grid(row = 0, column = 1, padx = 5)
        self.exit_button.grid(row = 0, column = 2, padx = 5)

    # Call functions in order. The multiple functions are required based on the way I've built this.
    def run_parse(event=None): # Set the 'event' to be None, in order to prevent the function claiming it has more arguments than needed
        try: # This try/except is in case the file is of the wrong filetype, or some other error springs up.
            file_path = filedialog.askopenfilename() # Request user open file
            parse_file(file_path) # Fill the item_list based on the selected file
            get_item_names() # Fill the loot_names list
            get_item_quantity() # Fill the loot_quantity list
            open_output_window(file_path) # Create the output window using the given file_path to grab the title
        except:
            print("Something went wrong loading that file, skipping")

    # This is functionally the same as run_parse(), but with a preset piece of data. All of the rest is the same as above
    def show_example(event=None):
        try: # This try/except is here in case the file_path fails to find the correct directory.
            file_path = f"{directory}/LootParse Data 6.txt" # Grab an example data set from the current folder
            parse_file(file_path)
            get_item_names()
            get_item_quantity()
            open_output_window(file_path)
        except:
            print("Something went wrong finding that file, skipping")

    # Exit button
    def exit(event=None):
        con.close() # Close connection before exit
        root.destroy() # I like the feeling that destroy() gives. Not much else to comment here


# Boilerplate "run program"
if __name__ == "__main__":
    root = tk.Tk()
    parse = loot_parse(root)
    root.mainloop()


con.close() # Failsafe in case the user hits X instead of the exit button



#   I attempted to add the Eve logo to the main window, and subsequent new windows. This didn't go well.
#   3 days of troubleshooting and changing the library I was using between PIL, Pillow, and PhotoImage, I couldn't get an image to load anywhere, with nonsense error messages.
#   When I had code segments that were *supposed* to add an image, what actually happened was all labels/buttons would disappear, and if I clicked where the buttons
#       were supposed to be, the program instead crashed. I have no idea why and concluded it was divine intervention deciding I wasn't worthy of images.

#   Forgive me, for I have sinned.