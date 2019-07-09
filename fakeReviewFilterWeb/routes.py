from __init__ import app
from flask import request, render_template, jsonify
from core.parseALink import parseALink
from core.infoDatabase.reviewModels import ProductType
from core.infoDatabase.dbSession import dbSession as Session


@app.route('/')
def index():
    session = Session()
    try:
        productTypes = session.query(ProductType).all()
    except:
        session.rollback()
    finally:
        session.close()
    return render_template('index.html', productTypes=productTypes)


@app.route('/parse')
def parse():
    productTypeId = int(request.args.get('productTypeId'))
    url = request.args.get('productLink')
    data = parseALink(url, productTypeId)
    return jsonify(data)
