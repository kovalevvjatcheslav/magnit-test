function setCities(){
    let regionsSelect = document.getElementById('regions');
    let currentRegionId = regionsSelect.options[regionsSelect.selectedIndex].value;
    let cities = getCities(currentRegionId);
    let citiesSelect = document.getElementById('cities');
    while (citiesSelect.hasChildNodes()) {
        citiesSelect.removeChild(citiesSelect.lastChild);
    }
    cities.forEach(function(city, index, array){
        let option = document.createElement('option');
        option.value = city.cityId;
        option.appendChild(document.createTextNode(city.cityName));
        citiesSelect.appendChild(option);
    });
}

function getCities(regionId){
    let req = new XMLHttpRequest();
    req.open('GET', `/cities/?regionId=${regionId}`, false);
    req.send();
    if (req.status != 200) {
        console.log('error in getCities');
        return;
    }
    else{
        return JSON.parse(req.responseText);
    }
}

function removeComment(removeButton){
    let row = removeButton.parentElement.parentElement;
    let commentId = row.querySelector('.id').textContent;
    let req = new XMLHttpRequest();
    req.open('POST', '/view/', false);
    req.send(JSON.stringify({commentId: commentId}));
    if (req.status != 200) {
        console.log('error in removeComment');
        return;
    }
    else{
        row.remove();
    }
}