import streamlit as st
from PyPDF2 import PdfMerger

st.subheader('Merge PDF files!')
st.write('Select pdfs to be merged.')
pdf_files = st.file_uploader('upload pdf siles here',type=["pdf","PDF"],accept_multiple_files=True, key=None)
