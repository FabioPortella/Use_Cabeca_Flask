from flask import Flask, render_template, request, escape, session
from vsearch import procura_letras
from checker import check_logged_in
from DBcm import UseDatabase

app = Flask(__name__)
app.secret_key = "MeuSenhorJesusCristo"

app.config['dbconfig'] = {'host': '127.0.0.1',
                          'user': 'vsearch',
                          'password': 'vsearchpasswd',
                          'database': 'vsearchlogDB',}


@app.route('/login')
def do_login() -> str:
    session['logged_in'] = True
    return "Você está LOGADO"


@app.route('/logout')
def do_logout() -> str:
    session.pop('logged_in')
    return "Você NÃO está mais logado"

     
def log_request(req: 'flask_request',  res: str) -> None:
    """Log detils of the web reueste and the reultes. """
    with UseDatabase(app.config['dbconfig']) as cursor:
        _SQL = """insert into log
                (phrase, letters, ip, browser_string, results)
                values
                (%s, %s, %s, %s, %s)"""
        cursor.execute(_SQL, (req.form['phrase'],
                              req.form['letters'],
                              req.remote_addr,
                              req.user_agent.browser,
                              res, ))


@app.route('/search4', methods=['POST'])
def do_search() -> 'html':
    frase = request.form['phrase']
    letras = request.form['letters']
    title = "Estes são os seus resultados:"
    results = str(procura_letras(frase, letras))
    log_request(request, results)
    return render_template('results.html',
        the_phrase=frase,
        the_letters=letras,
        the_title=title,
        the_results=results)


@app.route('/')
@app.route('/entrada')
def entry_page() -> 'html':
    return render_template('entry.html', the_title="Bem vindo ao search4leters para WEB")


@app.route('/verlog')
@check_logged_in
def view_the_log() -> 'html':
    """Display the contentes of the log file as a HTML table."""
    with UseDatabase(app.config['dbconfig']) as cursor:
        _SQL = """select phrase, letters, ip, browser_string, results
                  from log"""
        cursor.execute(_SQL)
        contents = cursor.fetchall()
    titles = ('Phrase', 'Letters', 'Remote_addr', 'User_agent', 'Results')
    return render_template('viewlog.html',
                           the_title='View Log',
                           the_row_title=titles,
                           the_data=contents,)


if __name__ == "__main__":
    app.run(debug=True)