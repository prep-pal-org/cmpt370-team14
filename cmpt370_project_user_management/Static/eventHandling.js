document.addEventListener('DOMContentLoaded', function(){
    const button1 = document.getElementById('CreateProfile')
    const button2 = document.getElementById('SeeUsers')

    button1.addEventListener('click',function() {
        window.location.href = "/create_profile";

    });

    button2.addEventListener('click',function() {
        window.location.href = "/user_list_for_testing";
    });

});