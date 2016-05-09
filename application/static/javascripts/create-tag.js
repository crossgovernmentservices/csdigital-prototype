(function($, window) {

  var addTag = function( tag, $list ) {
    var $tag = $("<li>").text( tag ).addClass("note-tag");
    $list.append( $tag );
  };

  $(function() {
    var $tag_list = $(".tag-list-user"),
        $tag_input = $(".create-tag-input");

    $tag_input.on('keydown', function(evt) {
      var $target = $(evt.currentTarget);
      if( evt.keyCode == 13 ) {
        addTag( $target.val(), $tag_list);
        evt.stopPropagation();
        $tag_input.val("").focus();
      }
    })
    .parents('form').on('submit', function() {
      return false;
    });
  });

}).call(this, jQuery, window);