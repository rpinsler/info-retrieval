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
    lipsum = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse laoreet mauris eu tortor" + \
    		 "interdum tempor. Sed vulputate odio odio. Sed arcu neque, accumsan et urna quis, ultrices" + \
    		 "consectetur turpis. Donec eu euismod sem, nec aliquam velit. Donec ac tristique mi."
    docs = [['Some interesting title', 'text', 1, 13.37, "this/is/some/key", "Bruce Lee and Jackie Chan", 2002, "SIGIR"],
    		['Another title', 'moretext', 2, 4.04, "yet/another/key", "John Doe", 2014, "WISDM"],
    		['It is all about the title', 'notext', 3, 1.01, "the/key/is/key", "Adam Smith", 1983, "KDD"]]
    results = [dict(title=doc[0], text=lipsum, rank=doc[2], score=doc[3], key=doc[4], authors=doc[5], year=doc[6], venue=doc[7]) for doc in docs]
    metadata = [dict(time=0.02)]
    return render_template('search.html', results=results, metadata=metadata)

if __name__ == '__main__':
    app.run()
