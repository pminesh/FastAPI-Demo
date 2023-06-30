import json
from app.ws.device_opr import add_device, get_devices, delete_devices
from ..database import SessionLocal

def device_operations(data):
    """
        Perform device operations based on the provided data.
    """
    db = SessionLocal()
    if data != {}:
        data = json.loads(data)
        if data['device_type'] == 'L':
            if data['opr'] == 'add':
                add_device(data=data, db=db)
            if data['opr'] == 'delete':
                delete_devices(data=data, db=db)
            if data['opr'] == 'update':
                print('update') #TODO
    return get_devices(db=db)