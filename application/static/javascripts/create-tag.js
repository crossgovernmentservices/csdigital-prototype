// extend Local Storage Object
Storage.prototype.setObject = function(key, value) {
    this.setItem(key, JSON.stringify(value));
};

Storage.prototype.getObject = function(key) {
    return this.getItem(key) && JSON.parse(this.getItem(key));
};

(function($, window) {

  // make it persist across prototype pages ??
  var updateLocalList = function( tag ) {
    var tags = localStorage.getObject('tags');
    var tagObj = {
      "name": tag,
      "count": 0
    };

    if( tags ) {
      tags.push( tagObj );
      localStorage.setObject( "tags", tags);
    } else {
      localStorage.setObject( "tags", [tagObj]);
    }
  };

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
        var tag = $target.val();
        addTag( tag, $tag_list);
        evt.stopPropagation();
        $tag_input.val("").focus();
        updateLocalList( tag );
      }
    })
    .parents('form').on('submit', function() {
      var tag = $tag_input.val();
      if( tag.length > 0 ) {
        addTag( tag, $tag_list);
        $tag_input.val("").focus();
        updateLocalList( tag );
      }
      return false;
    });
  });

}).call(this, jQuery, window);
