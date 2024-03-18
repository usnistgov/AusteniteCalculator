let cryst_download_btn = document.getElementById("button-cryst");
let instprm_download_btn = document.getElementById("button-instprm-json");

cryst_download_btn.addEventListener('click',getCrystFile);
instprm_download_btn.addEventListener('click',getInstprmJsonFile);

async function getCrystFile() {
    // gather info to send to server for request
    const response = await fetch('/cryst', {
        method: "POST",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
        body: JSON.stringify({
            var: 'Gimme my cryst file'
        })
    });

    console.log(response);
}

async function getInstprmJsonFile() {
    // gather info to send to server for request
    const response = await fetch('/instprm_json', {
        method: "POST",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
        body: JSON.stringify({
            var: 'Gimme my instprm and json files'
        })
    });

    console.log(response);
}