function reset_pw() {
    fetch(`/change_password`, {
        method: 'PATCH',
        headers: {
            'X-CSRFToken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
        },
        credentials: "same-origin",
    })
    .then(response => response.json())
    .then(result => {
        if(result['status'] == 400) {
            /* show error message if error*/
            const alert = document.getElementById('error_message')
            alert.innerHTML = result['message']
            alert.style.display='block'

            /* hide success message if any */
            document.getElementById('alert').style.display='none'
        } else {
            /* show error message if error*/
            const alert = document.getElementById('alert')
            alert.innerHTML = result['message']
            alert.style.display='block'

            /* hide success message if any */
            document.getElementById('error_message').style.display='none'
        }
    });
    return false
}
function generate_link_class() {
    globalUrl.searchParams.set('class_id', document.getElementById('class_select').value)
    document.getElementById("download").setAttribute('href', globalUrl)
}
function generate_link_complete() {
    globalUrl.searchParams.set('completed', document.getElementById('completed').value)
    document.getElementById("download").setAttribute('href', globalUrl)
}
function confirmation_msg() {
    alert_msg = document.getElementById("alert")
    alert_msg.setAttribute("class", "alert alert-success")
    alert_msg.innerHTML = "Homework exported successfully"
    alert_msg.style.display = "block"
}