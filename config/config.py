from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()

db_host = os.getenv('DB_HOST')
if ':' in db_host:
    host, port = db_host.split(':')
else:
    host, port = db_host, '24374' 

class Config:
    SQLALCHEMY_DATABASE_URI = (
    f"mysql+mysqlconnector://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}"
    f"@{host}:{port}/{os.getenv('DB_DATABASE')}?ssl_ca=ca_certificate.pem"
)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
