# Inventory Management Dashboard

A full-stack inventory management system for Open Project.

## Live Demo

- **App URL:** [Add your Render URL here]

## Features

- View, add, edit, and delete inventory items
- Data science insights with category breakdown and low stock alerts
- ML-powered shelf reconciliation system
- Natural language query interface

## Tech Stack

- **Frontend:** React 18
- **Backend:** Node.js + Express
- **Data Science:** Python, Pandas, Matplotlib
- **ML Pipeline:** Python with threshold-based reconciliation

## Local Development

```bash
# Install dependencies
npm install

# Start server
npm start

# Open http://localhost:3000
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/inventory | Get all items |
| POST | /api/inventory | Add new item |
| PUT | /api/inventory/:id | Update item |
| DELETE | /api/inventory/:id | Delete item |

## Python Scripts

```bash
# Data science analysis
python analysis/inventory_analysis.py

# ML pipeline
python ml/classifier.py
python ml/threshold_policy.py
python ml/reconciliation.py

# LLM prompt generator
python llm/chat_prompt.py
```
