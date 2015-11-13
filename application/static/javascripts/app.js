var toggleObjective = function(event){
    console.log('here');
    var clicked = event.currentTarget,
        details = $(clicked).next(),
        toggle = $(clicked).find('.toggle a');
    event.preventDefault();
    details.toggle();
    toggle.toggle();

};

$(document).ready(function(){
    $('.objective-header').click(toggleObjective);
});
