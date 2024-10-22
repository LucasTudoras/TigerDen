import pdfplumber

def write_text_to_file(file_path, text):
    # Open the file in append mode ('a')
    with open(file_path, 'a') as file:
        # Write the text to the file
        file.write(text)
        print(f"Text successfully written to {file_path}")

def filter_text(text):
    # Split the text into lines and filter out unwanted lines
    lines = text.splitlines()
    # Remove empty lines and lines that start with "Page"
    filtered_lines = [line for line in lines if line.strip() and not line.strip().startswith("Page")]
    return "\n".join(filtered_lines)

def extract_text_from_pdf(pdf_path, output_file_path):
    # Open the output file in write mode to clear any previous content
    with open(output_file_path, 'w') as file:
        file.write("")  # Clear the file content before writing new data
    
    # Open the PDF file
    with pdfplumber.open(pdf_path) as pdf:
        num_pages = len(pdf.pages)  # Get the total number of pages
        print(f"Total Pages: {num_pages}")

        # Iterate through each page of the PDF in proper order
        for page_num in range(num_pages):
            page = pdf.pages[page_num]  # Get each page in sequence
            # Extract the text from the page
            text = page.extract_text()

            # Process the extracted text
            if text:
                # Filter the text to remove unwanted lines
                filtered_text = filter_text(text)
                # Write the filtered text to the file without "Page X:"
                write_text_to_file(output_file_path, f"{filtered_text}\n")
            else:
                print(f"Page {page_num + 1}: No text found on this page.")

pdf_22 = "C:\\Users\\Kael\\Desktop\\COS 333\\CosProject\\Renaming Files\\PDF\\OrigAvailableRoomsList2022.pdf"
pdf_23 = "C:\\Users\\Kael\\Desktop\\COS 333\\CosProject\\Renaming Files\\PDF\\AvailableRoomsList2023.pdf"
pdf_24 = "C:\\Users\\Kael\\Desktop\\COS 333\\CosProject\\Renaming Files\\PDF\\AvailableRoomsList2024.pdf"

output22 = "C:\\Users\\Kael\\Desktop\\COS 333\\CosProject\\Renaming Files\\PDF\\22.txt"  
output23 = "C:\\Users\\Kael\\Desktop\\COS 333\\CosProject\\Renaming Files\\PDF\\23.txt"  
output24 = "C:\\Users\\Kael\\Desktop\\COS 333\\CosProject\\Renaming Files\\PDF\\24.txt"

with open(output22, 'w') as file:
    file.write("")  

with open(output23, 'w') as file:
    file.write("")

with open(output24, 'w') as file:
    file.write("")


extract_text_from_pdf(pdf_22, output22)
extract_text_from_pdf(pdf_23, output23)
extract_text_from_pdf(pdf_24, output24)
