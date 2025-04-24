import { Tag, TagMap } from "./queries/tags"
import { useTagsQuery } from "./queries/tags"


export function useMappedShowTags( showTagIds: Array<number>, maxTags:number|null=null) {
    const allTags =  useTagsQuery() ?? null;
    if(allTags){
        const showTags= showTagIds.reduce((tags:Tag[], tagId, idx) => {
                // if tagId is not in allTags, return tags
            if(!allTags[tagId]){
                return tags;
            }
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
    } else {
        return [];
    }
  }