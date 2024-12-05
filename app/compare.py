from difflib import SequenceMatcher
import docx
import PyPDF2
import os


# Reading a DOCX file
def read_docx(file_path):
    doc = docx.Document(file_path)
    text = []
    for paragraph in doc.paragraphs:
        text.append(paragraph.text)
    return '\n'.join(text)


# Reading a PDF file with artificial lines.
def read_pdf(file_path):
    text = []
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            extracted_text = page.extract_text()

            # Splitting extracted text into lines – adding artificial line breaks.
            if extracted_text:
                # We put every sentence on a new line to simulate PDF lines.
                lines = extracted_text.split('. ')  # Line break after a period.
                for line in lines:
                    text.append(line.strip())  # We are removing unnecessary spaces.
    return '\n'.join(text)


# Highlighting inline differences, common parts in green, differences in red.
def highlight_differences(seq1, seq2):
    matcher = SequenceMatcher(None, seq1, seq2)
    output = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            # Common parts in green
            output.append(f'<span style="color: green;">{seq1[i1:i2]}</span>')
        elif tag in ['replace', 'delete', 'insert']:
            # Differences in red
            output.append(f'<span style="color: red;">{seq1[i1:i2]}</span>')
            output.append(f'<span style="color: red;">{seq2[j1:j2]}</span>')
    return ''.join(output)


# Comparing documents line by line
def compare_documents(file1, file2):
    # Reading PDF and DOCX files
    pdf_text = read_pdf(os.path.join('./uploads', file1))
    docx_text = read_docx(os.path.join('./uploads', file2))

    pdf_lines = pdf_text.splitlines()
    docx_lines = docx_text.splitlines()

    html_diff = []

    # We compare the two documents line by line.
    for i in range(max(len(docx_lines), len(pdf_lines))):
        if i < len(docx_lines) and i < len(pdf_lines):
            if docx_lines[i] != pdf_lines[i]:
                # If the line differs, we look for differences within the line.
                highlighted_line = highlight_differences(docx_lines[i], pdf_lines[i])
                html_diff.append(f'<div>{highlighted_line}</div>')
            else:
                # If the rows are completely identical, we mark them with green text.
                html_diff.append(
                    f'<div style="background-color: yellow;"><span style="color: green;">{docx_lines[i]}</span></div>')
        elif i < len(docx_lines):
            # If a line exists in the DOCX file but not in the PDF, highlight the entire line in red.
            html_diff.append(f'<div><span style="color: red;">{docx_lines[i]}</span></div>')
        elif i < len(pdf_lines):
            # If a line exists in the PDF file but not in the DOCX file, the entire line should be in red.
            html_diff.append(f'<div><span style="color: red;">{pdf_lines[i]}</span></div>')

    return '<br>'.join(html_diff)


