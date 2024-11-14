import pdfplumber
from pathlib import Path

#defining underclass and upperclass lists
class Info:
    def __init__(self):
        self.Class = []

#writes the filtered text into the files themselves
def write_text_to_file(file_path, text):
    # Open the file in append mode ('a')
    with open(file_path, 'a') as file:
        # Write the text to the file
        file.write(text + "\n")

#filters the text to get rid of extra lines and page numbers
def filter_text(text):
    # Split the text into lines and filter out unwanted lines
    lines = text.splitlines()
    # Remove empty lines and lines that start with "Page"
    filtered_lines = [line for line in lines if line.strip() and not line.strip().startswith("Page")]
    return filtered_lines

#extracting the actual text from the pdf
def extract_text_from_pdf(pdf_path, output_file_path, college_names):
    x = 0
    # Open the PDF file
    with pdfplumber.open(pdf_path) as pdf:
        num_pages = len(pdf.pages)  # Get the total number of pages

        # Variable to hold the previous line
        previous_line = None
        
        # Iterate through each page of the PDF in proper order
        for page_num in range(num_pages):
            page = pdf.pages[page_num]  # Get each page in sequence
            # Extract the text from the page
            text = page.extract_text()
            
            # Process the extracted text
            if text:
                
                # Filter the text to remove unwanted lines
                filtered_lines = filter_text(text)

                for line in filtered_lines:
                    # Check if any college name is in the line
                    if any(college in line for college in college_names) :
                        # Write the previous line if it exists
                        if previous_line and x == 0:
                            write_text_to_file(output_file_path, previous_line)  # Write the previous line
                            x =1

                        # Write the current line that contains the college name
                    if x ==1:
                        write_text_to_file(output_file_path, line)

                    # Update the previous line with the current line
                    previous_line = line  # Always update to the current line

                # At the end of the page, reset the previous line
                previous_line = None  
            else:
                print(f"Page {page_num + 1}: No text found on this page.")

#gets the output files ready to receive the information
def clear_file(name_file):
    with open(name_file, 'w') as file:
        file.write("")

#Skips the intro part of the pdf until it reaches the data itself
def find_word_in_file(filename, words_to_find):
    try:
        with open(filename, 'r') as file:
            next(file)
            for line in file:
                # Split line into words
                words = line.split()
                x = 0
                for word in words:
                    # Check if the word is in the list of words to find
                    if word in words_to_find:
                        return True  # Return the found word
                    else:
                        return False
        print("No words found from the list.")
        return None  # Return None if no words were found
    except FileNotFoundError:
        print(f"The file {filename} does not exist.")
        return None

#adds the room information into the the underclass arrays   
def add_to_class( Hall, Room, info_instance):
    colleges = {
            '1967': "Butler College",
            '1976': "Butler College",
            'Bloomberg': "Butler College",
            'Bogle': "Butler College",
            'Scully': "Butler College",
            'Wilf': "Butler College",
            'Yoseloff': "Butler College",
            '99Alexander': "Forbes College",
            'Annex': "Forbes College",
            'Main': "Forbes College",
            'Blair': "Mathey College",
            'Campbell': "Mathey College",
            'Edwards': "Mathey College",
            'Joline': "Mathey College",
            'Little': "Mathey College",
            'Addy': "New College West",
            'Jose E. Feliciano': "New College West",
            'Aliya Kanji': "New College West",
            'Kwanza Jones': "New College West",
            'Buyers': "Rockefeller College",
            'Campbell': "Rockefeller College",
            'Holder': "Rockefeller College",
            'Witherspoon': "Rockefeller College",
            '1901': "Upperclass",
            'Feinberg': "Upperclass",
            'Patton': "Upperclass",
            '1903': "Upperclass",
            'Foulke': "Upperclass",
            'Pyne': "Upperclass",
            'Brown': "Upperclass",
            'Henry': "Upperclass",
            'Scully': "Upperclass",
            'Cuyler': "Upperclass",
            'Laughlin': "Upperclass",
            'Spelman': "Upperclass",
            'Dickinson Street, 2': "Upperclass",
            'Little': "Upperclass",
            'Walker': "Upperclass",
            'Dod': "Upperclass",
            'Lockhart': "Upperclass",
            'Wright': "Upperclass",
            '1981': "Whitman College",
            'Baker E': "Whitman College",
            'Baker S': "Whitman College",
            'Fisher': "Whitman College",
            'Hargadon': "Whitman College",
            'Lauritzen': "Whitman College",
            'Murley': "Whitman College",
            'Wendell B': "Whitman College",
            'Wendell C': "Whitman College",
            'Fu': "Yeh College",
            'Grousbeck': "Yeh College",
            'Hariri': "Yeh College",
            'Mannion': "Yeh College",
            "Forbes": "idk"
        }
    halls = colleges.keys()
    halls = [hall.upper() for hall in halls]
    if Hall not in halls:
        return
    if Hall == "FORBES":
        if Room[0] == "A":
            Hall = "Annex"
        else:
            Hall = "Main"
    
    UnderClass_dict = {
        'Hall': Hall.title(),
        'Room': Room.upper(),
        'RoomID': (Hall.title()+ Room.upper())
    }

    info_instance.Class.append(UnderClass_dict)

def NCW_hall_name(words):
    Hall_name = words[3]
    if Hall_name == "ADDY":
        return "ADDY", words[4]
    elif Hall_name == "ALIYA":
        return "ALIYA KANJI", words[5]
    elif Hall_name == "KWANZA":
        return "KWANZA JONES", words[5]
    elif Hall_name == "JOSE":
        return "JOSE FELICIANO", words[5]

def store_intoArray(starts_College, filename, info_instance):
    if starts_College:
        try:
            with open(filename, 'r') as file:
                next(file)
                for line in file:
                    words = line.split()
                    words = [word.upper() for word in words]
                    first_word = words[0]
                    if first_word == "UPPERCLASS":
                        add_to_class(words[1], words[2], info_instance)
                    else:
                        if first_word == "NEW":
                            Hall, Room = NCW_hall_name(words)
                        else:
                            Hall, Room =words[2], words[3]
                        add_to_class(Hall, Room, info_instance)
        except FileNotFoundError:
            print(f"The file {filename} does not exist.")
    else:
        try:
            with open(filename, 'r') as file:
                next(file)
                for line in file:
                    words = line.split()
                    words = [word.upper() for word in words]
                    is_Upperclass = words[4]
                    is_Underclass = words[5]
                    if is_Upperclass.find("UPPERCLASS") != -1:
                        add_to_class(words[0], words[1], info_instance)
                    elif is_Underclass.find("COLLEGE") != -1:
                        add_to_class(words[0], words[1], info_instance)
                    else:
                        first_word = words[0]
                        if first_word == "ADDY":
                            Hall, Room = "ADDY", words[2], 
                        elif first_word == "ALIYA":
                            Hall, Room ="ALIYA KANJI", words[3]
                        elif first_word == "BOSQUE":
                            Hall, Room ="FU", words[2]
                        elif first_word == "GROUSBECK":
                            Hall, Room = "GROUSBECK", words[2]
                        elif first_word == "H":
                            Hall, Room = "Hariri", words[2]
                        elif first_word == "JOSE":
                            Hall, Room = "JOSE FELICIANO", words[4]
                        elif first_word == "KWANZA":
                            Hall, Room = "KWANZA JONES", words[4]
                        elif first_word == "MANNION":
                            Hall, Room = "MANNION", words[2]
                        add_to_class(Hall, Room, info_instance)
        except FileNotFoundError:
            print(f"The file {filename} does not exist.")

def print_output(output, list):
    countUn = 0
    with open(output, 'w') as file:
        file.write("") 
    with open(output, 'a') as file:
        for x in list.Class:
            """ file.write(x["Hall"] + " ")
            file.write(x["Room"] + " ") """
            file.write(x["RoomID"] + "\n")
            countUn +=1
        print("Rooms: " + str(countUn))

def main(file):
    # Paths to the PDF files
    pdf = Path(file)
    pdf_output = Path("/tmp/temp.txt")

    uploaded_pdf = Info()

    # Define the college names to look for
    college_names = {
        "Butler", "Forbes", "Mathey", "NCW", "Rocky", "Upperclass", "Whitman", "Yeh",
        "1967", "1976", "Bloomberg", "Bogle", "Scully", "Wilf", "Yoseloff",
        "Annex", "Main", "Blair", "Campbell", "Edwards", "Hamilton", "Joline", "Little",
        "Addy", "Jose", "Kanji", "Kwanza",
        "Buyers", "Holder", "Witherspoon",
        "1901", "1903", "99Alexander", "Brown", "Cuyler", "Dickinson Street, 2",
        "Dod", "Feinberg", "Foulke", "Henry", "Little", "Lockhart", "Patton", "Pyne",
        "Scully", "Spelman", "Walker", "Wright",
        "1981", "Baker", "Fisher", "Hargadon", "Lauritzen",
        "Murley", "Wendell",
        "Fu", "Grousebeck", "Hariri", "Mannion"
    }

    # Extract text from both PDFs
    extract_text_from_pdf(pdf, pdf_output, college_names)
    

    colleges = {"Butler", "Forbes", "Mathey", "New College West", "Rocky", "Upperclass", "Whitman", "Yeh"}
    
    print("uploaded test")
    starts_College = find_word_in_file(pdf_output, colleges)
    store_intoArray(starts_College, pdf_output, uploaded_pdf)

    return uploaded_pdf.Class
