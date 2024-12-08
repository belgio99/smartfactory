module.exports = {
    content: [
        './src/**/*.{js,jsx,ts,tsx}'
    ],
    theme: {
        extend: {
            animation: {
                'spin-slow': 'spin 20s linear infinite',
            },
            colors: {
                'gray-25': 'rgba(255,255,255,0.8)',  // Lighter than gray-50, not as bright as white
            },
        },
    },
    plugins: [],
};
