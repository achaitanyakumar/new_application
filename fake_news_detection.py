import re
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from PyPDF2 import PdfReader
import docx2txt

# Load the model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("Pavan48/fake_news_detection_roberta")
model = AutoModelForSequenceClassification.from_pretrained("Pavan48/fake_news_detection_roberta")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Function to extract text from a PDF file
def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Function to extract text from a DOCX file using docx2txt
def extract_text_from_docx(file):
    text = docx2txt.process(file)
    return text

def extract_text_from_file(file):
    if file.filename.endswith('.pdf'):
        return extract_text_from_pdf(file)
    elif file.filename.endswith('.docx'):
        return extract_text_from_docx(file)
    else:
        return file.read().decode("utf-8") 

def infer_fake_news(title, text):
    # Combine title and text into one string for the model input
    combined_text = title + " " + text
    inputs = tokenizer(combined_text, return_tensors="pt", padding="max_length", truncation=True, max_length=512)
    input_ids = inputs["input_ids"].to(device)
    attention_mask = inputs["attention_mask"].to(device)

    with torch.no_grad():
        outputs = model(input_ids, attention_mask=attention_mask)
    
    logits = outputs.logits
    predicted_class = torch.argmax(logits, dim=-1).item()
    
    label = "Real" if predicted_class == 1 else "Fake"
    return label

def detect_fake_news(input_title, input_text, file=None):
    if file and file.filename:
        input_text = extract_text_from_file(file)
        input_title = input_text.split('\n')[0] 
        input_text = ' '.join(input_text.split('\n')[1:])  

    return infer_fake_news(input_title, input_text)
