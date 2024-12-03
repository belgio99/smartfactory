export const mockLogData = [
    {
        id: 1,
        type: 'Info',
        header: 'Report "Quarterly Report Q 2024" is ready for review',
        body: 'The scheduled report has been generated and is ready for review.',
        isRead: false,
    },
    {
        id: 2,
        type: 'Warning',
        header: 'High Power Usage Detected',
        body: 'Detected power usage of "Machine 3" is higher than usual by 30%. Consider investigating.',
        isRead: false,
    },
    {
        id: 3,
        type: 'Error',
        header: 'Machine Connection Failed',
        body: 'Unable to connect to Machine 24. Please contact the system administrator or maintenance staff.',
        isRead: true,
    },
    {
        id: 5,
        type: 'Warning',
        header: 'Idle Time Warning',
        body: 'Detected Idle Time of Machine 23 above the threshold set. Consider investigating.',
        isRead: true,
    },
];