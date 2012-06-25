function getHostData(handleData) {
    $.ajax({
        type:"GET",
        url:'/hosts',
        dataType:'json',
        success: function (results) {
            handleData(results);
        },
        error: function(error){
            console.log('oops');
        }
    });
};