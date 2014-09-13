// Author: Niclas
// My Little Ajax library
function ajax(way, uri, fnSuc, fnFail){
var ajaxObj = null;
if (window.XMLHttpRequest){// for brower without ie6
    ajaxObj = new XMLHttpRequest();
}
else{
        ajaxObj = new ActiveXObject("Mincsoft.XMLHTTP");
}

ajaxObj.open(way,uri+'?t='+ new Date().getTime() ,true);
ajaxObj.send();

ajaxObj.onreadystatechange=function()
{
    if(ajaxObj.readyState == 4){
        if(ajaxObj.status == 200){
            fnSuc(ajaxObj.responseText);
            //alert('sucess'+ ajaxObj.responsText);
        }else{
            fnFail(ajaxObj.status);
            //alert('fialed'+ ajaxObj.status);
        }
   }
};
}
