import { Tags, TagMap } from "./queries/tags"


export function useShowTags(allTags:TagMap, showTagIds: Array<number>, maxTags:number|null=null) {
   
    const showTags= showTagIds.reduce((tags:Tags[], tagId, idx) => {
        
        if(!maxTags || maxTags > idx){
            tags.push(allTags[tagId])
        }
        
        return tags;
    },[])

    return showTags;
   
  }