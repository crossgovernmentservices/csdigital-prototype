var toggleObjective = function(event) {
  console.log('here');
  var clicked = event.currentTarget,
    details = $(clicked).next(),
      toggle = $(clicked).find('.toggle a');
  event.preventDefault();
  details.toggle();
  toggle.toggle();
};

var templateEditable = function(event) {
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


var userLookup = function(event) {
  event.preventDefault();
  var input = $("input[name='q']"),
      searchValue = input.val().trim();
  $.ajax({
    type: 'GET',
    url: '/users.json?q='+searchValue,
    contentType: 'application/json',
    success: function(data) {
        renderUsers(data.users);
    },
    error: function(xhr, options, error) {
      console.log(error);
      $('.message').text('No results');
    }
  });
};


var renderUsers = function(users) {
  $.each(users, function(index, user) {
    var template = $.templates("#user-template"),
      html = template.render({
        'userEmail': user.email
    });
    $('#users').append(html);
  });
};


$(document).ready(function() {
  $('.objective-header').click(toggleObjective);
  $('.edit-controls').click(templateEditable);
  $('#user-lookup').click(userLookup);
});
