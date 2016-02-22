$(function () {
  $('.incremental-search').each(enableIncrementalSearch);

  function enableIncrementalSearch() {
    var searchUrl = $(this).data('search-url');
    var submitUrl = $(this).data('submit-url');
    var submitMethod = $(this).data('submit-method') || 'POST';
    var field = $('<input type="hidden" id="id" name="id">');
    var form = $(
      '<form action="' + submitUrl + '" method="' + submitMethod + '"/>').insertBefore(this);
    form.append(field);
    var searchBox = $('<input class="incremental-search-box"/>').insertBefore(this);
    var resultList = $('<ol class="incremental-search-results"/>').insertBefore(this);
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

    $(this).on('click', function (event) {
      event.preventDefault();
      event.stopPropagation();
      if (field.val()) {
        form.submit();
      }
      return false;
    });
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
