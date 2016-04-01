(function($, window) {

  // textarea handler
  function growTextarea(e) {
    e.currentTarget.style.height = 'auto';
    e.currentTarget.style.height = (e.currentTarget.scrollHeight) + 'px';
  }

  $(function() {
    var $addnoteform = $('.add-note-form');

    $addnoteform.find('textarea').focus();

    $addnoteform.on('click', function() {
      clearActive();
      $(this).addClass('active');
    });

    $addnoteform.find('textarea').on('keydown', function() {
      $addnoteform.addClass('active');
    });

    // taken from 
    // http://stackoverflow.com/questions/454202/creating-a-textarea-with-auto-resize
    $('textarea').each(function () {
      this.setAttribute('style', 'height:' + (this.scrollHeight) + 'px;overflow-y:hidden;');
    }).on('input focus', growTextarea);

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
  });

  function clearActive() {
    $('.note').removeClass("edit-mode");
    $('.add-note-form').removeClass("active");
  }

  function render_markdown(content, trunc) {
    var trunc = trunc || 249,
        trunc_content = content.substring(0, trunc) + "…";
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

    $note
      .find('.email-flag')
        .remove()
      .end()
      .find('.note-date')
        .text("now")
      .end()
      .find('.rendered-note')
        .empty()
        .append( render_markdown(content) )
      .end()
      .find('.note-form textarea')
        .val( content )
        .on('input focus', growTextarea)
      .end()
      .prependTo(".notes-list");
  }

}).call(this, jQuery, window);