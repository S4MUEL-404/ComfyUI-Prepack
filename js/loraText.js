import { app } from "../../../scripts/app.js";
import { ComfyWidgets } from "../../../scripts/widgets.js";
import { api } from "../../../scripts/api.js";

const PREPACK_LORAS_NODE = "PrepackLoras";

// Enhanced URI encoding for safe API calls
function encodeURIComponent2(str) {
    if (!str || typeof str !== 'string') {
        return '';
    }
    return encodeURIComponent(str).replace(/[!'()*]/g, (c) => `%${c.charCodeAt(0).toString(16).toUpperCase()}`);
}

// Sanitize text content to prevent XSS
function sanitizeText(text) {
    if (!text || typeof text !== 'string') {
        return '';
    }
    return text.replace(/[<>"'&]/g, (char) => {
        const entities = {
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;',
            '&': '&amp;'
        };
        return entities[char] || char;
    });
}

// Debounce utility function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Show user-friendly error message
function showErrorNotification(message) {
    console.error(message);
    if (app.ui && app.ui.dialog) {
        app.ui.dialog.show({
            title: "LoRA Text Error",
            message: message,
            buttons: ["OK"]
        });
    }
}

app.registerExtension({
    name: "prepack.lora_texts",
    
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === PREPACK_LORAS_NODE) {
            const onAdded = nodeType.prototype.onAdded;
            nodeType.prototype.onAdded = function() {
                onAdded?.apply(this, arguments);
                
                // Add cleanup on removal to prevent memory leaks
                const onRemoved = this.onRemoved;
                this.onRemoved = function() {
                    // Clean up event listeners and resources
                    if (this._loraTextCleanup) {
                        this._loraTextCleanup.forEach(cleanup => {
                            try {
                                cleanup();
                            } catch (error) {
                                console.warn('Error during cleanup:', error);
                            }
                        });
                        this._loraTextCleanup = null;
                    }
                    
                    // Clean up text content widget
                    if (this.cleanupTextContentWidget) {
                        this.cleanupTextContentWidget();
                    }
                    
                    onRemoved?.apply(this, arguments);
                };
                
                // Find all LoRA name and text widgets
                const loraWidgets = [
                    {
                        name: this.widgets.find(w => w.name === "lora_name_1"),
                        text: this.widgets.find(w => w.name === "lora_text_1"),
                        index: 1
                    },
                    {
                        name: this.widgets.find(w => w.name === "lora_name_2"),
                        text: this.widgets.find(w => w.name === "lora_text_2"),
                        index: 2
                    },
                    {
                        name: this.widgets.find(w => w.name === "lora_name_3"),
                        text: this.widgets.find(w => w.name === "lora_text_3"),
                        index: 3
                    }
                ].filter(w => w.name && w.text); // Only include existing widgets
                
                if (loraWidgets.length === 0) {
                    console.error("Could not find any LoRA widgets");
                    return;
                }
                
                // Create combo widgets for each LoRA text selector
                const comboWidgets = [];
                for (const loraWidget of loraWidgets) {
                    const comboWidget = ComfyWidgets["COMBO"](this, `lora_text_${loraWidget.index}`, [["None"], {}], app).widget;
                    comboWidget.value = "None";
                    comboWidgets.push({ combo: comboWidget, ...loraWidget });
                }
                
                // Create text content display widget
                let textContentWidget = null;
                
                const updateTextFiles = async (widgetData, preserveSelection = true) => {
                    try {
                        const loraName = widgetData.name.value;
                        if (!loraName || loraName === "None") {
                            // Reset when no LoRA selected
                            widgetData.combo.options.values = ["None"];
                            widgetData.combo.value = "None";
                            widgetData.text.value = "None";
                            return;
                        }
                        
                        // Validate LoRA name
                        if (typeof loraName !== 'string' || loraName.trim().length === 0) {
                            throw new Error('Invalid LoRA name provided');
                        }
                        
                        // Store current selection before updating options
                        const currentSelection = preserveSelection ? widgetData.text.value : null;
                        
                        // Fetch available text files with timeout
                        const controller = new AbortController();
                        const timeoutId = setTimeout(() => controller.abort(), 10000); // 10s timeout
                        
                        try {
                            const response = await api.fetchApi(`/prepack/lora-texts/${encodeURIComponent2(loraName)}`, {
                                signal: controller.signal
                            });
                            
                            clearTimeout(timeoutId);
                            
                            if (!response.ok) {
                                throw new Error(`API request failed: ${response.status} ${response.statusText}`);
                            }
                            
                            const textFiles = await response.json();
                            
                            // Validate response data
                            if (!Array.isArray(textFiles)) {
                                throw new Error('Invalid response format: expected array');
                            }
                            
                            if (textFiles.length > 0) {
                                // Sanitize file names
                                const sanitizedFiles = textFiles
                                    .filter(file => file && typeof file === 'string')
                                    .map(file => file.trim())
                                    .filter(file => file.length > 0);
                                
                                // Update combo options
                                widgetData.combo.options.values = ["None", ...sanitizedFiles];
                                
                                // Determine which value to set
                                let valueToSet = "None"; // Default to None
                                
                                if (preserveSelection && currentSelection !== null && currentSelection !== undefined) {
                                    // Always preserve the current selection if it exists in the options
                                    // This includes preserving "None" selection
                                    if (currentSelection === "None" || sanitizedFiles.includes(currentSelection)) {
                                        valueToSet = currentSelection;
                                    }
                                    // If the current selection is not available, keep default "None"
                                } else if (!preserveSelection && sanitizedFiles.length > 0) {
                                    // Only auto-select first file when explicitly requested (new node creation)
                                    valueToSet = sanitizedFiles[0];
                                }
                                
                                widgetData.combo.value = valueToSet;
                                widgetData.text.value = valueToSet;
                            } else {
                                // No text files found
                                widgetData.combo.options.values = ["None"];
                                widgetData.combo.value = "None";
                                widgetData.text.value = "None";
                            }
                        } catch (fetchError) {
                            clearTimeout(timeoutId);
                            throw fetchError;
                        }
                        
                        app.graph.setDirtyCanvas(true, true);
                        
                    } catch (error) {
                        const errorMessage = `Failed to update text files for LoRA "${widgetData.name.value}": ${error.message}`;
                        console.error(errorMessage, error);
                        
                        // Reset to safe state
                        widgetData.combo.options.values = ["None"];
                        widgetData.combo.value = "None";
                        widgetData.text.value = "None";
                        
                        // Show user-friendly error only for important errors
                        if (!error.name || error.name !== 'AbortError') {
                            showErrorNotification(errorMessage);
                        }
                        
                        app.graph.setDirtyCanvas(true, true);
                    }
                };
                
                const updateTextContent = async () => {
                    try {
                        let allContents = [];
                        let errors = [];
                        
                        // Collect content from all selected text files with parallel requests
                        const contentPromises = comboWidgets.map(async (widgetData) => {
                            const loraName = widgetData.name.value;
                            const textName = widgetData.combo.value;
                            
                            if (!loraName || loraName === "None" || !textName || textName === "None") {
                                return null;
                            }
                            
                            // Validate inputs
                            if (typeof loraName !== 'string' || typeof textName !== 'string') {
                                errors.push(`Invalid input types for ${loraName}/${textName}`);
                                return null;
                            }
                            
                            try {
                                const controller = new AbortController();
                                const timeoutId = setTimeout(() => controller.abort(), 8000); // 8s timeout
                                
                                const response = await api.fetchApi(
                                    `/prepack/lora-text-content/${encodeURIComponent2(loraName)}/${encodeURIComponent2(textName)}`,
                                    { signal: controller.signal }
                                );
                                
                                clearTimeout(timeoutId);
                                
                                if (!response.ok) {
                                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                                }
                                
                                const content = await response.text();
                                const trimmedContent = content.trim();
                                
                                if (trimmedContent) {
                                    // Sanitize content to prevent XSS
                                    return sanitizeText(trimmedContent);
                                }
                                return null;
                            } catch (error) {
                                if (error.name !== 'AbortError') {
                                    errors.push(`Error fetching ${loraName}/${textName}: ${error.message}`);
                                }
                                return null;
                            }
                        });
                        
                        // Wait for all requests to complete
                        const results = await Promise.all(contentPromises);
                        allContents = results.filter(content => content !== null);
                        
                        // Log errors if any
                        if (errors.length > 0) {
                            console.warn('Some text content requests failed:', errors);
                        }
                        
                        // Create or update text content widget
                        if (allContents.length > 0) {
                            if (!textContentWidget) {
                                textContentWidget = ComfyWidgets["STRING"](this, "text_content_display", ["STRING", { 
                                    multiline: true,
                                    dynamicPrompts: false
                                }], app).widget;
                                
                                // Configure widget appearance and behavior
                                if (textContentWidget.inputEl) {
                                    textContentWidget.inputEl.readOnly = true;
                                    textContentWidget.inputEl.style.cssText = `
                                        opacity: 0.8;
                                        resize: none;
                                        overflow: auto;
                                        box-sizing: border-box;
                                        background-color: rgba(255,255,255,.04);
                                        border: none;
                                        border-radius: 3px;
                                        padding: 8px;
                                    `;
                                }
                                
                                textContentWidget.name = "Combined Text Content (Preview)";
                            }
                            
                            // Safely set content with length limit
                            const combinedContent = allContents.join(", ");
                            const maxLength = 2000; // Prevent extremely long content
                            textContentWidget.value = combinedContent.length > maxLength 
                                ? combinedContent.substring(0, maxLength) + "..." 
                                : combinedContent;
                        } else {
                            // Clean up text content widget if no content
                            this.cleanupTextContentWidget();
                        }
                        
                        app.graph.setDirtyCanvas(true, true);
                        
                    } catch (error) {
                        console.error("Error updating combined text content:", error);
                        showErrorNotification(`Failed to update text content: ${error.message}`);
                        this.cleanupTextContentWidget();
                    }
                };
                
                // Helper function to clean up text content widget
                this.cleanupTextContentWidget = () => {
                    if (textContentWidget) {
                        try {
                            if (textContentWidget.inputEl && textContentWidget.inputEl.parentNode) {
                                textContentWidget.inputEl.remove();
                            }
                            const widgetIndex = this.widgets.indexOf(textContentWidget);
                            if (widgetIndex !== -1) {
                                this.widgets.splice(widgetIndex, 1);
                            }
                        } catch (cleanupError) {
                            console.warn("Error during widget cleanup:", cleanupError);
                        }
                        textContentWidget = null;
                    }
                };
                
                // Create debounced update functions for better performance
                const debouncedUpdateTextFiles = debounce(async (widgetData, preserveSelection) => {
                    await updateTextFiles(widgetData, preserveSelection);
                    await updateTextContent();
                }, 300);
                
                const debouncedUpdateTextContent = debounce(updateTextContent, 150);
                
                // Set up event listeners for each LoRA widget pair
                for (const widgetData of comboWidgets) {
                    // Store original callbacks to prevent memory leaks
                    const originalLoraCallback = widgetData.name.callback;
                    const originalComboCallback = widgetData.combo.callback;
                    
                    // LoRA name change listener with debouncing
                    widgetData.name.callback = function() {
                        try {
                            const result = originalLoraCallback?.apply(this, arguments) ?? widgetData.name.value;
                            // When LoRA name changes, preserve current text selection if possible
                            debouncedUpdateTextFiles(widgetData, true);
                            return result;
                        } catch (error) {
                            console.error('Error in LoRA name callback:', error);
                            return widgetData.name.value;
                        }
                    };
                    
                    // Text combo change listener with debouncing
                    widgetData.combo.callback = function() {
                        try {
                            const result = originalComboCallback?.apply(this, arguments) ?? widgetData.combo.value;
                            // Update the hidden string widget
                            widgetData.text.value = result;
                            debouncedUpdateTextContent();
                            return result;
                        } catch (error) {
                            console.error('Error in combo callback:', error);
                            return widgetData.combo.value;
                        }
                    };
                    
                    // Hide the original string widget by making it very small
                    widgetData.text.computeSize = () => [0, -4];
                    
                    // Store cleanup functions for proper disposal
                    if (!this._loraTextCleanup) {
                        this._loraTextCleanup = [];
                    }
                    this._loraTextCleanup.push(() => {
                        widgetData.name.callback = originalLoraCallback;
                        widgetData.combo.callback = originalComboCallback;
                    });
                }
                
                // Initialize all widgets with proper error handling
                const initializeWidgets = async () => {
                    try {
                        for (const widgetData of comboWidgets) {
                            // On initialization, always preserve existing selection (including "None")
                            // Only auto-select first file if there's no existing value at all (undefined/null/empty)
                            const hasExistingSelection = widgetData.text.value !== undefined && 
                                                        widgetData.text.value !== null && 
                                                        widgetData.text.value !== "";
                            await updateTextFiles(widgetData, hasExistingSelection);
                        }
                        await updateTextContent();
                    } catch (error) {
                        console.error('Error during widget initialization:', error);
                        showErrorNotification('Failed to initialize LoRA text widgets');
                    }
                };
                
                // Use requestAnimationFrame for better performance than setTimeout
                requestAnimationFrame(() => {
                    requestAnimationFrame(() => {
                        initializeWidgets();
                    });
                });
            };
        }
    }
});
