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

        const shortURL = `${window.location.origin}/${data.code}`;
		document.getElementById("shortenedURL").value = shortURL;
    }
}
