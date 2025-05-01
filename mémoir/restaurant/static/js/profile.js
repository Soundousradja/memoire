
document.getElementById('edit-button').addEventListener('click', function() {
    
    document.querySelectorAll('#profile-form input').forEach(function(input) {
        input.disabled = false;
    });
    
   
    document.getElementById('edit-button').style.display = 'none';
    document.getElementById('save-button').style.display = 'inline-block';
});

