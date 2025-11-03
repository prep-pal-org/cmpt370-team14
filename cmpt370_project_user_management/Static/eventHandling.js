// Linking the user and comments buttons - Randi
document.addEventListener('DOMContentLoaded', function(){
    const button1 = document.getElementById('CreateProfile')
    const button2 = document.getElementById('SeeUsers')
    const button3 = document.getElementById('comment')
    const button4 = document.getElementById('viewcomment')

    button1.addEventListener('click',function() {
        window.location.href = "/create_profile";

    });

    button2.addEventListener('click',function() {
        window.location.href = "/user_list_for_testing";
    });

    button3.addEventListener('click',function(){
        window.location.href = "/create_comment";
    });

    button4.addEventListener('click', function (){
        window.location.href = "/view_comments";
    });

});