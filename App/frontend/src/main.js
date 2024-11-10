window.onload = function ()
{
    let p = document.getElementById("text");
    p.innerText = "textLoading";
    fetch("http://backend:8000/")
        .then(data => data.json())
        .then(data =>
        {
            p.innerText = data.test;
        })
        .catch(error =>
        {
            console.error(error);
        });
}

