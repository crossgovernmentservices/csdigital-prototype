$(function () {
  $('.incremental-search').each(enableIncrementalSearch);

  function enableIncrementalSearch() {
    var searchUrl = $(this).data('search-url');
    var submitUrl = $(this).data('submit-url');
    var onSubmit = $(this).data('on-submit');
    var submitMethod = $(this).data('submit-method') || 'POST';
    var linkForm = $(this).data('link-form') || null;

    var form;
    var submitButton;
    if (linkForm) {
      form = $('form[data-linking-type="' + linkForm + '"]');
      form.empty();
      submitButton = $('<button>' + $(this).text() + '</button>');
      form.append(submitButton);
    } else {
      form = $('<form action="' + submitUrl + '" method="' + submitMethod + '"/>').insertBefore(this);
      submitButton = $(this);
    }

    var field = $('<input type="hidden" id="id" name="id">');
    form.append(field);
    var resultList = $('<ol class="incremental-search-results"/>');
    form.prepend(resultList);
    var searchBox = $('<input class="incremental-search-box form-control"/>');
    form.prepend(searchBox);

    var delayTimer = null;
    var delay = 200;

    function submit(name, value) {
      field.val(value);
      searchBox.val(name);
      resultList.empty();
    }

    searchBox.on('keypress', function (event) {

      if (delayTimer) {
        clearTimeout(delayTimer);
      }

      delayTimer = setTimeout(function () {
        var term = event.target.value;
        search(searchUrl, term, showResults(resultList, option(highlight(term), submit)));
      }, delay);
    });

    submitButton.on('click', function (event) {
      event.preventDefault();
      event.stopPropagation();
      if (field.val()) {
        form.submit();
      }
      return false;
    });

    if (typeof window[onSubmit] === 'function') {
      form.on('submit', window[onSubmit]);
    }
  }

  function search(url, term, callback) {
    $.getJSON(url, {"q": term}, callback);
  }

  function showResults(resultList, widget) {
    return function (data) {

      resultList.empty();

      for (var i in data.results) {
        resultList.append(widget(data.results[i]));
      }

    };
  }

  function option(format, submit) {
    return function (result) {
      var widget = $('<li>' + format(result.name) + '</li>');
      widget.on('click', function () { submit(result.name, result.value); });
      return widget;
    };
  }

  function highlight(term) {
    return function (s) {
      return s.replace(new RegExp(term, 'i'), '<b>$&</b>');
    };
  }

});
