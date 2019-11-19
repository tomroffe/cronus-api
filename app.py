import math
import json
import numpy as np
import pandas as pd
from flask import Flask
from flask import jsonify
from flask_cors import CORS

import os
import re

app = Flask(__name__)
cors = CORS(app)
csv_files = []
data_files = []
df = pd.DataFrame()

for root, dirs, files in os.walk("../data/"):
    for filename in files:
      match = re.search(r'Payments_over_500', filename)
      if match:
        csv_files.append(filename)

for file in csv_files:
    filename = '../data/{}'.format(file)
    print('Reading Data File: {}'.format(file))
    df = pd.read_csv('file:{}'.format(filename), encoding='utf-8')
    print('\t - Renaming Columns')
    df = (df.rename(index=str,
               columns={"Invoice Line Amount": "amount",
                        "Payment Date": "date",
                        "LA Department": "department",
                        "Expenditure Category/Description": "category"}))

    #print('\t - Fix department to remove slashes')
    #df.department = (df.department.replace(r'[\,)]',' - ', regex=True ))

    #print('\t - Fix category to remove slashes')
    #df.category = (df.category.replace(r'[\,)]','', regex=True ))

    print('\t - Fix data to datetime type')
    df.date = pd.to_datetime(df.date.str.strip(), format="%d/%m/%Y")

    print('\t - Fix amount to float type')
    df.amount = (df.amount.replace(r'[\,)]','', regex=True ).astype(float))

    print('\t - Auto infer for column types \n')
    df.apply(lambda x: pd.api.types.infer_dtype(x.values))

    data_files.append(df)

for data in data_files:
    df = pd.concat([df,data])

print('Dropping NaN\'s \n')
df = df.dropna()


@app.route("/payments/")
def payments_per_day():
    output_data = []

    for key, value in df.groupby(['date']).amount.count().items():
        dp = { "day": key.strftime("%Y-%m-%d"), "value": value }
        output_data.append(dp)

    return(jsonify(output_data))

@app.route("/amounts/")
def amounts_per_day():
    output_data = []

    for key, value in df.groupby(['date']).amount.sum().items():
        dp = { "day": key.strftime("%Y-%m-%d"), "value": value }
        output_data.append(dp)

    return(jsonify(output_data))

@app.route("/departments/")
def departments():
    output_data = []
    for item in df.department.unique().tolist():
        dp = { "value": item, "label": item }
        output_data.append(dp)

    return(jsonify(output_data))

@app.route("/categories/")
def categories():
    output_data = []
    for item in df.category.unique().tolist():
        dp = { "value": item, "label": item }
        output_data.append(dp)

    return(jsonify(output_data))

@app.route("/paymentsByDepartment/<department>")
def payments_per_department(department):
    output_data = []
    results = df.loc[df['department'] == department].groupby(['date']).amount.count()

    for key, value in results.items():
        dp = { "day": key.strftime("%Y-%m-%d"), "value": value }
        output_data.append(dp)

    return(jsonify(output_data))

@app.route("/paymentsByCategory/<category>")
def payments_per_category(category):
    output_data = []
    results = df.loc[df['category'] == category].groupby(['date']).amount.count()

    for key, value in results.items():
        dp = { "day": key.strftime("%Y-%m-%d"), "value": value }
        output_data.append(dp)

    return(jsonify(output_data))

@app.route("/paymentsByDepartmentCategory/<department>/<category>")
def payments_per_department_category(department, category):
    output_data = []
    dept_data =  df.loc[df['department'] == department]
    cat_data = dept_data.loc[dept_data['category'] == category]

    results = cat_data.groupby(['date']).amount.count()

    for key, value in results.items():
        dp = { "day": key.strftime("%Y-%m-%d"), "value": value }
        output_data.append(dp)

    return(jsonify(output_data))

@app.route("/amountsByDateAndDepartment/<date_from>/<date_to>/<department>")
def amounts_per_department_date(department, date_from, date_to):
    df_date = df[df.date.between(date_from, date_to)]
    df_date.loc[df_date['department'] == department]
    df_date.groupby(['department']).amount.sum()

@app.route("/paymentsByDateAndDepartment/<date_from>/<date_to>/<department>")
def payments_per_department_date(department, date_from, date_to):
    df_date = df[df.date.between(date_from, date_to)]
    df_date.loc[df_date['department'] == department]
    df_date.groupby(['department']).amount.count()


@app.route("/amountsByDateAndCategory/<date_from>/<date_to>/<category>")
def amounts_per_category_date(category, date_from, date_to):
    df_date = df[df.date.between(date_from, date_to)]
    df_date.loc[df_date['category'] == category]
    df_date.groupby(['category']).amount.sum()

@app.route("/paymentsByDateAndCategory/<date_from>/<date_to>/<category>")
def payments_per_category_date(category, date_from, date_to):
    df_date = df[df.date.between(date_from, date_to)]
    df_date.loc[df_date['category'] == category]
    df_date.groupby(['category']).amount.count()


@app.route('/amountsByDepartmentCategory/<department>/<category>/')
@app.route("/amountsByDepartmentCategory/<department>/<category>/<date_from>/<date_to>/")
def amounts_per_department_category(department,category, date_from='06-04-2014', date_to='05-04-2019'):
    output_data = []
    df_date = df[df.date.between(date_from, date_to)]
    df_dept = df_date.loc[df_date['department'] == department]
    df_cat = df_dept.loc[df_dept['category'] == category]
    results = df_cat.groupby(['name']).amount.sum().sort_values(ascending=False)[0:10]

    for item in results.iteritems():
        name = str(item[0]).title()
        value = int(float(item[1]))
        dp = { "value": value, "label": name,  "id": name}
        output_data.append(dp)

    return(jsonify(output_data))

@app.route("/departmentCategorySums/<department>")
@app.route("/departmentCategorySums/<department>/<date_from>/<date_to>/")
def department_category_sums(department, date_from='06-04-2014', date_to='05-04-2019'):
    output_data = []
    df_date = df[df.date.between(date_from, date_to)]
    data = df_date.loc[df_date['department'] == department]
    results = data.groupby(['category']).amount.sum().sort_values(ascending=False)[0:10]

    for item in results.iteritems():
        name = item[0]
        label = str(item[0]).title()
        value = int(float(item[1]))
        dp = { "value": value, "label": label,  "id": name}
        output_data.append(dp)

    return(jsonify(output_data))



@app.route("/departmentCategoriesByDate/<date_from>/<date_to>/<department>")
def department_categories_date(department, date_from, date_to):
    output_data = []
    df_date = df[df.date.between(date_from, date_to)]
    data = df_date.loc[df_date['department'] == department]

    for item in data.category.unique().tolist():
        dp = { "value": item, "label": item }
        output_data.append(dp)

    return(jsonify(output_data))

@app.route("/departmentCategories/<department>")
def department_categories(department):
    output_data = []
    data = df.loc[df['department'] == department]

    for item in data.category.unique().tolist():
        dp = { "value": item, "label": item }
        output_data.append(dp)

    return(jsonify(output_data))
