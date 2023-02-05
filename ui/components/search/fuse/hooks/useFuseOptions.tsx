

  export function useFuseOptions() {
   
    const options = {
        keys: [{name:'showName', weight:3}, {name:'desc', weight:2}, {name:'host', weight:1}],
        threshold: 0.4,
        distance: 1000,
        ingoreLocation: true,
        includeScore: true,
      };

    return options;
   
  }