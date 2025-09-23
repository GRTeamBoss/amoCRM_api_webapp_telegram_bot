import os

from sqlalchemy import create_engine, Column, Integer, String, select
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class Events(Base):
  __tablename__ = "events"
  id = Column(Integer, autoincrement=True, primary_key=True)
  event_id = Column(String, nullable=False, unique=True)
  type = Column(String, nullable=False)
  entity_id= Column(Integer, nullable=False)
  entity_type= Column(String, nullable=False)
  created_by = Column(Integer, nullable=False)
  created_at = Column(Integer, nullable=False)
  value_after = Column(String, nullable=False)
  value_before = Column(String, nullable=False)
  account_id = Column(Integer, nullable=False)
  _links = Column(String, nullable=False)
  _embedded = Column(String, nullable=False)



class DB:

  _DRIVER = os.getenv("SQLALCHEMY_DRIVER")
  _DB = os.getenv("SQLALCHEMY_DB")
  _USER = os.getenv("SQLALCHEMY_USER")
  _PASSWORD = os.getenv("SQLALCHEMY_PASSWORD")
  _HOST = os.getenv("SQLALCHEMY_HOST")
  _PORT = os.getenv("SQLALCHEMY_PORT")

  def __init__(self) -> None:
    self.engine = create_engine(f"{self._DRIVER}://{self._USER}:{self._PASSWORD}@{self._HOST}:{self._PORT}/{self._DB}")
    self._create_table_if_not_exist()
    self.session = sessionmaker(bind=self.engine)()


  def _create_table_if_not_exist(self) -> None:
    Base.metadata.create_all(self.engine)

  def add_event(self, value):
    check_if_exist = self.get_event(value["id"])
    if check_if_exist is None:
      new_event = Events(
        event_id=value["id"],
        type=value["type"],
        entity_id=value["entity_id"],
        entity_type=value["entity_type"],
        created_by=value["created_by"],
        created_at=value["created_at"],
        value_after=str(value["value_after"]),
        value_before=str(value["value_before"]),
        account_id=value["account_id"],
        _links=str(value["_links"]),
        _embedded=str(value["_embedded"])
      )
      self.session.add(new_event)
      self.session.commit()
    else:
      pass

  def get_event(self, id):
    process = select(Events).where(Events.event_id == id)
    event = self.session.scalar(process)
    return event.__dict__
  
  def get_events(self):
    process = select(Events)
    events = self.session.scalars(process)
    return events.all()
