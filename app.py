from flask import Flask
from flask import request
from flask import abort, jsonify
import json
import dialogFlowHelpers
from dialogFlowHelpers import *
import pandas as pd
from collections import OrderedDict

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

balance = 200


def check_intent():
    return  None

@app.route('/entry_point', methods=['POST'])
def entry_point():
    if not request.json or not 'query' in request.json:
        print("Something noo working")
        abort(400)

    if "open_account_data" in request.json.keys():
        first_name = request.json['first_name']
        dob = request.json['dob']
        last_name = request.json['last_name']
        id_number = request.json['id_number']
        phone_number = request.json['phone_number']
        post_code = request.json['post_code']
        complete_open_account(first_name, last_name, id_number, phone_number, post_code, dob)
        return jsonify({'response': "ok"}), 200
    elif "top_up_phone_amount" in request.json.keys():
        top_up_amount = request.json['top_up_phone_amount']
        response_text = "We successfully topped up your phone on the EE network with " + top_up_amount + "!"
        return jsonify({'response': response_text}), 200
    elif "spending_check_interval" in request.json.keys():
        spending_amount = check_spending_complete(request.json['spending_check_interval'], request.json['user_id'])
        return jsonify({'response': spending_amount})
    elif "latitude" in request.json.keys():
        atm_dict = OrderedDict(closest_atm(request).to_dict(orient='index'))
        dictlist = []
        for key, value in atm_dict.items():
            dictlist.append(value)
        return jsonify({'atm_list': dictlist})
        # return jsonify({'atms': closest_atm(request).to_json(orient='index')})
    else:
        resp = dialogFlowHelpers.getIntent(request)
        response_text = dialogFlowHelpers.parseIntent(resp, request)

    return jsonify({'response': response_text}), 201


def complete_open_account(first_name, last_name, id_number, phone_number, post_code, dob):
    df = pd.read_csv("./accounts.csv")

    new_df = pd.DataFrame([[first_name, last_name, id_number, phone_number, post_code, dob]], columns=
                          ["first_name", "last_name", "id_number", "phone_number", "post_code", "dob"])
    df = df.append(new_df)
    df.to_csv("./accounts.csv", index=False)



if __name__ == '__main__':
    app.run()
