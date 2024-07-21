import { useCallback, useEffect, useState } from "react"

type UseAsyncReturn = [boolean, Error | undefined, any | undefined];


export default function useAsync(callback: (...args: any[]) => Promise<any>, dependencies: any[]): UseAsyncReturn {
    // Abstraction to handles asynchronous operations. It takes a callback function that returns a promise. Memoizes the result of the callback, manages the state of the asynchronous operation, and automatically re-triggers the callback when the dependencies change. 
    // Adapted from Serge Leschev hook: https://github.com/sergeyleschev/react-custom-hooks/blob/main/src/hooks/useAsync/useAsync.js

    const [pending, setPending] = useState(true)
    const [error, setError] = useState<Error | undefined>(undefined)
    const [value, setValue] = useState<any | undefined>(undefined)
    const callbackCached = useCallback(():void => {
        setPending(true)
        setError(undefined)
        setValue(undefined)
        callback(...dependencies)
            .then(setValue)
            .catch(setError)
            .finally(() => setPending(false))
    }, dependencies)

    useEffect(() => {
        callbackCached()
    }, [callbackCached])

    return [ pending, error, value ]
}