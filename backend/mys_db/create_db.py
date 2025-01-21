import sys
import os
# Add the root directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config_parser import read_config

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from mys_db import db_tables
import requests
import os

files = os.listdir()
print("Files and directories in the current directory:", files)

config_path = "shared/config.ini"
config_values = read_config(config_path)

def load_json_data(url):
    """Load data from API."""
    return requests.get(url).json()

def preprocess_data(data):
    """Recursively replace empty strings with None in the data."""
    if isinstance(data, dict):
        return {k: preprocess_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [preprocess_data(item) for item in data]
    elif data == "":
        return None
    else:
        return data

def create_tables(session, employee_data):
    """Add employee data and related entities to the database."""
    employee = db_tables.Employee(
        name=employee_data.get('name'),
        title=employee_data.get('title'),
        organization=employee_data.get('organization'),
        level=employee_data.get('level'),
        directorate=employee_data.get('directorate'),
        score=employee_data.get('score'),
        mail=employee_data.get('mail'),
        phone=employee_data.get('phone'),
        whatsapp=employee_data.get('whatsapp'),
        birthday=employee_data.get('birthday'),
        age=employee_data.get('age'),
        birth_place=employee_data.get('birthPlace'),
        martial_status=employee_data.get('martialStatus'),
        home_address=employee_data.get('homeAddress'),
        is_absent=employee_data.get('isAbsent'),
        pre_job_duration=employee_data.get('preJobDuration'),
        pre_facade_related_job_duration=employee_data.get('preFacadeRelatedJobDuration'),
        mysStartDate=employee_data.get('mysStartDate'),
        mysDuration=employee_data.get('mysDuration'),
        mysFirstJob=employee_data.get('mysFirstJob')
    )

    if 'orgHierarchy' in employee_data:
        for org in employee_data['orgHierarchy']:
            org_hierarchy = db_tables.OrgHierarchy(
                hierarchy_level=org,
                employee=employee
            )
            session.add(org_hierarchy)

    if 'languages' in employee_data:
        for lang in employee_data['languages']:
            language = db_tables.Language(
                name=lang.get('name'),
                speaking=lang.get('speaking'),
                reading=lang.get('reading'),
                writing=lang.get('writing'),
                employee=employee
            )
            session.add(language)

    if 'softwares' in employee_data:
        for software in employee_data['softwares']:
            software_entry = db_tables.Software(
                name=software.get('name'),
                level=software.get('level'),
                practice=software.get('practice'),
                speed=software.get('speed'),
                employee=employee
            )
            session.add(software_entry)

    if 'education' in employee_data:
        for edu in employee_data['education']:
            education = db_tables.Education(
                school=edu.get('school'),
                start_date=edu.get('startDate'),
                end_date=edu.get('endDate'),
                department=edu.get('department'),
                degree=edu.get('degree'),
                school_type=edu.get('schoolType'),
                employee=employee
            )
            session.add(education)

    if 'certification' in employee_data:
        for cert in employee_data['certification']:
            certification = db_tables.Certification(
                name=cert.get('name'),
                start_date=cert.get('startDate'),
                end_date=cert.get('endDate'),
                employee=employee
            )
            session.add(certification)

    if 'workHistory' in employee_data:
        for work in employee_data['workHistory']:
            work_history = db_tables.WorkHistory(
                company=work.get('company'),
                start_date=work.get('startDate'),
                end_date=work.get('endDate'),
                department=work.get('department'),
                title=work.get('title'),
                employee=employee
            )
            session.add(work_history)

    if 'comments' in employee_data:
        for comment in employee_data['comments']:
            comment_entry = db_tables.Comment(
                comment=comment.get('comment'),
                score=comment.get('score'),
                dateTime=comment.get('dateTime'),
                evaluator=comment.get('evaluator'),
                employee=employee
            )
            session.add(comment_entry)

    if 'scores' in employee_data:
        for score_data in employee_data['scores']:
            for score_entry in score_data['scores']:
                score = db_tables.Score(
                    character=score_entry.get('character'),
                    compatibility=score_entry.get('compatibility'),
                    efficiency=score_entry.get('efficiency'),
                    technical=score_entry.get('technical'),
                    evaluator=score_entry.get('evaluator'),
                    score=score_entry.get('score'),
                    total=score_entry.get('total'),
                    employee=employee
                )
                session.add(score)
                if 'details' in score_entry and score_entry['details']:
                    details = db_tables.ScoreDetail(
                        chr1=score_entry['details'].get('chr1'),
                        chr2=score_entry['details'].get('chr2'),
                        chr3=score_entry['details'].get('chr3'),
                        chr4=score_entry['details'].get('chr4'),
                        chr5=score_entry['details'].get('chr5'),
                        cmp1=score_entry['details'].get('cmp1'),
                        cmp2=score_entry['details'].get('cmp2'),
                        cmp3=score_entry['details'].get('cmp3'),
                        cmp4=score_entry['details'].get('cmp4'),
                        cmp5=score_entry['details'].get('cmp5'),
                        cmp6=score_entry['details'].get('cmp6'),
                        cmp7=score_entry['details'].get('cmp7'),
                        cmp8=score_entry['details'].get('cmp8'),
                        cmp9=score_entry['details'].get('cmp9'),
                        cmp10=score_entry['details'].get('cmp10'),
                        cmp11=score_entry['details'].get('cmp11'),
                        eff1=score_entry['details'].get('eff1'),
                        eff2=score_entry['details'].get('eff2'),
                        eff3=score_entry['details'].get('eff3'),
                        eff4=score_entry['details'].get('eff4'),
                        eff5=score_entry['details'].get('eff5'),
                        tec1=score_entry['details'].get('tec1'),
                        tec2=score_entry['details'].get('tec2'),
                        tec3=score_entry['details'].get('tec3'),
                        tec4=score_entry['details'].get('tec4'),
                        tec5=score_entry['details'].get('tec5'),
                        tec6=score_entry['details'].get('tec6'),
                        tec7=score_entry['details'].get('tec7'),
                        tec8=score_entry['details'].get('tec8'),
                        tec9=score_entry['details'].get('tec9'),
                        tec10=score_entry['details'].get('tec10'),
                        tec11=score_entry['details'].get('tec11'),
                        tec12=score_entry['details'].get('tec12'),
                        score=score
                    )
                    session.add(details)

    if 'leaves' in employee_data:
        for leave in employee_data['leaves']:
            leave_entry = db_tables.Leaves(
                leave_type=leave.get('leaveType'),
                start_date=leave.get('startDate'),
                end_date=leave.get('endDate'),
                employee=employee
            )
            session.add(leave_entry)

    if 'mysProjects' in employee_data:
        for project in employee_data['mysProjects']:
            project_entry = db_tables.MysProject(
                manager=project.get('manager'),
                start_date=project.get('startDate'),
                end_date=project.get('endDate'),
                project_code=project.get('projectCode'),
                project_name=project.get('projectName'),
                employee=employee
            )
            session.add(project_entry)

    session.add(employee)

def create_db(db_path):
    """Create the database and insert data from JSON."""
    # Check if the database file exists
    if os.path.exists(db_path):
        os.remove(db_path)  # Delete the existing database file

    # Connect to the database
    engine = create_engine(f'sqlite:///{db_path}', echo=False, future=True)
    db_tables.Base.metadata.create_all(engine)

    # Create a session
    Session = sessionmaker(bind=engine)
    session = Session()

    # Load JSON data
    data = load_json_data(config_values['MysDB']['json_url'])
    data = preprocess_data(data)

    # Insert data
    for employee_data in data:
        create_tables(session, employee_data)

    # Commit the session
    session.commit()
    print("Database created successfully.")

if __name__ == "__main__":
    db_path = 'shared/MysFinal_db.db'
    create_db(db_path)


if __name__ == "__main__":
    db_path = 'shared/MysFinal_db.db'
    create_db(db_path)
    