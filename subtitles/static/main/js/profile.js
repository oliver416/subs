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

function touchWord(callback, word){
    let xhr = new XMLHttpRequest();
        xhr.addEventListener("load", function (e) {
            if (xhr.status === 200){
                return callback(xhr.response)
            }else {
                return 'Error'
            }
        });
        xhr.open("GET", '/touch/' + word, true);
        xhr.send(null);
};

function touchWordCallback(response){
    let word = JSON.parse(response)['word'];
    let exists = JSON.parse(response)['exists'];
    let button = document.getElementById(word);
    if (exists === true){
        button.classList.remove('btn-danger');
        button.classList.add('btn-success');
    }else{
        button.classList.remove('btn-success');
        button.classList.add('btn-danger');
    }
};

function wordButtonClick(e){
    let word = e.target.innerText.split(' ')[0];
    touchWord(touchWordCallback, word);
    // e.target.remove();
};

function uploadFile(){
    saveFile(saveFileCallback);

    function checkWord(callback, word, frequency){
        let xhr = new XMLHttpRequest();
        xhr.addEventListener("load", function (e) {
            if (xhr.status === 200){
                return callback(xhr.response, word, frequency)
            }else {
                return 'Error'
            }
        });
        xhr.open("GET", '/check/' + word, true);
        xhr.send(null);
    };

    function checkWordCallback(response, word, frequency){
        let button = document.createElement('button');
        let div = document.getElementById('canvas');
        button.innerText = word + ' ' + frequency;
        if (JSON.parse(response)['exists'] === true){
            button.className = 'btn btn-success m-3 word-button';
        }else{
            button.className = 'btn btn-danger m-3 word-button';
        }
        button.id = word;
        div.appendChild(button);
        button.addEventListener('click', wordButtonClick);
    };

    function saveFileCallback(data){
        let words = JSON.parse(data)['words'];
        let div = document.getElementById('canvas');
        div.innerHTML = '';
        // TODO: crutch
        for (let word in words){
            let caption = words[word][0]
            let frequency = words[word][1]
            checkWord(checkWordCallback, caption, frequency);
        }
    };

    function saveFile(callback){
        let file = document.getElementById("inputGroupFile04").files[0];  
        let xhr = new XMLHttpRequest();
        let formData = new FormData();
        xhr.addEventListener("load", function (e) {
            if (xhr.status === 200){
                return callback(xhr.response)
            }else {
                return 'Error'
            }
        });
        formData.append("file", file);
        formData.append("csrfmiddlewaretoken", getCookie('csrftoken'));
        xhr.open("POST", '/upload_file/', true);
        xhr.send(formData);
    };
};

function uploadText(){
    getText(getTextCallback);
    
    function getTextCallback(response){
        document.getElementById('textArea').value = response;
    };

    function getText(callback){
        let text = document.getElementById('textArea').value;
        let xhr = new XMLHttpRequest();
        let formData = new FormData();
        xhr.addEventListener("load", function (e) {
            if (xhr.status === 200){
                return callback(xhr.response)
            }else {
                return 'Error'
            }
        });
        formData.append('text', text);
        formData.append("csrfmiddlewaretoken", getCookie('csrftoken'));
        xhr.open("POST", '/get_text/', true);
        xhr.send(formData);
    };
};

let input = document.getElementById('inputGroupFile04');
// TODO: to change stranges id
input.addEventListener('change', showFileName);

let uploadButton = document.getElementById('inputGroupFileAddon04');
uploadButton.addEventListener('click', uploadFile);

let textAreaButton = document.getElementById('textAreaButton');
textAreaButton.addEventListener('click', uploadText);
// TODO: refactor js