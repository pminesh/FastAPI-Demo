from sqlalchemy.orm import Session
from app.ws.device_models import Device
from fastapi.encoders import jsonable_encoder


def add_device(data:dict, db: Session):
    """
        Add a new device to the database.
    """
    try:
        new_device = Device(
                name=data["name"],
                device_type=data["device_type"],
                app_type=data["app_type"],
                status=data["status"],
                device_id=data["device_id"],
                channel_id=data["channel_id"],
                is_dimmable=data["is_dimmable"]
        )
        db.add(new_device)
        db.commit()
        db.refresh(new_device)
    except Exception as e:
        print(f"Error adding device: {e}")
    
def get_devices(db: Session):
    """
        Get all devices from the database.
    """
    try:
        devices = db.query(Device).all()
        return {'status': 'success', 'results': len(devices), 'devices': jsonable_encoder(devices)}
    except Exception as e:
        print(f"Error adding device: {e}")
        return {}