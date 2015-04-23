var App = window.App = {};

var imageSelect, fileSelect, progressBar;
var mainColor, alternativeColors;
var imageFileView, imageDropView, imagePreviewView;

App.start = function(){
  imageSelect = document.getElementById('image_select');
  fileSelect = document.getElementById('file_select');
  progressBar = document.getElementById('progress_bar');

  mainColor = document.getElementById('main_color');
  alternativeColors = document.getElementById('alternative_colors');

  imageFileView = document.getElementById('image_file_view');
  imageDropView = document.getElementById('image_drop_view');
  imagePreviewView = document.getElementById('image_preview_view');

  fileSelect.onchange = function(){
    App.loadFile(this.files[0]);
  };

  function dragstart(){
    imageFileView.style['display'] = "none";
    imageDropView.style['display'] = "block";
    imagePreviewView.style['display'] = "none";
    return false;
  }
  function dragend(){
    App.reset();
    return false;
  }
  imageSelect.ondragover = dragstart;
  imageSelect.ondragleave = dragend;
  imageSelect.ondragend = dragend;
  imageSelect.ondrop = function(e){
    e.preventDefault();
    dragend();
    App.loadFile(e.dataTransfer.files[0]);
  }
};

App.reset = function(){
  imageFileView.style['display'] = "block";
  imageDropView.style['display'] = "none";
  imagePreviewView.style['display'] = "none";
  mainColor.style['background'] = 'white';
  mainColor.innerHTML = '';
  alternativeColors.innerHTML = '<td></td>';
};

App.loadFile = function(file){
  if (!file) return;

  App.previewFile(file);

  var formData = new FormData();
  formData.append('file', file);

  var xhr = new XMLHttpRequest();
  xhr.open('POST', 'upload');
  xhr.onload = function(e) {
    progressBar.style['width'] = ''+100+'%';
    var response = e.currentTarget.response;
    try {
      var rsp = JSON.parse(response);
      if (rsp.error) {
        imagePreviewView.innerHTML = '<p class="error">'+rsp.error+'</p>';
      } else {
        App.resultId = rsp.taskId;
        App.pollResult();
      }
    } catch (e) {
      App.reset();
    }
  };
  xhr.upload.onprogress = function(e){
    if (e.lengthComputable) {
      var complete = (e.loaded / e.total * 100 | 0);
      progressBar.style['width'] = ''+complete+'%';
    }
  };
  xhr.send(formData);
};

App.previewFile = function(file){
  var reader = new FileReader();
  reader.onload = function (e) {
    var image = new Image();
    image.src = e.target.result;

    imageFileView.style['display'] = "none";
    imageDropView.style['display'] = "none";
    imagePreviewView.style['display'] = "block";

    imagePreviewView.innerHTML = "";
    imagePreviewView.appendChild(image);
  };
  reader.readAsDataURL(file);
};

App.pollResult = function(){
  if (!App.resultId) return;
  App.queryResult(App.resultId, function(rsp){
    mainColor.innerHTML = '<div class="status">'+rsp.state+'</div>';
    if (rsp.state==='PENDING') {
      setTimeout(App.pollResult, 1000);
    } else if (rsp.state==="SUCCESS") {
      App.showResult(rsp.value);
    }
  }, function(err){
    console.error(err);
  });
};

App.queryResult = function(resultId, success, failure){
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "result/"+resultId, true);
  xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  xhr.onload = function (e) {
    if (xhr.readyState === 4) {
      if (xhr.status === 200) {
        try {
          var rsp = JSON.parse(xhr.responseText)
          if (success) success(rsp);
        } catch (e) {
          if (failure) failure(new Error("invalid response object"));
        }
      } else {
        if (failure) failure(xhr.statusText||new Error("request failed "+xhr.status));
      }
    }
  };
  xhr.onerror = function (e) {
    if (failure) failure(xhr.statusText||new Error("request failed "+xhr.status));
  };
  xhr.send();
};

App.showResult = function(value){
  mainColor.style['background'] = '#'+value.color;
  mainColor.innerHTML = "#"+value.color;
  alternativeColors.innerHTML = value.alternatives.map(function(color){
    return '<td style="background: #'+color+';">#'+color+'</td>';
  }).join('');
};
