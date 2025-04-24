type seconds = number | undefined;

export function useShowLength(duration:seconds) {
    if (duration === undefined) {return null}
    //if duration is longer than or equal to 1 hour, return hours otherwise return minutes
  
    if(duration > 3600){
      return `${Math.round(duration/60/60)}hrs`
    } else if(duration == 3600){
      return `1hr`
    } else {
      `${Math.round(duration/60)}min`;
    }

  }