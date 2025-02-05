from pydantic import BaseModel

class WifiSettings(BaseModel):
    ssid: str
    encryption: str
    password: str
    lan_ip: str
