const spinner = `<div class="spinner-border text-primary" role="status">
<span class="sr-only">Loading...</span>
</div>`;

let successButtons = [];

function getCookie(name) {
    let cookie = document.cookie
    if (document.cookie && document.cookie != ''){
        if (name === cookie.split('=')[0]){
            return cookie.split('=')[1].toString()
        }
    }
}

function replaceAll(str, find, replace) {
    return str.replace(new RegExp(find, 'g'), replace);
}

function toUppercaseFirst(str) {
    if (!str) return str;
  
    return str[0].toUpperCase() + str.slice(1);
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
}

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
}

function touchWordCallback(response){
    let word = JSON.parse(response)['word'];
    let exists = JSON.parse(response)['exists'];
    let newWords = document.getElementsByClassName('newWords')[0];
    let userWords = document.getElementsByClassName('userWords')[0];
    let buttonGroup = document.getElementById(word.toLowerCase());
    let buttonWord = buttonGroup.getElementsByClassName('word-button')[0];
    let buttonDropdown = buttonGroup.getElementsByClassName('button-dropdown')[0];
    if (exists === true){
        buttonWord.classList.remove('btn-danger');
        buttonWord.classList.add('btn-success');
        buttonDropdown.classList.remove('btn-danger');
        buttonDropdown.classList.add('btn-success');
        newWords.innerText = Number(newWords.innerText) - 1;
        userWords.innerText = Number(userWords.innerText) + 1;
    }else{
        buttonWord.classList.remove('btn-success');
        buttonWord.classList.add('btn-danger');
        buttonDropdown.classList.remove('btn-success');
        buttonDropdown.classList.add('btn-danger');
        newWords.innerText = Number(newWords.innerText) + 1;
        userWords.innerText = Number(userWords.innerText) - 1;
    }
}

function checkWordCallback(response){
    let json = JSON.parse(response)['words'];
    let canvas = document.getElementById('canvas');
    canvas.innerHTML = '';
    for (let item in json){
        let word = json[item]['word'];
        let frequency = json[item]['frequency'];
        let exsistance = json[item]['exists'];
        let buttonGroup = document.createElement('div');
        buttonGroup.id = word;
        buttonGroup.className = 'btn-group p-3 buttonGroup';
        canvas.appendChild(buttonGroup);
        let button = document.createElement('button');
        // TODO[refactoring]: refactoring needed - dirty code??
        button.innerText = word + ' ' + frequency;
        let dropdownStyle = '';
        if (exsistance === true){
            button.className = 'btn btn-success word-button';
            dropdownStyle = 'btn-success';
        }else{
            button.className = 'btn btn-danger word-button';
            dropdownStyle = 'btn-danger';
            let newWords = document.getElementsByClassName('newWords')[0];
            newWords.innerText = Number(newWords.innerText) + 1;
        }
        buttonGroup.innerHTML = `
            ` + button.outerHTML + `
            <button type="button" class="btn ` + dropdownStyle + ` dropdown-toggle dropdown-toggle-split button-dropdown" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
            <span class="sr-only">Toggle Dropdown</span>
            </button>
            <div class="dropdown-menu">
            <button class="dropdown-item button-translate">Translate</button>
            <div class="dropdown-divider"></div>
            <button class="dropdown-item bg-info button-name">Mark as a Name</button>
            <!--<button class="dropdown-item bg-secondary button-mistake">Mark as a mistake</button>-->
            </div>
        `
        buttonGroup.getElementsByClassName('word-button')[0].addEventListener('click', wordButtonClick);
        buttonGroup.getElementsByClassName('button-dropdown')[0].addEventListener('click', markerButtonClick);
        buttonGroup.getElementsByClassName('button-translate')[0].addEventListener('click', translateButtonClick);
        buttonGroup.getElementsByClassName('button-name')[0].addEventListener('click', nameButtonClick);
    }  
}

function uploadTextCallback(data){
    let words = JSON.parse(data)['words'];
    let div = document.getElementById('canvas');
    let allWords = document.getElementsByClassName('allWords')[0];
    allWords.innerText = words.length;
    let newWords = document.getElementsByClassName('newWords')[0];
    newWords.innerText = '0';
    div.innerHTML = '';
    div.innerHTML = spinner;
    let context = [['words', JSON.stringify(words)] , ['csrfmiddlewaretoken', getCookie('csrftoken')]]; 
    postRequest(checkWordCallback, '/check/', context);
}

function wordButtonClick(e){
    let word = e.target.innerText.split(' ')[0];
    getRequest(touchWordCallback, '/touch/' + word);
    getRequest(()=>{}, '/check_vocabulary/' + word);
}

function uploadText(){
    let text = document.getElementById('textArea').value;
    let textDisplay = document.getElementById('textDisplay');
    textDisplay.innerText = text;
    let context = [['text', text] , ['csrfmiddlewaretoken', getCookie('csrftoken')]];
    postRequest(uploadTextCallback, '/get_text/', context);
}

function translateButtonClick(e){
    let word = e.target.parentElement.parentElement.id;
    let container = document.getElementById('translation-id');;
    container.innerHTML = spinner;
    getRequest(translateCallback, '/translate/' + word);
}

function translateCallback(response){
    let container = document.getElementById('translation-id');
    let html = JSON.parse(response)['translation'];
    container.innerHTML = html;
}

function markerButtonClick(e){
    let word = e.target.parentElement.id;
    let textDisplay = document.getElementById('textDisplay');
    let text = textDisplay.innerHTML;
    let words = [word, toUppercaseFirst(word)]

    text = replaceAll(text, '<span id="targetWord" class="bg-warning">', '');
    text = replaceAll(text,'</span>', '');
    for (let i in words){
        text = replaceAll(text, words[i], '<span id="targetWord" class="bg-warning">' + words[i] + '</span>');
    }
    textDisplay.innerHTML = text;

    let targetWord = document.getElementById('targetWord');
    if (targetWord !== null){
        targetWord.scrollIntoView();
    }
}

function nameButtonClick(e){
    let word = e.target.parentElement.parentElement.id;
    word = word.replace(word[0], word[0].toUpperCase())
    getRequest(touchWordCallback, '/touch/' + word);
    getRequest(()=>{}, '/check_vocabulary/' + word);
}

function hideWords(e){
    if (e.target.localName === 'label'){
        if (e.target.classList.contains('active') === true){
            let buttons = document.getElementsByClassName('buttonGroup');
            buttons = Array.prototype.slice.call(buttons);
            for (let i in buttons){
                let buttonGroup = buttons[i];
                if (buttonGroup.getElementsByClassName('btn-success').length > 0){
                    successButtons.push(buttonGroup);
                }
            }
            successButtons.forEach(e => e.remove());
        }else{
            let canvas = document.getElementById('canvas');
            successButtons.forEach(e => canvas.appendChild(e));
        }
    }
}

function goTo(data){
    window.location.href=data;
}

let textAreaButton = document.getElementById('textAreaButton');
textAreaButton.addEventListener('click', uploadText);

let hideWordsButton = document.getElementsByClassName('hideWords')[0];
hideWordsButton.addEventListener('click', hideWords);