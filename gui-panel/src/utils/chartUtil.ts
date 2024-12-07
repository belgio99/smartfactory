// Helper function to format date as 'HH:mm' for hours, 'DD' for days, 'MMM' for months
export const formatTimeFrame = (timestamp: string, timeUnit?: string): string => {
    const date = new Date(timestamp);

    switch (timeUnit) {
        case 'hour':
            return `${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`; // HH:mm
        case 'day':
            return `${String(date.getDate()).padStart(2, '0')}`; // DD (day of the month plus month name)
        case 'week':
            return `${date.toLocaleString('default', {month: 'short'})} ${date.getDate()}`; // MMM DD
        case 'month':
            return `${date.toLocaleString('default', {month: 'short'})}`; // MMM (Month abbreviation)
        default:
            return date.toLocaleString(); // fallback
    }
};

//various colors for the charts
export const COLORS = ['#8884d8', '#83a6ed', '#8dd1e1', '#82ca9d',
    '#a4de6c', '#d0ed57', '#ffc658', '#ffc658',
    '#ff9e58', '#ff6058', '#ff58b2', '#c108fddd'];

export const getColor = (value: number, min: number, max: number) => {
    // Define a simple color gradient from blue to red based on value
    const ratio = (value - min) / (max - min);
    const r = Math.round(255 * ratio);
    const g = Math.round(255 * (1 - ratio));
    const b = 255 - r;

    return `rgb(${r},${g},${b})`;
};