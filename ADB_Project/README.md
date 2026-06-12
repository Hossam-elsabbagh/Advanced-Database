# Database Algorithms GUI Project

Advanced database project built in Python and Flask. The project combines two separate academic implementations into one working web application:

1. Buffer Pool Replacement Simulator
2. B+ Tree Indexing and Range Search Visualizer

The application provides a simple browser-based interface where users can test page replacement policies, build a B+ Tree, view its levels, inspect the leaf chain, and run range searches.

## Project Overview

This project merges the logic from two original submissions:

- A Buffer Pool simulator that supports common page replacement algorithms.
- A B+ Tree implementation that supports insertion, tree display, and range search.

Instead of keeping them as separate console-based projects, both were refactored into clean Python modules and connected to a Flask GUI.

## Features

### Buffer Pool Simulator

- Simulates page requests step by step.
- Supports the following replacement policies:
  - LRU
  - LRU-2
  - CLOCK
  - 2Q
- Shows hit and miss results.
- Shows evicted pages.
- Displays final buffer state.
- Shows extra internal state for CLOCK and 2Q.

### B+ Tree Visualizer

- Builds a B+ Tree from user-entered keys.
- Supports custom tree order.
- Inserts keys in sorted order inside leaf nodes.
- Splits leaf and internal nodes when needed.
- Displays the tree level by level.
- Displays the linked leaf chain.
- Supports range search using the leaf-level linked list.

### Web Interface

- Built using Flask, HTML, CSS, and JavaScript.
- No database setup is required.
- Runs locally in the browser.
- Uses JSON API endpoints between the frontend and backend.

## Requirements

Python 3.10 or higher is recommended.

Install the required dependency:

```bash
pip install -r requirements.txt
```

The project only requires Flask.

## How to Run Locally

Clone or download the project folder, then open a terminal inside the project directory.

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment on Windows:

```bash
.venv\Scripts\activate
```

Activate the virtual environment on macOS or Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the Flask application:

```bash
python app.py
```

Open this link in your browser:

```text
http://127.0.0.1:5000
```

## How to Use the Application

### Buffer Pool Section

1. Choose a replacement policy: LRU, LRU-2, CLOCK, or 2Q.
2. Enter the buffer size.
3. Enter a page reference sequence such as:

```text
1, 2, 3, 1, 4, 2, 5
```

4. Click Run Buffer Simulation.
5. Review the hit/miss table, evictions, and final buffer state.

### B+ Tree Section

1. Enter the tree order.
2. Enter the keys to insert such as:

```text
10, 20, 5, 15, 25, 30
```

3. Enter an optional range start and range end.
4. Click Build B+ Tree.
5. Review the tree levels, leaf chain, and range search results.

## API Endpoints

### Buffer Pool Simulation

```text
POST /api/buffer/simulate
```

Example request body:

```json
{
  "policy": "LRU",
  "size": 3,
  "pages": "1, 2, 3, 1, 4, 2, 5"
}
```

### B+ Tree Build

```text
POST /api/bplustree/build
```

Example request body:

```json
{
  "order": 3,
  "keys": "10, 20, 5, 15, 25, 30",
  "value_prefix": "Record",
  "range_start": 10,
  "range_end": 25
}
```

## Project Structure

```text
ADB_Project/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── buffer_pool.py
│   └── bplus_tree.py
├── templates/
│   └── index.html
├── static/
│   ├── style.css
│   └── script.js
├── examples/
│   └── demo.py
└── originals/
    ├── buffer_pool_original.ipynb
    ├── bplus_tree_original.zip
    └── bplus_tree_original_extracted/
```

## Main Files

### app.py

Runs the Flask server and connects the GUI to the Python modules.

### src/buffer_pool.py

Contains the BufferPool class and the logic for LRU, LRU-2, CLOCK, and 2Q.

### src/bplus_tree.py

Contains the BPlusTree and BPlusTreeNode classes, insertion logic, range search logic, and visualization helpers.

### templates/index.html

Contains the main GUI layout.

### static/style.css

Contains the interface styling.

### static/script.js

Sends requests to the Flask backend and displays results dynamically.

## How to Push to GitHub

Create a new repository on GitHub, then run these commands from inside the project folder.

Initialize Git:

```bash
git init
```

Add all project files:

```bash
git add .
```

Create the first commit:

```bash
git commit -m "Initial merged database algorithms GUI project"
```

Rename the branch to main:

```bash
git branch -M main
```

Connect your local project to your GitHub repository:

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git
```

Push the project:

```bash
git push -u origin main
```

Replace YOUR_USERNAME and YOUR_REPOSITORY_NAME with your actual GitHub username and repository name.

## Notes

- The original uploaded files are kept inside the originals folder for reference.
- The working version is refactored into src/buffer_pool.py and src/bplus_tree.py.
- The web interface does not require any external database.
- The app is suitable for demonstrating database indexing and memory management concepts in a course project.

## Author

Ahmed Ashraf

Computer Science and AI Student

Egypt
