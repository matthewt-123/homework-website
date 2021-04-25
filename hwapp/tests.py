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
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
