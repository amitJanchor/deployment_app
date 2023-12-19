import streamlit as st
import PyPDF2
from io import BytesIO
import openai

st.write('Hello User!')
file_type = st.text_input('Choose source type [ pdf , audio ]:')
max_len_str = st.text_input('Chunk size:')
if max_len_str:
	max_len = int(max_len_str)

file_title = st.text_input('File title:')

model_option = st.selectbox(
    'Which model would you like to use?',
    ('gpt-4-1106-preview', 'gpt-3.5-turbo-1106'))

uploaded_file = st.file_uploader("Choose a PDF file:", type="pdf")


full_text = ''


def Note_maker(model_option, t_list, api_key):
	client = openai.OpenAI(api_key=api_key)
	st.write(1,'/',len(t_list),'\n')
	message_list = [
	    {
	      "role": "system",
	      "content": "Generate detailed call notes of the conversation for an investment firm.\nGenerate notes pointwise under each of all the Important Sections, (Convert all text numbers to numbers, Include all important information and numbers.)\n"
	    },
	    {
	      "role": "user",
	      "content": t_list[0]
	    }
	  ]
	
	response = client.chat.completions.create(
	  model=model_option,
	  messages=message_list,
	  temperature=1.5,
	  max_tokens=4096,
	  top_p=0.6,
	  frequency_penalty=0,
	  presence_penalty=0
	)
	
	Notes = []
	
	for i in range(1,len(t_list)):
		
	    st.write(i+1,'/',len(t_list),'\n')
		
	    Notes.append(response.choices[0].message.content)
	    
	    message_list.append({
	      "role": "assistant",
	      "content": response.choices[0].message.content
	    })
	    
	    stock = "This is continuation of the transcript.\nGenerate call notes pointwise for an investment firm under each of all the Important Sections, (Convert all text numbers to numbers, Include all important information and numbers.)\n"
	    cont = stock + t_list[i]
	    
	    message_list.append({
	      "role": "user",
	      "content": cont
	    })
	    
	    response = client.chat.completions.create(
	      model=model_option,
	      messages=message_list,
	      temperature=1.5,
	      max_tokens=4096,
	      top_p=0.6,
	      frequency_penalty=0,
	      presence_penalty=0
	    )
	    
	Notes.append(response.choices[0].message.content)

	Notes_Final = ''

	for i in Notes:
	    Notes_Final = Notes_Final + i + '\n\n'
	
	return Notes_Final

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

		t_list = []

		words_per_segment = max_len
		words = Transcript_final.split()
		
		for i in range(0, len(words), words_per_segment):
		    segment = " ".join(words[i:i + words_per_segment])
		    t_list.append(segment)

		Notes_final_ans = Note_maker(model_option, t_list, st.secrets["openai_key"])

		file_actual_name = file_title + '.txt'
		st.download_button('Download Call Notes', Notes_final_ans, file_name=file_actual_name)
