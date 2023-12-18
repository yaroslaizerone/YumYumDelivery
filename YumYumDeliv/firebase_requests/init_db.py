from firebase_admin import credentials


def create_firebase_app():
 cred = credentials.Certificate('PATH OF FIREBASE SERVICE FILE ')
 firebase = firebase_admin.initialize_app(cred)
 return firebase