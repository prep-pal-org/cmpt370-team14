document.addEventListener('DOMContentLoaded', function() {
    const button = document.getElementById('showTableButton');
    const table = document.getElementById('myTable');

    button.addEventListener('click', function() {
        table.style.display = 'table';
    });
});