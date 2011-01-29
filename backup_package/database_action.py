'''
Created on Dec 21, 2010

@author: Stephen
'''

import os
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class BackupDB(object):
    '''
    classdocs
    '''

    name = "backup.db"

    def __init__(self,path):
        '''
        Constructor
        '''
        
        self.path = path;
        
    def create_backup_session(self,time_stamp):
        self.time_stamp = time_stamp;
        history = BackupHistory(self.time_stamp)
        self.session.add(history)
    
    def exists(self):
        return os.path.exists(os.path.join(self.path,self.name))
    
    def create(self,source):
        if self.exists():
            return
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        self.engine = create_engine('sqlite:///%s' % \
                                    os.path.join(self.path,self.name))
        Base.metadata.create_all(self.engine)
        self.initialize()
        info_source = BackupInfo('root',source)
        self.session.add(info_source)
        
    def connect(self):
        self.engine = create_engine('sqlite:///%s' % \
                                    os.path.join(self.path,self.name))
        self.initialize()
    
    def initialize(self):
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        

    
        
class CurrentFile(Base):
    __tablename__ = 'current_files'
    
    path = Column(String, primary_key=True)
    time_stamp = Column(String)
    
    def __init__ (self,path,time_stamp):
        self.path = path
        self.time_stamp = time_stamp
    
    def __repr__(self):
        return "<CurrentFile('%s','%s')>" % (self.path, self.time_stamp)
    
class HistoricFile(Base):
    __tablename__ = 'historic_files'
    
    path = Column(String, primary_key=True)
    time_stamp = Column(String, primary_key=True)
    action = Column(String)
    
    def __init__ (self,path,time_stamp,action):
        self.path = path
        self.time_stamp = time_stamp
        self.action = action
    
    def __repr__(self):
        return "<HistoricFile('%s','%s','%s')>" % (self.path, \
                                self.time_stamp, self.action)
    
class BackupHistory(Base):
    __tablename__ = 'backup_history'
    
    revision = Column(Integer, primary_key=True)
    time_stamp = Column(String)
    num_added = Column(Integer)
    num_changed = Column(Integer)
    num_removed = Column(Integer)
    in_progress = Column(Boolean)
    was_fixed = Column(Boolean)
    
    def __init__ (self,time_stamp):
        self.time_stamp = time_stamp
        self.num_added = 0
        self.num_changed = 0
        self.num_removed = 0
        self.in_progress = 1
        self.was_fixed = 0
    
    def __repr__(self):
        return "<BackupHistory('%s','%s','%s','%s','%s','%s','%s')>" % (self.revision, \
                            self.time_stamp, self.num_added, self.num_changed, \
                            self.num_removed,self.in_progress,self.was_fixed)
    
class BackupInfo(Base):
    __tablename__ = 'info'
    
    property_name = Column(String, primary_key=True)
    property_value = Column(String)
    
    def __init__ (self,name,value):
        self.property_name = name
        self.property_value = value
    
    def __repr__(self):
        return "<Info('%s','%s')>" % (self.property_name, self.property_value)