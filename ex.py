import streamlit as st
import PyPDF2
from io import BytesIO

st.write('Hello User!')
file_type = st.text_input('Choose source type [ pdf , audio ]')
max_len = int(st.text_input('Chunk size:'))
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
full_text = ''

if file_type == 'pdf':
	if uploaded_file is not None:
		reader = PyPDF2.PdfReader(uploaded_file)
		page_wise = []
				
		for i in range(len(reader.pages)):    
			p = reader.pages[i]
			t = p.extract_text()
			page_wise.append(t.strip())	
			full_text = full_text + "\n" + t

Transcript_final = full_text
    
