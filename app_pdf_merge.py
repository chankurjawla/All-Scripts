import streamlit as st
from PyPDF2 import PdfMerger
import io

st.subheader('Merge PDF files!')

pdf_files = st.file_uploader('Upload files to be merged', type=["pdf"], accept_multiple_files=True)

def merge_pdfs(files):
    merger = PdfMerger()
    for pdf in files:
        merger.append(pdf)
    
    # Create a byte buffer to hold the PDF in memory
    output_stream = io.BytesIO()
    merger.write(output_stream)
    merger.close()
    
    # Seek to the start of the stream so the download button can read it
    output_stream.seek(0)
    return output_stream

if pdf_files:
    if st.button('Merge PDFs'):
        with st.spinner('Merging...'):
            merged_pdf_stream = merge_pdfs(pdf_files)
            
            st.success('Done!')
            st.download_button(
                label="Download merged PDF",
                data=merged_pdf_stream,
                file_name="merged_document.pdf",
                mime="application/pdf"
            )
else:
    st.info("Please upload at least two PDF files.")
