import React, { useState } from "react";
import { Hydrate, QueryClient, QueryClientProvider } from "react-query";
import type { AppProps } from "next/app";
import "../styles/globals.scss";
import { getShows, showsStaleTime } from "../hooks/queries/shows";

function App({ Component, pageProps }: AppProps) {
  
  const [queryClient] = useState(() => new QueryClient());
  queryClient.setQueryDefaults('shows', { queryFn: getShows, staleTime: showsStaleTime()})

  return (
    <QueryClientProvider client={queryClient}>
      <Hydrate state={pageProps.dehydratedState}>
        <Component {...pageProps} />
      </Hydrate>
    </QueryClientProvider>
  );
}

export default App;
