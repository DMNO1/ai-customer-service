"""
Document Parser
处理PDF、Word等文档的解析和文本提取。
"""

import os
from typing import List, Optional
from PyPDF2 import PdfReader
from docx import Document

class DocParser:
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)
    
    def parse_pdf(self, file_path: str) -> str:
        """
        解析PDF文件并返回文本内容。
        
        Args:
            file_path: PDF文件的路径。
            
        Returns:
            提取的文本内容。
        """
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"Error parsing PDF {file_path}: {e}")
            return ""
    
    def parse_docx(self, file_path: str) -> str:
        """
        解析Word (.docx) 文件并返回文本内容。
        
        Args:
            file_path: .docx文件的路径。
            
        Returns:
            提取的文本内容。
        """
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            print(f"Error parsing DOCX {file_path}: {e}")
            return ""
    
    def parse_document(self, file_path: str) -> Optional[str]:
        """
        根据文件扩展名自动选择解析器。
        
        Args:
            file_path: 文档文件的路径。
            
        Returns:
            提取的文本内容，如果无法解析则返回None。
        """
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        if ext == ".pdf":
            return self.parse_pdf(file_path)
        elif ext == ".docx":
            return self.parse_docx(file_path)
        else:
            print(f"Unsupported file type: {ext}")
            return None

# 用于测试的主函数
if __name__ == "__main__":
    parser = DocParser()
    # 注意：此测试需要在实际环境中提供示例文件
    # sample_pdf = "sample.pdf"
    # sample_docx = "sample.docx"
    # print(parser.parse_document(sample_pdf))
    # print(parser.parse_document(sample_docx))