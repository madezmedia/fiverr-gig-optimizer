// Heuristics and redefinitions
const heuristics = {
    categories: {
        "Programming & Tech": {
            keywords: ["development", "coding", "programming", "tech", "software"],
            weight: 1.5
        },
        "Digital Marketing": {
            keywords: ["marketing", "seo", "social media", "advertising"],
            weight: 1.3
        },
        "Writing & Translation": {
            keywords: ["writing", "content", "translation", "copywriting"],
            weight: 1.2
        },
        "Design": {
            keywords: ["design", "logo", "graphic", "ui", "ux"],
            weight: 1.4
        }
    },
    
    calculateRelevance(text, category) {
        const keywords = this.categories[category].keywords;
        const weight = this.categories[category].weight;
        const matches = keywords.filter(kw => text.toLowerCase().includes(kw));
        return (matches.length / keywords.length) * weight;
    }
};
