import React, { useEffect, useRef } from 'react';

// see https://usehooks.com/useEventListener/

function useEventListener(eventName, handler, element=window, passive=false) {
    const savedHandler = useRef(); 

    useEffect(() => {
        savedHandler.current = handler;
    }, [handler]);

    useEffect(
        () => {
            const isSupported = element && element.addEventListener; // addEventListener supported
            if (!isSupported) return;

            const eventListener = event => savedHandler.current(event);

            element.addEventListener(eventName, eventListener, passive);

            return function cleanup() {
                element.removeEventListener(eventName, eventListener);
            };

        },
        [eventName, element]
    );
}

export default useEventListener;