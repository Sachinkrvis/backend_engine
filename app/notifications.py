# # app/notifications.py
import os
import firebase_admin
from firebase_admin import credentials, messaging

# Initialize Firebase app once
if not firebase_admin._apps:
    cred_path = os.getenv(
        "FCM_CREDENTIALS_JSON",
        "keys/localhost.json",
    )
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)


def send_fcm_notification(token: str, title: str, body: str, data: dict | None = None):
    """Send push notification to a specific device token."""
    message = messaging.Message(
        token=token,
        notification=messaging.Notification(title=title, body=body),
        data=data or {},
    )
    response = messaging.send(message)
    return response
    # print(f"Sending FCM notification to {token}: {title} - {body} with data {data}")
    # return "FCM notification sent"


if __name__ == "__main__":
    send_fcm_notification(
        token="emQ5vQUcSHmAzMrkzT1ECP:APA91bF-EpCJDrPpfjqk3bC1jc6cxjTXVAligO0cscGAYuv8diCm1gYrF6EO1bsO9cBKzfXbwdCFC4M39tvT2kxrX6FS64JWkK1YAqsNDVVpcgG7mY327vQ",
        title="Alert",
        body="This is a test notification",
        data={"key": "value"},
    )
