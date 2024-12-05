# Hype Office Portal

Hype Office Portal is a comprehensive Flask-based platform designed to streamline document management and office tasks. The portal integrates multiple applications, making it a versatile solution for office workflows.

## Key Applications

1. **Document Comparison**  
   Upload a PDF and a DOCX file, and compare their content line by line. Highlighted differences make it easy to spot changes or inconsistencies.

2. **PDF Price Proposal**  
   Generate professional price proposals directly in PDF format from your input data.

3. **PDF Watermarking**  
   Apply custom watermarks to PDF files. Ideal for branding, confidentiality, or version control.

4. **Phonebook with Search Engine**  
   An integrated phonebook with a powerful search engine that allows users to find contacts by name, department, email, and more.

---


### Key Files
- **`server.py`:** The main entry point for the Flask application.
- **`config.py`:** Application configuration, including database settings and secret keys.
- **`models.py`:** Defines database models for `User` and `Contact`.
- **`compare.py`:** Contains the logic for comparing PDF and DOCX documents.
- **`templates/`:** Contains HTML templates for rendering the UI.
- **`static/`:** Stores static assets like CSS and images.

---

## Installation and Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/officePortal.git
cd officePortal
```

### 2. Create a Virtual Environment
python3 -m venv venv
source venv/bin/activate


### 3. Install Dependencies
pip install -r requirements.txt


### 4. Set Up the Database
Ensure MySQL is installed and running.
Create a database named compare.
Update config.py with your MySQL credentials.


### 5. Initialize the Database
flask shell
from app.models import db
db.create_all()
exit()


### 6. Run the Application
flask run


Usage
Login
Navigate to http://127.0.0.1:5000 and log in with your credentials.

Applications
Document Comparison: Upload a PDF and DOCX file to view highlighted differences.
PDF Price Proposal: Generate PDF documents for price proposals.
PDF Watermarking: Apply watermarks to uploaded PDFs.
Phonebook Search: Search for contacts using keywords.
Dependencies
This project relies on the following Python packages:

Flask Framework: Backend framework for the application.
Flask-SQLAlchemy: For database integration.
PyPDF2: PDF reading and watermarking.
python-docx: DOCX file handling.
bcrypt: Secure password hashing.
WeasyPrint: HTML to PDF conversion.
Magic: MIME type validation.
For a complete list, see requirements.txt.



