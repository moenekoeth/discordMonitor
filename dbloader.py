from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session
import sqlalchemy as sa
from datetime import datetime, timezone
import os
import sys
import json

def load_config(config_file):
    if os.path.isfile(config_file):
        config = json.load(open(config_file))
        config["path"] = os.path.dirname(os.path.abspath(config_file)).strip()
        config["cogs_path"] = os.environ.get('HOMU_COGS_PATH',"./cogs/")
    else:
        print("E", config_file + " file is missing")
        sys.exit()
    return config

inner_config = load_config("./config/config.json")

if inner_config["db"]["engine"] == "sqlite":
    if os.name == 'nt':
       SQLALCHEMY_DATABASE_URI = "sqlite:///" + inner_config["path"] + str(os.path.sep) + "db.sqlite3"
       SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('\\',"\\\\")
    else:
       SQLALCHEMY_DATABASE_URI = "sqlite:////" + inner_config["path"] + str(os.path.sep) + "db.sqlite3"
else:
    SQLALCHEMY_DATABASE_URI = "{}://{}:{}@{}:{}/{}".format(
        inner_config["db"]["engine"],
        inner_config["db"]["user"],
        inner_config["db"]["password"],
        inner_config["db"]["host"],
        str(inner_config["db"]["port"]),
        inner_config["db"]["name"],
    )

try:
    base = orm.declarative_base()
    engine = sa.create_engine(SQLALCHEMY_DATABASE_URI)
    base.metadata.bind = engine
    Session = scoped_session(orm.sessionmaker(bind=engine))
    session = Session()
    base.query = Session.query_property()
    session._model_changes = {}
except Exception as e:
    print("Unable to connect to database - " + str(e))


def db_check(db_pks,db_table):
    """
    Checks database for data.
    Useful for inserts
    """
    cur_item = db_table.query.filter_by(**db_pks).first()
    return cur_item


def db_insert(db_data, db_table):
    """
    Insert data into database, preps it into a list of inserts first,
     then merges it with the data in the table.

    Paramaters:
    ===========
    db_data : list[dicts]
        contains a list of the dictionaries to insert.
    db_table : sqlalchemy Table Class
        Table Class that will be upserted into
    """

    inserts = []
    for dbd in db_data:
        inserts.append(db_table(**dbd))
    for dbr in inserts:
        try:
            session.add(dbr)
            session.commit()
        except:
            pass
def db_merge(db_obj):
    session.merge(db_obj)
    session.commit()

def db_update(db_value_data,db_where,db_is,db_table):
    """
    Upserts data into database directly.

    Paramaters:
    ===========
    db_field : str
        field to update,
    db_data : list[dicts]
        contains a list of the dictionaries to insert.
    db_table : sqlalchemy Table Class
        Table Class that will be upserted into
    """
    db_up = db_table.__table__.update().values(**db_value_data).where(db_where == db_is)
    session.execute(db_up)
    session.commit()


def db_upsert(db_data, db_table):
    """
    Upserts data into database, preps it into a list of inserts first,
     then merges it with the data in the table.

    Paramaters:
    ===========
    db_data : list[dicts]
        contains a list of the dictionaries to insert.
    db_table : sqlalchemy Table Class
        Table Class that will be upserted into
    """

    upserts = []
    for dbd in db_data:
        upserts.append(db_table(**dbd))
    for dbr in upserts:
        session.merge(dbr)
    session.commit()

def db_commit():
    session.commit()


## Table Classes definitions

class disHist(base):
    __tablename__ = "hist"
    __tablename__ = inner_config["tables"]["disHist"]
    srvid = sa.Column("srvid", sa.String)
    duser = sa.Column("duser",sa.String)
    did = sa.Column("did",sa.String)
    dlast = sa.Column("dlast",sa.DateTime)
    dmsg = sa.Column("dmsg",sa.String)
    __table_args__ = (
        sa.PrimaryKeyConstraint(srvid,did),{},
    )

class disConf(base):
    __tablename__ = inner_config["tables"]["disConf"]
    srvid = sa.Column("srvid", sa.String, primary_key=True)
    cjson = sa.Column("cjson", sa.JSON)




## End of table definitions
# Load / Create tables
base.metadata.create_all(bind=engine)