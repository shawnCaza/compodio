const SearchForm = (props) => {
    let ariaActiveDesc = null;
    const setComboItemSelected = props.setComboItemSelected;
    const comboItemSelected = props.comboItemSelected;
    const searchItemType = props.searchItemType;

    if (props.comboItemSelected) {
        ariaActiveDesc = props.searchItemType + props.comboItemSelected;
    }

    const ariaComboBoxKeyCheck = (e) => {
        
        e.stopPropagation();
       
        e.preventDefault();
        let KeyCode = {
            BACKSPACE: 8,
            TAB: 9,
            RETURN: 13,
            ESC: 27,
            SPACE: 32,
            PAGE_UP: 33,
            PAGE_DOWN: 34,
            END: 35,
            HOME: 36,
            LEFT: 37,
            UP: 38,
            RIGHT: 39,
            DOWN: 40,
            DELETE: 46
          };

        let key = e.which || e.keyCode;
        console.log('key press', key);
        if(comboItemSelected){
            switch (key) {
                case KeyCode['DOWN']:
                    setComboItemSelected(prevComboItemSelected => prevComboItemSelected + 1)
                    break;
            
                case KeyCode['UP']:
                    setComboItemSelected(prevComboItemSelected => prevComboItemSelected - 1)
                    break;
                
                case KeyCode['RETURN']:
                    document.getElementById(searchItemType+comboItemSelected).children[0].click();
                    
                    break;
            
                default:
                    break;
                }
        }
    }
        
    return (

        <>
            <div className="search-bar">
                

            <form  onSubmit={props.submit} className='search-form'>
            
                    <span className="search-icon">
                    {props.children}
                    </span>
                    
                    <input
                        
                    ref={props.searchInput}
                    onKeyUp={ariaComboBoxKeyCheck}                    
                    placeholder={props.pHolderText}
                    onChange={props.submit}
                    type="search"
                    dir="ltr"
                    aria-autocomplete="list"
                    aria-controls={props.listBoxId}
                    aria-label={props.label}
                    autoComplete="off"
                    spellCheck="false"
                    aria-invalid="false"
                        
                    aria-activedescendant={ariaActiveDesc}
                
                />
            </form>
            </div>
            </>
    )
};

export default SearchForm;