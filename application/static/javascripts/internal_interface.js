(function($, window) {

  $(function() {

    // toggle add staff member form
    $('.staff-list__add-btn').on('click', function() {
      $(this).toggleClass('active');
      $('.add-staff-member-form').toggle();
      return false;
    });

    var $linkForms = $('.add-link-form');
    // toggle add another link form
    $('.add-link-btn').on('click', function() {
      $(this).toggleClass('active');

      var linkType = $(this).data('link-form');
      $linkForms.filter( "[data-linking-type='" + linkType + "']" ).toggle();
      return false;
    });

  });

}).call(this, jQuery, window);