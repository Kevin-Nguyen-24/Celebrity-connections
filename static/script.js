let selectedCelebrity1 = '';
let selectedCelebrity2 = '';
let searchTimeout1 = null;
let searchTimeout2 = null;

// Function to update example in "How it works" section
function updateExample() {
    const celeb1 = selectedCelebrity1 || celebrityDropdown1.value || 'Brad Pitt';
    const celeb2 = selectedCelebrity2 || celebrityDropdown2.value || 'BTS';
    
    document.getElementById('exampleCeleb1').textContent = celeb1;
    document.getElementById('exampleCeleb2').textContent = celeb2;
    document.getElementById('exampleStart').textContent = celeb1;
    document.getElementById('exampleEnd').textContent = celeb2;
    
    // Update the pronoun based on the name (simple heuristic)
    const pronoun = celeb1.toLowerCase().includes('band') || 
                    celeb1.toLowerCase().includes('group') || 
                    celeb1 === 'BTS' ? 'Their' : 'His/Her';
    document.getElementById('exampleStartText').textContent = `${pronoun} Wikipedia page links to...`;
}

const celebrityDropdown1 = document.getElementById('celebrityDropdown1');
const celebrityDropdown2 = document.getElementById('celebrityDropdown2');
const celebrity1Input = document.getElementById('celebrity1');
const celebrity2Input = document.getElementById('celebrity2');
const suggestions1 = document.getElementById('suggestions1');
const suggestions2 = document.getElementById('suggestions2');
const info1Div = document.getElementById('info1');
const info2Div = document.getElementById('info2');
const findConnectionBtn = document.getElementById('findConnection');
const loadingDiv = document.getElementById('loading');
const resultDiv = document.getElementById('result');
const errorDiv = document.getElementById('error');

// Load famous celebrities into dropdowns
loadCelebrities();

// Load famous celebrities
async function loadCelebrities() {
    try {
        const response = await fetch('/api/celebrities');
        const data = await response.json();
        
        if (data.celebrities) {
            data.celebrities.forEach(celeb => {
                const option1 = document.createElement('option');
                option1.value = celeb;
                option1.textContent = celeb;
                celebrityDropdown1.appendChild(option1);
                
                const option2 = document.createElement('option');
                option2.value = celeb;
                option2.textContent = celeb;
                celebrityDropdown2.appendChild(option2);
            });
        }
    } catch (error) {
        console.error('Error loading celebrities:', error);
    }
}

// Handle dropdown selection for celebrity 1
celebrityDropdown1.addEventListener('change', async (e) => {
    const selected = e.target.value;
    if (selected) {
        selectedCelebrity1 = selected;
        celebrity1Input.value = '';
        await loadCelebrityInfo(selected, info1Div);
        updateExample();
    } else {
        info1Div.classList.add('hidden');
    }
});

// Handle dropdown selection for celebrity 2
celebrityDropdown2.addEventListener('change', async (e) => {
    const selected = e.target.value;
    if (selected) {
        selectedCelebrity2 = selected;
        celebrity2Input.value = '';
        await loadCelebrityInfo(selected, info2Div);
        updateExample();
    } else {
        info2Div.classList.add('hidden');
    }
});

// Load celebrity information
async function loadCelebrityInfo(name, infoElement) {
    try {
        const response = await fetch(`/api/celebrity-info/${encodeURIComponent(name)}`);
        const data = await response.json();
        
        let entitiesHTML = '';
        if (data.entities && data.entities.length > 0) {
            entitiesHTML = '<div class="entities"><strong>Related:</strong> ';
            data.entities.forEach((entity, idx) => {
                const badge = entity.type === 'studio' ? '🎬' : 
                             entity.type === 'company' ? '🏢' : '🔗';
                entitiesHTML += `<span class="entity-badge" title="${entity.type}">${badge} ${entity.name}</span>`;
                if (idx < data.entities.length - 1) entitiesHTML += ' ';
            });
            entitiesHTML += '</div>';
        }
        
        infoElement.innerHTML = `
            <div class="info-header">ℹ️ ${data.title}</div>
            <div class="info-extract">${data.extract || 'Loading information...'}</div>
            ${entitiesHTML}
        `;
        infoElement.classList.remove('hidden');
    } catch (error) {
        console.error('Error loading celebrity info:', error);
    }
}

// Search suggestions for celebrity 1
celebrity1Input.addEventListener('input', (e) => {
    const query = e.target.value.trim();
    clearTimeout(searchTimeout1);
    celebrityDropdown1.value = ''; // Clear dropdown when typing
    
    if (query.length < 2) {
        suggestions1.classList.remove('active');
        info1Div.classList.add('hidden');
        return;
    }
    
    searchTimeout1 = setTimeout(() => {
        searchCelebrity(query, suggestions1, async (title) => {
            selectedCelebrity1 = title;
            celebrity1Input.value = title;
            suggestions1.classList.remove('active');
            await loadCelebrityInfo(title, info1Div);
            updateExample();
        });
    }, 300);
});

// Search suggestions for celebrity 2
celebrity2Input.addEventListener('input', (e) => {
    const query = e.target.value.trim();
    clearTimeout(searchTimeout2);
    celebrityDropdown2.value = ''; // Clear dropdown when typing
    
    if (query.length < 2) {
        suggestions2.classList.remove('active');
        info2Div.classList.add('hidden');
        return;
    }
    
    searchTimeout2 = setTimeout(() => {
        searchCelebrity(query, suggestions2, async (title) => {
            selectedCelebrity2 = title;
            celebrity2Input.value = title;
            suggestions2.classList.remove('active');
            await loadCelebrityInfo(title, info2Div);
            updateExample();
        });
    }, 300);
});

// Search for celebrities
async function searchCelebrity(query, suggestionsElement, onSelect) {
    try {
        const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        
        if (data.results && data.results.length > 0) {
            displaySuggestions(data.results, suggestionsElement, onSelect);
        } else {
            suggestionsElement.classList.remove('active');
        }
    } catch (error) {
        console.error('Search error:', error);
    }
}

// Display suggestions
function displaySuggestions(results, suggestionsElement, onSelect) {
    suggestionsElement.innerHTML = '';
    
    results.forEach(result => {
        const item = document.createElement('div');
        item.className = 'suggestion-item';
        item.innerHTML = `
            <div class="suggestion-title">${result.title}</div>
            <div class="suggestion-desc">${result.description}</div>
        `;
        
        item.addEventListener('click', () => {
            onSelect(result.title);
        });
        
        suggestionsElement.appendChild(item);
    });
    
    suggestionsElement.classList.add('active');
}

// Close suggestions when clicking outside
document.addEventListener('click', (e) => {
    if (!celebrity1Input.contains(e.target) && !suggestions1.contains(e.target)) {
        suggestions1.classList.remove('active');
    }
    if (!celebrity2Input.contains(e.target) && !suggestions2.contains(e.target)) {
        suggestions2.classList.remove('active');
    }
});

// Find connection button
findConnectionBtn.addEventListener('click', async () => {
    const celeb1 = selectedCelebrity1 || celebrityDropdown1.value || celebrity1Input.value.trim();
    const celeb2 = selectedCelebrity2 || celebrityDropdown2.value || celebrity2Input.value.trim();
    
    if (!celeb1 || !celeb2) {
        showError('Please enter both celebrities');
        return;
    }
    
    if (celeb1 === celeb2) {
        showError('Please select two different celebrities');
        return;
    }
    
    // Hide previous results
    resultDiv.classList.add('hidden');
    errorDiv.classList.add('hidden');
    loadingDiv.classList.remove('hidden');
    findConnectionBtn.disabled = true;
    
    try {
        const response = await fetch('/api/connect', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                start: celeb1,
                end: celeb2,
                max_depth: 7, // Six degrees of Wikipedia (degrees = max_depth - 1)
                timeout: 10   // seconds
            })
        });
        
        const data = await response.json();
        
        loadingDiv.classList.add('hidden');
        findConnectionBtn.disabled = false;
        
        if (data.success) {
            displayPath(data.path, data.length, data.details);
        } else {
            showError(data.message || 'No connection found. Try different celebrities or increase search depth.');
        }
    } catch (error) {
        loadingDiv.classList.add('hidden');
        findConnectionBtn.disabled = false;
        showError('An error occurred. Please try again.');
        console.error('Connection error:', error);
    }
});

// Display the path
function displayPath(path, length, details) {
    const pathVisualization = document.getElementById('pathVisualization');
    const pathLengthSpan = document.getElementById('pathLength');
    
    pathVisualization.innerHTML = '';
    pathLengthSpan.textContent = length;
    
    path.forEach((node, index) => {
        const detail = details && details[index] ? details[index] : null;
        
        // Add node
        const nodeDiv = document.createElement('div');
        nodeDiv.className = 'path-node';
        
        let entitiesHTML = '';
        if (detail && detail.entities && detail.entities.length > 0) {
            entitiesHTML = '<div class="node-entities">';
            detail.entities.forEach(entity => {
                const badge = entity.type === 'studio' ? '🎬' : 
                             entity.type === 'company' ? '🏢' : '🔗';
                entitiesHTML += `<span class="entity-badge" title="${entity.type}">${badge} ${entity.name}</span> `;
            });
            entitiesHTML += '</div>';
        }
        
        if (index === 0) {
            nodeDiv.classList.add('start');
            nodeDiv.innerHTML = `
                <div class="path-node-label">Start</div>
                <div class="path-node-title">${node}</div>
                ${detail && detail.extract ? `<div class="node-info">${detail.extract.substring(0, 150)}...</div>` : ''}
                ${entitiesHTML}
            `;
        } else if (index === path.length - 1) {
            nodeDiv.classList.add('end');
            nodeDiv.innerHTML = `
                <div class="path-node-label">Destination</div>
                <div class="path-node-title">${node}</div>
                ${detail && detail.extract ? `<div class="node-info">${detail.extract.substring(0, 150)}...</div>` : ''}
                ${entitiesHTML}
            `;
        } else {
            nodeDiv.innerHTML = `
                <div class="path-node-label">Step ${index}</div>
                <div class="path-node-title">${node}</div>
                ${detail && detail.extract ? `<div class="node-info">${detail.extract.substring(0, 100)}...</div>` : ''}
                ${entitiesHTML}
            `;
        }
        
        pathVisualization.appendChild(nodeDiv);
        
        // Add connector arrow (except for last node)
        if (index < path.length - 1) {
            const connector = document.createElement('div');
            connector.className = 'path-connector';
            connector.textContent = '↓';
            pathVisualization.appendChild(connector);
        }
    });
    
    resultDiv.classList.remove('hidden');
    resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Show error
function showError(message) {
    const errorMessage = document.getElementById('errorMessage');
    errorMessage.textContent = message;
    errorDiv.classList.remove('hidden');
    errorDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}
