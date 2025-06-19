# import hashlib
# import pandas as pd #type:ignore
# from langchain_core.documents import Document #type:ignore

# def get_file_hash(uploaded_file):
#     """Generate MD5 hash of file content."""
#     return hashlib.md5(uploaded_file.getvalue()).hexdigest()

# def validate_excel(file):
#     """Check if file is Excel."""
#     return file.name.endswith(('.xlsx', '.xls'))

# def process_excel(uploaded_file):
#     """Convert Excel to cleaned DataFrame."""
#     df = pd.read_excel(uploaded_file)
#     df = df.dropna(how='all')
#     df = df[~df.apply(lambda row: all(str(cell).strip() == '' for cell in row), axis=1)]
    
#     # RACI code mapping
#     raci_mapping = {'R': 'Responsible', 'A': 'Accountable', 
#                    'C': 'Consulted', 'I': 'Informed'}
#     df = df.map(lambda x: raci_mapping.get(str(x).strip(), x))
#     df = df.fillna('')
    
#     # Convert to LangChain Documents
#     documents = [
#         Document(
#             page_content=" | ".join(row.astype(str)),
#             metadata={"source": uploaded_file.name, "row": idx}
#         )
#         for idx, row in df.iterrows()
#     ]
#     return documents






import hashlib
import pandas as pd
from langchain_core.documents import Document
from typing import List, Union
from document_parser import parse_pdf, parse_docx

def get_file_hash(uploaded_file) -> str:
    """Generate MD5 hash of file content."""
    return hashlib.md5(uploaded_file.getvalue()).hexdigest()


def validate_file(file) -> bool:
    """Check if file is of supported format."""
    return file.name.lower().endswith(('.xlsx', '.xls', '.pdf', '.docx', '.doc'))


def process_excel(uploaded_file) -> List[Document]:
    """Convert Excel to Documents with first row as headers."""
    try:
        df = pd.read_excel(uploaded_file)
        if not df.empty:
            # Use first row as headers and reset the DataFrame
            df.columns = df.iloc[0]
            df = df[1:].reset_index(drop=True)
            df = df.dropna(how='all')
            
            documents = [
                Document(
                    page_content=" | ".join(row.astype(str)),
                    metadata={
                        "source": uploaded_file.name,
                        "row": idx,
                        "type": "excel"
                    }
                )
                for idx, row in df.iterrows()
            ]
            return documents
        return []
    except Exception as e:
        raise Exception(f"Excel processing error: {str(e)}")
    

def process_file(uploaded_file) -> List[Document]:
    """Process file based on its type."""
    lower_name = uploaded_file.name.lower()
    if lower_name.endswith(('.xlsx', '.xls')):
        return process_excel(uploaded_file)
    elif lower_name.endswith('.pdf'):
        return parse_pdf(uploaded_file)
    elif lower_name.endswith('.docx'):
        return parse_docx(uploaded_file)
    elif lower_name.endswith('.doc'):
        return parse_doc(uploaded_file)
    return []



