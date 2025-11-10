# Markdown Notes API

A RESTful API service that allows users to manage Markdown notes with grammar checking capabilities.

Completed as a solution to the roadmapsh markdown project - https://roadmap.sh/projects/markdown-note-taking-app

## Features

- Grammar validation for notes
- Save and store Markdown notes
- List all saved notes
- Convert and render Markdown notes to HTML

## API Endpoints

### Grammar Check
```
GET /notes/{id}/grammar
```
Validates the grammar of the provided note text.

### Save Note
```
POST /notes
```
Saves a new Markdown note to the system.

### List Notes
```
GET /notes
```
Retrieves a list of all saved Markdown notes.

### Render Note
```
GET /notes/{id}
```
Returns the Markdown note.

## Getting Started

### Prerequisites
see requirement.txt

### Installation
```bash
# Clone the repository
git clone https://github.com/chiyonofujikam/md-note-taking.git
# Navigate to project directory
cd md-note-taking

# Install dependencies
python -m pip install uv
uv sync
```

### Configuration
Create your .env file with your postgres details (owner and pg_password)

## Usage

1. Start the server:
```bash
uv run md_note_taking/manage.py runserver
```

2. The API will be available at `http://localhost:8000`
