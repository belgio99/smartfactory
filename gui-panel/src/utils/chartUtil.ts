// Helper function to format date as 'HH:mm' for hours, 'DD' for days, 'MMM' for months
import {TimeFrame} from "../components/Selectors/TimeSelect";

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
export const handleTimeAdjustments = (timeFrame: TimeFrame, isRollbackTime: boolean) => {
    if (isRollbackTime) {
        console.log("TimeFrame before rollback:", timeFrame);

        const lastDate = new Date(2024, 9, 19); // 19 October 2024
        const databaseStartDate = new Date(2024, 2, 1); // 1 March 2024
        const fromDate = new Date(timeFrame.from);
        const toDate = new Date(timeFrame.to);

        // Validate input dates
        if (isNaN(fromDate.getTime()) || isNaN(toDate.getTime())) {
            throw new Error("Invalid timeFrame dates");
        }

        // Calculate the difference in milliseconds
        const diff = toDate.getTime() - fromDate.getTime();

        // Adjust the 'from' and 'to' dates for rollback
        const newTo = new Date(lastDate); // End date is fixed to 19 October 2024
        const newFrom = new Date(newTo.getTime() - diff); // Shift the range backward

        // Validate 'newFrom' against the database start date
        if (newFrom < databaseStartDate) {
            console.warn("New 'from' date exceeds database start date. Adjusting...");
            // Calculate the difference between the database start date and the adjusted 'from' date
            const adjustedDiff = newTo.getTime() - databaseStartDate.getTime();

            // Adjust the 'to' date by the same difference (i.e., keep the range consistent)
            return {
                from: databaseStartDate,
                to: new Date(databaseStartDate.getTime() + adjustedDiff),
                aggregation: timeFrame.aggregation,
            };
        }

        console.log("TimeFrame after rollback:", {from: newFrom, to: newTo, aggregation: timeFrame.aggregation});
        return {
            from: newFrom,
            to: newTo,
            aggregation: timeFrame.aggregation,
        };
    }
    console.log("TimeFrame without rollback:", timeFrame);

    // No rollback, return original time frame
    return timeFrame;
}