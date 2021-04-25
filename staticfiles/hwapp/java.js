var validate = function(e) {
    var t = e.value;
    e.value = (t.indexOf(".") >= 0) ? (t.substr(0, t.indexOf(".")) + t.substr(t.indexOf("."), 1)) : t;
    
}
$('#hw_completion').change(function(){
    var name = $(this).attr('name')
    $("input[type=hidden][name=" + name + "]").val(($(this).is(":checked") ? "Yes" : "No"));
    console.log($("input[type=hidden][name=" + name + "]").val());
})
$(document).ready(function(){
    // click on button submit
    $('#hwform').click(function(){
        // send ajax
        $.ajax({
            url: '/', // url where to submit the request
            type : "POST", // type of action POST || GET
            dataType : 'json', // data type
            data : $("#hwform").serialize(), // post data || get data
            success : function(result) {
                // you can see the result from the console
                // tab of the developer tools
                console.log(result);
            },
            error: function(xhr, resp, text) {
                console.log(xhr, resp, text);
            }
        })
    });
});
