import { useCallback, useEffect, useState } from "react"

type UseAsyncReturn = [boolean, Error | undefined, any | undefined];


export default function useAsync(callback: (...args: any[]) => Promise<any>, dependencies: any[]): UseAsyncReturn {
    const [pending, setPending] = useState(true)
    const [error, setError] = useState<Error | undefined>(undefined)
    const [value, setValue] = useState<any | undefined>(undefined)
    const callbackMemoized = useCallback(():void => {
        setPending(true)
        setError(undefined)
        setValue(undefined)
        callback(...dependencies)
            .then(setValue)
            .catch(setError)
            .finally(() => setPending(false))
    }, dependencies)

    useEffect(() => {
        callbackMemoized()
    }, [callbackMemoized])

    return [ pending, error, value ]
}