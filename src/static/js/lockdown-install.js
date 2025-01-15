// Security lockdown and installation
const lockdown = {
    installed: false,
    
    install() {
        if (this.installed) return;
        
        // Lock down global objects
        Object.freeze(Object.prototype);
        Object.freeze(Array.prototype);
        Object.freeze(Function.prototype);
        
        // Prevent modifications to window
        Object.defineProperty(window, 'eval', {
            value: undefined,
            configurable: false,
            writable: false
        });
        
        this.installed = true;
        console.log('Security lockdown installed');
    }
};

// Auto-install on load
document.addEventListener('DOMContentLoaded', () => {
    lockdown.install();
});
