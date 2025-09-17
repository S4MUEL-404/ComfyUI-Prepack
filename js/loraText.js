import { app } from "../../../scripts/app.js";
import { ComfyWidgets } from "../../../scripts/widgets.js";
import { api } from "../../../scripts/api.js";

const PREPACK_LORAS_NODE = "PrepackLoras";

// Encode URI components for safe API calls
function encodeURIComponent2(str) {
    return encodeURIComponent(str).replace(/[!'()*]/g, (c) => `%${c.charCodeAt(0).toString(16).toUpperCase()}`);
}

app.registerExtension({
    name: "prepack.lora_texts",
    
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === PREPACK_LORAS_NODE) {
            const onAdded = nodeType.prototype.onAdded;
            nodeType.prototype.onAdded = function() {
                onAdded?.apply(this, arguments);
                
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
                
                const updateTextFiles = async (widgetData) => {
                    try {
                        const loraName = widgetData.name.value;
                        if (!loraName || loraName === "None") {
                            // Reset when no LoRA selected
                            widgetData.combo.options.values = ["None"];
                            widgetData.combo.value = "None";
                            widgetData.text.value = "None";
                            return;
                        }
                        
                        // Fetch available text files
                        const response = await api.fetchApi(`/prepack/lora-texts/${encodeURIComponent2(loraName)}`);
                        const textFiles = await response.json();
                        
                        if (textFiles && textFiles.length > 0) {
                            // Update combo options
                            widgetData.combo.options.values = ["None", ...textFiles];
                            widgetData.combo.value = textFiles[0]; // Select first text file by default
                            
                            // Update hidden string widget with selected value
                            widgetData.text.value = textFiles[0];
                        } else {
                            // No text files found
                            widgetData.combo.options.values = ["None"];
                            widgetData.combo.value = "None";
                            widgetData.text.value = "None";
                        }
                        
                        app.graph.setDirtyCanvas(true, true);
                        
                    } catch (error) {
                        console.error("Error updating text files:", error);
                        widgetData.combo.options.values = ["None"];
                        widgetData.combo.value = "None";
                        widgetData.text.value = "None";
                        app.graph.setDirtyCanvas(true, true);
                    }
                };
                
                const updateTextContent = async () => {
                    try {
                        let allContents = [];
                        
                        // Collect content from all selected text files
                        for (const widgetData of comboWidgets) {
                            const loraName = widgetData.name.value;
                            const textName = widgetData.combo.value;
                            
                            if (loraName && loraName !== "None" && textName && textName !== "None") {
                                try {
                                    const response = await api.fetchApi(`/prepack/lora-text-content/${encodeURIComponent2(loraName)}/${encodeURIComponent2(textName)}`);
                                    const content = await response.text();
                                    if (content.trim()) {
                                        allContents.push(content.trim());
                                    }
                                } catch (error) {
                                    console.error(`Error fetching content for ${loraName}/${textName}:`, error);
                                }
                            }
                        }
                        
                        // Create or update text content widget
                        if (allContents.length > 0) {
                            if (!textContentWidget) {
                                textContentWidget = ComfyWidgets["STRING"](this, "text_content_display", ["STRING", { 
                                    multiline: true,
                                    dynamicPrompts: false
                                }], app).widget;
                                textContentWidget.inputEl.readOnly = true;
                                textContentWidget.inputEl.style.opacity = 0.8;
                                textContentWidget.inputEl.style.resize = "none";  // Disable manual resize
                                textContentWidget.inputEl.style.overflow = "auto";
                                textContentWidget.inputEl.style.boxSizing = "border-box";
				textContentWidget.inputEl.style.backgroundColor = "rgba(255,255,255,.04)";
				textContentWidget.inputEl.style.border = "none";
				textContentWidget.inputEl.style.borderRadius = "3px";
				textContentWidget.inputEl.style.padding = "8px";
                                textContentWidget.name = "Combined Text Content (Preview)";
                                
                                // Use default ComfyUI widget behavior for scaling
                                // Remove any fixed sizing to let it scale naturally
                            }
                            
                            textContentWidget.value = allContents.join(", ");
                        } else {
                            // Remove text content widget if no content
                            if (textContentWidget) {
                                textContentWidget.inputEl.remove();
                                const widgetIndex = this.widgets.indexOf(textContentWidget);
                                if (widgetIndex !== -1) {
                                    this.widgets.splice(widgetIndex, 1);
                                }
                                textContentWidget = null;
                            }
                        }
                        
                        app.graph.setDirtyCanvas(true, true);
                        
                    } catch (error) {
                        console.error("Error updating combined text content:", error);
                    }
                };
                
                // Set up event listeners for each LoRA widget pair
                for (const widgetData of comboWidgets) {
                    // LoRA name change listener
                    const originalLoraCallback = widgetData.name.callback;
                    widgetData.name.callback = function() {
                        const result = originalLoraCallback?.apply(this, arguments) ?? widgetData.name.value;
                        updateTextFiles(widgetData).then(() => updateTextContent());
                        return result;
                    };
                    
                    // Text combo change listener
                    const originalComboCallback = widgetData.combo.callback;
                    widgetData.combo.callback = function() {
                        const result = originalComboCallback?.apply(this, arguments) ?? widgetData.combo.value;
                        // Update the hidden string widget
                        widgetData.text.value = result;
                        updateTextContent();
                        return result;
                    };
                    
                    // Hide the original string widget by making it very small
                    widgetData.text.computeSize = () => [0, -4];
                }
                
                // Initialize all widgets without complex repositioning to avoid widget state corruption
                setTimeout(async () => {
                    for (const widgetData of comboWidgets) {
                        await updateTextFiles(widgetData);
                    }
                    await updateTextContent();
                }, 200);  // Increased delay to ensure stable widget state
            };
        }
    }
});
