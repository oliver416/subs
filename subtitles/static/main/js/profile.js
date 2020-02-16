function showFileName(e){
    let fileName = e.target.files[0].name;
    let label = document.getElementsByClassName('custom-file-label')[0];
    label.innerHTML = fileName;
};

function getCookie(name) {
    let cookie = document.cookie
    if (document.cookie && document.cookie != ''){
        if (name === cookie.split('=')[0]){
            return cookie.split('=')[1].toString()
        }
    }
  };

function replaceAll(str, find, replace) {
    return str.replace(new RegExp(find, 'g'), replace);
}

function getRequest(callback, url, context){
    let xhr = new XMLHttpRequest();
    xhr.addEventListener("load", function (e) {
        if (xhr.status === 200){
            return callback(xhr.response, context)
        }else {
            return 'Error'
        }
    });
    xhr.open("GET", url, true);
    xhr.send(null);
};

function postRequest(callback, url, context){
    let xhr = new XMLHttpRequest();
    let formData = new FormData();
    xhr.addEventListener("load", function (e) {
        if (xhr.status === 200){
            return callback(xhr.response, context)
        }else {
            return 'Error'
        }
    });
    if (typeof context === 'object' && typeof context[Symbol.iterator] === 'function'){
        for (let data of context){
            formData.append(data[0], data[1]);   
        }
    }
    xhr.open("POST", url, true);
    xhr.send(formData);
};

function touchWordCallback(response){
    let word = JSON.parse(response)['word'];
    let exists = JSON.parse(response)['exists'];
    let buttonGroup = document.getElementById(word);
    let buttonWord = buttonGroup.getElementsByClassName('word-button')[0];
    let buttonDropdown = buttonGroup.getElementsByClassName('button-dropdown')[0];
    if (exists === true){
        buttonWord.classList.remove('btn-danger');
        buttonWord.classList.add('btn-success');
        buttonDropdown.classList.remove('btn-danger');
        buttonDropdown.classList.add('btn-success');
    }else{
        buttonWord.classList.remove('btn-success');
        buttonWord.classList.add('btn-danger');
        buttonDropdown.classList.remove('btn-success');
        buttonDropdown.classList.add('btn-danger');
    }
};

function checkWordCallback(response, context){
    // let button = document.createElement('button');
    let word = context[0];
    let frequency = context[1];
    let canvas = document.getElementById('canvas');
    let buttonGroup = document.createElement('div');
    buttonGroup.id = word;
    buttonGroup.className = 'btn-group p-3';
    canvas.appendChild(buttonGroup);
    let button = document.createElement('button');
    // TODO: It's a sort of bullshit
    button.innerText = word + ' ' + frequency;
    let dropdownStyle = ''
    if (JSON.parse(response)['exists'] === true){
        button.className = 'btn btn-success word-button';
        dropdownStyle = 'btn-success';
    }else{
        button.className = 'btn btn-danger word-button';
        dropdownStyle = 'btn-danger';
    }
    // button.id = word;
    // buttonGroup.appendChild(button);
    buttonGroup.innerHTML = `
        ` + button.outerHTML + `
        <button type="button" class="btn ` + dropdownStyle + ` dropdown-toggle dropdown-toggle-split button-dropdown" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
          <span class="sr-only">Toggle Dropdown</span>
        </button>
        <div class="dropdown-menu">
        <button class="dropdown-item button-translate">Translate</button>
        <button class="dropdown-item bg-warning button-marker">Mark a word</button>
        <!--<div class="dropdown-divider"></div>
        <button class="dropdown-item bg-warning button-name">Mark as a Name</button>
        <button class="dropdown-item bg-secondary button-mistake">Mark as a mistake</button>-->
        </div>
    `
    buttonGroup.getElementsByClassName('word-button')[0].addEventListener('click', wordButtonClick);
    buttonGroup.getElementsByClassName('button-translate')[0].addEventListener('click', translateButtonClick);
    buttonGroup.getElementsByClassName('button-marker')[0].addEventListener('click', markerButtonClick);
};

function saveFileCallback(data){
    let words = JSON.parse(data)['words'];
    let div = document.getElementById('canvas');
    div.innerHTML = '';
    // TODO: crutch
    for (let word in words){
        let caption = words[word][0];
        let frequency = words[word][1];
        getRequest(checkWordCallback, '/check/' + caption, [caption, frequency]);
    }
};

function wordButtonClick(e){
    let word = e.target.innerText.split(' ')[0];
    getRequest(touchWordCallback, '/touch/' + word);
};

function uploadFile(){
    let file = document.getElementById("inputGroupFile04").files[0];
    let context = [['file', file] , ['csrfmiddlewaretoken', getCookie('csrftoken')]]; 
    postRequest(saveFileCallback, '/upload_file/', context);
};

function uploadText(){
    let text = document.getElementById('textArea').value;
    let textDisplay = document.getElementById('textDisplay');
    textDisplay.innerText = text;
    let context = [['text', text] , ['csrfmiddlewaretoken', getCookie('csrftoken')]];
    postRequest(saveFileCallback, '/get_text/', context);
};

function translateButtonClick(e){
    let word = e.target.parentElement.parentElement.id;
    getRequest(translateCallback, '/translate/' + word)
};

function translateCallback(response){
    let container = document.getElementById('translation-id');
    let html = JSON.parse(response)['translation'];
    container.innerHTML = html;
};

function markerButtonClick(e){
    let word = e.target.parentElement.parentElement.id;
    let textDisplay = document.getElementById('textDisplay');
    let text = textDisplay.innerHTML;
    // text = text.replace('<span class="bg-warning">', '');
    // text = text.replace('</span>', '');
    // text = text.replace(word, '<span class="bg-warning">' + word + '</span>');
    // TODO: crutch
    text = replaceAll(text, '<span class="bg-warning">', '');
    text = replaceAll(text,'</span>', '');
    text = replaceAll(text, word, '<span class="bg-warning">' + word + '</span>');
    textDisplay.innerHTML = text;
};

let input = document.getElementById('inputGroupFile04');
// TODO: to change stranges id
input.addEventListener('change', showFileName);

let uploadButton = document.getElementById('inputGroupFileAddon04');
uploadButton.addEventListener('click', uploadFile);

let textAreaButton = document.getElementById('textAreaButton');
textAreaButton.addEventListener('click', uploadText);