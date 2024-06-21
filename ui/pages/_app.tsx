import React, { useState } from "react";
import { Hydrate, QueryClient, QueryClientProvider } from "react-query";
import type { AppProps } from "next/app";
import "../styles/globals.scss";
import Layout from "../components/layout/Layout";
import { getShows, showsStaleTime } from "../hooks/queries/shows";
import { getTags, tagsStaleTime } from "../hooks/queries/tags";
import { HydrationProvider} from "react-hydration-provider";
import { useScrollRestoration } from "../hooks/next-restore-scroll-position";
import { useRouter } from "next/router";

// check localStorage for userId
// if not present, create a new one
//  var userId = localStorage.getItem('userId');
//   if (!userId) {
//     userId = Math.random().toString(36).substring(7);
//     localStorage.setItem('userId', userId);
//   }





function App({ Component, pageProps,  }: AppProps) {
  
  const [queryClient] = useState(() => new QueryClient());
  // queryClient.invalidateQueries(); // for testing use this temporarily to clear cache on page load
  queryClient.setQueryDefaults('shows', { queryFn: getShows, staleTime: showsStaleTime()})
  queryClient.setQueryDefaults('tags', { queryFn: getTags, staleTime: tagsStaleTime()})
  
  const router = useRouter();
  useScrollRestoration(router, {scrollAreaId: 'content'});

  return (
    <QueryClientProvider client={queryClient}>
      <Hydrate state={pageProps.dehydratedState}>
        <HydrationProvider>
          <Layout>
            <Component {...pageProps} />
          </Layout>
        </HydrationProvider>
      </Hydrate>
    </QueryClientProvider>
  );
}

export default App;
