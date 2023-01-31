
import React, {useState,  ReactNode } from "react";
import { Show } from "../../hooks/queries/shows"; 

import { useCombobox } from 'downshift'
import ShowLink from "../show/ShowLink";


interface comboBoxProps {
    handleSearch: Function,
    handleSelection: Function
}

interface fuseResult{
  item: Show;
  score: number;
  refIndex: number;
}

const itemToString = (result:fuseResult | null) => (result ? result.item.showName : '')


function ComboBox ({handleSearch, handleSelection}:comboBoxProps) {
    
    const [inputItems, setInputItems] = useState<fuseResult[]>([])
    
    if(!inputItems){return null}
    

    const {
    isOpen,
    getToggleButtonProps,
    getLabelProps,
    getMenuProps,
    getInputProps,
    highlightedIndex,
    getItemProps,
    selectedItem,
    selectItem,
  } = useCombobox({
    items: inputItems,
    itemToString,
    onInputValueChange: ({ inputValue }) => {
      setInputItems(
        handleSearch(inputValue)
      )
    },
    onSelectedItemChange: ({ selectedItem }) => {
      
      if(selectedItem){ handleSelection(selectedItem)};
    },
  })
    return (
      <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        width: 'fit-content',
        justifyContent: 'center',
        position:"relative",
        zIndex:"90009",
        alignSelf: 'center',
      }}
      >
        <label
          className="screen-reader-text"
          style={{
            fontWeight: 'bolder',
            color: selectedItem ? selectedItem : 'black',
          }}
          {...getLabelProps()}
        >
          Choose an element:
        </label>
        <div>
          <input
            style={{padding: '4px'}}
            {...getInputProps()}
            data-testid="combobox-input"
          />
          <button
            style={{padding: '4px 8px'}}
            aria-label="Search"
            data-testid="combobox-toggle-button"
            {...getToggleButtonProps()}
          >
            {isOpen ? <>&#8593;</> : <>&#8595;</>}
          </button>
          <button
            style={{padding: '4px 8px'}}
            aria-label="Clear Search"
            data-testid="clear-button"
            onClick={() => selectItem(null)}
          >
            &#10007;
          </button>
        </div>
        <ul
          {...getMenuProps()}
          style={{
            listStyle: 'none',
            width: '100%',
            padding: '0',
            margin: '4px 0 0 0',
            position:"absolute",
            backgroundColor:'#eee',
            top:'100%',
            zIndex:"9999"
          }}
        >
          {isOpen &&
            inputItems.map((result, index) => (
              <li
                style={{
                  padding: '4px',
                  backgroundColor: highlightedIndex === index ? '#bde4ff' : "inherit",
                }}
                {...getItemProps({result, index, key: result.item.id})}
              >
                {/* <ShowLink slug={result.item.slug}> */}
                  {result.item.showName}
                {/* </ShowLink> */}
              </li>
            ))}
        </ul>
      </div>
    )
}

export default ComboBox;