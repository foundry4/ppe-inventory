from flask import Blueprint, current_app, Markup, request, redirect, render_template, send_from_directory, abort
from werkzeug.utils import secure_filename
from flask_basicauth import BasicAuth
from flask_sslify import SSLify
import markdown
import markdown.extensions.tables
import re
import os

wiki = Blueprint('wiki', __name__)

# Flask routes

# @wiki.route('/', defaults={'path': ''})
# @wiki.route('/<path:path>')
# def catch_all(path):
#     """ Catch-all route 

#     Renders markdown for the requested path, 
#     if a corresponding .md file can be found.

#     TODO: potential misuse of user-supplied path here
#     """

#     # Otherwise, try to render a page
#     print(f'Requested path: {path}')

#     # Locate markdown
#     # Avoid a dodgy path by only taking the filename:
#     page_name = secure_filename(os.path.basename(path).strip('/'))
#     if not path:
#         # Wiki home page
#         page_name = 'Home'
#     print(f'Page name: {page_name}')

#     # Be a bit lenient with capitalisation
#     page_path = case_lenient_markdown(page_name)
#     if not page_path:
#         print(f'Page {page_name} not found.')
#         abort(404)
#     print(f'Markdow file: {page_path}')
    
#     # Render content
#     page_title = menu().get(page_name.lower())
#     print(f'Title for {page_name} is {page_title}')
#     return render(page_name, page_title, page_path)

@wiki.route('/assets/<path:path>')
def govuk_frontend_assets(path):
    """ Fix for Govuk frontend requests. """
    print(f"Fixed govuk path: /assets/{path}")
    return send_from_directory('static/assets', path)

@wiki.route('/uploads/<path:path>')
def uploads(path):
    """ Serve images and other files added to the wiki.   """
    filename = secure_filename(os.path.basename(path))
    directory = os.path.join(os.getcwd(), 'wiki', 'uploads')
    print(f'Serving uploaded file: {filename}')
    return send_from_directory(directory, filename)

@wiki.errorhandler(404)
def page_not_found(e):
    page_name = '404'
    page_path = default_file(f'{page_name}.md')
    print(f'404 markdown: {page_path}')
    return render(page_name, "Page not found", page_path, 400)

@wiki.errorhandler(500)
def internal_server_error(e):
    page_name = '500'
    page_path = default_file(f'{page_name}.md')
    print(f'500 markdown: {page_path}')
    return render(page_name, "Server error", page_path, 500)


# Supporting wiki content

def wiki_title():
    """ Parse the wiki title """
    repo = os.getenv('GITHUB_REPO')
    segments = repo.split('/')
    return segments[len(segments) - 1]

def menu():
    """ Parse sidebar navigation menu links """

    sidebar_file = default_file('_Sidebar.md')
    menu = {'home': "Home"}
    with open(sidebar_file) as sidebar:
        md = sidebar.read()
        # We're looking for: [link & text](relative/url)
        # So: [...non-]...](...non-)...) 
        # Regex: \[([^\]]+)\]\(([^\)]+)\)
        matches = re.findall('\\[([^\\]]+)\\]\\(([^\\)]+)\\)', md)
        for match in matches:
            filename = match[1]
            page_title = match[0]
            menu[filename.lower()] = page_title
    return menu

def nav():
    """ Render navigation markup """

    sidebar_file = default_file('_Sidebar.md')
    with open(sidebar_file) as sidebar:
        md = sidebar.read()
        return style_nav(markdown.markdown(md))


# Helper functions

def case_lenient_markdown(page_name):
    """ Returns a path and filename, being lenient with case 
        and falling back to a default if available. 
    """

    # Find a file in the wiki folder

    original = os.path.join('wiki', f'{page_name}.md')
    if os.path.isfile(original):
        return original
    
    lowercase = os.path.join('wiki', f'{page_name.lower()}.md')
    if os.path.isfile(lowercase):
        return lowercase

    capitalised = os.path.join('wiki', f'{page_name.lower().capitalize()}.md')
    if os.path.isfile(capitalised):
        return capitalised
    
    # Fall back to a default file - we know these names are capitalised

    default = os.path.join('default-pages', page_name.lower().capitalize())
    if os.path.isfile(default):
        return default
    
    return None

def default_file(filename):
    """ Returns a path and filename, falling back to a default if available. 
    """

    wiki_file = os.path.join('wiki', filename)
    if os.path.isfile(wiki_file):
        return wiki_file
    
    default_file = os.path.join('default-pages', filename)
    if os.path.isfile(default_file):
        return default_file
    
    return None

def render(page_name, page_title, page_path, response_code=200):
    
    # Render content
    print(f'Rendering {page_path}')
    with open(page_path) as f:
        content = f.read()
        html = style(markdown.markdown(content, extensions=['tables']))
    return render_template('page.html', 
        wiki_title=wiki_title(),
        title=page_title, 
        path=page_name, 
        content=Markup(html), 
        nav=Markup(nav())
        ), response_code


# Styling functions

def style(html):
    styled = html

    # Avoid image overflow
    styled = styled.replace('<img', '<img style="max-width:100%"')

    # Add Govuk styles
    styled = styled.replace('<h1>', '<h1 class="govuk-heading-l">')
    styled = styled.replace('<h2>', '<h2 class="govuk-heading-m">')
    styled = styled.replace('<h3>', '<h3 class="govuk-heading-s">')
    styled = styled.replace('<h4>', '<h3 class="govuk-heading-xs">')
    styled = styled.replace('<p>', '<p class="govuk-body">')
    # Link
    styled = styled.replace('<a ', '<a class="govuk-link" ')
    # List
    styled = styled.replace('<ul>', '<ul class="govuk-list govuk-list--bullet">')
    styled = styled.replace('<ol>', '<ol class="govuk-list govuk-list--number">')
    # Table
    styled = styled.replace('<table>', '<table class="govuk-table">')
    styled = styled.replace('<thead>', '<thead class="govuk-table__head">')
    styled = styled.replace('<tr>', '<tr class="govuk-table__row">')
    styled = styled.replace('<th>', '<th scope="col" class="govuk-table__header">')
    styled = styled.replace('<tbody>', '<tbody class="govuk-table__body">')
    styled = styled.replace('<td>', '<td class="govuk-table__cell">')

    return styled

def style_nav(html):
    styled = html
    # Menu-specific styles
    styled = styled.replace('<ul>', '<ul class="govuk-list govuk-!-font-size-16">')
    styled = styled.replace('<li>', '<li class="gem-c-related-navigation__link">')
    # The rest of the Govuk styles
    return style(styled)
