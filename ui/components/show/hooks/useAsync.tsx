import { useCallback, useEffect, useState } from "react"


export default function useAsync(callback: () => Promise<any>, dependencies: []) {
    const [pending, setPending] = useState(true)
    const [error, setError] = useState()
    const [value, setValue] = useState()
    const callbackMemoized = useCallback(() => {
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