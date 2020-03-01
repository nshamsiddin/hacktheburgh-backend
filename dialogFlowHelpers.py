import dialogflow_v2 as dialogflow
from google.api_core.exceptions import InvalidArgument
DIALOGFLOW_PROJECT_ID = "banking-eggspq"
DIALOGFLOW_LANGUAGE_CODE = 'en-US'
GOOGLE_APPLICATION_CREDENTIALS = '1234567abcdef.json'
CLIENT_TOKEN = "f7c3adfc32974ba3b5834a0bc66edb0d"
DEVELOPER_TOKEN = "ed9dc32659654c03a843cc30183759d7"
import pandas as pd
from flask import jsonify
import numpy as np
import datetime
from datetime import datetime, timedelta
import os
from math import sin, cos, sqrt, atan2, radians


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./banking-eggspq-ae0a57855476.json"

def getIntent(response):

    # Constant vals

    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(DIALOGFLOW_PROJECT_ID, response.json["user_id"])

    inputText = response.json["query"]

    # Create text input
    text_input = dialogflow.types.TextInput(text=inputText, language_code=DIALOGFLOW_LANGUAGE_CODE)

    # Create query input
    query_input = dialogflow.types.QueryInput(text=text_input)

    try:
        resp = session_client.detect_intent(session=session, query_input=query_input)

    except InvalidArgument:
        return None
    return resp

def parseIntent(response, request):
    """
    Parse the intent string and figure out what the actual intent category is, for example, open account,
    top up credit, etc.

    :param resp:
    :return:
    """

    intent_text = str(response.query_result.intent.display_name)
    CHECK_BALANCE = 'account.balance.check'
    OPEN_ACCOUNT = 'account.open'
    CLOSEST_ATM = 'account.balance.closest_atm'
    TOP_UP_PHONE = 'top.up.phone'
    CHECK_SPENDING = 'account.spending.check'

    response_text = None

    if (intent_text== CHECK_BALANCE):
        response_text = str(check_balance(request))
        response_text = response.query_result.fulfillment_text + response_text

    elif (intent_text == OPEN_ACCOUNT):
        response_text = str(open_account())

    elif (intent_text == CLOSEST_ATM ):
        response_text = str(closest_atm(request))
        response_text = response.query_result.fulfillment_text + response_text
    elif (intent_text == TOP_UP_PHONE):
        response_text = top_up_phone()
    elif (intent_text == CHECK_SPENDING):
        response_text = response.query_result.fulfillment_text
    else:
        return None

    return response_text

def check_spending_complete(last_nr_of_days, user_id):
    df = pd.read_csv("./transactions.csv")
    transaction_dates = pd.to_datetime(df['date_time'])
    start_date = datetime.today() - timedelta(days=int(last_nr_of_days))
    transaction_dates_of_interest_indices = transaction_dates.index[transaction_dates > start_date].to_list()
    amounts = df.iloc[transaction_dates_of_interest_indices]
    print(amounts.dtypes)
    amounts_successful = amounts[(amounts['successful'] == True) & (amounts['user_id'] == float(user_id))]
    sum_amount = sum(amounts_successful['amount'])
    return str(sum_amount)

def top_up_phone():
    return "top_up_phone"

def open_account():
    return "open_account"

def check_balance(request):

    user_id = request["user_id"]

    df = pd.read_csv("./balance_table.csv")
    df = df[df.user_id == int(user_id)]
    balance = float(df["balance"])
    return balance

def closest_atm(request):

    user_latitude = radians(float(request.json['latitude']))
    user_longitude = radians(float(request.json['longitude']))

    df = pd.read_csv("./atm.csv")

    R = 6373.0

    distances = []

    for index, row in df.iterrows():
        atm_latitude = radians(row['latitude'])
        atm_longitude = radians(row['longitude'])

        d_longitude = atm_longitude - user_longitude
        d_latitude = atm_latitude - user_latitude

        a = (sin(d_latitude / 2)) ** 2 + cos(user_latitude) * cos(atm_latitude) * (sin(d_longitude / 2)) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c
        distances.append(distance)

    distances_indices = np.argsort(distances)

    closest_atm_machine = df.iloc[distances_indices]

    return closest_atm_machine
