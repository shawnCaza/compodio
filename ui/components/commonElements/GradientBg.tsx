import {  ReactNode } from "react";
import { json } from "stream/consumers";


interface gradientBgProps{
    colours: string | null,
    children: ReactNode
}



function define_bg_colours(colours: string | null){
    
    let coloursArr = ['#000000'];
    
    if (colours){
        coloursArr = JSON.parse(colours);
    }

    if (coloursArr.length > 0){
        
        // Transform array into string of colours for css
        const gradient_colour_def = coloursArr.reduce(
            (gradient_string:string, colour:string, idx:number) =>{ 
                
                let current_colour_def = `${gradient_string} ${colour}`;
                
                if(idx < coloursArr.length -1){
                    current_colour_def += ", "
                }

                return current_colour_def


            }, "#111, "
        )
        
        const gradient_css = `linear-gradient(to bottom, ${gradient_colour_def}, transparent)`

        return gradient_css
    }  else{

        return "#000";
    }


}

function GradientBg({colours, children}:gradientBgProps) {

    const bg_colour:string = define_bg_colours(colours);
    if(!bg_colour){return null}
    return (
        <>  
            <div className="gradientBG" style={{background:bg_colour}}>

                {children}
            </div>
        </>
    )
} 

export default GradientBg;