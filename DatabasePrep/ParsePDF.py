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
    UnderClass_dict = {
        'Hall': Hall.upper(),
        'Room': Room.upper(),
        'RoomID': (Hall+" " + Room).upper()
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

def main():
    # Paths to the PDF files
    pdf_22 = Path("PDF/OrigAvailableRoomsList2022.pdf")
    pdf_24 = Path("PDF/AvailableRoomsList2024.pdf")
    pdf_23 = Path("PDF/AvailableRoomsList2023.pdf")

    # Paths to the output text files
    output22 = Path("PDF/22.txt")
    output23 = Path("PDF/23.txt")
    output24 = Path("PDF/24.txt") 

    # Clear the output files before extraction
    clear_file(output22)
    clear_file(output23)
    clear_file(output24)

    PDF_22 = Info()
    PDF_23 = Info()
    PDF_24 = Info()

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
    extract_text_from_pdf(pdf_22, output22, college_names)
    extract_text_from_pdf(pdf_23, output23, college_names)
    extract_text_from_pdf(pdf_24, output24, college_names)

    colleges = {"Butler", "Forbes", "Mathey", "New College West", "Rocky", "Upperclass", "Whitman", "Yeh"}
    
    print("2022 data:")
    starts_College = find_word_in_file(output22, colleges)
    store_intoArray(starts_College, output22, PDF_22)
    print_output(Path("PDF/22rooms.txt"), PDF_22)
    # newline
    print("")   

    print("2023 data:")
    starts_College = find_word_in_file(output23, colleges)
    store_intoArray(starts_College, output23, PDF_23)
    print_output(Path("PDF/23rooms.txt"), PDF_23)
    # newline
    print("")  
    
    print("2024 data:")
    starts_College = find_word_in_file(output24, colleges)
    store_intoArray(starts_College, output24, PDF_24)
    print_output(Path("PDF/24rooms.txt"), PDF_24)

main()
