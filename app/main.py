#!/usr/bin/env python3
"""
File: main.py
Author: James C. Hill
Created: 2026-02-02
Description:
    Description goes here.
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.services.datasets import list_datasets, readiness_check
from app.models.schema import DatasetListResponse, HealthResponse

# Create the fast api app.
app = FastAPI(title="Dataset Dashboard Backend")


@app.get("/")
def root():
    return {
        "service": "dataset-dashboard-backend",
        "status": "ok",
        "endpoints": ["/health", "/datasets", "/docs"],
    }


@app.get("/datasets", response_model=DatasetListResponse)
def datasets():
    return {"datasets": list_datasets()}


@app.get("/health", response_model=HealthResponse)
def health():
    report = readiness_check()
    status_code = 200 if report.get("ready") else 503
    return JSONResponse(content=report, status_code=status_code)
