from meross_iot.manager import MerossManager
from meross_iot.meross_event import MerossEventType
from meross_iot.cloud.devices.light_bulbs import GenericBulb
from meross_iot.cloud.devices.power_plugs import GenericPlug
from meross_iot.cloud.devices.door_openers import GenericGarageDoorOpener
import time
import os
import sys
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import datetime

# Use a service account
cred = credentials.Certificate({
			  "type": "service_account",
			  "project_id": os.environ.get('PROJECT_ID'),
			  "private_key_id": os.environ.get('PRIVATE_KEY_ID'),
			  "private_key": os.environ.get('PRIVATE_KEY').replace('\\n', '\n'),
			  "client_email": os.environ.get('CLIENT_EMAIL'),
			  "client_id": os.environ.get('CLIENT_ID'),
			  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
			  "token_uri": "https://oauth2.googleapis.com/token",
			  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
			  "client_x509_cert_url": os.environ.get('CLIENT_CERT_URL')
		})
firebase_admin.initialize_app(cred)
db = firestore.client()

EMAIL = os.environ.get('MEROSS_EMAIL')
PASSWORD = os.environ.get('MEROSS_PASSWORD')

def event_handler(eventobj):
    if eventobj.event_type == MerossEventType.DEVICE_ONLINE_STATUS:
        print("Device online status changed: %s went %s" % (eventobj.device.name, eventobj.status))
        sys.stdout.flush()
        pass
    elif eventobj.event_type == MerossEventType.DEVICE_SWITCH_STATUS:
        print("Switch state changed: Device %s (channel %d) went %s" % (eventobj.device.name, eventobj.channel_id,
                                                                        eventobj.switch_state))
        sys.stdout.flush()
    else:
        print(eventobj)
        sys.stdout.flush()


if __name__=='__main__':
    # Initiates the Meross Cloud Manager. This is in charge of handling the communication with the remote endpoint
    manager = MerossManager(meross_email=EMAIL, meross_password=PASSWORD)

    # Register event handlers for the manager...
    manager.register_event_handler(event_handler)

    # Starts the manager
    manager.start()

    # You can also retrieve devices by the UUID/name
    # a_device = manager.get_device_by_name("My Plug")
    # a_device = manager.get_device_by_uuid("My Plug")

    # Or you can retrieve all the device by the HW type
    # all_mss310 = manager.get_devices_by_type("mss310")

    plug = manager.get_device_by_name("plug0")

    while plug.supports_electricity_reading():
        print("Current consumption is: %s" % str(plug.get_electricity()))
        doc_ref = db.collection(u'plug-logs').add(plug.get_electricity())
        doc_ref.set({ u'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") })
        sys.stdout.flush()
        time.sleep(5)

    # At this point, we are all done playing with the library, so we gracefully disconnect and clean resources.
    print("We are done playing. Cleaning resources...")
    manager.stop()

    print("Bye bye!")