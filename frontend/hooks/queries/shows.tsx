import { type } from 'os';
import { dehydrate, QueryClient, useQuery } from 'react-query';

//shows query has defaults set at app level defining stale time and queryFn based on functions here.


export const showsStaleTime = () => {
  const staleTime = 3600000; //= 1 hour = 1000(1 second in milliseconds) * 60 (seconds) * 60 (minutes) * 1 (hour);
  return staleTime;
}
// define shows as the following interface or undefined



interface Show {
  desc: string | null,
  duration: number,
  email: string | null,
  ext_link: string | null,
  host: string | null,
  id: string,
  dom_colours: string | null,
  sizes: string | null,
  internal_link: string,
  mp3: string,
  newestEpDate: string,
  showName: string,
  slug: string | null,
  source: string,
  tagIds: string | null,
  extFeeds: string | null,
}

export type {Show};

export const getShows = async () => {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URI}/get_all_shows.php`);
    if (!res.ok) {
      throw new Error('Network error.')
    }
    const response = await res.json();
  
    return response;
  };
  
  export function useShowsQuery() {
    const { data, isLoading } = useQuery<Show[]| undefined>( "shows");
    if (isLoading) {
      return;
    }
    return data;
  }
