# # app/notifications.py
# import os
# import firebase_admin
# from firebase_admin import credentials, messaging

# # Initialize Firebase app once
# if not firebase_admin._apps:
#     cred_path = os.getenv("FCM_CREDENTIALS_JSON", "/secrets/fcm.json")
#     cred = credentials.Certificate(cred_path)
#     firebase_admin.initialize_app(cred)

# def send_fcm_notification(token: str, title: str, body: str, data: dict | None = None):
#     """Send push notification to a specific device token."""
#     message = messaging.Message(
#         token=token,
#         notification=messaging.Notification(title=title, body=body),
#         data=data or {},
#     )
#     response = messaging.send(message)
#     return response
