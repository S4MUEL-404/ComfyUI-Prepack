import { app } from "../../../scripts/app.js";
import { ComfyWidgets } from "../../../scripts/widgets.js";

const PREPACK_SEED_NODE = "PrepackSeed";

// Store seed history (max 50 items per node)
const seedHistory = new Map(); // nodeId -> array of seeds

// Generate random integer to match ComfyUI's range (approximately 13-16 digits)
function generateRandomInt() {
    // ComfyUI seems to use a range that produces 13-16 digit numbers
    // Using 2^50 which gives us numbers up to ~1.1 quadrillion (similar to ComfyUI)
    return Math.floor(Math.random() * Math.pow(2, 50));
}

// Add seed to history
function addToHistory(nodeId, seed) {
    if (!seedHistory.has(nodeId)) {
        seedHistory.set(nodeId, []);
    }
    const history = seedHistory.get(nodeId);
    // Avoid duplicates by checking if the seed is already at the top
    if (history.length === 0 || history[0] !== seed) {
        history.unshift(seed); // Add to beginning
        if (history.length > 50) {
            history.splice(50); // Keep only last 50
        }
        seedHistory.set(nodeId, history);
    }
}

// Get history as formatted string
function getHistoryString(nodeId) {
    const history = seedHistory.get(nodeId) || [];
    if (history.length === 0) {
        return "No seeds generated yet.";
    }
    return history.map((seed, index) => `${index + 1}. ${seed}`).join('\n');
}

app.registerExtension({
    name: "prepack.seed",
    
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === PREPACK_SEED_NODE) {
            const onAdded = nodeType.prototype.onAdded;
            nodeType.prototype.onAdded = function() {
                onAdded?.apply(this, arguments);
                
                // Get unique node ID
                const nodeId = this.id || Math.random().toString(36);
                
                // Find the seed widget
                const seedWidget = this.widgets.find(w => w.name === "seed");
                if (!seedWidget) {
                    console.error("Could not find seed widget in PrepackSeed node");
                    return;
                }
                
                // Create history display widget (readonly text area)
                const historyWidget = ComfyWidgets["STRING"](this, "seed_history", ["STRING", { 
                    multiline: true,
                    dynamicPrompts: false
                }], app).widget;
                historyWidget.inputEl.readOnly = true;
                historyWidget.inputEl.style.opacity = 0.8;
                historyWidget.inputEl.style.resize = "none";
                historyWidget.inputEl.style.fontSize = "11px";
                historyWidget.inputEl.style.fontFamily = "monospace";
                historyWidget.inputEl.style.lineHeight = "1.2";
                historyWidget.inputEl.style.backgroundColor = "rgba(255,255,255,.04)";
                historyWidget.inputEl.style.border = "none";
                historyWidget.inputEl.style.borderRadius = "3px";
		historyWidget.inputEl.style.padding = "8px";
                historyWidget.inputEl.style.overflow = "auto";
                historyWidget.inputEl.style.boxSizing = "border-box";
                historyWidget.name = "Seed History (Last 50)";
                
                // Use ComfyUI's default widget behavior for scaling
                // Remove any fixed sizing to let it scale naturally
                
                // Update history display
                const updateHistoryDisplay = () => {
                    historyWidget.value = getHistoryString(nodeId);
                };
                
                // Monitor seed value changes (for workflow execution)
                let lastSeedValue = seedWidget.value;
                let ignoreNextChange = false;
                
                const originalSeedCallback = seedWidget.callback;
                seedWidget.callback = function(value) {
                    const result = originalSeedCallback ? originalSeedCallback.apply(this, arguments) : value;
                    if (!ignoreNextChange && value !== lastSeedValue && value !== 0) {
                        addToHistory(nodeId, value);
                        updateHistoryDisplay();
                        lastSeedValue = value;
                    }
                    ignoreNextChange = false;
                    return result;
                };
                
                // Monitor node execution to catch runtime seed generation
                const originalOnExecuted = this.onExecuted;
                this.onExecuted = function(message) {
                    if (originalOnExecuted) {
                        originalOnExecuted.apply(this, arguments);
                    }
                    // Check if seed value changed after execution
                    setTimeout(() => {
                        if (seedWidget.value !== lastSeedValue && seedWidget.value !== 0) {
                            addToHistory(nodeId, seedWidget.value);
                            updateHistoryDisplay();
                            lastSeedValue = seedWidget.value;
                        }
                    }, 100);
                };
                
                // Backup monitoring - check periodically for seed changes
                const checkInterval = setInterval(() => {
                    if (seedWidget.value !== lastSeedValue && seedWidget.value !== 0) {
                        addToHistory(nodeId, seedWidget.value);
                        updateHistoryDisplay();
                        lastSeedValue = seedWidget.value;
                    }
                }, 1000);
                
                // Create Random button
                const randomButton = this.addWidget("button", "Random", null, () => {
                    // Generate new random integer
                    const newRandomSeed = generateRandomInt();
                    ignoreNextChange = true;
                    seedWidget.value = newRandomSeed;
                    
                    // Add to history
                    addToHistory(nodeId, newRandomSeed);
                    updateHistoryDisplay();
                    lastSeedValue = newRandomSeed;
                    
                    // Mark the graph as dirty to trigger update
                    app.graph.setDirtyCanvas(true, true);
                });
                
                // Style the button
                randomButton.computeSize = () => [seedWidget.size?.[0] || 200, 30];
                
                // Position widgets: Random button after control_after_generate, History at the end
                setTimeout(() => {
                    // Simple approach: put Random button after seed, history at the end
                    const randomButtonIndex = this.widgets.indexOf(randomButton);
                    const historyIndex = this.widgets.indexOf(historyWidget);
                    
                    if (randomButtonIndex !== -1) this.widgets.splice(randomButtonIndex, 1);
                    if (historyIndex !== -1) this.widgets.splice(this.widgets.indexOf(historyWidget), 1);
                    
                    // Find seed widget and put Random button after it
                    const seedIndex = this.widgets.indexOf(seedWidget);
                    if (seedIndex !== -1) {
                        // Check if there's a control_after_generate widget after seed
                        let insertIndex = seedIndex + 1;
                        for (let i = seedIndex + 1; i < this.widgets.length; i++) {
                            if (this.widgets[i].name && this.widgets[i].name.includes("control_after_generate")) {
                                insertIndex = i + 1;
                                break;
                            }
                        }
                        this.widgets.splice(insertIndex, 0, randomButton);
                    } else {
                        this.widgets.push(randomButton);
                    }
                    
                    // Add history widget at the end
                    this.widgets.push(historyWidget);
                }, 100);
                
                // Initialize history display
                updateHistoryDisplay();
                
                // If there's already a non-zero seed value, add it to history
                if (seedWidget.value !== 0) {
                    setTimeout(() => {
                        lastSeedValue = seedWidget.value;
                        addToHistory(nodeId, seedWidget.value);
                        updateHistoryDisplay();
                    }, 300);
                }
            };
        }
    }
});