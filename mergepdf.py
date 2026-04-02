from PyPDF2 import PdfMerger
import os

# List of PDF files to merge (replace with your actual file paths)
# Make sure these files exist in your Colab environment or Google Drive.
# Example: pdf_files = ['/content/file1.pdf', '/content/folder/file2.pdf']
pdf_files = [
    '/content/Receipt1.pdf', # Replace with the path to your first PDF file
    '/content/Receipt2.pdf', # Replace with the path to your second PDF file
    # Add more file paths as needed
]

output_filename = 'merged_document.pdf' # The name for the merged PDF

# Initialize PdfMerger
merger = PdfMerger()

# Check if input files exist before merging
all_files_exist = True
for pdf_file in pdf_files:
    if not os.path.exists(pdf_file):
        print(f"Error: File not found: {pdf_file}")
        all_files_exist = False
        break

if all_files_exist:
    # Append each PDF to the merger
    for pdf_file in pdf_files:
        merger.append(pdf_file)

    # Write the merged PDF to an output file
    with open(output_filename, 'wb') as output_pdf:
        merger.write(output_pdf)

    merger.close()
    print(f"Successfully merged {len(pdf_files)} PDF files into '{output_filename}'")
else:
    print("Merging aborted due to missing file(s).")

