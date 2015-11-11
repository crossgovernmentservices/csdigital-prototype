var toggleObjective = function(event){
    var objective = event.currentTarget,
        link = $(objective).find('a'),
        details = $(objective).find('.details');
    event.preventDefault();
    details.toggle();
    link.toggle();

};

$(document).ready(function(){
    $('.objective').click(toggleObjective);
});
