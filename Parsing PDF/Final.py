import pdfplumber

#writes the filtered text into the files themselves
def write_text_to_file(file_path, text):
    # Open the file in append mode ('a')
    with open(file_path, 'a') as file:
        # Write the text to the file
        file.write(text + "\n")
        print(f"Text successfully written to {file_path}")

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
        print(f"Total Pages: {num_pages}")

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


#defining underclass and upperclass lists
UpCollege = []
UpHall = []
UpRoom = []
UpType = []
UpSqft = []

UnCollege = []
UnHall = []
UnRoom = []
UnType = []
UnSqft = []

#adds the room information into the the underclass arrays   
def add_to_underclass(College, Hall, Room, Type, Sqft):
    UnCollege.append(College)
    UnHall.append(Hall)
    UnRoom.append(Room)
    UnType.append(Type)
    UnSqft.append(Sqft)

def add_to_upperclass(College, Hall, Room, Type, Sqft):
    UpCollege.append(College)
    UpHall.append(Hall)
    UpRoom.append(Room)
    UpType.append(Type)
    UpSqft.append(Sqft)

def NCW_hall_name(words):
    Hall_name = words[3]
    if Hall_name == "ADDY":
        return words[3], words[4], words[4], words[5]
    elif Hall_name == "ALIYA":
        return "ALIYA KANJI", words[5], words[6], words[7]
    elif Hall_name == "KWANZA":
        return "KWANZA JONES", words[5], words[6], words[7]
    elif Hall_name == "JOSE":
        return "JOSE FELICIANO", words[5], words[6], words[7]

def store_intoArray(starts_College, filename):
    if starts_College:
        try:
            with open(filename, 'r') as file:
                next(file)
                for line in file:
                    words = line.split()
                    words = [word.upper() for word in words]
                    first_word = words[0]
                    if first_word == "UPPERCLASS":
                        add_to_upperclass(words[0], words[1], words[2], words[3], words[4])
                    else:
                        if first_word == "NEW":
                            hall, room, type, sqft = NCW_hall_name(words)
                            add_to_underclass("NCW", hall, room, type, sqft)
                        else:
                            College = words[0]
                            add_to_underclass(College, words[2], words[3], words[4], words[5])
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
                        add_to_upperclass(is_Upperclass, words[0], words[1], words[2], words[3])
                    elif is_Underclass.find("COLLEGE") != -1:
                        add_to_underclass(words[4], words[0], words[1], words[2], words[3])

                    else:
                        first_word = words[0]
                        if first_word == "ADDY":
                            add_to_underclass("NCW", "ADDY", words[2], words[3], words[4])
                        elif first_word == "ALIYA":
                            add_to_underclass("NCW", "ALIYA KANJI", words[3], words[4], words[5])
                        elif first_word == "BOSQUE":
                            add_to_underclass("YEH", "FU", words[2], words[3], words[4])
                        elif first_word == "GROUSBECK":
                            add_to_underclass("YEH", "GROUSBECK", words[2], words[3], words[4])
                        elif first_word == "H":
                            add_to_underclass("YEH", "Hariri", words[2], words[3], words[4])
                        elif first_word == "JOSE":
                            add_to_underclass("NCW", "JOSE FELICIANO", words[4], words[5], words[6])
                        elif first_word == "KWANZA":
                            add_to_underclass("NCW", "KWANZA JONES", words[4], words[5], words[6])
                        elif first_word == "MANNION":
                            add_to_underclass("YEH", "MANNION", words[2], words[3], words[4])
        except FileNotFoundError:
            print(f"The file {filename} does not exist.")

def Main():
    # Paths to the PDF files
    pdf_22 = "PDF\\OrigAvailableRoomsList2022.pdf"
    pdf_24 = "PDF\\AvailableRoomsList2024.pdf"
    pdf_23 = "PDF\\AvailableRoomsList2023.pdf"

    # Paths to the output text files
    output22 = "PDF\\22.txt"
    output23 = "PDF\\23.txt"  
    output24 = "PDF\\24.txt" 

    # Clear the output files before extraction
    clear_file(output22)
    clear_file(output23)
    clear_file(output24)

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
    filename = output24
    starts_College = find_word_in_file(filename, colleges)

    store_intoArray(starts_College, filename)

    output = "PDF\\24rooms.txt"  

    countUn = 0
    with open(output, 'w') as file:
        file.write("") 
    with open(output, 'a') as file:
        for x in range(len(UnCollege)):
            file.write(UnCollege[x] + " " + UnHall[x] + " " + UnRoom[x] + " " + UnType[x] + " " + UnSqft[x] + "\n")
            countUn +=1
        countUp = 0
        for y in range(len(UpCollege)):
            file.write(UpCollege[y] + " " + UpHall[y] + " " + UpRoom[y] + " " + UpType[y] + " " + UpSqft[y] + "\n")
            countUp +=1
    print("UnderClass = " + str(countUn))
    print("UpperClass = " + str(countUp))
    print(starts_College)  

Main()