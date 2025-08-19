from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import docx2txt
import PyPDF2
import re

# Load the model and tokenizer 
def load_model_and_tokenizer(summary_type):
    if summary_type == "abstractive":
        tokenizer = AutoTokenizer.from_pretrained("Pavan48/bart-base-cnn-dailymail_256")
        model = AutoModelForSeq2SeqLM.from_pretrained("Pavan48/bart-base-cnn-dailymail_256")
    elif summary_type == "highlights":
        tokenizer = AutoTokenizer.from_pretrained("Pavan48/bart-base-cnn-dailymail-highlights-256")
        model = AutoModelForSeq2SeqLM.from_pretrained("Pavan48/bart-base-cnn-dailymail-highlights-256")
    return tokenizer, model

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
    if files and 'file' in files:
        file = files['file']
        filename = file.filename.lower()
        
        if filename.endswith('.pdf'):
            text = extract_text_from_pdf(file)
        elif filename.endswith('.docx'):
            text = extract_text_from_docx(file)
        elif filename.endswith('.txt'):
            text = extract_text_from_txt(file)
    
    text = re.sub(r'(?<=[.!?])\s+', ' ', text)
    return text

# Function to split text into chunks
def chunk_text(text, chunk_size=512, chunk_overlap=0):
    sentences = re.split(r'(?<=[!?]) +', text)
    chunks = []
    current_chunk = []

    for sentence in sentences:
        current_chunk.append(sentence)
        if len(" ".join(current_chunk).split()) >= chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = current_chunk[-chunk_overlap:]

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def generate_summary(text, tokenizer, model, summary_type="abstractive"):
    input_ids = tokenizer.encode(text, return_tensors="pt", max_length=512, truncation=True)

    if summary_type == "highlights":
        summary_ids = model.generate(input_ids, max_length=256, min_length=32, do_sample=True,
                                    length_penalty=2.0, num_beams=4, no_repeat_ngram_size=3,
                                    temperature=0.7, top_k=100, top_p=0.95)
    elif summary_type == "abstractive":
        summary_ids = model.generate(input_ids, do_sample=True,
                                    bos_token_id=model.config.bos_token_id,
                                    eos_token_id=model.config.eos_token_id,
                                    length_penalty=2.0, repetition_penalty=1.2,
                                    max_length=256, min_length=32, num_beams=4,
                                    temperature=0.7, no_repeat_ngram_size=3,
                                    top_k=100, top_p=0.95)

    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

def summarize(text, summary_type="abstractive", files=None):
    text = process_input(text, files)
    tokenizer, model = load_model_and_tokenizer(summary_type)

    input_length = len(tokenizer.encode(text, truncation=True))
    
    if input_length < 512:
        return generate_summary(text, tokenizer, model, summary_type)
    else:
        chunks = chunk_text(text)
        summaries = [generate_summary(chunk, tokenizer, model, summary_type) for chunk in chunks]
        return " ".join(summaries)