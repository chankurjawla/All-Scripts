import streamlit as st
from PyPDF2 import PdfMerger
import os

st.subheader('Merge PDF files!')
#st.write('Select pdfs to be merged.')
pdf_files = st.file_uploader('upload files to be merged',type=["pdf","PDF"],accept_multiple_files=True, key=None)

def mergepdf():
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
        return output_pdf
    else:
        print("Merging aborted due to missing file(s).")

if st.button('Merge pdf'):
    mergepdf()
    st.rerun()
st.download_button('Download merged file',output_pdf)