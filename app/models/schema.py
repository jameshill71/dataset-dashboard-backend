#!/usr/bin/env python3
"""
File: schema.py
Author: James C. Hill
Created: 2026-02-02
Description:
    Description goes here.
""" 
from pydantic import BaseModel
from typing import List, Dict, Any

class DatasetMetaData(BaseModel):
    id: str
    filename: str
    row_count: int
    columns: List[str]
    size_bytes: int
    modified_time: str

class DatasetListResponse(BaseModel):
    datasets: List[DatasetMetaData]

class HealthChecks(BaseModel):
    data_dir_exists: bool
    data_dir_is_dir: bool
    csv_count: int
    csv_readable: int
    csv_unreadable: int
    errors: List[str]

class HealthResponse(BaseModel):
    status: str
    ready: bool
    datasets_found: int | None = None
    checks: HealthChecks
    
def main():
    print("Hello from schema.py")
    
# Script entry point
if __name__ == "__main__":
    main()
