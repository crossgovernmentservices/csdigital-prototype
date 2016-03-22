(function($, window) {

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
    }).on('input focus', function () {
      this.style.height = 'auto';
      this.style.height = (this.scrollHeight) + 'px';
    });

    $('.note').on('click', function() {
      clearActive();
      $(this)
        .addClass("edit-mode")
        .find('textarea')
          .focus();
    })
  });

  function clearActive() {
    $('.note').removeClass("edit-mode");
    $('.add-note-form').removeClass("active");
  }

}).call(this, jQuery, window);