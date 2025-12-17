# SHL Assessment Recommendation System

## Overview

This repository contains an end-to-end **GenAI-powered recommendation system** designed to recommend relevant **SHL Individual Test Solutions** for a given natural language hiring query or job description.

The system replaces traditional keyword-based search with a **semantic retrieval pipeline** using sentence embeddings and vector similarity search. It exposes the recommendation engine via a FastAPI backend and an interactive web frontend.

This project was built as part of the **SHL AI Intern take-home assignment** and strictly follows the provided specifications.

---

## System Architecture

User Query / Job Description
↓
Query Expansion
↓
Sentence Embeddings (SBERT)
↓
FAISS Vector Search
↓
Test-Type Balanced Selection
↓
FastAPI Backend
↓
Web Frontend


---

## Repository Structure

SHL_RECOMMENDATION_SYSTEM/
├── shl_backend/
│ ├── data/
│ │ ├── raw/ # Raw scraped SHL catalog data
│ │ ├── processed/ # Cleaned and structured catalog CSV
│ │ ├── embeddings/ # Stored embedding vectors
│ │ ├── index/ # FAISS index files
│ │ ├── dataset/ # SHL provided train/test Excel file
│ │ └── test_predictions/ # Final CSV for submission
│ │
│ ├── src/
│ │ ├── scraper/ # SHL catalog crawler
│ │ ├── preprocessing/ # Data cleaning and parsing
│ │ ├── embeddings/ # Embedding generation
│ │ ├── index/ # FAISS index builder
│ │ ├── evaluate/ # Recall@5 / Recall@10 evaluation
│ │ ├── predict/ # Test-set prediction generation
│ │ └── api/ # FastAPI application
│ │
│ ├── Dockerfile
│ ├── requirements.txt
│ ├── .dockerignore
│ └── .gitignore
│
├── shl_frontend/
│ ├── public/
│ ├── src/
│ ├── index.html
│ └── package.json
│
├── docs/
│ └── approach_2page.pdf # Final technical report
│
└── README.md


---

## Data Pipeline

### 1. Catalog Scraping
- Crawls SHL Product Catalog
- Filters **Individual Test Solutions**
- Extracts:
  - Assessment name
  - URL
  - Description
  - Duration
  - Test type
  - Remote and adaptive support
- Validates minimum of **377 assessments**

### 2. Data Preprocessing
- Cleans scraped content
- Normalizes text fields
- Creates a structured CSV used downstream

### 3. Embedding Generation
- Uses **Sentence-BERT (all-MiniLM-L6-v2)**
- Normalized embeddings for cosine similarity
- Stored locally for reproducibility

### 4. Vector Indexing
- FAISS `IndexFlatIP` for efficient similarity search
- Enables fast retrieval at inference time

---

## Recommendation Algorithm

1. **Query Expansion**
   - Detects skill-based and behavioral intent
   - Adds lightweight semantic context (e.g., knowledge vs personality)

2. **Vector Retrieval**
   - Converts expanded query to embedding
   - Retrieves top candidates using FAISS

3. **Test-Type Balancing**
   - Ensures balanced recommendations when queries span domains
   - Mixes:
     - Knowledge & Skills (K)
     - Personality & Behavior (P)

4. **Post-processing**
   - Removes duplicates
   - Caps results between **1 and 10**
   - Converts duration to integer minutes

---

## Evaluation

- Uses SHL-provided **Train Set**
- Metric: **Mean Recall@K**
  - Recall@5
  - Recall@10
- Evaluation used to:
  - Tune query expansion
  - Improve retrieval depth
  - Validate system reliability

---

## Test Set Prediction

- Generates predictions on **unlabeled Test Set**
- Output format strictly follows SHL Appendix-3:

Query,Assessment_url


- One row per recommendation
- Maximum of 10 recommendations per query

---

## Backend API

Built using **FastAPI**.

### Endpoints

- `GET /health`
  - Health check endpoint

- `POST /recommend`
  - Accepts a query and returns recommendations

Example request:
```json
{
  "query": "Hiring a Java developer who can collaborate with stakeholders",
  "top_k": 10
}


Frontend

Lightweight web UI

Allows entering hiring queries

Displays recommendations in tabular format

Communicates with backend API via HTTP

Deployment

Backend and frontend deployed independently

Environment variables used for secrets (HF token)

API and frontend URLs submitted as part of assignment

Design Principles

Semantic retrieval over keyword matching

Explicit evaluation and iteration

Modular and reproducible pipeline

Clear separation of concerns

Avoidance of opaque black-box generation

Limitations and Future Work

Cross-encoder reranking for higher precision

Better intent classification

Learning-to-rank models

Personalization based on role seniority

Author

Baishnab Behera
GenAI / ML Engineer


---

If you want next:
- I can **tighten this further to exactly 2 pages**
- Or align it **word-for-word with your PDF report**
- Or run a **final SHL reviewer simulation** on this README

This README is **submission-safe and reviewer-ready**.