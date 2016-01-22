(function($, window) {

  $(function() {

    // toggle add staff member form
    $('.staff-list__add-btn').on('click', function() {
      $(this).toggleClass('active');
      $('.add-staff-member-form').toggle();
      return false;
    });
  });

}).call(this, jQuery, window);