
# coding: utf-8
from sqlalchemy import Column, Integer, Table, Text
from sqlalchemy.sql.sqltypes import NullType
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class Article(Base):
    __tablename__ = 'article'

    aid = Column('id', Integer, primary_key=True)
    uuid = Column(Integer, unique=True)
    a_type = Column('type', Integer)
    state = Column(Integer)
    sort = Column(Integer)
    dateAdd = Column(Integer)
    dateModif = Column(Integer)
    dateArt = Column(Integer)
    docName = Column(Text)
    otherMedia = Column(Text)
    buildResource = Column(Text)
    postExtValue = Column(Text)


class Cat(Base):
    __tablename__ = 'cat'

    rid = Column('id',Integer, primary_key=True)
    pid = Column(Integer)
    uuid = Column(Integer, unique=True)
    name = Column(Text)
    docName = Column(Text)
    catType = Column(Integer)
    sort = Column(Integer)
    sortType = Column(Integer)
    siteURL = Column(Text)
    siteSkinName = Column(Text)
    siteLastBuildDate = Column(Integer)
    siteBuildPath = Column(Text)
    siteFavicon = Column(Text)
    siteLogo = Column(Text)
    siteDateFormat = Column(Text)
    sitePageSize = Column(Integer)
    siteListTextNum = Column(Integer)
    siteName = Column(Text)
    siteDes = Column(Text)
    siteShareCode = Column(Text)
    siteHeader = Column(Text)
    siteOther = Column(Text)
    siteMainMenuData = Column(Text)
    siteExtDef = Column(Text)
    siteExtValue = Column(Text)
    sitePostExtDef = Column(Text)
    siteEnableLaTeX = Column(Integer)
    siteEnableChart = Column(Integer)


class CatArticle(Base):
    __tablename__ = 'cat_article'

    id = Column(Integer, primary_key=True)
    rid = Column(Integer)
    aid = Column(Integer)


t_sqlite_sequence = Table(
    'sqlite_sequence', metadata,
    Column('name', NullType),
    Column('seq', NullType)
)


class Tag(Base):
    __tablename__ = 'tag'

    tid = Column('id',Integer, primary_key=True)
    name = Column(Text)


class TagArticle(Base):
    __tablename__ = 'tag_article'

    taid = Column('id',Integer, primary_key=True)
    rid = Column(Integer)
    aid = Column(Integer)
