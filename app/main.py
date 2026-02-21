#!/usr/bin/env python3
"""
File: main.py
Author: James C. Hill
Created: 2026-02-02
Description:
    Description goes here.
""" 
from fastapi import FastAPI
from app.services.datasets import list_datasets

# Create the fast api app. 
app = FastAPI(title="Dataset Dashboard Backend")

@app.get("/datasets")
def datasets():
    return {"datasets": list_datasets()}

@app.get("/health")
def health():
    return {"status": "ok"}

# Note: main is here, but ignored when running an API server with uvicorn
def main():
    print(health())
    
    
# Script entry point
if __name__ == "__main__":
    main()
