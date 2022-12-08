from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI, Depends

# SQLALCHEMY_DATABASE_URL = 'postgresql://sismosu:123@localhost:5432/sismosdb'
# engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Base de datos Cloud
engine = create_engine('postgresql://postgres:postgres@34.95.248.189:5432/sismosdb', pool_size=50, max_overflow=0) 
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Sismos(Base):
    
    __tablename__ = 'sismos'
    
    idsismo = Column(Integer, primary_key=True, index = True)
    idpais = Column(Integer, ForeignKey('pais.idpais'))
    mag = Column(Float)
    place = Column(Text)
    time = Column(Text)
    url = Column(Text)
    tsunami = Column(Integer)
    title =  Column(Text)
    lng = Column(Float)
    lat = Column(Float)
    depth = Column(Float)
    peligro = Column(Integer)
    year = Column(Text)
    month = Column(Text)
    day = Column(Text)
    
    pais_r = relationship('Pais', back_populates = 'sismos_r')
    
class Tsunamis(Base):
    
    __tablename__ = 'tsunamis'
    
    id = Column(Integer, primary_key=True, index = True) # No se le pone idvolcanes
    idpais = Column(Integer, ForeignKey('pais.idpais'))
    altura_oleaje = Column(Float)
    place = Column(Text)
    time = Column(Text)
    year = Column(Integer)
    month = Column(Integer)
    day = Column(Integer)
    url = Column(Text)
    mag = Column(Float)
    lng = Column(Float)
    lat = Column(Float)
    depth = Column(Float)

    pais_r2 = relationship('Pais', back_populates = 'tsunamis_r')
    
class Volcanes(Base):
    
    __tablename__ = 'volcanes'
    
    id = Column(Integer, primary_key=True, index = True) # No se le pone idvolcanes
    idpais = Column(Integer, ForeignKey('pais.idpais'))
    nombre = Column(String)
    tipo = Column(String)
    elevacion = Column(Float)
    place = Column(Text)
    ultima_erupcion = Column(String)
    lat = Column(Float)
    lng = Column(Float)
    url = Column(Text)
    
    pais_r3 = relationship('Pais', back_populates = 'volcanes_r')
    

class Pais(Base):
    
    __tablename__ = 'pais'
    
    idpais = Column(Integer, primary_key=True, index = True)
    pais = Column(Text)
    
    sismos_r = relationship('Sismos', back_populates = 'pais_r')
    tsunamis_r = relationship('Tsunamis', back_populates = 'pais_r2')
    volcanes_r = relationship('Volcanes', back_populates = 'pais_r3')
    
    
app = FastAPI(title='Sismos', description='En esta APi podras encontrar información acerca de eventos sísmicos y tsunamis ocurridos en Chile, Japón y Estados Unidos. Adicionalmente, permite hacer consultas de los volcanes en dichos paises.\n Para filtrar por país se deberá escribir el nombre del país de la siguiente manera: Chile, Japón, USA')

Base.metadata.create_all(bind = engine)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
def obtener_sismos(db: Session):
    sismos = db.query(Sismos).limit(100).all()
    return sismos

# SISMOS


@app.get('/',tags=['Sismos'])
def inicio(db: Session = Depends(get_db)):
    return {'Hola':'Bienvenido a la API de EARTH DATA, por favor dirigite a la página: '}

@app.get('/sismos/all',tags=['Sismos'], description='Petición para obtener todos los registros de sismos.')
def sismos_todos(db: Session = Depends(get_db)):
    sismos_todos = obtener_sismos(db)
    return sismos_todos

# Obtener los registros de sismos filtrando por características.
@app.get('/sismos/',tags=['Sismos'], description='Petición para obtener los registros  de sismos filtrados según sus características.')
def sismos_filtrados(max_depth: float | None = 800, min_depth: float | None = 0, min_mag: float | None = 0, max_mag: float | None = 9.9,
         min_lat: float | None = -90, max_lat: float | None = 90, min_long: float | None = -180, max_long:float | None = 180,
         min_anio: float | None = 2000, max_anio:float | None = 2022, pais : str | None = 'japon',
         db: Session = Depends(get_db)):
    pais_valor = pais(pais)
    sismos = db.query(Sismos).filter(Sismos.depth >= min_depth).filter(Sismos.depth <= max_depth).\
            filter(Sismos.mag <= max_mag).filter(Sismos.mag >= min_mag).\
                filter(Sismos.lat <= max_lat).filter(Sismos.lat >= min_lat).\
                    filter(Sismos.lng <= max_long).filter(Sismos.lng >= min_long).\
                        filter(Sismos.year <= max_anio).filter(Sismos.year >= min_anio).\
                            filter(Sismos.idpais == pais_valor).limit(100).all()
    return sismos


# Sismo mas fuerte para el año deseado en el pais de interes.
@app.get('/sismos/evento_maximo', tags=['Sismos'], description='Petición que retorna el sismo mas fuerte para el año deseado en el pais de interes.')
def sismo_maximo(pais_i : str,anio: int, db: Session = Depends(get_db)):
    max_sismo = db.query((Sismos),).select_from(Sismos).join(Pais, Sismos.idpais == Pais.idpais,).\
        filter(Pais.pais == pais_i).filter(Sismos.year == anio).order_by(Sismos.mag.desc()).limit(1).all()
    return max_sismo
    

# # TSUNAMIS 

# Obtener todos los registros de tsunamis
@app.get('/tsunamis/all',tags=['Tsunamis'], description='Petición para obtener todos los registros de tsunamis.')
def tsunamis_todos(db: Session = Depends(get_db)):
    tsunamis = db.query(Tsunamis).all()
    return tsunamis

# Obtener los registros de intento filtrando por características.
@app.get('/tsunamis/',tags=['Tsunamis'], description='Petición para obtener los registros  de tsunamis filtrados según sus características.')
def tsunamis_filtrados(altura_olas_max: float | None = 100, altura_olas_min: float | None = 0, max_depth: float | None = 800, min_depth: float | None = 0, min_mag: float | None = 0, max_mag: float | None = 9.9,
         min_lat: float | None = -90, max_lat: float | None = 90, min_long: float | None = -180, max_long:float | None = 180,
         min_anio: float | None = 2000, max_anio:float | None = 2022,
         db: Session = Depends(get_db)):
    tsunamis = db.query(Tsunamis).filter(Tsunamis.lat <= max_lat).filter(Tsunamis.lat >= min_lat).\
        filter(Tsunamis.lng <= max_long).filter(Tsunamis.lng >= min_long).\
            filter(Tsunamis.altura_oleaje <= altura_olas_max).filter(Tsunamis.altura_oleaje >= altura_olas_min).\
                filter(Tsunamis.depth >= min_depth).filter(Tsunamis.depth <= max_depth).\
                    filter(Tsunamis.mag <= max_mag).filter(Tsunamis.mag >= min_mag).\
                        filter(Tsunamis.year <= max_anio).filter(Tsunamis.year >= min_anio).limit(100).all()
    return tsunamis

# Top 5 Tsunami mas fuertes para el año deseado en el pais de interes
@app.get('/Tsunamis/eventos_maximos', tags=['Tsunamis'], description='Petición para obtener los 5 tsunamis con mayor elevación de marea filtrados según pais y año.')
def tsunamis_maximos(pais_i: str, anio: int, db: Session = Depends(get_db)):
    tsunami_maximo = db.query(Tsunamis).select_from(Tsunamis).join(Pais, Tsunamis.idpais == Pais.idpais).\
        filter(Tsunamis.year == anio).filter(Pais.pais == pais_i).order_by(Tsunamis.altura_oleaje.desc()).limit(5).all()
    return tsunami_maximo

# VOLCANES

# Obtener todos los registros de volcanes.
@app.get('/volcanes/all', tags=['Volcanes'], description='Petición para obtener los volcanes de los paises de interes')
def volcanes_todos(db: Session = Depends(get_db)):
    volcanes_todos = db.query(Volcanes).all()
    return volcanes_todos

# Obtener todos los registros de volcanes segun el pais.
@app.get('/volcanes/', tags=['Volcanes'], description='Petición para obterner los volcanes filtrados por pais.')
def volcanes_filtrados(pais_i: str,db: Session = Depends(get_db)):
    volcanes_filtrados = db.query(Volcanes).select_from(Volcanes).join(Pais, Volcanes.idpais == Pais.idpais).\
        filter(Pais.pais == pais_i).all()
    return volcanes_filtrados
