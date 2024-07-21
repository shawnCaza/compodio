import { useCallback, useEffect, useState } from "react"

interface useAsyncProps {
    callback: () => Promise<any>,
    dependencies: []
}


export default function useAsync(callback, dependencies = []) {
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