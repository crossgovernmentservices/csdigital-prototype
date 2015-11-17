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

var emailLookup = function(event) {
  event.preventDefault();
  var input = $("input[name='q']"),
      searchValue = input.val().trim();
  $.ajax({
    type: 'GET',
    url: '/users.json?q='+searchValue,
    contentType: 'application/json',
    success: function(data) {
        renderRecipients(data.users);
    },
    error: function(xhr, options, error) {
      console.log(error);
      $('.message').text('No results');
    }
  });
};

var renderRecipients = function(users) {
  $.each(users, function(index, user) {
    var template = $.templates("#recipient-template"),
      html = template.render({
        'userEmail': user.email
    });
    $('#recipient-list').append(html);
    $('#recipient-list li a').click(removeRecipient);
  });
  if( $('#recipient-list li').length > 0 ) {
    $('#submit-request').show();
  }
};

var removeRecipient = function(event) {
  event.preventDefault();
  var toRemove = event.currentTarget;
  $(toRemove).parent().remove();
  debugger;
  if( $('#recipient-list li').length == 0 ) {
    $('#submit-request').hide();
  }
};

var submitRequest = function(event) {
  console.log('do it');
  var recipients = $('#recipient-list');
  debugger;
  $.ajax({
    type: 'POST',
    url: '/feedback-request.json',
    contentType: 'application/json',
    success: function(data) {
      console.log('ok then');
    },
    error: function(xhr, options, error) {
      console.log(error);
      $('.message').text('No results');
    }
  });
};

$(document).ready(function() {
  $('.objective-header').click(toggleObjective);
  $('.edit-controls').click(templateEditable);
  $('.search-form').submit(emailLookup);
});
