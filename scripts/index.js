$(document).ready(function($) {

  $( "#searchInput" ).keyup( function( ) {        
    $( "#SearchItems" ).empty( );
    var newarr = [];
    var typ;
    var str;
    for ( var i = 0; i < arr.length; i++ ) {
      si = $( "#searchInput" ).val( ).trim( ).length;
      if (arr[i].length == 3){
        // fragrance data
        typ = 1;
        pos = 2;
        str = arr[i][1] + ': ' + arr[i][0];
      }
      if (arr[i].length == 2){
        // note data
        typ = 2;
        pos = 0;
        str = 'Notes: ' + arr[i][0];
      }
      if ( si > 2
        && str.toLowerCase( ).includes( $( "#searchInput" ).val( ).toLowerCase( ).trim( ) )
        && $( "#searchInput" ).val( ).trim( ).length > 0 ) {
        $( "#SearchItems" ).append( "<p>"
          + '<button style="font-size:36px" onclick="addPref(' + "'" + arr[i][pos] + "'" + ','+typ+',3);"><i class="g fa fa-thumbs-o-up"></i></button>&nbsp&nbsp<button style="font-size:36px" onclick="addPref(' + "'" + arr[i][pos] + "'" + ','+typ+',1);"><i class="r fa fa-thumbs-o-down"></i></button>&nbsp&nbsp'
          + str
          + "</p>");
      }
    }
  });

  $("table tr td i").on('click', function(e){
     alert($(this).closest('td').parent()[0].sectionRowIndex-1);
     alert($(this).closest('td').index()-2);
  });
});

function addPref(num,type,pref){
  var url = "http://127.0.0.1:5000/item/" + num;
  // pref == 3 --> LIKE
  // pref == 1 --> DISLIKE
  // pref == 0 --> CLEARALL
  var txt = '{' +'"typ" : ' + type + ',' +'"prefs"  : ' + pref +'}';
  var hdr = "Content-Type:application/json";
  var obj = JSON.parse(txt);
  var settings = {
      "async": true,
      "crossDomain": true,
      "url": url,
      "type": "PUT",
      "headers": {},
      "data": obj
  }
  $.ajax(settings).done(function (response) {
    populateTable(type, response);
    if (type == 1){
      getRecs(3);
    }
    if (type == 2){
      getRecs(1);
      getRecs(2);
    }
  });
 
}

function getRecs(type) {
  console.log('starting!');
  var url = "http://127.0.0.1:5000/item/" + type;

  var settings = {
      "async": true,
      "crossDomain": true,
      "url": url,
      "method": "GET",
      "headers": {},
      "data": "{}"
  }
  $.ajax(settings).done(function (response) {
      populateRecs(type, response);
  });
};

function convertArray(array, reverse) {
  var arr = [];
  var j = 0;
  if (reverse) {
    for (var i = array.length-1; i >= 0; i--){
      arr[j] = []
      arr[j] = array[i]
      j++;
    }
  }else{
    for (var i = 0; i < array.length; i++){
      arr[j] = []
      arr[j] = array[i]
      j++;
    }
  }
  return arr;
}
function goToSite(link){
  window.open(link, "_blank");
}

function populateRecs(type, array){
  if (type == 1){
    console.log("here it is");
    var table = $("#t-body-1");
    $("#t-body-1 tr").remove(); 
    // var table = $("#rec1Table");
  }
  if (type == 2){
    var table = $("#t-body-2");
    $("#t-body-2 tr").remove(); 
    // var table = $("#rec1Table");
  }
  if (type == 3){
    var table = $("#t-body-3");
    $("#t-body-3 tr").remove(); 
    // var table = $("#rec1Table");
  }
  if (type == 4){
    var table = $("#t-body-4");
    $("#t-body-4 tr").remove(); 
  }
  if (type == 3){
    for (var row in array){
      for (var item in array[row]){
        name = array[row][item][0] + ": " + array[row][item][1];
        sim = array[row][item][2];
        num = array[row][item][3];
        console.log('look');
        console.log(array[row][item]);
        b = "'" + dict_links[num][0] + "'";
        f = "'" + dict_links[num][1] + "'";
        tableRow = "<tr>"
          + "<td>" + name + "</td>"
          + "<td>" + sim + "</td>"
          + '<td><button onclick="goToSite(' + b + ');"><img src="images/b.png"></button></td>'
          + '<td><button onclick="goToSite(' + f + ');"><img src="images/f.png"></button></td>'
          + "</tr>";
        table.append(tableRow);
      }
    }
  }else{
    for (var row in array){
      name = array[row][0] + ": " + array[row][1];
      sim = array[row][2];
      num = array[row][3];
      console.log('look');
      console.log(array[row]);
      b = "'" + dict_links[num][0] + "'";
      f = "'" + dict_links[num][1] + "'";
      tableRow = "<tr>"
        + "<td>" + name + "</td>"
        + "<td>" + sim + "</td>"
        + '<td><button onclick="goToSite(' + b + ');"><img src="images/b.png"></button></td>'
        + '<td><button onclick="goToSite(' + f + ');"><img src="images/f.png"></button></td>'
        + "</tr>";
      table.append(tableRow);
    }
  }
}

function populateTable(type, array) {
  var local_arr;
  console.log('type = ');
  console.log(type);
  console.log('array = ');
  console.log(array);
  var local_arr;
  if (type == 1){
    console.log('inside if');
    local_arr = convertArray(arr, false);
    pos = 2;
    var tableLikes = $("#fragLikesTable");
    var tableDislikes = $("#fragDislikesTable");
    $("#fragLikesTable tbody tr").remove(); 
    $("#fragDislikesTable tbody tr").remove(); 
  }
  if (type == 2){
    local_arr = convertArray(arr, true);
    pos = 0;
    var tableLikes = $("#noteLikesTable");
    var tableDislikes = $("#noteDislikesTable");
    $("#noteLikesTable tbody tr").remove(); 
    $("#noteDislikesTable tbody tr").remove(); 
  }
  var name;
  var brand;
  var tableRow;
  for (var row in array){
    for ( var i = 0; i < local_arr.length; i++ ) {
      if (String(local_arr[i][pos]) == String(array[row][0])){
        name = local_arr[i][0];
        if (type == 1){
          brand = local_arr[i][1];
          brandtd = "<td>" + brand + "</td>";
        }else{
          brandtd = '';
        }
        pref = array[row][1];
        tableRow = "<tr>"
          + brandtd
          + "<td>" + name + "</td>"
          + "</td>"
          + ''
          + "<td>" + '<button style="font-size:24px" onclick="addPref(' + "'" + local_arr[i][pos] + "'" + ',' + type + ',0);"><i class="fa fa-close"></i></button></button>' + "</td>"
          // + '<button style="font-size:24px" onclick="addPref(' + "'" + arr[i][pos] + "'" + ','+typ+',3);"><i class="fa fa-thumbs-o-up"></i></button><button style="font-size:24px" onclick="addPref(' + "'" + arr[i][pos] + "'" + ','+typ+',1);"><i class="fa fa-thumbs-o-down"></i></button>'
          + "</tr>";
        if (pref == 1){
          tableDislikes.append(tableRow);
        }
        if (pref == 3){
          tableLikes.append(tableRow);
        }
        break;
      }
    }
  }
}

var arr;
function doStuff1(data){
  arr = data;
}
function doStuff2(data){
  arr_links = data;
  dict_links = {};
  for (var i = 0; i < arr_links.length; i++){
    dict_links[arr_links[i][0]];
    dict_links[arr_links[i][0]] = [arr_links[i][1], arr_links[i][2]];
  }
}

function parseData(url, callBack){
  Papa.parse(url, {
    download: true,
    dynamicTyping: true,
    complete: function(results){
      callBack(results.data);
    }
  });
}

parseData("csv/f_table.csv", doStuff1);
parseData("csv/links_table.csv", doStuff2);
