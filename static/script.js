async function shorten(){
    
    document.getElementById("shortenedURL").value = '';
    
    const URL = document.getElementById("url").value;

    if(URL){
        const response = await fetch("/shorten", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({url: URL})
        });

        const data = await response.json();
        
        if(data["shortURL"]){
            document.getElementById("errorField").textContent = ''
            document.getElementById("shortenedURL").value = data.shortURL;
        }else{
            document.getElementById("errorField").textContent = data.error
        }
        
        
    }
}
