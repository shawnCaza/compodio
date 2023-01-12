import { useEffect, useState } from "react";
// import lunr from 'lunr'
// import { useLunr } from 'react-lunr'
import ResultItem from './resultItem'
import {useItemSelectedValidation} from './itemSelectedValidationHook'
    
const SearchBarRes = (props) => {
//     const searchingFor = props.searchingFor;
//     const [searchResult, setSearchResult] = useState();
//     const [idx, setIdx] = useState(null);
//     let lunrQuery = '';
//     const setComboItemSelected = props.setComboItemSelected;
//     const resultLimit = 10;
  


//     if (shows.length && idx===null) {
// //create lunr index
//         setIdx(lunr(function () {
//             this.ref('id')
//             this.field('showtitle')
//             this.field('desc')
          
//             shows.forEach(function (doc) {
//                 this.add(doc)
//             }, this)
//         })
//         );
        
//         // map id to object + convert array to object - so we can map by id results later.
//         setMappedShowsProdObj(Object.fromEntries(shows.map(show => [show.id, {
//             id: show.id,
//             desc:show.desc,
//             title:show.title,
//         }]
//         )
//         ));  
//     }
        
    

//     if (searchingFor) {
//         lunrQuery = searchingFor.trim();
//         const words = lunrQuery.split(' ');
//         // console.log('words len ',words.length)
//         if (words.length > 1) {
            
//             if (words[words.length - 1].length < 4) {
//                 //multiple words - last word too short for it + wildcard to be as important as other complete words
//                 lunrQuery = words.join('^3 ') + '*';  //^ makes complete words x times more important in search
//             } else {
//                 //because having a 2 complete words with * at end of second word seemed make the second  word not important once complete?
//                 lunrQuery = words.join('^4 ') + '^3 ' + words[words.length - 1] + '*';
//             }
//         } else if (words.length === 1) {
//             //gives stronest preference for full word match, some preference for begining of word match
//             lunrQuery = '*' + lunrQuery + '* ' + lunrQuery + '*^5 ' + lunrQuery + '^10';
//         } else {

//             lunrQuery = lunrQuery + '*';
//         }
        
//         // console.log(lunrQuery);

//     } else {
//         lunrQuery = searchingFor;  
//     }
    
//     let lunrResult = useLunr(lunrQuery, idx, mappedShowsProdObj);
    

//     useEffect(() => {
//         if (!lunrResult.length && lunrResult) {
//             setSearchResult(null)
//         };

//         if (!lunrResult.length) return;
        
//         setSearchResult(lunrResult);
        
  
//     },[lunrResult])

//     useItemSelectedValidation(lunrResult, setComboItemSelected, props.comboItemSelected, resultLimit)

    return (
        
        <>
            {/* {searchResult &&

                <ul
                    id={props.listBoxId}
                    role='listbox'
                    className='search-result-container'
                >
                
                {(searchResult) && searchResult.slice(0, resultLimit).map((item,index) => (
                        
                    <ResultItem
                        searchItemType={props.searchItemType}
                        key={item.id}
                        index={index+1}
                        comboItemSelected={props.comboItemSelected}
                        clickFunc={props.resetShowSearch}
                        itemText={item.brand + " " + item.strain} 
                        itemLink={`/product/${item.handle}`}

                    />
                        
                
                    ))}
                </ul>
            } */}
            </>
    )
};

export default SearchBarRes;