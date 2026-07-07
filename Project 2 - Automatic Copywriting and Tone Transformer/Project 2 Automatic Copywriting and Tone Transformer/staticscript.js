console.log("Automatic Copywriting App Loaded");

// DOM Elements
const promptInput = document.getElementById('prompt');
const toneSelect = document.getElementById('tone');
const generateBtn = document.getElementById('generateBtn');
const outputSection = document.getElementById('outputSection');
const outputContent = document.getElementById('outputContent');
const copyBtn = document.getElementById('copyBtn');
const transformBtn = document.getElementById('transformBtn');
const transformSection = document.getElementById('transformSection');
const transformToneSelect = document.getElementById('transformTone');
const applyTransformBtn = document.getElementById('applyTransformBtn');

let currentText = '';
let currentTone = '';

// Generate Copy
generateBtn.addEventListener('click', async () => {
    const prompt = promptInput.value.trim();
    const tone = toneSelect.value;
    
    if (!prompt) {
        alert('Please enter a topic or prompt first!');
        return;
    }
    
    // Show loading state
    generateBtn.disabled = true;
    generateBtn.innerHTML = '<span class="loading"></span> Generating...';
    outputSection.style.display = 'none';
    
    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ prompt, tone })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentText = data.content;
            currentTone = tone;
            displayOutput(data.content);
            outputSection.style.display = 'block';
            transformSection.style.display = 'none';
        } else {
            showError(data.error || 'Failed to generate copy');
        }
    } catch (error) {
        showError('Network error: ' + error.message);
    } finally {
        generateBtn.disabled = false;
        generateBtn.innerHTML = 'Generate Copy ✨';
    }
});

// Transform Tone
applyTransformBtn.addEventListener('click', async () => {
    const newTone = transformToneSelect.value;
    
    if (!currentText) {
        alert('Please generate some copy first!');
        return;
    }
    
    // Show loading
    applyTransformBtn.disabled = true;
    applyTransformBtn.innerHTML = '<span class="loading"></span> Transforming...';
    
    try {
        const response = await fetch('/transform', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                text: currentText, 
                tone: newTone 
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentText = data.transformed_text;
            currentTone = newTone;
            displayOutput(data.transformed_text);
            outputSection.style.display = 'block';
            transformSection.style.display = 'none';
            showSuccess(`Tone transformed to ${newTone}!`);
        } else {
            showError(data.error || 'Failed to transform text');
        }
    } catch (error) {
        showError('Network error: ' + error.message);
    } finally {
        applyTransformBtn.disabled = false;
        applyTransformBtn.innerHTML = 'Apply Transformation';
    }
});

// Display Output
function displayOutput(text) {
    outputContent.textContent = text;
    outputContent.style.borderLeftColor = '#28a745';
}

// Show Transform Section
transformBtn.addEventListener('click', () => {
    if (!currentText) {
        alert('Please generate some copy first!');
        return;
    }
    transformSection.style.display = 'block';
    outputSection.scrollIntoView({ behavior: 'smooth' });
});

// Copy to Clipboard
copyBtn.addEventListener('click', async () => {
    if (!currentText) {
        alert('Nothing to copy!');
        return;
    }
    
    try {
        await navigator.clipboard.writeText(currentText);
        showSuccess('Copied to clipboard!');
    } catch (error) {
        // Fallback
        const textarea = document.createElement('textarea');
        textarea.value = currentText;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        showSuccess('Copied to clipboard!');
    }
});

// Helper Functions
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error';
    errorDiv.textContent = '❌ ' + message;
    errorDiv.style.marginTop = '10px';
    document.querySelector('.input-section').appendChild(errorDiv);
    setTimeout(() => errorDiv.remove(), 5000);
}

function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'success';
    successDiv.textContent = '✅ ' + message;
    successDiv.style.marginTop = '10px';
    document.querySelector('.input-section').appendChild(successDiv);
    setTimeout(() => successDiv.remove(), 3000);
}

// Keyboard shortcuts
promptInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && e.ctrlKey) {
        generateBtn.click();
    }
});

// Auto-resize textarea
promptInput.addEventListener('input', () => {
    promptInput.style.height = 'auto';
    promptInput.style.height = promptInput.scrollHeight + 'px';
});