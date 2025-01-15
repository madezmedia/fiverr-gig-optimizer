// Extension state management
const extensionState = {
    initialized: false,
    settings: {},
    
    initialize() {
        if (this.initialized) return;
        this.initialized = true;
        this.loadSettings();
    },
    
    loadSettings() {
        const savedSettings = localStorage.getItem('extension_settings');
        this.settings = savedSettings ? JSON.parse(savedSettings) : {};
    },
    
    saveSettings() {
        localStorage.setItem('extension_settings', JSON.stringify(this.settings));
    }
};
