var selectizeInit = function(data) {
    var items = data.map(function(x) { return { item: x }; });
    $('.input-tags').selectize({
      delimiter: ',',
      openOnFocus: false,
      closeAfterSelect: true,
      labelField: "item",
      valueField: "item",
      sortField: "item",
      searchField: "item",
      options: items,
      create: true,
      onChange: function(value) {
        console.log('onChange', value);
      },
      onItemAdd: function(value, $item) {
        currentInput = $item.parent().parent().prev();
        addTagToEntry(value, currentInput.data().entryId);
      }
  });
};

var addTagToEntry = function(tag, entryId) {
   $.ajax({
    url: '/my-log/entry/'+entryId+'/tags',
    type: 'POST',
    async: false,
    contentType: 'application/json',
    data:  JSON.stringify({"tag": tag}),
    success: function(data) {
      console.log('all done');
    }
  });
}

var tagsInit = function() {
  $.ajax({
    url: '/my-log/tags.json',
    type: 'GET',
    success: function(data) {
      var tags = [];
      $.each(data.tags, function(i, tag) {
        tags.push(tag.name);
      });
      selectizeInit(tags);
    }
  });
};

var watchInputs = function(event) {
  console.log('watchInputs');
};

$(document).ready(function() {
  tagsInit();
});
