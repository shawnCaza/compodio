
import React, {useState,  ReactNode } from "react";
import { useCombobox } from 'downshift'
import ShowLink from "../show/ShowLink";


interface comboBoxProps {
    handleSearch: Function,
    itemToString: Function,
    children: ReactNode
}

function ComboBoxSearch ({handleSearch, itemToString, children}:comboBoxProps) {
    
    const [inputItems, setInputItems] = useState([])
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
      console.log('User typed: ', inputValue);
      setInputItems(
        handleSearch(inputValue)
      )
    },
    onSelectedItemChange: ({ selectedItem }) => {
      console.log('User selected: ', selectedItem)
    },
  })

    return (
        <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        width: 'fit-content',
        justifyContent: 'center',
        marginTop: 100,
        alignSelf: 'center',
      }}
    >
      <label
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
          aria-label="toggle menu"
          data-testid="combobox-toggle-button"
          {...getToggleButtonProps()}
        >
          {isOpen ? <>&#8593;</> : <>&#8595;</>}
        </button>
        <button
          style={{padding: '4px 8px'}}
          aria-label="toggle menu"
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
        }}
      >
        {isOpen &&
          inputItems.slice(0,7).map((result, index) => (
            <li
              style={{
                padding: '4px',
                backgroundColor: highlightedIndex === index ? '#bde4ff' : null,
              }}
              key={result.item.id}
            >
              <ShowLink slug={result.item.slug}>
                {result.item.showName}
              </ShowLink>
            </li>
          ))}
      </ul>
    </div>
    )
}

export default ComboBoxSearch;