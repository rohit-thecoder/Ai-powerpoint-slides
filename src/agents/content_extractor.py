import os
import pandas as pd
import fitz  # PyMuPDF
from llama_index.core import Document as LlamaDocument  # Aliased to prevent collision
from llama_index.core import SimpleDirectoryReader
from docx import Document as DocxDocument  # Added explicit python-docx import

class ContentExtractor:
    def __init__(self, directory="data/"):
        self.directory = directory

    def extract_text_from_txt(self, file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read() 

    def extract_text_from_pdf(self, file_path):
        text = ""
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text("text") + "\n"
        return text    

    def extract_text_from_docx(self, file_path):
       
        doc = DocxDocument(file_path)
        return "\n".join([para.text for para in doc.paragraphs])

    def extract_text_from_csv(self, file_path):
        df = pd.read_csv(file_path)
        return df.to_string()

    def extract_from_file(self, file_path):
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()  
        if ext == ".txt":
            return self.extract_text_from_txt(file_path)
        elif ext == ".pdf":
            return self.extract_text_from_pdf(file_path)
        elif ext == ".docx":
            return self.extract_text_from_docx(file_path)
        elif ext == ".csv":
            return self.extract_text_from_csv(file_path)
        else:
            raise ValueError(f"Unsupported File Format: {ext}")

    def extract_from_directory(self):
        extracted_data = {}
        if not os.path.exists(self.directory):
            raise FileNotFoundError(f"Directory Not Found {self.directory}")

        for filename in os.listdir(self.directory):
            file_path = os.path.join(self.directory, filename)
            if os.path.isfile(file_path):
                try:
                    extracted_data[filename] = self.extract_from_file(file_path)
                except Exception as e:
                    print(f"Error Processing {filename}: {e}")
        return extracted_data                

# Fixed: Moved completely outside the class body (Zero Indentation)
if __name__ == "__main__":
    # Optional: Quick check to create data folder if it doesn't exist so it won't crash
    if not os.path.exists("data"):
        os.makedirs("data")
        print("Created empty 'data/' directory. Place your files inside it.")

    extractor = ContentExtractor(directory="data/")
    extracted_content = extractor.extract_from_directory()

    for file, content in extracted_content.items():
        print(f"\n Extracted content from {file}: \n {content[:2000]}....\n")
