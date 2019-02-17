from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, form, StringField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask import Flask, render_template, url_for, flash, request, redirect
import sqlite3
import time
import subprocess
from shlex import quote

app = Flask(__name__)
app.config['SECRET_KEY'] = '73Eb55c45b63227065cF248acf4dcDa'
app.config['DEBUG'] = True

def update_db(input):
    conn = sqlite3.connect('/home/anton/projects/bandersnatch/pypi_packages.db')
    c = conn.cursor()
    exec_out = c.execute("SELECT package_name FROM pypi WHERE package_name = ? and has_been_added is null LIMIT 1", (input,))
    exec_out = exec_out.fetchall()
    if len(exec_out) != 0:
        c.execute("UPDATE pypi SET has_been_added = 1 WHERE package_name = ?", (input,))
        conn.commit()
        conn.close()
        return True
    else:
        return False


def get_dependencies(data):
    # foobar = quote(data) # https://docs.python.org/3/library/shlex.html#shlex.quote
    for i in data:
        pip_show = subprocess.Popen(['pip', 'show', i], stdout=subprocess.PIPE)
        grep = subprocess.Popen(['grep', 'Requires'], stdin=pip_show.stdout,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        pip_show.stdout.close()
        out, err = grep.communicate()
        output = str(out).strip('b\'Requires:').strip('\\n').lstrip()
        split_result = output.split(', ')

    return split_result

def fetch_results(search):
    conn = sqlite3.connect('/home/anton/projects/bandersnatch/pypi_packages.db')
    c = conn.cursor()
    c.execute("SELECT package_name FROM pypi WHERE package_name LIKE ? LIMIT 50", (search+'%',))

    return c.fetchall()

def add_to_banderconf(append_to_file):
    bandersnatch_conf = '/home/anton/Environments/bandersnatch/bandersnatch.conf'

    if len(append_to_file) > 1:
        for i in append_to_file:
            if update_db(i):
                with open(bandersnatch_conf, "a") as myfile:
                    flash(i +' has been added', 'success')
                    myfile.write('    ' + i + "\n")
            else:
                flash(i +' has already been added', 'warning')
    else:
        append = append_to_file[0]
        if update_db(append):
            with open(bandersnatch_conf, "a") as myfile:
                flash(append +' has been added', 'success')
                myfile.write('    ' + append + "\n")
        else:
            flash(append +' has already been added', 'warning')

class SearchForm(FlaskForm):
    search = StringField('What pypi package are you looking for?', validators=[DataRequired(), Length(min=2, max=50)])
    submit = SubmitField('Submit')

@app.route("/", methods=['GET', 'POST'])
def index():
    form = SearchForm()
    if request.method == 'POST' and request.form['submit'] == 'search':
        data = form.search.data
        package = fetch_results(data)
        count_package = len(package)
        #return redirect(url_for('index'))
        return render_template('index.html', form=form,
                        package=package,
                        count_package=count_package)
    elif request.method == 'POST' and request.form['submit'] == 'add_package':
        form_keys = request.form.getlist("packages")
        dependencies = get_dependencies(form_keys)
        add_to_banderconf(form_keys)
        add_to_banderconf(dependencies)
        return redirect(url_for('index'))
    else:
       return render_template('index.html', form=form)

if __name__ == '__main__':
    app.run()