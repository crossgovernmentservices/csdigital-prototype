(function($, window) {

  $(function() {
    var $form = $(".objective-tags-form"),
        $first = $(".tag-entry-group").first();

    $(".add-tag-btn").on("click", function(evt) {
      var $input = $first.clone(true).find(".tag-entry-field").val("").end();
      $(".objective-tags").append( $input );
      evt.preventDefault();
      return false;
    });

    $(".msg-box-btn--del").on("click", function(evt) {
      $(evt.currentTarget).parents(".tag-entry-group").remove();
      return false;
    });
  });

}).call(this, jQuery, window);
