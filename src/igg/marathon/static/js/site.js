$("a[data-toggle=modal]").click(function (e) {
  $("#gameDetailModalHeading").text($(this).attr('title'));
  $("#gameDetailModalBody").load($(this).attr('href'));
  $('#gameDetailModal').modal('show');
  e.preventDefault();
  e.stopPropagation();
})
