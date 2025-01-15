// Utility functions
const utils = {
    formatDate: (date) => {
        return new Date(date).toLocaleDateString();
    },
    
    formatCurrency: (amount) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    },
    
    truncateText: (text, length = 100) => {
        if (text.length <= length) return text;
        return text.substring(0, length) + '...';
    }
};
