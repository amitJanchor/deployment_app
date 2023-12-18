import streamlit as st
st.code("pip install PyPDF2")
import PyPDF2
from io import BytesIO

st.write('Hello World')
file_type = st.text_input('Choose source type [ pdf , audio ]')

if file_type == 'pdf':
	uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
	if uploaded_file is not None:
		reader = PyPDF2.PdfReader(uploaded_file)
		page_wise = []
		full_text = ''
				
		for i in range(len(reader.pages)):    
			p = reader.pages[i]
			t = p.extract_text()
			page_wise.append(t.strip())	
			full_text = full_text + "\n" + t

st.write(full_text)
    
