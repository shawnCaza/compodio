import Link from "next/link";
const ConditionalLink = ({ children, to }) => (to)
      ? <Link to={to}>{children}</Link>
      : <><a>{children}</a></>;

function ResultItem(props) {
    let selected = '';
    props.comboItemSelected === props.index ? selected = 'true' : selected = 'false';
    
    return(
        <>
            <li id={props.searchItemType+props.index} onClick={props.clickFunc} role="option"  aria-selected={selected}>
                <ConditionalLink to={props.itemLink}>
                {props.itemText}
                </ConditionalLink>
        </li>
          
        </>
    )
}

export default ResultItem;