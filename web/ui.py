from flask import Flask, request, redirect, url_for, render_template

app = Flask(__name__)
app.config.update(
    DEBUG=True,
)


@app.route('/')
def index():
    return render_template('search.html')


@app.route('/search', methods=['GET'])
def query():
    # q = request.form['search']
    docs = [['doc1', 'text'], ['doc2', 'moretext'], ['doc3', 'notext']]
    results = [dict(title=doc[0], text=doc[1]) for doc in docs]
    return render_template('search.html', results=results)

if __name__ == '__main__':
    app.run()
