$(document).ready(function () {
    // Gen
    $('#btn-Generate').click(function () {

        // Make prediction by calling api /predict
        $.ajax({
            type: 'POST',
            url: '/Gen',
            contentType: false,
            cache: false,
            processData: false,
            async: true,
            success: function (data) {}
    })});

});