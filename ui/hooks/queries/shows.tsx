import { type } from 'os';
import { dehydrate, QueryClient, useQuery } from 'react-query';

//shows query has defaults set at app level defining stale time and queryFn based on functions here.


export const showsStaleTime = () => {
  const staleTime = 3600000; //= 1 hour = 1000(1 second in milliseconds) * 60 (seconds) * 60 (minutes) * 1 (hour);
  return staleTime;
}

interface Show {
  desc: string | null,
  duration: number,
  email: string | null,
  ext_link: string | null,
  host: string | null,
  id: number,
  img: string | null,
  internal_link: string,
  mp3: string,
  newestEpDate: string,
  showName: string,
  slug: string | null,
  source: string,
  tags: string[] | null,

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
    const { data } = useQuery<Show[]>( "shows");
    return data;
  }