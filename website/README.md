# Intelligent 8-Puzzle Solver & Search Space Visualizer

An interactive full-stack web application designed to demonstrate, analyze, and visualize classical Artificial Intelligence search strategies using an 8-puzzle sliding grid. This platform transforms pathfinding algorithms from terminal output into a visual and interactive learning experience suitable for academic demonstrations and technical presentations.

---

## Institutional Profile & Team

**Institution:** Techno Main SaltLake  
**Department:** Computer Science & Engineering(Data Science)

### Team Members

- Anuska Dey (`13030523008`)
- Avinanda Guchait (`13030523016`)
- Ayush Kumar Shaw (`13030523018`)
- Tapasi Garai (`13030523058`)

---

## Core Features

### Interactive Grid Workspace

- Manual tile movement and drag-and-drop support.
- Custom puzzle configuration creation.
- Solvable puzzle generation through intelligent shuffling.

### Solution Playback Engine

- Step backward and forward through solutions.
- Play and pause automatic solution playback.
- Real-time step tracking.

### Search Space Visualization

- View generated and expanded nodes.
- Explore discovered board states.
- Display the final solution path separately from the search tree.

### Performance Analytics

- Compare:
  - A* (Manhattan Distance)
  - A* (Misplaced Tiles)
  - Breadth-First Search (BFS)
- Logarithmic performance charts using Chart.js.
- Export benchmark results as CSV reports.

---

## Project Structure

```text
website/
├── app.py
├── solver.py
├── requirements.txt
├── README.md
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
└── templates/
    └── index.html
```

---

## Installation and Execution

Open a terminal and run:

```bash
cd website
pip install -r requirements.txt
python app.py
```

Open the application in your browser:

```text
http://127.0.0.1:5000/
```

---

## Technologies Used

- Python
- Flask
- HTML5
- CSS3
- JavaScript
- Chart.js

---

## License

This project is intended for educational and academic purposes.
