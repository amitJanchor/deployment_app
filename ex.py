import streamlit as st
import PyPDF2
from io import BytesIO
import openai
import pydub

st.write('Hello User!')

file_type = st.selectbox(
    'Choose source type [ pdf , audio ]:',
    ('pdf', 'audio'))

max_len_str = st.text_input('Chunk size:')
if max_len_str:
	max_len = int(max_len_str)

file_title = st.text_input('File title:')

model_option = st.selectbox(
    'Which model would you like to use?',
    ('gpt-4-1106-preview', 'gpt-3.5-turbo-1106'))

uploaded_file = st.file_uploader("Choose a PDF file:", type=["pdf","mp3","m4a","wav"], accept_multiple_files=True)


full_text = ''


def Note_maker(model_option, t_list, api_key):
	client = openai.OpenAI(api_key=api_key)
	st.write('[Note Making] Progress update:','\n')
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

		if (model_option=='gpt-3.5-turbo-1106'):
			try:
				del message_list[2:4]
			except:
				pass
		elif (model_option=='gpt-4-1106-preview'):
			try:
				if len(message_list)>=8:
					del message_list[2:4]
			except:
				pass
		
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

	st.write('Process done!','\n')
	return Notes_Final

def pdf_processor(uploaded_file, max_len, full_text):
	for i in range(len(uploaded_file)):
		reader = PyPDF2.PdfReader(uploaded_file[i])
				
		for i in range(len(reader.pages)):    
			p = reader.pages[i]
			t = p.extract_text()
				
			full_text = full_text + "\n" + t
	
	Transcript_final = full_text
	
	t_list = []
	
	words_per_segment = max_len
	words = Transcript_final.split()
	
	for i in range(0, len(words), words_per_segment):
		segment = " ".join(words[i:i + words_per_segment])
		t_list.append(segment)

	return t_list	

def audio_processor(uploaded_file, max_len, string_transcript_audio):
	audio = pydub.AudioSegment.from_file(uploaded_file)
	total_duration = len(audio)
	chunk_length_ms = 60000
	num_chunks = total_duration // chunk_length_ms
	
	client = openai.OpenAI(api_key=st.secrets["openai_key"])
	st.write('[Transcription] Progress update:','\n')
	for i in range(num_chunks):
		st.write(i+1,'/',num_chunks,'\n')
		start_time = i * chunk_length_ms
		end_time = (i + 1) * chunk_length_ms
	
		if end_time > total_duration:
			end_time = total_duration
	
		chunk = audio[start_time:end_time]
		chunk.export(str(i)+".mp3", format="mp3")
	
		with open(str(i)+".mp3",'rb') as audio_file:
			transcript = client.audio.transcriptions.create(
					  model="whisper-1", 
					  file=audio_file, 
					  response_format="text"
					)
			string_transcript_audio = string_transcript_audio + transcript + ' '
	st.write('Transcription Done!','\n')
	Transcript_final = string_transcript_audio
	
	t_list = []
	
	words_per_segment = max_len
	words = Transcript_final.split()
	
	for i in range(0, len(words), words_per_segment):
		segment = " ".join(words[i:i + words_per_segment])
		t_list.append(segment)

	return t_list

if file_type == 'pdf':
	if uploaded_file is not None and len(uploaded_file)!=0:

		t_list = pdf_processor(uploaded_file, max_len, full_text)

		Notes_final_ans = Note_maker(model_option, t_list, st.secrets["openai_key"])

		file_actual_name = file_title + '.txt'
		st.download_button('Download Call Notes', Notes_final_ans, file_name=file_actual_name)

string_transcript_audio=''

if file_type == 'audio':
	if uploaded_file is not None and len(uploaded_file)!=0:

		t_list = audio_processor(uploaded_file[0], max_len, string_transcript_audio)

		Notes_final_ans = Note_maker(model_option, t_list, st.secrets["openai_key"])

		file_actual_name = file_title + '.txt'
		st.download_button('Download Call Notes', Notes_final_ans, file_name=file_actual_name)		
