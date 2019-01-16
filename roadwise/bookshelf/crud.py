# Copyright 2015 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from bookshelf import get_model
from flask import Blueprint, redirect, render_template, request, url_for
import googleapiclient.discovery

crud = Blueprint('crud', __name__)


# helper to simplify traffic prediction
def prdict(numb):
    if numb < 1:
        return "Heavy Traffic Expected - Hang in there :( - Predicted Value  {}".format(numb)
    elif numb >= 1 and numb < 2 :
        return "Likely Heavy Traffic Expected - Hang tight! Predicted Value  {}".format(numb)
    elif numb <= 2 and numb < 2.8:
        return "Medium Traffic Expected - Not too bad right! - Predicted Value  {}".format(numb)
    else:
        return "Free Traffic Expected - Have fun :) - Predicted Value  {}".format(numb)

# helper to convert military time
def mtimer(m2):
    import datetime
    # m2 = "1:35"
    currenttime = datetime.datetime.now().time().strftime("%H:%M")
    if currenttime >= "10:00" and currenttime <= "13:00":
        if m2 >= "10:00" and m2 >= "12:00":
            m2 = ("""%s%s""" % (m2, " AM"))
        else:
            m2 = ("""%s%s""" % (m2, " PM"))
    else:
        m2 = ("""%s%s""" % (m2, " PM"))
    return m2


# [START list]
@crud.route("/")
def list():
    token = request.args.get('page_token', None)
    if token:
        token = token.encode('utf-8')

    books, next_page_token = get_model().list(cursor=token)

    return render_template(
        "list.html",
        books=books,
        next_page_token=next_page_token)
# [END list]


@crud.route('/<id>')
def view(id):
    book = get_model().read(id)
    return render_template("view.html", book=book[0])


# [START add]
@crud.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        data = request.form.to_dict(flat=True)
        # book = get_model().read(data['Region ID'])
        #
        # # return render_template(".result", book=book)

        return redirect(url_for('.view', id=data['Region ID']))

    return render_template("form.html", action="Add", book={})
# [END add]


# [START r]
@crud.route('/predict', methods=['GET', 'POST'])
def predict():

    if request.method == 'POST':

        data = request.form.to_dict(flat=True)
        hr = data['Hour']
        data['Hour'] = data['Hour'].split(':')[0]
        for k, v in data.items():
          data[k] = int(v)
        MODEL_NAME = 'roadpredict'
        VERSION_NAME = 'staging'
        service = googleapiclient.discovery.build('ml', 'v1')
        name = 'projects/data-streamwise/models/%s' % MODEL_NAME
        name += '/versions/%s' % VERSION_NAME

        responses = service.projects().predict(name=name,
                                               body={'instances': [data]}).execute()

        resp = get_model().read_gl(str(data['Region ID']))

        resp[0]['predicted_traffic'] = prdict(responses['predictions'][0])
        if ':' not in hr:
            hr = hr+':00'
        resp[0]['_time'] = mtimer(hr)

        return render_template("result.html", book=resp[0])

    return render_template("predict.html", action="Add", book={})
# [END add]


@crud.route('/<id>/edit', methods=['GET', 'POST'])
def edit(id):
    book = get_model().read(id)

    if request.method == 'POST':
        data = request.form.to_dict(flat=True)

        book = get_model().update(data, id)


        return redirect(url_for('.view', id=book['id']))

    return render_template("form.html", action="Edit", book=book)


@crud.route('/<id>/delete')
def delete(id):
    get_model().delete(id)
    return redirect(url_for('.list'))
