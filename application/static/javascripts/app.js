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
  var editLink = event.currentTarget,
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


var userLookup = function(event){
  event.preventDefault();

  var input = $("input[name='q']"),
      searchValue = input.val().trim();

  if(searchValue.length < 3){
    console.log('do nothing');
    $('#company-selector').hide();
    $('#companies').empty();
    return;
  }

  $('#user-selector').hide();
  $('#users').empty();
  $('.message').empty();

  $.ajax({
    type: 'GET',
    url: '/user-search?q='+searchValue,
    contentType: 'application/json',
    success: function(data) {
        renderUsers(data);
        $('#user-selector').show();
        $('.user-link').click(stuffAddressInPage);
    },
    error: function(xhr, options, error) {
      console.log(error);
      $('#user-selector').empty();
      $('.message').text('No results');
    }
  });
};

var stuffUsersIntoPage = function(event){
  event.preventDefault();
  $('#selected-user').text('');
  var template = $.templates("#selected-user-template"),
      data = $(event.currentTarget).data(),
      html = template.render({
          'user_email': event.currentTarget.text,
      });
  $('#selected-user').append(html);
  $('#user-selector').hide();
  $('#users').empty();
};

var renderUsers = function(addresses) {
  $.each(addresses, function(index, user) {
    var template = $.templates("#user-template"),
      html = template.render({
        'user': user.email
    });
    $('#users').append(html);
  });
};


$(document).ready(function(){
  $('.objective-header').click(toggleObjective);
  $('.edit-controls').click(templateEditable);
});
