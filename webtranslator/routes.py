from flask import render_template,flash, redirect, send_from_directory, url_for, request
from webtranslator import app, db
from webtranslator.forms import InputForm, TranslateForm
from webtranslator.translator import get_all_urls, create_translation_doc, get_title
from webtranslator.models import Webtranslation
import datetime
import os
import logging



# Homepage route
@app.route('/', methods=['GET', 'POST'])
def index():
    # clear_data(db)
    # clears the db on each run. probably should find a better solution. used for testing. 
    form = InputForm()
    session_id = 1
    if form.validate_on_submit():
        i=1
        main_url = form.url.data
        ignored_urls = {(main_url + "disclaimer/"), (main_url + "privacy-statement-us/"), (main_url + "privacy-policy/"), (main_url + "opt-out-preferences/"), (main_url + "blog/")}
        urls = get_all_urls(form.url.data, ignored_urls)
        session_id = hash(form.url.data)
        for u in urls:
            title = get_title(u)
            url_element = Webtranslation(session_id=session_id,url_num=hash(u + str(datetime.datetime.now())),address = u, title=title)
            db.session.add(url_element)
        db.session.commit()
        urls = Webtranslation.query.filter(Webtranslation.session_id == session_id)
        print(session_id)
        for u in urls:
            print(u)
        form = TranslateForm()
        return redirect(url_for('filter_urls', session_id=session_id))
    urls = Webtranslation.query.filter(session_id == session_id)
    return render_template('index.html', form = form, urls = urls)


#test

# Filter URLS route 
@app.route('/filter_urls/', methods=['GET','POST'])
def filter_urls():
    session_id=request.args.get('session_id')
    print(session_id)
    urls = Webtranslation.query.filter(Webtranslation.session_id == session_id)
    for u in urls:
        print(u)
    form = TranslateForm()
    if form.validate_on_submit():
        company_name=form.company_name.data
        source_lang=form.source_lang.data
        target_lang=form.target_lang.data
        urls = Webtranslation.query.filter(Webtranslation.session_id == session_id)
        workbook = create_translation_doc(company_name=company_name, all_urls=urls, source_language=source_lang, target_language=target_lang)
        return render_template('success.html', workbook=workbook.filename)
    return render_template('filter_urls.html', urls=urls, form=form)

# Exlcude URL route. Removes the url from the db and redirects back to filter urls
@app.route('/exclude_url/<url_num>')
def exclude_url(url_num):
    url_to_delete = Webtranslation.query.get_or_404(url_num)
    db.session.delete(url_to_delete)
    db.session.commit()
    return redirect('/filter_urls')

# Route for download page
@app.route('/download_link/', methods=['GET', 'POST'])
def download_link():
   filename=request.args.get('workbook')
   filename=filename[5, len(filename)-1]
   print(filename)
   permitted_directory='/tmp'
   return send_from_directory(directory=permitted_directory, path=filename, as_attachment=True)

# def clear_data(session):
#     # clears the db 
#     meta = db.metadata
#     for table in reversed(meta.sorted_tables):
#         print ('Clear table %s' % table)
#         session.execute(table.delete())
#     session.commit()
