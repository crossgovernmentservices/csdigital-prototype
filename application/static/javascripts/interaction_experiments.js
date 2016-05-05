(function($, window) {
  
  $(function() {
      var availableTags = [
        "Delivering Value for Money",
        "Seeing the Big Picture",
        "Changing and Improving", 
        "Making Effective Decisions",
        "Leading and Communicating",
        "Collaborating and Partnering",
        "Building Capability for All",
        "Achieving Commercial Outcomes",
        "Managing a Quality Service", 
        "Delivering at Pace",
        "Development",
        "Email",
        "Feedback"
      ];
      var availableTags_lower = [];
      availableTags.forEach( function(element, index, array){
        availableTags_lower.push(element.toLowerCase());
      } );
      $( "#tagging" ).autocomplete({
        source: availableTags
      }).on('keydown', function(evt) {
        // add a tag on return
        if(evt.keyCode == 13) {
          var $target = $(evt.currentTarget);
          console.log( $target.parents('form') );
          appendTag( $target.val(), $target.parents('form') );
          $target.val('')
          return false;
        }
      });

      // flaky flaky flaky
      $(".example-text").on('keydown', function(evt) {
        var $target = $( evt.currentTarget );
        // split on space
        if (evt.keyCode == 32 || evt.keyCode == 13) {
          var hashtags = $target.val().split(/\s+/).filter(function(token) {
            return token.charAt(0) === "#" && token.length > 1;
          })
          if (hashtags.length !== 0) {
            addTags( hashtags, $target.parent('form') );
          }
        }
      });

    var appendTag = function( tag, $parent ) {
      var $tag = $("<span>").text( tag ).addClass("note-tag");
      $parent.append( $tag );
    };

    var addTags = function( hashtags, $el ) {
      var currentTags = $el.data('tags') || [];
      // won't work if hashtags are removed
      // should compare arrays?
      hashtags.forEach(function(item, index, array) {
        console.log(item);
        if(currentTags.length > 0 && $.inArray( item.substring(1), currentTags ) >= 0 ) {
          console.log( "already exists" );
        } else {
          currentTags.push( item.substring(1) );
          var $tag = $("<span>").text( item.substring(1) ).addClass("note-tag");
          $el.append( $tag );
        }
      });
      $el.data('tags', currentTags);
    };
  });
  
  $(function(){
    $('select').selectToAutocomplete({
      "remove-valueless-options": false
    });
    $('form').submit(function(){
      console.log( $(this).find(".ui-autocomplete-input").val() );
      alert( $(this).serialize() );
      return false;
    });
  });

}).call(this, jQuery, window);