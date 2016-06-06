(function($, window) {

  $(function() {
    var $tagSections = $(".tag-type-section");

    $tagSections.on("click", '.edit-link, .cancel-link', function(evt) {
      $(evt.delegateTarget).toggleClass('edit-mode');
      return false;
    });

    $(".tag-list-edit").on("click", ".save-btn", function(evt) {
      evt.stopPropagation();
      return false;
    });

    $(".tag-list-edit .tag-list-add-btn").on("click", function(evt) {
      var $this = $(evt.currentTarget);
      var $lastTagInput = $this.parent(".tag-list-edit").find("form").last();

      $lastTagInput
        .clone( true )
          .find('input')
            .val("")
            .data('original-value', "")
          .end()
          .insertAfter( $lastTagInput );
    });

    $(".tag-entry-field").on("input keypress", function(evt) {
      var $this = $(this),
          $wrap = $this.parents(".tag-entry-group");

      if( $(this).val() != $(this).data("original-value") ) {
        $wrap.addClass("changed");
      } else {
        $wrap.removeClass("changed");
      }
    });
  });

}).call(this, jQuery, window);
