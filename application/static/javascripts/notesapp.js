(function($, window) {
  var URL = window.URL || window.webkitURL;

  // the tags available to the autocomplete
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
    "Feedback",
    "Obj 1",
    "Corporate Obj"
  ];

  var aliases = [
    "DaP",
    "dap",
    "Deliver Pace",
    "Delivery at Pace",
    "delivery at pace",
    "pacey delivery"
  ];

  // textarea handler
  function growTextarea(e) {
    e.currentTarget.style.height = 'auto';
    e.currentTarget.style.height = (e.currentTarget.scrollHeight) + 'px';
  }

  $(function() {
    var takePic = document.querySelector("#take-picture");
    var $addnoteform = $('.add-note-form');
    var $tag_inputs = $(".tag-input");

    $addnoteform.find('textarea').focus();

    $addnoteform.on('click', function() {
      clearActive();
      $(this).addClass('active');
    });

    $addnoteform.find('textarea').on('keydown', function() {
      $addnoteform.addClass('active');
    });

    // add handlers to the note entry textarea
    // taken from 
    // http://stackoverflow.com/questions/454202/creating-a-textarea-with-auto-resize
    $('textarea').each(function () {
      this.setAttribute('style', 'height:' + (this.scrollHeight) + 'px;overflow-y:hidden;');
    })
    .on('input focus', growTextarea)
    .on('keydown', function(evt) {
      var $target = $( evt.currentTarget );
      // split on space
      if (evt.keyCode == 32 || evt.keyCode == 13) {
        var hashtags = $target.val().split(/\s+/).filter(function(token) {
          return token.charAt(0) === "#" && token.length > 1;
        })
        if (hashtags.length !== 0) {
          addTags( hashtags, $target.parents('.note').find('.tag-list ul') );
        }
      }
    });

    $('.notes-list')
      .on('click', '.note', function() {
        // TO FIX:
        // this will cause a problem if user clicks to different section
        // of the note they are already editing
        saveNote( $('.edit-mode') );

        clearActive();
        $(this)
          .addClass("edit-mode")
          .find('textarea')
            .data( "original_content", $(this).find('textarea').val() )
            .focus();
      })
      .on('click', '.note-form button', function() {
        saveNote( $(this).parents(".note") );
        return false;
      })
      .on('click', '.close-btn', function() {
        clearActive();
        return false;
      })
      .on('click', '.tag-input', function(evt) {
        // do something
        evt.stopPropagation();
      });

    // dismiss box event
    $('.dismiss').on('click', function() {
      $(this).parent('.message-box').hide();
    });

    // add note
    $addnoteform.on('click', "button", function(e) {
      var $textarea = $addnoteform.find('textarea');
      var note_content = $textarea.val();
      createNote( note_content );
      $textarea
        .val("")
        .focus();
      return false;
    });

    // adding tags to a note
    $tag_inputs
      .autocomplete({ source: availableTags })
      .on('keydown', addTagHandler);

    // for uploading an image
    if( takePic ) {
      // change event
      takePic.onchange = function(ev) {
        // reference to taken pic or chosen file
        var files = ev.target.files,
            file;
        if( files && files.length > 0 ) {
          file = files[0];
          var imgURL = URL.createObjectURL(file);
          createImgNote(imgURL);
        }
      };
    }
  });

  function addTagHandler(evt) {
    // add a tag on return
    if(evt.keyCode == 13) {
      var $target = $(evt.currentTarget);
      var $tagList = $target.parents('.note').find('.tag-list ul');
      var tagToAdd = $target.val();

      // smoke and mirrors
      // notice similar tags
      console.log($.inArray( tagToAdd, aliases));
      if( $.inArray( $target.val(), aliases) >= 0 ) {
        $target
          .parents(".note")
            .find(".tag_suggestions")
              .show(400)
              .find('button')
                .on('click', function(evt) {
                  var $button = $(evt.currentTarget);
                  if( $button.text() === "Yes" ) {
                    appendTag( "Delivering at Pace", $tagList );
                  } else {
                    appendTag( tagToAdd, $tagList );
                  }
                  $target.val('').focus();
                  $button.parents(".tag_suggestions").hide(400);
                  evt.stopPropagation();
                });
      } else {
        appendTag( tagToAdd, $tagList );
        $target.val('');
      }
      return false;
    }
  }

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
        var $tag = $("<li>").text( item.substring(1) ).addClass("note-tag");
        $el.append( $tag );
      }
    });
    $el.data('tags', currentTags);
  };

  function clearActive() {
    $('.note').removeClass("edit-mode");
    $('.add-note-form').removeClass("active");
  }

  function render_markdown(content, trunc) {
    var trunc = trunc || 249,
        trunc_content = (content.length > 249) ? content.substring(0, trunc) + "…" : content;
    return markdown.toHTML( trunc_content );
  }

  function saveNote( $note ) {
    var $textarea = $note.find('textarea');
    if ( $textarea.val() !== $textarea.data("original_content") ) {
      var content = $textarea.val();
      // only need to replace the visible rendered bit
      $note
        .find('.rendered-note')
          .empty()
          .append( render_markdown(content) )
        .end()
        .removeClass('edit-mode')
        .addClass('undo-mode');
      return true;
    } else {
      return false;
    }
  }

  function createNote( content ) {
    var $note = $(".note:first-of-type").clone();

    // do I need to add the handler each time?
    $note
      .find('.email-flag')
        .remove()
      .end()
      .find('.note-date')
        .text("now")
      .end()
      .find('.tag-list ul')
        .empty()
      .end()
      .find('.rendered-note')
        .empty()
        .append( render_markdown(content) )
      .end()
      .find('.note-form textarea')
        .val( content )
        .on('input focus', growTextarea)
      .end()
      .find('.tag-input')
        .autocomplete({ source: availableTags })
        .on('keydown', addTagHandler)
      .end()
      .prependTo(".notes-list");

  }

  var appendTag = function( tag, $parent ) {
    var $link = $("<a>").attr("href", "/notesapp/tag/" + tag).text( tag );
    var $tag = $("<li>").addClass("note-tag").append( $link );
    $parent.append( $tag );
  };

  function createImgNote( imgURL ) {
    var $note = $(".note:first-of-type").clone();

    var $img = $("<img />").attr("width", "100%").attr("src", imgURL).on('load', function() {
        URL.revokeObjectURL(imgURL);
    });

    $note
      .find('.email-flag')
        .remove()
      .end()
      .find('.note-date')
        .text("now")
      .end()
      .find('.rendered-note')
        .empty()
        .append( $img )
      .end()
      .prependTo(".notes-list");
  }

}).call(this, jQuery, window);