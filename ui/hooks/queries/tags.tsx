import { type } from 'os';
import { dehydrate, QueryClient, useQuery } from 'react-query';

//shows query has defaults set at app level defining stale time and queryFn based on functions here.

export const tagsStaleTime = () => {
  const staleTime = 86400000; //= 1 day = 1000(1 second in milliseconds) * 60 (seconds) * 60 (minutes) * 24 (hour);
  return staleTime;
}

interface Tags {
  id: number,
  tag: string,
  frequency: number
}

type TagMap = Record<string, Tags>;

export type {Tags, TagMap};

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
