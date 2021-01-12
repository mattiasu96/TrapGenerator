console.log('gestione js');

$(document).ready(function() {

    // avoid hard-coding urls...
    var yourApp = {
        contaUrl: "prova",
        bareru: "wait",
        mG: "midiGeneration"
    };


    $('#gatto').on("load", function(e) {

        console.log('WAIT');

        // $.get(yourApp.contaUrl);
        $.get(yourApp.mG, function(json) {     
            //  alert("I have finished counting");                    
            //  parent.window.location.reload(true);      
            // $.get(yourApp.bareru);
            console.log('entrato');
            window.location.href = "/midiGeneration";
        });
    });
});
/*
$(document).ready(function() {

    // avoid hard-coding urls...
    var yourApp = {
        contaUrl: "prova",
        bareru: "wait"
    };


    $('#btnGo').click(function(e) {
        e.preventDefault();  
        // set css classes and text of button
        $(this)
            // .removeClass('btn-primary')
            // .addClass('btn-danger disabled') // with *disabled* I'm sure that the button is not clickable
            .text('WAIT');

        console.log('WAIT');


        $.get(yourApp.contaUrl, function(json) {     
            //  alert("I have finished counting");                    
            //  parent.window.location.reload(true);      
            $.get(yourApp.bareru);
            window.location.href = "/wait";
        });
    });
});*/