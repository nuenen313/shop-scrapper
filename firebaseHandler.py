import firebase_admin
from firebase_admin import credentials, storage, db


class FirebaseManager:
    def __init__(self, service_account_key, bucket_name, database_url):
        """
        Initialize the FirebaseManager with the required credentials, bucket, and database URL.

        :param service_account_key: Path to the service account key JSON file.
        :param bucket_name: Firebase Storage bucket name.
        :param database_url: Firebase Realtime Database URL.
        """
        self.service_account_key = service_account_key
        self.bucket_name = bucket_name
        self.database_url = database_url
        self._initialize_firebase()

    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK if not already initialized."""
        if not firebase_admin._apps:
            cred = credentials.Certificate(self.service_account_key)
            firebase_admin.initialize_app(cred, {
                'storageBucket': self.bucket_name,
                'databaseURL': self.database_url
            })
            print("Firebase app initialized.")

    def upload_image(self, image_path, storage_path):
        """
        Uploads an image to Firebase Storage.

        :param image_path: Local path to the image file.
        :param storage_path: Path in Firebase Storage where the image will be saved.
        :return: The public URL of the uploaded image.
        """
        bucket = storage.bucket()
        blob = bucket.blob(storage_path)
        blob.upload_from_filename(image_path)
        blob.make_public()
        public_url = blob.public_url
        print(f"Image uploaded to {public_url}")
        return public_url

    def upload_data(self, data, reference_path='offers'):
        """
        Uploads a dictionary to Firebase Realtime Database.

        :param data: The dictionary to upload.
        :param reference_path: The path in the database where the data will be stored.
        """
        ref = db.reference(reference_path)
        ref.set(data)
        print(f"Data pushed to database under path: {reference_path}")
