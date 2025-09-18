from __future__ import annotations
from typing import List, Optional, Set
from pydantic import BaseModel

class Requirement(BaseModel):
    id: str
    title: str
    risk: Optional[str] = None
    tests: List[str] = []
    tags: List[str] = []
    file: Optional[str] = None
    line: Optional[int] = None

class TestCase(BaseModel):
    id: str
    file: Optional[str] = None
    line: Optional[int] = None
    requirements: List[str] = []

class Finding(BaseModel):
    rule_id: str
    severity: str   # error|warning|info
    message: str
    file: Optional[str] = None
    line: Optional[int] = None
    related_ids: List[str] = []

class Model(BaseModel):
    requirements: List[Requirement] = []
    tests: List[TestCase] = []
    junit_tests: Set[str] = set()