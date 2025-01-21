""" 
Unfortunately SQLAlchemy does not support importing table objects from other directories.
I had to write such a big piece of code because dividing this code into smaller pieces didnt work.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, REAL
from sqlalchemy.orm import relationship, declarative_base

"""
1. Start by calling the base class.
2. Then call the child classes.
3. If a child class has its own child classes, call those first before the parent child class.
4. Finally, call the parent class again.
"""

Base = declarative_base()

class OrgHierarchy(Base):
    __tablename__ = 'orgHierarchy'
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    hierarchy_level = Column(String, nullable=True)
    employee = relationship('Employee', back_populates='orgHierarchy')

class Language(Base):
    __tablename__ = 'languages'
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    name = Column(String)
    speaking = Column(Integer)
    reading = Column(Integer)
    writing = Column(Integer)
    
class Software(Base):
    __tablename__ = 'softwares'
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    name = Column(String)
    level = Column(Integer)
    practice = Column(Integer)
    speed = Column(Integer)

class Education(Base):
    __tablename__ = 'educations'
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    school = Column(String, nullable=True)
    start_date = Column(String, nullable=True)
    end_date = Column(String, nullable=True)
    department = Column(String, nullable=True)
    degree = Column(REAL, nullable=True) 
    school_type = Column(String, nullable=True)
    
class Certification(Base):
    __tablename__ = 'certification'
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    name = Column(String)
    start_date = Column(String, nullable=True)
    end_date = Column(String, nullable=True)
    
class WorkHistory(Base):
    __tablename__ = 'workHistory'
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    company = Column(String, nullable=True)
    start_date = Column(String, nullable=True)
    end_date = Column(String, nullable=True)
    department = Column(String, nullable=True)
    title = Column(String, nullable=True)

class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    comment = Column(String, nullable=True)
    score = Column(String, nullable=True)
    dateTime = Column(String, nullable=True)
    evaluator = Column(String, nullable=True)

class ScoreDetail(Base):
    __tablename__ = 'score_details'
    id = Column(Integer, primary_key=True, autoincrement=True)
    score_id = Column(Integer, ForeignKey('scores.id'))
    chr1 = Column(Integer)
    chr2 = Column(Integer)
    chr3 = Column(Integer)
    chr4 = Column(Integer)
    chr5 = Column(Integer)
    cmp1 = Column(Integer)
    cmp2 = Column(Integer)
    cmp3 = Column(Integer)
    cmp4 = Column(Integer)
    cmp5 = Column(Integer)
    cmp6 = Column(Integer)
    cmp7 = Column(Integer)
    cmp8 = Column(Integer)
    cmp9 = Column(Integer)
    cmp10 = Column(Integer)
    cmp11 = Column(Integer)
    eff1 = Column(Integer)
    eff2 = Column(Integer)
    eff3 = Column(Integer)
    eff4 = Column(Integer)
    eff5 = Column(Integer)
    tec1 = Column(Integer)
    tec2 = Column(Integer)
    tec3 = Column(Integer)
    tec4 = Column(Integer)
    tec5 = Column(Integer)
    tec6 = Column(Integer)
    tec7 = Column(Integer)
    tec8 = Column(Integer)
    tec9 = Column(Integer)
    tec10 = Column(Integer)
    tec11 = Column(Integer)
    tec12 = Column(Integer)

class Score(Base):
    __tablename__ = 'scores'
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    character = Column(Integer)
    compatibility = Column(Integer)
    efficiency = Column(Integer)
    technical = Column(Integer)
    details = relationship('ScoreDetail', backref='score')
    evaluator = Column(String, nullable=True)
    score = Column(REAL)
    total = Column(Integer)
    
class Leaves(Base):
    __tablename__ = 'leaves'
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    leave_type = Column(String, nullable=True)
    start_date = Column(String, nullable=True)
    end_date = Column(String, nullable=True)

class MysProject(Base):
    __tablename__ = 'mysProjects'
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    manager = Column(String, nullable=True)
    start_date = Column(String, nullable=True)
    end_date = Column(String, nullable=True)
    project_code = Column(String, nullable=True)
    project_name = Column(String, nullable=True)

class Employee(Base):
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    title = Column(String, nullable=True)
    organization = Column(String, nullable=True)
    orgHierarchy = relationship('OrgHierarchy', back_populates='employee')
    level = Column(Integer)
    directorate = Column(String, nullable=True)
    score = Column(REAL)
    mail = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    whatsapp = Column(String, nullable=True)
    birthday = Column(String, nullable=True)
    age = Column(Integer)
    birth_place = Column(String, nullable=True)
    martial_status = Column(String, nullable=True)
    home_address = Column(String, nullable=True)
    is_absent = Column(Integer)
    languages = relationship('Language', backref='employee')
    softwares = relationship('Software', backref='employee')
    education = relationship('Education', backref='employee')
    certification = relationship('Certification', backref='employee')
    work_history = relationship('WorkHistory', backref='employee')
    pre_job_duration = Column(String, nullable=True)
    pre_facade_related_job_duration = Column(REAL)
    comments = relationship('Comment', backref='employee')
    scores = relationship('Score', backref='employee')
    mysStartDate = Column(String, nullable=True)
    mysDuration = Column(REAL)
    mysFirstJob = Column(String, nullable=True)
    leaves = relationship('Leaves', backref='employee')
    mysProjects = relationship('MysProject', backref='employee')