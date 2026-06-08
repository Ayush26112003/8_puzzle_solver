let currentState = [1, 2, 3, 4, 5, 6, 7, 8, 0];
const boardEl = document.getElementById('board');
const statusEl = document.getElementById('status');

// --- PLAYBACK VARIABLES ---
// --- PLAYBACK VARIABLES ---
let solutionStates = [];
let currentStepIndex = 0;
let playbackTimer = null;
let isPlaying = false;
let currentTreeEdges = []; // NEW: Store the search tree

// --- MERGED RENDER FUNCTION ---
function renderBoard() {
    boardEl.innerHTML = '';
    currentState.forEach((num, index) => {
        const div = document.createElement('div');
        div.className = `tile ${num === 0 ? 'empty' : ''}`;
        div.textContent = num === 0 ? '' : num;
        
        if (num !== 0) {
            div.draggable = true;
            
            div.addEventListener('dragstart', (e) => {
                e.dataTransfer.setData('text/plain', index);
                div.classList.add('dragging');
            });
            
            div.addEventListener('dragend', () => {
                div.classList.remove('dragging');
            });
        } else {
            div.addEventListener('dragover', (e) => {
                e.preventDefault(); 
                div.classList.add('drag-over');
            });
            
            div.addEventListener('dragleave', () => {
                div.classList.remove('drag-over');
            });
            
            div.addEventListener('drop', (e) => {
                e.preventDefault();
                div.classList.remove('drag-over');
                
                const dragIdx = parseInt(e.dataTransfer.getData('text/plain'));
                const emptyIdx = index;
                
                const isUp = dragIdx === emptyIdx - 3;
                const isDown = dragIdx === emptyIdx + 3;
                const isLeft = dragIdx === emptyIdx - 1 && dragIdx % 3 !== 2;
                const isRight = dragIdx === emptyIdx + 1 && dragIdx % 3 !== 0;
                
                if (isUp || isDown || isLeft || isRight) {
                    [currentState[dragIdx], currentState[emptyIdx]] = [currentState[emptyIdx], currentState[dragIdx]];
                    
                    pausePlayback();
                    document.getElementById('playback-controls').style.display = 'none';
                    
                    renderBoard(); 
                    
                    document.getElementById('val-nodes').innerText = '-';
                    document.getElementById('val-time').innerText = '-';
                    document.getElementById('val-steps').innerText = '-';
                    statusEl.innerText = "Manual move. Ready to solve.";
                    statusEl.style.color = "#888888";
                }
            });
        }
        boardEl.appendChild(div);
    });
}

function shuffleBoard() {
    pausePlayback();
    document.getElementById('playback-controls').style.display = 'none';

    let state = [1, 2, 3, 4, 5, 6, 7, 8, 0];
    let emptyIdx = 8;
    for(let i = 0; i < 40; i++) {
        const moves = [];
        if (emptyIdx >= 3) moves.push(-3);
        if (emptyIdx <= 5) moves.push(3); 
        if (emptyIdx % 3 > 0) moves.push(-1); 
        if (emptyIdx % 3 < 2) moves.push(1);  
        
        const move = moves[Math.floor(Math.random() * moves.length)];
        const targetIdx = emptyIdx + move;
        [state[emptyIdx], state[targetIdx]] = [state[targetIdx], state[emptyIdx]];
        emptyIdx = targetIdx;
    }
    
    currentState = state;
    renderBoard();
    
    document.getElementById('val-nodes').innerText = '-';
    document.getElementById('val-time').innerText = '-';
    document.getElementById('val-steps').innerText = '-';
    statusEl.innerText = "Board shuffled. Ready to solve.";
    statusEl.style.color = "#aaaaaa";
}

async function solve() {
    const btn = document.getElementById('solveBtn');
    const shuffleBtn = document.getElementById('shuffleBtn');
    const selection = document.getElementById('algorithm').value.split('-');
    
    const reqData = {
        state: currentState,
        algorithm: selection[0],
        heuristic: selection[1]
    };

    btn.disabled = true;
    shuffleBtn.disabled = true;
    statusEl.innerText = "Computing optimal path...";
    statusEl.style.color = "#F59E0B"; 

    try {
        const response = await fetch('/api/solve', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(reqData)
        });
        
        const data = await response.json();

        if (data.success) {
            document.getElementById('val-nodes').innerText = data.nodes_expanded.toLocaleString();
            document.getElementById('val-time').innerText = data.time_taken + 's';
            document.getElementById('val-steps').innerText = data.steps;
            
            // NEW: Save the edges returned by Flask
            currentTreeEdges = data.tree_edges; 
            
            statusEl.innerText = "Solution loaded! Use controls to view.";
            statusEl.style.color = "#10B981"; 
            
            preparePlayback(currentState, data.path);
        } else {
            statusEl.innerText = data.error;
            statusEl.style.color = "#EF4444"; 
        }
    } catch (error) {
        statusEl.innerText = "Server connection error.";
        statusEl.style.color = "#EF4444";
    }

    btn.disabled = false;
    shuffleBtn.disabled = false;
}

// --- PLAYBACK ENGINE ---
function preparePlayback(initialState, actions) {
    pausePlayback();
    solutionStates = [[...initialState]];
    let tempState = [...initialState];

    for (let action of actions) {
        let emptyIdx = tempState.indexOf(0);
        let targetIdx;

        if (action === 'UP') targetIdx = emptyIdx - 3;
        if (action === 'DOWN') targetIdx = emptyIdx + 3;
        if (action === 'LEFT') targetIdx = emptyIdx - 1;
        if (action === 'RIGHT') targetIdx = emptyIdx + 1;

        let nextState = [...tempState];
        [nextState[emptyIdx], nextState[targetIdx]] = [nextState[targetIdx], nextState[emptyIdx]];
        
        solutionStates.push(nextState);
        tempState = nextState;
    }

    currentStepIndex = 0;
    document.getElementById('playback-controls').style.display = 'flex';
    updateBoardState();
}

function updateBoardState() {
    currentState = [...solutionStates[currentStepIndex]];
    renderBoard(); 
    document.getElementById('step-counter').innerText = `Step ${currentStepIndex} of ${solutionStates.length - 1}`;
    
    document.getElementById('btn-prev').disabled = (currentStepIndex === 0);
    
    if (currentStepIndex === solutionStates.length - 1) {
        pausePlayback();
        document.getElementById('btn-next').disabled = true;
    } else {
        document.getElementById('btn-next').disabled = false;
    }
}

function nextStep() {
    if (currentStepIndex < solutionStates.length - 1) {
        currentStepIndex++;
        updateBoardState();
    }
}

function prevStep() {
    if (currentStepIndex > 0) {
        currentStepIndex--;
        updateBoardState();
    }
}

function togglePlay() {
    if (isPlaying) {
        pausePlayback();
    } else {
        if (currentStepIndex === solutionStates.length - 1) {
            currentStepIndex = 0;
            updateBoardState();
        }
        isPlaying = true;
        document.getElementById('btn-play').innerText = '⏸ Pause';
        playbackTimer = setInterval(nextStep, 400); 
    }
}

function pausePlayback() {
    isPlaying = false;
    clearInterval(playbackTimer);
    
    const playBtn = document.getElementById('btn-play');
    if(playBtn) playBtn.innerText = '▶ Play';
}

// Initial render
renderBoard();

// --- COMPARATIVE ANALYTICS ENGINE ---
let comparisonData = null;
let comparisonChart = null;

async function runComparison() {
    const btn = document.getElementById('compareBtn');
    btn.disabled = true;
    statusEl.innerText = "Running all algorithms. This may take a moment...";
    statusEl.style.color = "#8B5CF6";

    try {
        const response = await fetch('/api/compare', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ state: currentState })
        });
        
        const data = await response.json();
        if (data.success) {
            comparisonData = data.results;
            showModal();
            statusEl.innerText = "Comparison complete.";
            statusEl.style.color = "#10B981";
        }
    } catch (error) {
        console.error("Comparison Error Details:", error);
        statusEl.innerText = "Comparison failed.";
        statusEl.style.color = "#EF4444";
    }
    btn.disabled = false;
}

function showModal() {
    document.getElementById('analyticsModal').style.display = 'flex';
    
    const labels = comparisonData.map(d => d.algorithm);
    const nodesData = comparisonData.map(d => d.nodes_expanded === 'Skipped (Too Deep)' ? 0 : d.nodes_expanded);
    
    const ctx = document.getElementById('comparisonChart').getContext('2d');
    
    // Destroy old chart if it exists
    if (comparisonChart) comparisonChart.destroy();
    
    comparisonChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Nodes Expanded (Lower is Better)',
                data: nodesData,
                backgroundColor: ['#3B82F6', '#10B981', '#F59E0B'],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { 
                    type: 'logarithmic', // Log scale because BFS explores exponentially more
                    grid: { color: '#333' },
                    ticks: { color: '#aaa' }
                },
                x: {
                    grid: { color: '#333' },
                    ticks: { color: '#aaa', font: { size: 14 } }
                }
            },
            plugins: {
                legend: { labels: { color: '#fff' } }
            }
        }
    });
}

function closeModal() {
    document.getElementById('analyticsModal').style.display = 'none';
}

function downloadCSV() {
    if (!comparisonData) return;
    
    let csvContent = "data:text/csv;charset=utf-8,";
    csvContent += "Algorithm,Nodes Expanded,Time Taken (s),Path Steps\n";
    
    comparisonData.forEach(row => {
        csvContent += `"${row.algorithm}","${row.nodes_expanded}","${row.time_taken}","${row.steps}"\n`;
    });
    
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "8_puzzle_performance_report.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// --- EXPLORED NODES VISUALIZER ---

function viewExploredNodes() {
    if (!currentTreeEdges || currentTreeEdges.length === 0) {
        alert("Please run 'Calculate & Solve' first to generate a search tree.");
        return;
    }

    const container = document.getElementById('explored-grids');
    container.innerHTML = ''; // Clear previous grids

    // Update subtitle based on how many nodes we are actually showing
    const displayCount = Math.min(currentTreeEdges.length, 500);
    document.getElementById('explored-subtitle').innerText = 
        `Displaying ${displayCount} states explored by the algorithm (in order of generation).`;

    // Loop through the edges and draw the mini boards
    for (let i = 0; i < displayCount; i++) {
        const edge = currentTreeEdges[i];
        const state = edge[1]; // The newly discovered child state

        const boardDiv = document.createElement('div');
        boardDiv.className = 'mini-board';

        state.forEach(num => {
            const tile = document.createElement('div');
            tile.className = `mini-tile ${num === 0 ? 'empty' : ''}`;
            tile.textContent = num === 0 ? '' : num;
            boardDiv.appendChild(tile);
        });

        container.appendChild(boardDiv);
    }

    document.getElementById('exploredModal').style.display = 'flex';
}

function closeExploredModal() {
    document.getElementById('exploredModal').style.display = 'none';
}

// --- SOLUTION PATH VISUALIZER ---

function viewSolutionPath() {
    if (!solutionStates || solutionStates.length === 0) {
        alert("Please run 'Calculate & Solve' first to generate the solution path.");
        return;
    }

    const container = document.getElementById('path-sequence-grids');
    container.innerHTML = ''; // Clear out old elements

    solutionStates.forEach((state, index) => {
        // Create a wrapper for each individual step board and its label
        const boardWrapper = document.createElement('div');
        boardWrapper.style.textAlign = 'center';

        // Add step indicator text above the board
        const label = document.createElement('div');
        label.style.fontSize = '12px';
        label.style.color = '#888';
        label.style.marginBottom = '5px';
        label.style.fontWeight = 'bold';
        label.innerText = index === 0 ? 'Start' : `Step ${index}`;
        boardWrapper.appendChild(label);

        // Build the mini 3x3 board
        const boardDiv = document.createElement('div');
        boardDiv.className = 'mini-board'; // Reuses your existing mini-board layout rules
        
        // Give the final target state a distinct green border accent
        if (index === solutionStates.length - 1) {
            boardDiv.style.border = '2px solid #10B981';
        }

        state.forEach(num => {
            const tile = document.createElement('div');
            tile.className = `mini-tile ${num === 0 ? 'empty' : ''}`;
            tile.textContent = num === 0 ? '' : num;
            boardDiv.appendChild(tile);
        });

        boardWrapper.appendChild(boardDiv);
        container.appendChild(boardWrapper);

        // Inject a transitional arrow between steps if it isn't the final state
        if (index < solutionStates.length - 1) {
            const arrow = document.createElement('div');
            arrow.className = 'path-arrow';
            arrow.innerText = '→';
            container.appendChild(arrow);
        }
    });

    document.getElementById('solutionPathModal').style.display = 'flex';
}

function closeSolutionPathModal() {
    document.getElementById('solutionPathModal').style.display = 'none';
}