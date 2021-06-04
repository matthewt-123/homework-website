var validate = function(e) {
    var t = e.value;
    e.value = (t.indexOf(".") >= 0) ? (t.substr(0, t.indexOf(".")) + t.substr(t.indexOf("."), 1)) : t;
    
}



$('tr.date_field').each(function() {
    var t = this.cells[1].textContent.split('-');
    $(this).data('_ts', new Date(t[2], t[1]-1, t[0]).getTime());
}).sort(function (a, b) {
   return $(a).data('_ts') < $(b).data('_ts');
}).appendTo('tbody');