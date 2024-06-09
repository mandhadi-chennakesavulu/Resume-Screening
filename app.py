import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from docx import Document
from dotenv import load_dotenv
import time
import json  # Import json for parsing

load_dotenv()  # Load all our environment variables

genai.configure(api_key="AIzaSyB_MfpqTjenjmCAqczJ0eoRvKiyMXxRVFM")  # Replace with your actual API key

# Function to instantiate model and get response
def get_gemini_response(input):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(input)
    return response.text

# Function to extract text from PDF
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page_n in range(len(reader.pages)):
        page = reader.pages[page_n]
        text += str(page.extract_text())
    return text

# Function to extract text from DOCX
def input_docx_text(uploaded_file):
    doc = Document(uploaded_file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

# Prompt template
input_prompt = """
Hey act like a skilled or very experienced ATS (Application Tracking System)
with a deep understanding of tech field, software engineering, data science, data analyst
and bit data engineer. Your task is to evaluate the resume based on the given job description.
You must consider the job market is very competitive and you should provide best assistance
for improving the resumes. Assign the percentage matching based on JD (Job Description)
and the missing keywords with high accuracy.

I want the response in json structure like
{
    "JD Match": "%",
    "Missing Keywords": [],
    "Profile Summary": ""
}
"""

# Create folders if they don't exist
if not os.path.exists('Suitable'):
    os.makedirs('Suitable')
if not os.path.exists('Unsuitable'):
    os.makedirs('Unsuitable')

# Streamlit app
st.title("Resume Screening Software (ATS)")
st.subheader("Match Your Resume Against the Job Description")
jd = st.text_area("Paste the Job Description")
uploaded_files = st.file_uploader("Upload Resumes", type=["pdf", "docx"], accept_multiple_files=True, help="Please upload the PDF or DOCX")

submit = st.button("Submit")

if submit:
    if uploaded_files:
        for uploaded_file in uploaded_files:
            # Extract text based on file type
            if uploaded_file.type == "application/pdf":
                text = input_pdf_text(uploaded_file)
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                text = input_docx_text(uploaded_file)
            
            # Generate AI response
            response_text = get_gemini_response([input_prompt, "Job Description\n" + jd, "Resume\n" + text])

            # Progress bar simulation
            bar = st.progress(0)
            for percent in range(50, 101, 10):
                time.sleep(0.3)  # Simulate processing time
                bar.progress(percent)
            
            # Handle JSON parsing errors
            try:
                response = json.loads(response_text.replace('\n', ''))  # Handle JSON parsing
                st.json(response)
                
                # Extract JD match percentage and determine folder
                match_percentage = float(response.get("JD Match", "0").replace("%", ""))
                
                # Save to appropriate folder based on match percentage
                filename = uploaded_file.name
                if match_percentage >= 60:  # Assuming 60% as the threshold for suitability
                    folder = "Suitable"
                else:
                    folder = "Unsuitable"
                
                # Write file to appropriate folder
                with open(os.path.join(folder, filename), "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                st.write(f"Resume '{filename}' saved to '{folder}' folder.")
            except json.JSONDecodeError as e:
                st.error(f"Error parsing response: {str(e)}")
                st.error("Response text:")
                st.code(response_text)
