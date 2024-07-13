from config import config
from sqlalchemy import create_engine, Column, Integer, String, Enum
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import SQLAlchemyError

Base = declarative_base()

class IpEvent(Base):
    __tablename__ = 'ip_events'

    id = Column(Integer, primary_key=True)
    ip_address = Column(String(15))
    event_type = Column(Enum('Failure', 'Recovery'))
    date_ = Column(String(50))
    recovery_time = Column(Integer, nullable=True)


config = config()
connection_url = (
    f"mssql+pyodbc://{config['database']['username']}:{config['database']['password']}@"
    f"{config['database']['server']}/{config['database']['database']}?driver={config['database']['driver']}"
)

engine = create_engine(connection_url)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

def add_ip_event(ip_address: str, event_type: str, date_: str, recovery_time: int = None) :
    session = Session()
    try:
        session.begin()
        ip_event = IpEvent(ip_address=ip_address, event_type=event_type, date_=date_, recovery_time=recovery_time)
        session.add(ip_event)
        session.commit()
        print(f"Event added: {event_type} for IP {ip_address} at {date_}")
        if recovery_time:
            print(f"Recovery time: {recovery_time} seconds")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error adding event: {e}")
    finally:
        session.close()
