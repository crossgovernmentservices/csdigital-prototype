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
    editableContainer = $(editLink).next();
  if( $(editableContainer).attr('contentEditable') == 'false'){
    $(editableContainer).attr('contentEditable', 'true');
    $(editableContainer).focus();
  } else {
    $(editableContainer).attr('contentEditable', 'false');
    $(editableContainer).blur();
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
      existing = $('li:not(:contains(' + user.email + ')'),
      html = template.render({
        'userEmail': user.email
      });
    if(existing.length == 0){
      $('#recipient-list').append(html);
      $('#recipient-list li a').click(removeRecipient);
      $("input[name='q']").val('');
    } else {
      console.log('email', user.email, 'already in list');
    }
  });
  if( $('#recipient-list li').length > 0 ) {
    $('#submit-request').show();
  }
};

var removeRecipient = function(event) {
  event.preventDefault();
  var toRemove = event.currentTarget;
  $(toRemove).parent().remove();
  if( $('#recipient-list li').length == 0 ) {
    $('#submit-request').hide();
  }
};

var submitRequest = function(event) {
  event.preventDefault();
  var recipientList = $('.recipient-email'),
    recipients = [];

  recipientList.each(function(){
    recipients.push($(this).text().trim());
  });
  $.ajax({
    type: 'POST',
    url: '/performance-review/feedback-request',
    contentType:  'application/json',
    data: JSON.stringify({"recipients": recipients}),
    success: function(data) {
      console.log('ok then');
      $('#submit-request').hide();
      $('#recipient-list li').each(function() {
        $(this).find('a').remove();
        if($(this).find('.request-status').text() != "Requested"){
          $(this).append('<span class="request-status">Requested</span>');
        }
        $("input[name='q']").val('');
      });
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
  $('#submit-request').click(submitRequest);
});
