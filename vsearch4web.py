from flask import Flask, render_template, request, escape
from vsearch import procura_letras
from datetime import date, datetime, timedelta

app = Flask(__name__)


def log_request(req: 'flask_request',  res: str) -> None:
    dbconfig = { 'host': 'localhost',
                 'user': 'vsearch',
                 'password': 'vsearchpasswd',
                 'database': 'vsearchlogDB',}

    import mysql.connector

    conn = mysql.connector.connect(**dbconfig)
    cursor = conn.cursor()

    _SQL = """insert into log
              (phrase, letters, ip, browser_string, results)
              values
              (%s, %s, %s, %s, %s)"""
    
    cursor.execute(_SQL, (req.form['phrase'],
                          req.form['letters'],
                          req.remote_addr,
                          req.user_agent.browser,
                          res, ))

    conn.commit()
    cursor.close()
    conn.close()


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
def view_the_log() -> 'html':
    contents = []
    with open('vsearch.log') as log:
        for line in log:
            contents.append([])
            for item in line.split('|'):
                contents[-1].append(escape(item))
    titles = ('Form Data', 'Remote_addr', 'User_agent', 'Results')
    return render_template('viewlog.html',
                           the_title='View Log',
                           the_row_title=titles,
                           the_data=contents,)


if __name__ == "__main__":
    app.run(debug=True)