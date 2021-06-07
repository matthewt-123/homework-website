var validate = function(e) {
    var t = e.value;
    e.value = (t.indexOf(".") >= 0) ? (t.substr(0, t.indexOf(".")) + t.substr(t.indexOf("."), 1)) : t;
    
}





$('#non_functional_form').submit(function () {
    return false;
   });
$(document).ready(function() {
    $('#class_filter').multiselect();
});

   
