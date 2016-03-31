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

    $('.notes-list').on('click', '.note', function() {
      clearActive();
      $(this)
        .addClass("edit-mode")
        .find('textarea')
          .focus();
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

  function render_markdown(content) {
    return markdown.toHTML( content );
  }

  function createNote( content ) {
    var $note = $(".note:first-of-type").clone(),
        trunc_content = content.substring(0, 249) + "…";

    $note
      .find('.email-flag')
        .remove()
      .end()
      .find('.note-date')
        .text("now")
      .end()
      .find('.rendered-note')
        .empty()
        .append( render_markdown(trunc_content) )
      .end()
      .find('.note-form textarea')
        .val( content )
        .on('input focus', growTextarea)
      .end()
      .prependTo(".notes-list");
  }

}).call(this, jQuery, window);