$(document).ready(function() {
    $('#searchButton').click(function() {
        $('inputDiv').css('display', 'none');
        $('#cover').slideDown();
        $('div.inputDiv').css('display', 'block');
        $('#result').css('display', 'none');
        $('.header').css('display','none');
    });
});
