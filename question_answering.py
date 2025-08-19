from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import docx2txt
import PyPDF2

# Load model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("Pavan48/flan_t5_small_newsqa")
model = AutoModelForSeq2SeqLM.from_pretrained("Pavan48/flan_t5_small_newsqa")

# Prediction function to get answers from context
def predict_answer(question, context, tokenizer, model, max_length=128):
    input_text = f"question: {question} context: {context}"
    
    inputs = tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True).to('cuda' if torch.cuda.is_available() else 'cpu')

    outputs = model.generate(
        inputs['input_ids'],
        max_length=max_length,
        num_beams=4,
        temperature=0.7,
        do_sample=True,
    )

    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    return answer

# Function to process file inputs
def process_file(file):
    input_text = ""
    filename = file.filename.lower()

    if filename.endswith('.pdf'):
        # Process PDF file
        pdf_reader = PyPDF2.PdfReader(file)
        input_text = " ".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())
    
    elif filename.endswith('.docx'):
        # Process DOCX file
        input_text = docx2txt.process(file)
    
    elif filename.endswith('.txt'):
        # Process TXT file
        input_text = file.read().decode('utf-8')
    
    return input_text

# Function to handle context and question-answering
def ask_question(context, question, files=None):
    input_text = ""

    # Check if a file is uploaded and process accordingly
    if files and 'file' in files and files['file'].filename != '':
        file = files['file']
        input_text = process_file(file)
    
    elif context:
        input_text = context

    # Answer the question if there is valid text
    if input_text and question:
        answer = predict_answer(question, input_text, tokenizer, model)
        return answer

    return "No valid input provided for question answering."
