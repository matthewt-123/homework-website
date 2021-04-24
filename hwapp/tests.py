from django.test import TestCase

# Create your tests here.
$(document).ready(function() {           
    $('table tbody tr td .completed').click(function() {   
            $.ajax({ 
                data: $(this).serialize(), 
                type: $(this).attr('method'), 
                url: $(this).attr('action'), 
                      
                success: function(response) { 
                    // on success..
                },
                error: function(e, x, r) { 
                   // on error...                           

                }

            }); 
        return false;

    }); 
});