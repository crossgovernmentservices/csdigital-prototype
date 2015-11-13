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
        editableSection = $(editLink).next();

    if( $(editLink).attr('contenteditable') == 'true'){
        $(editableSection).attr('contenteditable', 'false');
        $(editableSection).blur();
    } else {
        $(editableSection).attr('contenteditable', 'true');
        $(editableSection).focus();
    }
    $('.edit-controls a').toggle();
};

$(document).ready(function(){
    $('.objective-header').click(toggleObjective);
    $('.edit-controls').click(templateEditable);
});
