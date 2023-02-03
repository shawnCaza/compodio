type seconds = number | undefined;

export function useShowLength(duration:seconds) {
    if (duration === undefined) {return null}
    //if duration is longer than 1 hour, return hours otherwise return minutes
    const showLength = duration > 3600 
                     ? `${Math.round(duration/60/60)} hours` 
                     : `${Math.round(duration/60)} minutes`;
    return showLength
  }