var toggleObjective = function(event){
    console.log('here');
    var clicked = event.currentTarget,
        details = $(clicked).next(),
        toggle = $(clicked).find('.toggle a');
    event.preventDefault();
    details.toggle();
    toggle.toggle();
};

var templateEditable = function(event){
    event.preventDefault();
    var editLink = event.currentTarget
        editableContainer = $(editLink).next(),
            editableSection = $(editableContainer).find('textarea');

    if( $(editableSection).attr('disabled') ){
        $(editableSection).removeAttr('disabled');
        $(editableSection).focus();
    } else {
        $(editableSection).attr('disabled', 'true');
        $(editableSection).blur();
    }
    $('.edit-controls a').toggle();
};

$(document).ready(function(){
    $('.objective-header').click(toggleObjective);
    $('.edit-controls').click(templateEditable);
});
