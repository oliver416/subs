const spinner = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
Loading...`;

let currentUser = '';

function showFileName(e){
    let fileName = e.target.files[0].name;
    let label = document.getElementsByClassName('custom-file-label')[0];
    label.innerHTML = fileName;
}

function getCookie(name) {
    let cookie = document.cookie
    if (document.cookie && document.cookie != ''){
        if (name === cookie.split('=')[0]){
            return cookie.split('=')[1].toString()
        }
    }
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

function getCurrentUserCallback(data){
    let json = JSON.parse(data);
    currentUser = json['current_user'];
}

function getCurrentUser(){
    getRequest(getCurrentUserCallback, '/accounts/profile/files/get_current_user/');
}

function addFileIntoList(fileArray){
    let fileList = document.getElementsByClassName('file-list')[0];
    for (let file in fileArray){
        let fileName = fileArray[file];
        let newFile = document.createElement('li');
        newFile.className = "list-group-item d-flex justify-content-between lh-condensed"
        newFile.innerHTML = 
        `<a href="/static/main/storage/`+fileName+`">`+fileName+`</a>
        <button type="button" class="close ml-auto" aria-label="Close" onclick="deleteFileClick(this)">
            <span aria-hidden="true">×</span>
        </button>
        <br>`
        fileList.appendChild(newFile);
        if (fileArray.length === 1){
            newFile.scrollIntoView();
        }
    }
}

function addMessageIntoList(messageArray){
    let messageList = document.getElementsByClassName('message-list')[0];
    for (let msg in messageArray){
        let user = messageArray[msg]['user'];
        let date = messageArray[msg]['date'];
        let text = messageArray[msg]['text'];
        let newMessage = document.createElement('li');
        if (currentUser === user){
            newMessage.className = "list-group-item list-group-item-success text-left";
            newMessage.innerHTML = 
            user + ` <span>` + date + `</span>` +
            `<button type="button" class="close ml-auto" aria-label="Close" onclick="deleteMessageClick(this)">
                <span aria-hidden="true">×</span>
            </button> 
            <br>
            <strong>` + text + `</strong>`;
        }else{
            newMessage.className = "list-group-item list-group-item-danger text-right";
            newMessage.innerHTML = 
            user + ` <span>` + date + `</span>` +
            `<br>
            <strong>` + text + `</strong>`;
        }
        messageList.appendChild(newMessage);
        if (messageArray.length === 1){
            newMessage.scrollIntoView();
        }
    }
    
}

function saveFileCallback(data){
    let button = document.getElementById('inputGroupFile');
    let json = JSON.parse(data);
    if (json['uploaded'] === true){
        addFileIntoList([json['file_name']]);
    }
    button.innerHTML = 'Upload';
}

function uploadFile(){
    let button = document.getElementById('inputGroupFile');
    let file = document.getElementById("inputGroup").files[0];
    let context = [['file', file] , ['csrfmiddlewaretoken', getCookie('csrftoken')]]; 
    button.innerHTML = spinner;
    postRequest(saveFileCallback, '/accounts/profile/files/upload_file/', context);
}

function sendMessageCallback(data){
    let json = JSON.parse(data);
    if (json['saved'] === true){
        addMessageIntoList([{'user': json['user'], 'date': json['date'], 'text':json['message']}]);
    }
}

function sendMessage(){
    let textArea = document.getElementsByClassName('form-control')[0];
    let context = [['text', textArea.value] , ['csrfmiddlewaretoken', getCookie('csrftoken')]];
    postRequest(sendMessageCallback, '/accounts/profile/files/send_message/', context);
}

function deleteFileCallback(data){
    let json = JSON.parse(data);
    let statusBar = document.getElementById('statusBar');
    if (json['deleted'] === true){
        statusBar.innerText = 'File has been deleted'
    }else{
        statusBar.innerText = 'Error deleting file'
    }
}

function deleteFileClick(e){
    let parentNode = e.parentNode;
    let file_name = parentNode.getElementsByTagName('a')[0].innerText;
    let context = [['file_name', file_name], ['csrfmiddlewaretoken', getCookie('csrftoken')]];
    postRequest(deleteFileCallback, '/accounts/profile/files/delete_file/', context);
    parentNode.remove();
}

function allFilesCallback(data){
    let json = JSON.parse(data);
    let fileList = document.getElementsByClassName('file-list')[0];
    fileList.innerText = '';
    addFileIntoList(json['files'])
}

function allFilesButtonClick(){
    getRequest(allFilesCallback, '/accounts/profile/files/check_files/');
}

function deleteMessageCallback(data){
    let json = JSON.parse(data);
    let statusBar = document.getElementById('statusBar');
    if (json['deleted'] === true){
        statusBar.innerText = 'Message has been deleted'
    }else{
        statusBar.innerText = 'Error deleting message'
    }
}

function deleteMessageClick(e){
    let parentNode = e.parentNode;
    let message = parentNode.getElementsByTagName('strong')[0].innerText;
    let context = [['message', message], ['csrfmiddlewaretoken', getCookie('csrftoken')]];
    postRequest(deleteMessageCallback, '/accounts/profile/files/delete_message/', context);
    parentNode.remove();
}

function allMessagesCallback(data){
    let json = JSON.parse(data);
    let messageList = document.getElementsByClassName('message-list')[0];
    messageList.innerText = '';
    addMessageIntoList(json['messages']);
}

function allMessagesButtonClick(){
    getRequest(allMessagesCallback, '/accounts/profile/files/get_messages/');
}

if (currentUser === ''){
    getCurrentUser();
};

function goTo(data){
    window.location.href=data;
}

let input = document.getElementById('inputGroup');
input.addEventListener('change', showFileName);

let uploadButton = document.getElementById('inputGroupFile');
uploadButton.addEventListener('click', uploadFile);

let sendButton = document.getElementById('sendButton');
sendButton.addEventListener('click', sendMessage);

let allFilesButton = document.getElementById('allFilesButton');
allFilesButton.addEventListener('click', allFilesButtonClick);

let allMessagesButton = document.getElementById('receiveButton');
allMessagesButton.addEventListener('click', allMessagesButtonClick);

// TODO[usability]: edit layout (including medium screens)