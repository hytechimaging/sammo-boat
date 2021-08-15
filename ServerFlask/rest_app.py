# coding: utf8

__contact__ = "info@hytech-imaging.fr"
__copyright__ = "Copyright (c) 2021 Hytech Imaging"

from flask import render_template
import connexion

app = connexion.App(__name__, specification_dir='./')
app.add_api('openapi/specifications.yml')

@app.route('/')
def home():
    return render_template('home.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
