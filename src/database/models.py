from sqlalchemy import Column, Integer, String, Enum, Table, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

playlist_media_association = Table(
    'playlist_media', Base.metadata,
    Column('playlist_id', Integer, ForeignKey('playlists.id')),
    Column('media_id', Integer, ForeignKey('media.id'))
)

class Media(Base):
    __tablename__ = 'media'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    file_path = Column(String, nullable=False, unique=True)
    media_type = Column(String)
    artist = Column(String, nullable=True)
    album = Column(String, nullable=True)
    duration = Column(Integer, default=0)
    custom_cover_path = Column(String, nullable=True)
    date_added = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Media(title='{self.title}', type='{self.media_type}')>"

class Playlist(Base):
    __tablename__ = 'playlists'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    media_items = relationship("Media", secondary=playlist_media_association, backref="playlists")

    def __repr__(self):
        return f"<Playlist(name='{self.name}')>"
