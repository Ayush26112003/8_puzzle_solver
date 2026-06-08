from flask import Flask, render_template, request, jsonify
from solver import PuzzleSolver

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/solve', methods=['POST'])
def solve_puzzle():
    data = request.get_json()
    
    # Extract data from the frontend
    initial_state = tuple(data.get('state', []))
    algorithm = data.get('algorithm', 'A*')
    heuristic = data.get('heuristic', 'manhattan')

    # Catch invalid states
    if len(initial_state) != 9 or set(initial_state) != set(range(9)):
        return jsonify({'error': 'Invalid board state provided.'}), 400

    # Initialize and run the solver
    solver = PuzzleSolver(initial_state)
    result = solver.solve(algorithm=algorithm, heuristic=heuristic)

    # Inside your @app.route('/api/solve', methods=['POST'])
    if result:
        return jsonify({
            'success': True,
            'path': result['path'],
            'steps': result['steps'],
            'nodes_expanded': result['nodes_expanded'],
            'time_taken': round(result['time_taken'], 4),
            # NEW: Send the first 500 explored edges to prevent browser DOM crashing
            'tree_edges': result['tree_edges'][:500] 
        })
    else:
        return jsonify({'success': False, 'error': 'No solution found or state is unsolvable.'})

@app.route('/api/compare', methods=['POST'])
def compare_algorithms():
    data = request.get_json()
    initial_state = tuple(data.get('state', []))

    if len(initial_state) != 9 or set(initial_state) != set(range(9)):
        return jsonify({'error': 'Invalid board state provided.'}), 400

    solver = PuzzleSolver(initial_state)
    strategies = [
        ('A*', 'manhattan'),
        ('A*', 'misplaced'),
        ('BFS', None)
    ]
    
    results = []
    for alg, heur in strategies:
        # Failsafe for BFS on hard boards to prevent server timeouts
        if alg == 'BFS' and solver.heuristic_manhattan(initial_state) > 16:
            results.append({
                'algorithm': 'BFS',
                'nodes_expanded': 'Skipped (Too Deep)',
                'time_taken': 'N/A',
                'steps': 'N/A'
            })
            continue
            
        res = solver.solve(algorithm=alg, heuristic=heur)
        display_name = f"{alg} ({heur})" if heur else alg
        
        if res:
            results.append({
                'algorithm': display_name,
                'nodes_expanded': res['nodes_expanded'],
                'time_taken': round(res['time_taken'], 4),
                'steps': res['steps']
            })

    return jsonify({'success': True, 'results': results})


if __name__ == '__main__':
    app.run(debug=True)