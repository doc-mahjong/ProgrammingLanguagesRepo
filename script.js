async function shorten(){
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
        document.getElementById("shortenedURL").value = data.shortURL;
    }
}
