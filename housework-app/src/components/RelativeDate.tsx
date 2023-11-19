import { DateTime } from 'luxon';
import React, { useEffect, useState } from 'react';

const RelativeDate = ({ value }: { value: string }) => {
    const [display, setDisplay] = useState<string>(DateTime.fromISO(value).toRelative() || "Invalid Time");

    useEffect(() => {
        const intervalId = setInterval(() => {
            setDisplay(DateTime.fromISO(value).toRelative() || "Invalid Time");
        }, 60000);

        return () => clearInterval(intervalId);
    }, [setDisplay, value]);

    return<>{display}</>;
};

export default RelativeDate;
