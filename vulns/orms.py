# coding = utf8

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, TEXT, Integer, CHAR, BOOLEAN, DATE
from vulns.settings import CNNVD_TABLE, BUGTRAQ_TABLE


class CnnvdVuln(declarative_base()):
    __tablename__ = CNNVD_TABLE
    #url = Column(String(255))
    cnnvd = Column(String(127), primary_key=True)
    name = Column(TEXT)
    cve = Column(String(31))
    grade = Column(String(31))
    vuln_type = Column(TEXT)
    threat_type = Column(TEXT)
    release_time = Column(DATE)
    update_time = Column(DATE)
    vuln_desc = Column(TEXT)
    vuln_bulletin = Column(TEXT)
    ref_urls = Column(TEXT)
    source = Column(TEXT)
    vendor = Column(TEXT)
    affected = Column(TEXT)
    patch_url = Column(TEXT)


class BugtraqVuln(declarative_base()):
    __tablename__ = BUGTRAQ_TABLE
    bid = Column(Integer, primary_key=True)
    name = Column(TEXT)
    vuln_class = Column(TEXT)
    cve = Column(TEXT)
    is_remote = Column(BOOLEAN)
    is_local = Column(BOOLEAN)
    publish_date = Column(DATE)
    update_date = Column(DATE)
    credit = Column(TEXT)
    effection = Column(TEXT)
    exclude_effection = Column(TEXT)
