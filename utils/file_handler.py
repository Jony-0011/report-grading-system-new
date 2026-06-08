import os
import tempfile
from core.parser import parse_document

def save_uploaded_file(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.type.split('/')[-1]}") as f:
        f.write(uploaded_file.getbuffer())
        return f.name

def get_file_type(file_name):
    lower_name = file_name.lower()
    if lower_name.endswith('.docx'):
        return 'docx'
    elif lower_name.endswith('.pdf'):
        return 'pdf'
    else:
        return None

def process_uploaded_files(uploaded_files):
    results = []
    
    for uploaded_file in uploaded_files:
        file_type = get_file_type(uploaded_file.name)
        if not file_type:
            results.append({
                'name': uploaded_file.name,
                'success': False,
                'error': '不支持的文件格式'
            })
            continue
        
        try:
            temp_path = save_uploaded_file(uploaded_file)
            parsed_data = parse_document(temp_path, file_type)
            os.unlink(temp_path)
            
            results.append({
                'name': uploaded_file.name,
                'success': True,
                'data': parsed_data,
                'type': file_type
            })
        except Exception as e:
            results.append({
                'name': uploaded_file.name,
                'success': False,
                'error': str(e)
            })
    
    return results