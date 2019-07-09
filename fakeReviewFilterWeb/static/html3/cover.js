$(document).ready(function() {
    $('#submitButton').click(function() {
        $('div.header').css('display', 'block');
        $('div#result').css('display', 'block');
        $('div.inputDiv').css('display', 'none');
        $('#cover').slideUp();
	return false;
    });
});
