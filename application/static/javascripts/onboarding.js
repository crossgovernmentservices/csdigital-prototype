(function($, window) {

  $(function() {
    var $form = $(".objective-tags-form"),
        $first = $(".tag-entry-group").first();

    $(".add-tag-btn").on("click", function(evt) {
      
      $(".objective-tags").append( $first.clone(true) );
      evt.preventDefault();
      return false;
    });

    $(".msg-box-btn--del").on("click", function(evt) {
      $(evt.currentTarget).parents(".tag-entry-group").remove();
      return false;
    });
  });

}).call(this, jQuery, window);
