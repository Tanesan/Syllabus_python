
import firebase_admin
from firebase_admin import credentials
import pandas as pandas
from firebase_admin import db

cred = credentials.Certificate("univ-syllabus-firebase-adminsdk-nfe0l-f0a68c4baa.json")
# firebase_admin.initialize_app(cred)

# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://univ-syllabus-default-rtdb.firebaseio.com/'
})

# As an admin, the app has access to read and write all data, regradless of Security Rules
ref = db.reference('rate')
json_open_all = open("docs/all.json", 'r')

df = pandas.read_json(json_open_all)

urls = []
a = {}

for i in df.columns.values.tolist():
    a.update({
        i : {
            'average': 0,
            'review': [""],
            'people': [""],
            'time': [""],
            'user': {}
        }
    })


ref.set(a)

