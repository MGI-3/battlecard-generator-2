import os
import tempfile
from typing import Dict, List
import PyPDF2
import docx
import textract

class DocumentProcessor:
    def __init__(self):
        self.supported_extensions = {
            '.pdf': self._process_pdf,
            '.docx': self._process_docx,
            '.doc': self._process_doc,
            '.txt': self._process_txt,
            '.rtf': self._process_textract,
            '.odt': self._process_textract,
        }

    def process_file(self, file_path: str) -> str:
        """Process a file and extract its text content."""
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        if ext not in self.supported_extensions:
            raise ValueError(f"Unsupported file type: {ext}")
        
        processor = self.supported_extensions[ext]
        return processor(file_path)

    def _process_pdf(self, file_path: str) -> str:
        """Extract text from a PDF file."""
        text = ""
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text

    def _process_docx(self, file_path: str) -> str:
        """Extract text from a DOCX file."""
        doc = docx.Document(file_path)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text

    def _process_doc(self, file_path: str) -> str:
        """Extract text from a DOC file using textract."""
        return self._process_textract(file_path)

    def _process_txt(self, file_path: str) -> str:
        """Extract text from a TXT file."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            return file.read()

    def _process_textract(self, file_path: str) -> str:
        """Extract text using textract for various formats."""
        try:
            text = textract.process(file_path).decode('utf-8')
            return text
        except Exception as e:
            print(f"Error extracting text with textract: {e}")
            return ""

    def process_multiple_files(self, file_paths: List[str]) -> Dict[str, str]:
        """Process multiple files and return their text content."""
        results = {}
        for file_path in file_paths:
            try:
                file_name = os.path.basename(file_path)
                text = self.process_file(file_path)
                results[file_name] = text
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
                results[file_name] = f"Error: {str(e)}"
        return results