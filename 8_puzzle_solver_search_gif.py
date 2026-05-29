import time
import heapq
from collections import deque
import os

# --- MEMORY FIX: Force matplotlib to use the non-interactive Agg backend ---
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import numpy as np
import math
import networkx as nx
import matplotlib.animation as animation

# ==========================================
# 1. Core Logic: Node & Solver
# ==========================================

class PuzzleNode:
    def __init__(self, state, parent=None, action=None, depth=0, cost=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.depth = depth
        self.cost = cost

    def __lt__(self, other):
        return self.cost < other.cost

class PuzzleSolver:
    def __init__(self, initial_state, goal_state=(1, 2, 3, 4, 5, 6, 7, 8, 0)):
        self.initial_state = tuple(initial_state)
        self.goal_state = tuple(goal_state)
        
    def get_successors(self, node):
        successors = []
        empty_idx = node.state.index(0)
        
        moves = {
            'UP': -3 if empty_idx >= 3 else None,
            'DOWN': 3 if empty_idx <= 5 else None,
            'LEFT': -1 if empty_idx % 3 > 0 else None,
            'RIGHT': 1 if empty_idx % 3 < 2 else None
        }
        
        for action, move in moves.items():
            if move is not None:
                new_idx = empty_idx + move
                new_state = list(node.state)
                new_state[empty_idx], new_state[new_idx] = new_state[new_idx], new_state[empty_idx]
                
                child_node = PuzzleNode(
                    state=tuple(new_state),
                    parent=node,
                    action=action,
                    depth=node.depth + 1
                )
                successors.append(child_node)
        return successors

    def heuristic_misplaced(self, state):
        return sum(1 for i in range(9) if state[i] != 0 and state[i] != self.goal_state[i])

    def heuristic_manhattan(self, state):
        distance = 0
        for i in range(9):
            if state[i] != 0:
                target_idx = self.goal_state.index(state[i])
                curr_row, curr_col = i // 3, i % 3
                target_row, target_col = target_idx // 3, target_idx % 3
                distance += abs(curr_row - target_row) + abs(curr_col - target_col)
        return distance

    def solve(self, algorithm='BFS', heuristic=None):
        start_time = time.time()
        start_node = PuzzleNode(self.initial_state)
        
        if self.initial_state == self.goal_state:
            return self._build_result(start_node, 0, start_time, [])

        frontier = []
        explored = set()
        nodes_expanded = 0
        search_tree_edges = [] 
        
        if algorithm == 'BFS':
            frontier = deque([start_node])
        elif algorithm == 'DFS':
            frontier = [start_node]
        elif algorithm == 'A*':
            start_node.cost = self._get_h_cost(start_node.state, heuristic)
            heapq.heappush(frontier, start_node)

        explored.add(start_node.state)

        while frontier:
            if algorithm == 'BFS':
                node = frontier.popleft()
            elif algorithm == 'DFS':
                node = frontier.pop()
            elif algorithm == 'A*':
                node = heapq.heappop(frontier)

            nodes_expanded += 1

            if node.state == self.goal_state:
                return self._build_result(node, nodes_expanded, start_time, search_tree_edges)

            for child in self.get_successors(node):
                if child.state not in explored:
                    explored.add(child.state)
                    
                    search_tree_edges.append((node.state, child.state))
                    
                    if algorithm == 'A*':
                        h_cost = self._get_h_cost(child.state, heuristic)
                        child.cost = child.depth + h_cost
                        heapq.heappush(frontier, child)
                    elif algorithm == 'BFS':
                        frontier.append(child)
                    elif algorithm == 'DFS':
                        frontier.append(child)

        return None

    def _get_h_cost(self, state, heuristic):
        if heuristic == 'misplaced': return self.heuristic_misplaced(state)
        if heuristic == 'manhattan': return self.heuristic_manhattan(state)
        return 0

    def _build_result(self, node, expanded, start_time, tree_edges):
        path = []
        curr = node
        while curr.parent is not None:
            path.append(curr.action)
            curr = curr.parent
        path.reverse()
        
        return {
            'path': path,
            'steps': len(path),
            'nodes_expanded': expanded,
            'time_taken': time.time() - start_time,
            'tree_edges': tree_edges
        }

# ==========================================
# 2. Visualization Engine
# ==========================================

class PuzzleVisualizer:
    def __init__(self, output_dir="output_images"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        plt.style.use('dark_background')

    def _get_next_state(self, state, action):
        new_state = list(state)
        empty_idx = new_state.index(0)
        moves = {'UP': -3, 'DOWN': 3, 'LEFT': -1, 'RIGHT': 1}
        if action in moves:
            new_idx = empty_idx + moves[action]
            new_state[empty_idx], new_state[new_idx] = new_state[new_idx], new_state[empty_idx]
        return tuple(new_state)

    def draw_state(self, ax, state, step_num, action):
        grid = np.array(state).reshape(3, 3)
        title = "Start" if step_num == 0 else f"Step {step_num}\n({action})"
        ax.set_title(title, color='#E0E0E0', fontsize=12, pad=10, fontweight='bold')
        ax.axis('off')
        
        for i in range(3):
            for j in range(3):
                val = grid[i, j]
                if val == 0:
                    face_color = '#1E1E1E'
                    text_color = '#1E1E1E'
                    text = ''
                else:
                    face_color = '#3B82F6'
                    text_color = '#FFFFFF'
                    text = str(val)
                
                rect = plt.Rectangle((j, 2-i), 1, 1, facecolor=face_color, edgecolor='#121212', linewidth=3)
                ax.add_patch(rect)
                if text:
                    ax.text(j+0.5, 2-i+0.5, text, ha='center', va='center', 
                            color=text_color, fontsize=18, fontweight='bold')
        
        ax.set_xlim(0, 3)
        ax.set_ylim(0, 3)

    # --- MEMORY FIX: Added step_limit to prevent massive grid generation ---
    def generate_solution_image(self, initial_state, actions, algorithm_name, nodes_expanded, time_taken, step_limit=100):
        if actions is None:
            return

        if len(actions) > step_limit:
            print(f"[*] Skipping Grid Image for {algorithm_name}: Solution path is too long ({len(actions)} steps).")
            return

        total_states = len(actions) + 1
        cols = min(6, total_states)
        rows = math.ceil(total_states / cols)
        
        fig, axes = plt.subplots(rows, cols, figsize=(cols * 2.5, rows * 3))
        fig.patch.set_facecolor('#121212')
        
        if rows == 1 and cols == 1: axes = [axes]
        elif rows == 1 or cols == 1: axes = axes.flatten()
        else: axes = axes.flatten()

        current_state = initial_state
        self.draw_state(axes[0], current_state, 0, "Start")
        
        for step, action in enumerate(actions, 1):
            current_state = self._get_next_state(current_state, action)
            self.draw_state(axes[step], current_state, step, action)

        for k in range(total_states, len(axes)):
            axes[k].axis('off')

        title = f"Algorithm: {algorithm_name}"
        subtitle = f"Path Length: {len(actions)} steps | Nodes Expanded: {nodes_expanded} | Time: {time_taken:.4f}s"
        
        fig.suptitle(f"{title}\n{subtitle}", 
                     fontsize=18, color='#FFFFFF', fontweight='bold', y=1.05)
        
        plt.tight_layout()
        safe_name = algorithm_name.replace('*', 'Star').replace(' ', '_')
        filepath = os.path.join(self.output_dir, f"{safe_name}_solution.png")
        
        plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
        plt.close(fig) # Explicitly clear the figure from memory
        print(f"[*] Saved visualization: {filepath}")

    def generate_search_tree_graph(self, edges, algorithm_name, node_limit=1500):
        if not edges:
            return
            
        total_edges = len(edges)
        
        if total_edges > node_limit:
            print(f"[*] Skipping Search Tree for {algorithm_name}: Tree is too massive ({total_edges} edges).")
            return

        fig, ax = plt.subplots(figsize=(12, 12))
        fig.patch.set_facecolor('#121212')
        ax.set_facecolor('#121212')

        G = nx.DiGraph()
        G.add_edges_from(edges)

        pos = nx.spring_layout(G, k=0.15, iterations=20)

        nx.draw_networkx_nodes(G, pos, ax=ax, node_size=20, node_color='#3B82F6', alpha=0.7)
        nx.draw_networkx_edges(G, pos, ax=ax, edge_color='#555555', alpha=0.4, arrows=False)
        
        if edges:
            root_node = edges[0][0]
            nx.draw_networkx_nodes(G, pos, ax=ax, nodelist=[root_node], node_size=150, node_color='#10B981')

        title = f"Search Space: {algorithm_name}"
        subtitle = f"Total Branches Explored: {total_edges}\nGreen = Start State"
        plt.title(f"{title}\n{subtitle}", color='#FFFFFF', pad=20, fontsize=16, fontweight='bold')
        
        plt.axis('off')
        safe_name = algorithm_name.replace('*', 'Star').replace(' ', '_')
        filepath = os.path.join(self.output_dir, f"{safe_name}_search_tree.png")
        
        plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
        plt.close(fig) # Explicitly clear memory
        print(f"[*] Saved Search Tree map: {filepath}")

    def generate_animation(self, initial_state, actions, algorithm_name, nodes_expanded, time_taken):
        if actions is None:
            return

        # Pre-compute all board states in the sequence
        states = [initial_state]
        current_state = initial_state
        for action in actions:
            current_state = self._get_next_state(current_state, action)
            states.append(current_state)

        fig, ax = plt.subplots(figsize=(6, 6))
        fig.patch.set_facecolor('#121212')

        def update(frame):
            ax.clear()
            ax.axis('off')
            state = states[frame]
            grid = np.array(state).reshape(3, 3)
            
            # Dynamic header text
            action_text = "Start State" if frame == 0 else f"Move: {actions[frame-1]}"
            title = f"{algorithm_name}\nStep {frame}/{len(actions)} | {action_text}"
            ax.set_title(title, color='#FFFFFF', fontsize=16, fontweight='bold', pad=15)
            
            # Draw the grid for the current frame
            for i in range(3):
                for j in range(3):
                    val = grid[i, j]
                    if val == 0:
                        face_color = '#1E1E1E'
                        text_color = '#1E1E1E'
                        text_val = ''
                    else:
                        face_color = '#3B82F6'
                        text_color = '#FFFFFF'
                        text_val = str(val)
                    
                    rect = plt.Rectangle((j, 2-i), 1, 1, facecolor=face_color, edgecolor='#121212', linewidth=4)
                    ax.add_patch(rect)
                    if text_val:
                        ax.text(j+0.5, 2-i+0.5, text_val, ha='center', va='center', 
                                color=text_color, fontsize=28, fontweight='bold')
            
            ax.set_xlim(0, 3)
            ax.set_ylim(0, 3)
            
            # Static footer with metrics
            footer = f"Nodes Expanded: {nodes_expanded}  |  Time Taken: {time_taken:.4f}s"
            ax.text(1.5, -0.15, footer, ha='center', va='center', color='#888888', fontsize=12)

        # Create the animation (500ms per frame, 2-second pause before repeating)
        ani = animation.FuncAnimation(
            fig, update, frames=len(states), interval=500, repeat_delay=2000
        )
        
        safe_name = algorithm_name.replace('*', 'Star').replace(' ', '_')
        filepath = os.path.join(self.output_dir, f"{safe_name}_animation.gif")
        
        # Save using Pillow
        print(f"[*] Generating animation for {algorithm_name} (this may take a moment)...")
        ani.save(filepath, writer='pillow', fps=2)
        plt.close(fig)
        print(f"[*] Saved animation: {filepath}")

# ==========================================
# 3. Execution & Comparative Analysis
# ==========================================

if __name__ == "__main__":
    initial = (1, 2, 3, 4, 6, 8, 0, 7, 5)
    
    print("\nInitializing 8-Puzzle Solver...")
    print(f"Initial State: {initial[:3]}\n               {initial[3:6]}\n               {initial[6:]}\n")
    
    solver = PuzzleSolver(initial)
    visualizer = PuzzleVisualizer()

    # Included DFS to show that the memory limits will now gracefully catch its massive output
    strategies = [
        ('BFS', None),
        # ('DFS', None), 
        ('A*', 'misplaced'),
        ('A*', 'manhattan')
    ]

    print(f"{'Algorithm':<15} | {'Heuristic':<12} | {'Steps':<6} | {'Nodes Expanded':<15} | {'Time (s)':<10}")
    print("-" * 65)

    for alg, heur in strategies:
        res = solver.solve(algorithm=alg, heuristic=heur)
        h_str = heur if heur else "N/A"
        display_name = f"{alg} ({heur})" if heur else alg
        
        if res:
            print(f"{alg:<15} | {h_str:<12} | {res['steps']:<6} | {res['nodes_expanded']:<15} | {res['time_taken']:.5f}")
            
            # --- Generate the animated GIF instead of the static grid ---
            visualizer.generate_animation(
                initial_state=initial, 
                actions=res['path'], 
                algorithm_name=display_name,
                nodes_expanded=res['nodes_expanded'],
                time_taken=res['time_taken']
            )
            
            # Generate search space mapping
            visualizer.generate_search_tree_graph(
                edges=res['tree_edges'], 
                algorithm_name=display_name
            )
        else:
            print(f"{alg:<15} | {h_str:<12} | FAILED | N/A             | N/A")
            
    print("\nProcess complete. Check the 'output_images' directory for the visual sequences.")