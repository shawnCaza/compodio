import React from "react";
import Fuse from "fuse.js";
import { dehydrate, QueryClient} from 'react-query';
import ContentSection from "../components/layout/ContentSection/contentSection";
import ShowCards from "../components/show/showCards/ShowCards";
import { useShowsQuery, Show } from "../hooks/queries/shows";
import { getTags } from "../hooks/queries/tags";
import { useFuseOptions } from "../components/search/fuse/hooks/useFuseOptions";
import { useSearchParams } from 'next/navigation'
import { GetServerSidePropsContext } from 'next';



// export async function getServerSideProps(context: GetServerSidePropsContext) {
  
//   const searchTerm = context.query.s;

//   const queryClient = new QueryClient();
//   await Promise.all([
//     queryClient.prefetchQuery('tags', getTags),
//     queryClient.prefetchQuery('shows', getShows)
//   ]);
  

//     return {props: {
//       dehydratedState: dehydrate(queryClient),
//       searchTerm: searchTerm}
//     }
//     // will be passed to the page component as props
//   }


interface HandleFuseSearchProps {
  shows: Show[],
  searchTerm: string
}


function HandleFuseSearch({shows, searchTerm}:HandleFuseSearchProps) {

  const fuse = new Fuse(shows, useFuseOptions());
  const searchResults = Object.values(fuse.search(searchTerm));
  //create array using only the item prop from each object in the searchResults array
  const searchItems = searchResults.map((result) => result.item);

  return (
    <ShowCards shows={searchItems} />
  )
}

  export default function SearchPage(){

    const searchParams = useSearchParams();
    const searchTerm = searchParams.get('s');
    const shows = useShowsQuery();
    if (!shows || !searchTerm ){
      return;
    }

    console.log('searchTerm', searchTerm)
    return (      
        <ContentSection heading={`Searching for: ${searchTerm}`} tag='h1'>
          <HandleFuseSearch shows={shows} searchTerm={searchTerm} />

        </ContentSection>
      );
}