function displayGameModal(e,title,url)
{
    $("#gameDetailModalHeading").text(title);
    $("#gameDetailModalBody").load(url);
    $('#gameDetailModal').modal('show');
    e.preventDefault();
    e.stopPropagation();
}
function pad2(x)
{
    return (x < 10 ? '0' : '') + x;
}
$("a[data-toggle=modal]").click(function (e) {
    displayGameModal(e,$(this).attr('title'),$(this).attr('href'));
})
