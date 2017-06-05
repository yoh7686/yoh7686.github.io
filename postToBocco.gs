function getAccessKeyOfBocco(){//アクセスキーを取得
  var prop = PropertiesService.getScriptProperties().getProperties();
  var bapikey = prop.BOCCO_API;
  var bemail = prop.BOCCO_EMAIL;
  var bpass = prop.BOCCO_PASS;
  var URL = "https://api.bocco.me/alpha/sessions"
  var options = {
    method : "post",
    followRedirects: false,
    contentType: "application/x-www-form-urlencoded",
    payload : {
      apikey: bapikey,
      email: bemail,
      password: bpass
    }
  };
  var response = UrlFetchApp.fetch(URL, options);
  var json = JSON.parse(response);
  var access_token = json["access_token"];
  PropertiesService.getScriptProperties().setProperty("BOCCO_ACCESS_TOKEN", access_token);
}

function getRoomIDOfBocco(){//RoomIDを取得
    var prop = PropertiesService.getScriptProperties().getProperties();
    var access_token = prop.BOCCO_ACCESS_TOKEN;
    var URL = "https://api.bocco.me/alpha/rooms/joined?access_token=";
    var response = UrlFetchApp.fetch(URL+access_token);
    var json = JSON.parse(response);
    PropertiesService.getScriptProperties().setProperty("BOCCO_UUID", json[0]["uuid"]);
}

function sendMessageToBocco(posttext){//Boccoにメッセージを送信
  var prop = PropertiesService.getScriptProperties().getProperties();
  var roomID = prop.BOCCO_UUID;
  var URL = "https://api.bocco.me/alpha/rooms/"+roomID+"/messages";
  var token = prop.BOCCO_ACCESS_TOKEN;
  var uuid = guid();
  Logger.log(uuid);
  var options = {
    method : "post",
    followRedirects: false,
    contentType: "application/x-www-form-urlencoded",
    payload : {
      access_token: token,
      media: "text",
      unique_id: uuid, 
      text: posttext,
      "Accept-Language": "ja"
    }
  };
  var response = UrlFetchApp.fetch(URL,options);
  var json = JSON.parse(response);
  if(json["code"]=="401001"){
    getAccessKeyOfBocco();
    getRoomIDOfBocco();
    sendMessageToBocco(posttext);
    exit;
  }
}
