from flask import Flask, render_template, request, escape, session
from flask import copy_current_request_context

from vsearch import procura_letras

from checker import check_logged_in
from DBcm import UseDatabase, ConnectionError, CredentialsError, SQLError

from time import sleep
from threading import Thread

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


@app.route('/search4', methods=['POST'])
def do_search() -> 'html':

    @copy_current_request_context
    def log_request(req: 'flask_request',  res: str) -> None:
        """Log detils of the web reueste and the reultes. """
        sleep(15)  # simulando a domora de 15 segundos para gravar no DB
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

    frase = request.form['phrase']
    letras = request.form['letters']
    title = "Estes são os seus resultados:"
    results = str(procura_letras(frase, letras))
    try:
        t = Thread(target=log_request, args=(request, results))
        t.start()
    except  Exception as err:
        print('***** Logging failed with this error', str(err))
    return render_template('results.html',
        the_phrase=frase,
        the_letters=letras,
        the_title=title,
        the_results=results,)


@app.route('/')
@app.route('/entrada')
def entry_page() -> 'html':
    return render_template('entry.html', 
                            the_title="Bem vindo ao search4leters para WEB")


@app.route('/verlog')
@check_logged_in
def view_the_log() -> 'html':
    """Display the contentes of the log file as a HTML table."""
    try:
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
    except ConnectionError as err:
        print("O seu Banco de Dados está ligado? Erro: ", str(err))
    except CredentialsError as err:
        print("Erro de Usuário/Senha. Error: ", str(err))
    except SQLError as err:
        print("Sua QUERY está correta?  Error: ", str(err))    
    except Exception as err:
        print("Algo deu errado: ", str(err))
    return "Error"


if __name__ == "__main__":
    app.run(debug=True)