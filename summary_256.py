from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import docx2txt
import PyPDF2
import re

# Load the fine-tuned summarization model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("Pavan48/bart-base-cnn-dailymail_256")
model = AutoModelForSeq2SeqLM.from_pretrained("Pavan48/bart-base-cnn-dailymail_256")

def extract_text_from_txt(file):
    return file.read().decode("utf-8")

def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_docx(file):
    return docx2txt.process(file)

def process_input(text, files):
    if files and files.get('file'):
        file = files['file']
        filename = file.filename.lower()
        
        if filename.endswith('.pdf'):
            text = extract_text_from_pdf(file)
        elif filename.endswith('.docx'):
            text = extract_text_from_docx(file)
        elif filename.endswith('.txt'):
            text = extract_text_from_txt(file)
    return text

# Function to split text into chunks
def chunk_text(text, chunk_size=512, chunk_overlap=64):
    # Split text into sentences using period (.) as delimiter, assuming each sentence ends with a period
    sentences = re.split(r'(?<=[!?]) +', text)
    
    chunks = []
    current_chunk = []

    for sentence in sentences:
        current_chunk.append(sentence)
        if len(" ".join(current_chunk).split()) >= chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = current_chunk[-chunk_overlap:]  # Overlap the last few sentences

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

def generate_summary(text):
    input_ids = tokenizer.encode(text, return_tensors="pt", max_length=512, truncation=True)
    
    summary_ids = model.generate(input_ids,do_sample=True,
        bos_token_id=model.config.bos_token_id,
    #   eos_token_id=model.config.eos_token_id,
        length_penalty=2.0,
        repetition_penalty=1.2,
        max_length=256,
        min_length=16,
        num_beams=4,
        temperature=0.7,
        no_repeat_ngram_size=3,
#         pad_token_id=tokenizer.pad_token_id,
        top_k=100,
        top_p=0.95,)
    
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

def summarize(text, files=None):
    text = process_input(text, files)
    
    chunks = chunk_text(text)
    summaries = [generate_summary(chunk) for chunk in chunks]
    return " ".join(summaries)
