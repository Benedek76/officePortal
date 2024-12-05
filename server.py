from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from config import Config
from app.models import db, User, Contact
import bcrypt
import os
from werkzeug.utils import secure_filename
from app.compare import compare_documents
import magic
from functools import wraps
from app.compare import read_docx, read_pdf, compare_documents
from weasyprint import HTML
import io
import PyPDF2


app = Flask(__name__)

# Root of the project
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# UPLOAD_FOLDER absolut path
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'uploads')

# Let's check if the UPLOAD_FOLDER exists, and if not, let's create it.
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])





# Loading Flask configuration from config.py
app.config.from_object(Config)


# Initialization of the database
db.init_app(app)


# **Create the login_required decorator here!**
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:  # If 'user_id' is not in the session, redirect the user to the login page.
            flash('Please log in to access!', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

## Connection test
# @app.route('/')
# def index():
#     try:
#         users = User.query.all()
#         return f"Connection ok, {len(users)} user is exist."
#     except Exception as e:
#         return f"Connection failed, issue: {str(e)}"


@app.route("/<string:page_name>")
def html_page(page_name):
    # Tiltott oldalak, amelyeket nem lehet közvetlenül elérni
    restricted_pages = ['convert.html', 'compare.html']

    # Ha valaki közvetlenül akarja elérni ezeket az oldalakat, átirányítjuk a login oldalra
    if page_name in restricted_pages:
        flash("Direct access to this page is not allowed!", "danger")
        return redirect(url_for('login'))

    # Alapértelmezés szerint a sablonok betöltése
    if not page_name.endswith(".html"):
        page_name += ".html"
    return render_template(page_name)


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # User searching in the database
        user = User.query.filter_by(username=username).first()

        if not user:
            flash('User not found!', 'danger')
            return redirect(url_for('login'))

        # Check the password by bcrypt.
        if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            # Saving user data to the session
            session['user_id'] = user.id
            session['username'] = username
            flash('Login successful!', 'success')

            # Clearing flash messages after redirect
            session.pop('_flashes', None)
            return redirect(url_for('compare'))
        else:
            flash('Wrong password!', 'danger')

    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    # if request.method == 'POST'
    session.clear()  # Clearing all session data
    flash('You have successfully logged out!', 'success')
    return redirect(url_for('login'))


# Cache-invalidation function
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Files compare:
app.config['UPLOAD_FOLDER'] = './uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/compare', methods=['GET', 'POST'])
@login_required  # Here we add the login_required decorator.
def compare():
    username = session.get('username')  # We read the user's name from the session.
    if request.method == 'POST':
        # Let's check if both files are uploaded.
        if 'file1' not in request.files or 'file2' not in request.files:
            flash('Both files must be uploaded!', 'danger')
            return redirect(request.url)

        file1 = request.files['file1']
        file2 = request.files['file2']

        if file1.filename == '' or file2.filename == '':
            flash('No file selected!', 'danger')
            return redirect(request.url)

        # Saving a secure filename
        filename1 = secure_filename(file1.filename)
        filename2 = secure_filename(file2.filename)
        file1_path = os.path.join(app.config['UPLOAD_FOLDER'], filename1)
        file2_path = os.path.join(app.config['UPLOAD_FOLDER'], filename2)

        # Save the files
        file1.save(file1_path)
        file2.save(file2_path)

        # Reading the contents of files
        pdf_content = read_pdf(file1_path)
        docx_content = read_docx(file2_path)

        # Let's check the actual type of the files using the magic module."
        mime_type1 = magic.from_file(file1_path, mime=True)
        mime_type2 = magic.from_file(file2_path, mime=True)

        print(f"file1 MIME type: {mime_type1}")
        print(f"file2 MIME type: {mime_type2}")

        # Check: the first file should be a PDF, and the second should be a DOCX."
        if mime_type1 != 'application/pdf':
            flash('The first file must be a PDF!', 'danger')
            os.remove(file1_path)
            os.remove(file2_path)
            return redirect(request.url)

        if mime_type2 != 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            flash('The first file must be a DOCX!', 'danger')
            os.remove(file1_path)
            os.remove(file2_path)
            return redirect(request.url)

        # Comparing files if the file formats are correct.
        result = compare_documents(filename1, filename2)
        return render_template('compare_result.html', result=result, docx_content=docx_content, username=username)

    return render_template('compare.html', username=username)


@app.route('/convert')
@login_required  # Here we add the login_required decorator.
def convert():
    username = session.get('username')  # We read the user's name from the session.
    return render_template('convert.html', username=username)


@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    data = request.get_json()
    html_content = data.get('content')

    # Generating PDF from HTML using WeasyPrint.
    pdf_file = HTML(string=html_content).write_pdf()

    # Returning the PDF as a download.
    return send_file(
        io.BytesIO(pdf_file),
        mimetype='application/pdf',
        as_attachment=True,
        download_name='converted_content.pdf'
    )


@app.route('/watermark', methods=['GET', 'POST'])
# @login_required  # If it is need
def watermark():
    username = session.get('username')

    # The watermarking process runs in the case of a POST request.
    if request.method == 'POST':
        print("POST request received for watermarking")

        # Check, that the uploaded file is exist
        if 'file' not in request.files:
            flash('No file part')
            print("No file part found in request")
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file for watermarking!', 'danger')
            print("File was not selected")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            print(f"File saved at {file_path}")

            # Path of watermark
            watermark_path = os.path.join(BASE_DIR, 'static/assets/images/wtr.pdf')
            if not os.path.exists(watermark_path):
                flash("Watermark file not found.")
                print("Watermark file not found at specified path")
                return redirect(request.url)

            # Add watermark to the PDF
            with open(file_path, 'rb') as pdf_file, open(watermark_path, 'rb') as watermark_file:
                template = PyPDF2.PdfReader(pdf_file)
                watermark = PyPDF2.PdfReader(watermark_file)
                output = PyPDF2.PdfWriter()

                for page in template.pages:
                    page.merge_page(watermark.pages[0])
                    output.add_page(page)
                print("Watermark added to each page")

                # Sorting resoult in the memory
                watermarked_pdf = io.BytesIO()
                output.write(watermarked_pdf)
                watermarked_pdf.seek(0)

            # Returning to the browser for download.
            print("Sending watermarked PDF for download")
            return send_file(
                watermarked_pdf,
                as_attachment=True,
                download_name='watermarked_output.pdf',
                mimetype='application/pdf'
            )

        flash('Allowed file type is PDF only')
        print("Uploaded file type is not PDF")
        return redirect(request.url)

    # In the case of a GET request, we display the form.
    return render_template('compare.html', username=username)



@app.route('/contacts', methods=['GET', 'POST'])
@login_required
def phonebook():
    username = session.get('username')
    # Ha keresést hajtanak végre (POST kérés)
    if request.method == 'POST':
        search_query = request.form.get('search')  # Retrieving the search query from the form.

        # We query the contacts table based on the search query.
        contacts = Contact.query.filter(
            Contact.id.ilike(f'%{search_query}%') |
            Contact.dept_name.ilike(f'%{search_query}%') |
            Contact.name.ilike(f'%{search_query}%') |
            Contact.dept.ilike(f'%{search_query}%') |
            Contact.number.ilike(f'%{search_query}%') |
            Contact.extension.ilike(f'%{search_query}%')  |
            Contact.email.ilike(f'%{search_query}%')
        ).all()

    else:
        # If there is no search query, display all contacts
        contacts = Contact.query.all()

    return render_template('compare.html', username=username, contacts=contacts)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Creating database if necessery.
    app.run(debug=True)  # Debug mode.



