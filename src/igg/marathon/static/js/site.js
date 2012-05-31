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

/* http://www.mredkj.com/javascript/nfbasic.html */
function addCommas(nStr) {
  nStr += '';
  x = nStr.split('.');
  x1 = x[0];
  x2 = x.length > 1 ? '.' + x[1] : '';
  var rgx = /(\d+)(\d{3})/;
  while (rgx.test(x1)) {
    x1 = x1.replace(rgx, '$1' + ',' + '$2');
  }
  return x1 + x2;
}

/* http://stackoverflow.com/a/9695058 */
function removeAllButLast(string, token) {
    var parts = string.split(token),
        front = parts.slice(0,-1).join(''),
        back  = parts.slice(-1).join('')
    if (front.length == 0) {
      front = "0"
    }
    if (back.length > 2) {
      back = back.slice(0,2)
    }
    while (back.length < 2) {
      back += "0"
    }
    return front + token + back
}
