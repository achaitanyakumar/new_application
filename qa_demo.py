from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import docx2txt
import PyPDF2


tokenizer = AutoTokenizer.from_pretrained("Pavan48/flan_t5_small_newsqa")
model = AutoModelForSeq2SeqLM.from_pretrained("Pavan48/flan_t5_small_newsqa")

# Prediction function
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

def ask_question(text, question, files):
    input_text = ""
    
    if 'file' in files and files['file'].filename != '':
        file = files['file']
        filename = file.filename.lower()
        
        if filename.endswith('.pdf'):
            # Process PDF file
            pdf_reader = PyPDF2.PdfReader(file)
            input_text = " ".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())
        
        elif filename.endswith('.docx'):
            # Process DOCX file
            input_text = docx2txt.process(file)

    else:
        input_text = text

    # Answer the question if there is text
    if input_text and question:
        answer = predict_answer(question, input_text, tokenizer, model)
        return answer
