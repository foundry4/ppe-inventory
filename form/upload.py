from flask import Blueprint, Markup, request, redirect, render_template
from werkzeug.utils import secure_filename
import markdown
import os
import tempfile
from .wiki import wiki_title, nav, style
from .github import commit, pull

upload = Blueprint('upload', __name__)


# Wiki file uploads

@upload.route('/', methods=['GET'])
def redirect_to_form():
    return redirect("/ppe-inventory")

@upload.route('/ppe-inventory', methods=['GET'])
def ppe_inventory_form():
    """ Form to upload images and other files to the wiki. """
    return render_template('ppe-inventory.html' if os.getenv('GITHUB_ACCESS_TOKEN') else 'upload.html', 
        hospital="Hammersmith Hospital"
        )

@upload.route('/upload', methods=['POST'])
def upload_post():
    """ Process an uploaded file, then render a page that contains just the markdown and displays the file. """

    # Process the uploaded file
    upload = request.files.get('file')
    if upload:
        username = request.form.get("username") or os.getenv('GITHUB_USERNAME')
        password = request.form.get("password") or os.getenv('GITHUB_ACCESS_TOKEN')
        filename = secure_filename(upload.filename)
        with tempfile.NamedTemporaryFile(delete=False) as t:
            t.write(upload.read())
            temp = t.name

        # Commit to Github and, if successful, save locally:
        path = os.path.join('uploads', filename)
        print(f'attempting to commit {path} to Github')
        if commit(path, temp, username, password):
            # Render a page to show the upload
            extension = os.path.splitext(filename)[1].lower()
            md_filename = "upload_image.md" if extension in [".jpg", ".jpeg", ".gif", ".png"] else "upload_file.md"
            with open(f"default-pages/{md_filename}") as f:
                content = f.read()
            repo = os.getenv('GITHUB_REPO')
            content = content.replace("{filename}", filename)
            content = content.replace("{repo}", repo)
            md = markdown.markdown(content)
            html = style(md)
            
            return render_template('page.html', 
                wiki_title=wiki_title(),
                title="Upload", 
                path="Upload",
                content=Markup(html), 
                nav=Markup(nav()),
                repo=repo)
        else:
            print('Commit failed?')
    
    # Fallback
    return redirect(request.url)

