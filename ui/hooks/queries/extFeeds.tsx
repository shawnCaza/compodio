import { type } from 'os';
import { dehydrate, QueryClient, useQuery } from 'react-query';

//query has defaults set at app level defining stale time and queryFn based on functions here.

export const extFeedsStaleTime = () => {
  const staleTime = 86400000; //= 1 day = 1000(1 second in milliseconds) * 60 (seconds) * 60 (minutes) * 24 (hour);
  return staleTime;
}

// typescript interface for date that looks like this: {"83": {"google": "https://podcasts.google.com/feed/aHR0cHM6Ly9hbmNob3IuZm0vcy8zMThmNTE4NC9wb2RjYXN0L3Jzcw==", "spotify": "https://open.spotify.com/show/6oc3vLTSn4cUf5k86EsdQb"}, "112": {"apple": "https://podcasts.apple.com/ca/podcast/food-farm-talk/id1479236009", "google": "https://www.google.com/podcasts?feed=aHR0cHM6Ly9hbmNob3IuZm0vcy9kZWIxZDA4L3BvZGNhc3QvcnNz"},...}
interface ExtFeed {
  [key: string]: {
    [key: string]: string
  }


type TagMap = Record<string, Tag>;

export type {Tag, TagMap};

export const getTags = async () => {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URI}/get_all_tags.php`);
    if (!res.ok) {
      throw new Error('Network error.')
    }
    const response = await res.json();
    
    return response;
  };
  
  export function useTagsQuery() {
    const { data } = useQuery<TagMap>( "tags");
    return data;
  }
