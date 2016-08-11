
jQuery(function () {
  var $bib_uri_inputs = $('#fieldset-references input[id$="\\|bibliographic_uri"]');
  $bib_uri_inputs.each(function (i, el) {
    var count = ("000" + i).slice(-3);
    var $bib_uri_input = $(el);
    var $lookup = $('<button class="BibInfoFetchButton" title="Fetch zotero data"><span>Fetch Zotero</span></button>');
    $bib_uri_input.after($lookup);
    $lookup.click(function (ev) {
      var uri = $bib_uri_input.val();
      ev.preventDefault();
      if (uri) {
        var p_url = portal_url[portal_url.length - 1] != '/' ? portal_url : portal_url.substring(0, portal_url.length - 1)
        var fetch_url = p_url + '/@@fetch-bibliographic-data';
        $.getJSON(
          fetch_url,
          {"url": uri},
          function (data) {
            if (data.error) {
              alert(data.error);
              return;
            }
            var prefix = '\\:'+count+'\\|'
            var $title = $bib_uri_input.parents().find('input[id$="' + prefix + 'short_title"]');
            var $detail = $bib_uri_input.parents().find('input[id$="' + prefix + 'citation_detail"]');
            var $formatted = $bib_uri_input.parents().find('input[id$="' + prefix + 'formatted_citation"]');
            var $access_uri = $bib_uri_input.parents().find('input[id$="' + prefix + 'access_uri"]');
            if (!$title.val()) {
              $title.val(data.title);
            }
            if (!$detail.val()) {
              $detail.val(data.citation_detail);
            }
            if (!$formatted.val()) {
              $formatted.val(data.formatted_citation);
            }
            if (!$access_uri.val()) {
              $access_uri.val(data.access_uri);
            }
          }
        ).error(function (resp) {var data = JSON.parse(resp.responseText); alert(data.error);});
      }
      return false;
    });
  });
});
