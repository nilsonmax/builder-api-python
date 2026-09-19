from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuración de conexión MySQL (ajusta usuario/password de tu MySQL/XAMPP)
# Formato: mysql+pymysql://usuario:password@host:puerto/nombre_base_datos
MYSQL_URL = "mysql+pymysql://root:@localhost:3306/saas_builder_db"

engine = create_engine(MYSQL_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependencia para obtener la sesión de la base de datos en los endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()