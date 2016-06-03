(function($, window) {

  $(function() {
    var $form = $(".objective-tags-form"),
        $first = $(".tag-entry-group").first(),
        $emailForm = $(".additional-email-form"),
        $emailList = $(".list-emails");

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

    // listen for clicks on btn to add email
    $emailForm.find("button").on("click", function(evt) {
      var $input = $emailForm.find("input"),
          email = $input.val();
      addEmailToList( email, $emailList );
      $input.val("");
      return false;
    });

    // remove item if link is clicked
    $emailList.on("click", "a.remove-link", function() {
      $(this).parents("li").remove();
      return false;
    });

    // function to add item to email list
    var addEmailToList = function( email, $list ) {
      var $item = $emailList.find("li").last().clone(),
          $removeLink = $("<span>").append( $("<a>").attr("href", "/").addClass("remove-link").text("Remove") );

      $item.empty().text( email ).append( $removeLink );
      $list.append( $item );
    };

  });

}).call(this, jQuery, window);
