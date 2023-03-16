import { Tag, TagMap } from "./queries/tags"


export function useMappedShowTags(allTags:TagMap, showTagIds: Array<number>, maxTags:number|null=null) {
   
    const showTags= showTagIds.reduce((tags:Tag[], tagId, idx) => {
        
            tags.push(allTags[tagId])
        
        return tags;
    },[])

    // sort tags by frequency

    showTags.sort((a:Tag, b:Tag) => a.freq - b.freq);
    
    if(!maxTags || maxTags >= showTags.length){
        return showTags;
    } else { 
        const leastFrequentTags = showTags.slice(0, maxTags-1)
        
        const mostCommonTag = showTags[showTags.length-1]
        
        return [...leastFrequentTags, mostCommonTag];
    }
  }