
jQuery(function () {
  function enable_zotero() {
    var $bib_uri_inputs = $('#archetypes-fieldname-array-fieldset-referenceCitations input[id$="\\|bibliographic_uri"]');
    $bib_uri_inputs.each(function (i, el) {
      var count = ("000" + i).slice(-3);
      var $bib_uri_input = $(el);
      // Check for button presence
      if ($bib_uri_input.siblings('button.BibInfoFetchButton').length) {
        return;
      }
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
              var prefix = '\\:'+count+'\\|';
              var $title = $bib_uri_input.parents().find('input[id$="' + prefix + 'short_title"]');
              var $detail = $bib_uri_input.parents().find('input[id$="' + prefix + 'citation_detail"]');
              var $formatted = $bib_uri_input.parents().find('input[id$="' + prefix + 'formatted_citation"]');
              var $access_uri = $bib_uri_input.parents().find('input[id$="' + prefix + 'access_uri"]');
              var title = data.short_title || data.title;
              if (title) {
                $title.val(title);
              }
              if (data.citation_detail) {
                $detail.val(data.citation_detail);
              }
              if (data.formatted_citation) {
                $formatted.val(data.formatted_citation);
              }
              if (data.access_uri && ! $access_uri.val()) {
                $access_uri.val(data.access_uri);
              }
              if (data.bibliographic_uri) {
                $bib_uri_input.val(data.bibliographic_uri);
              }
            }
          ).error(function (resp) {
            try {
              var data = JSON.parse(resp.responseText);
              window.alert(data.error);
            } catch(err) {
              window.alert('Error code: ' + resp.status + ' while retrieving Zotero response');
            }
          });
        }
        return false;
      });
    });
  }
  enable_zotero();
  $('#archetypes-fieldname-referenceCitations').on(
      'click',
      'input.context[value="Add reference"]',
      enable_zotero
  );
  console.log($('.copy-zotero-uri').prev().find("input"));
  $('.copy-zotero-uri').prev().find("input").on('keyup', function (ev) {
    var $this = $(this);
    var currentValue = $this.val();
    $button = $this.parent().next();
    if (currentValue == "") {
      $button.css("opacity", "0.5");
    } else {
      $button.css("opacity", "1");
    }
  });

  $('.copy-zotero-uri').on('click', function (ev) {
    // The field we're interested in is the previous sibling of the button
    var $inputField = $(this).prev().find("input");
    var $bibliographicURIField = $('input[id$="bibliographic_uri"]')
    var currentValue = $inputField.val();
    if (currentValue) {
      var url = window.portal_url + '/query-bibliographic-data?q=' + encodeURIComponent(currentValue);
      // Send a request to the backend using the fetch api, and log the result to the console
      fetch(url).then(function(response) {
        return response.json();
      }).then(function(data) {
        if (data.length == 1) {
          $inputField.val(data[0].data.shortTitle);
          $bibliographicURIField.val(data[0].links.alternate.href);
        }
      }).catch(function(err) {
        console.log('Fetch Error :-S', err);
      });
    }
    return false;
  });
});
