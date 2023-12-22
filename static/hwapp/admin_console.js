function confirm_refresh() {
    var result = confirm("Would you like to send an email to all users?");
        if (result == true) {
            doc = admin(function1="refresh");
        } else {
            alert("Action Cancelled");
        }
};
function admin(function1) {
    fetch(`/admin_view`, {
        method: 'POST',
        headers: {
                'X-CSRFToken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
            },
        credentials: 'same-origin',
        body: JSON.stringify({
            'function': `${function1}`
        })
    })
    .then(response=>response.json())
    .then(result => {
        if(result['status'] == 200) {
            const alert = document.getElementById('alert')
            alert.innerHTML = `${function1} completed successfully`
            alert.style.display='block'
        }
    })
}