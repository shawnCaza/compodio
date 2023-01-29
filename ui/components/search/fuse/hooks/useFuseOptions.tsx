

  export function useFuseOptions() {
   
    const options = {
        keys: [{name:'showName', weight:1}, {name:'desc', weight:3}, {name:'host', weight:1}],
        threshold: 0.4,
        distance: 1000,
        ingoreLocation: true,
        includeScore: true,
      };

    return options;
   
  }