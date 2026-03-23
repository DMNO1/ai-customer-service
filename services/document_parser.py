"""
Document Parser Service for AI Customer Service System
Handles parsing of various document formats (PDF, DOCX, TXT)
"""

import logging
from typing import List, Optional
from pathlib import Path
from PyPDF2 import PdfReader
from pdfplumber import open as pdf_open
import docx
from io import StringIO

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentParser:
    def __init__(self):
        logger.info("DocumentParser initialized successfully")

    def parse_pdf(self, file_path: str) -> str:
        """
        Parse PDF file and extract text content
        :param file_path: Path to the PDF file
        :return: Extracted text content
        """
        try:
            logger.info(f"Parsing PDF file: {file_path}")
            
            text = ""
            with pdf_open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
            
            logger.info(f"Successfully parsed PDF file: {file_path}")
            return text
            
        except Exception as e:
            logger.error(f"Error parsing PDF file {file_path}: {str(e)}")
            # Fallback to PyPDF2
            try:
                logger.info("Trying fallback method with PyPDF2")
                text = ""
                reader = PdfReader(file_path)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                
                logger.info(f"Successfully parsed PDF file using fallback method: {file_path}")
                return text
            except Exception as fallback_error:
                logger.error(f"Fallback method also failed for PDF file {file_path}: {str(fallback_error)}")
                raise fallback_error

    def parse_docx(self, file_path: str) -> str:
        """
        Parse DOCX file and extract text content
        :param file_path: Path to the DOCX file
        :return: Extracted text content
        """
        try:
            logger.info(f"Parsing DOCX file: {file_path}")
            
            doc = docx.Document(file_path)
            paragraphs = [paragraph.text for paragraph in doc.paragraphs]
            text = "\n".join(paragraphs)
            
            logger.info(f"Successfully parsed DOCX file: {file_path}")
            return text
            
        except Exception as e:
            logger.error(f"Error parsing DOCX file {file_path}: {str(e)}")
            raise e

    def parse_txt(self, file_path: str) -> str:
        """
        Parse TXT file and extract text content
        :param file_path: Path to the TXT file
        :return: Extracted text content
        """
        try:
            logger.info(f"Parsing TXT file: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            logger.info(f"Successfully parsed TXT file: {file_path}")
            return text
            
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                logger.info("UTF-8 failed, trying with GBK encoding")
                with open(file_path, 'r', encoding='gbk') as file:
                    text = file.read()
                
                logger.info(f"Successfully parsed TXT file with GBK encoding: {file_path}")
                return text
            except Exception as e:
                logger.error(f"Error parsing TXT file {file_path}: {str(e)}")
                raise e
        except Exception as e:
            logger.error(f"Error parsing TXT file {file_path}: {str(e)}")
            raise e

    def parse_document(self, file_path: str) -> str:
        """
        Universal document parser that detects file type and uses appropriate parser
        :param file_path: Path to the document file
        :return: Extracted text content
        """
        file_path_obj = Path(file_path)
        file_ext = file_path_obj.suffix.lower()
        
        if file_ext == '.pdf':
            return self.parse_pdf(str(file_path_obj))
        elif file_ext in ['.docx', '.doc']:
            return self.parse_docx(str(file_path_obj))
        elif file_ext == '.txt':
            return self.parse_txt(str(file_path_obj))
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")

# Example usage and testing
if __name__ == "__main__":
    parser = DocumentParser()
    
    # Example usage (uncomment to test with actual files):
    # content = parser.parse_document("path/to/your/document.pdf")
    # print(content)