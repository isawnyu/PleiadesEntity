
jQuery(function () {
  var p_url = portal_url[portal_url.length - 1] != '/' ? portal_url : portal_url.substring(0, portal_url.length - 1)
  var fetch_url = p_url + '/@@fetch-bibliographic-data';

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
  $('.short-title-wrapper input').live('keyup', function (ev) {
    var $this = $(this);
    var currentValue = $this.val();
    $button = $this.parent().next();
    if (currentValue == "") {
      $button.css("opacity", "0.5");
    } else {
      $button.css("opacity", "1");
    }
  });

  const setIcon = (button, icon) => {
    button.text(button.text().trim().replace(/^[^ ]* /, icon + ' '));
  }

  $('.short-title-wrapper .copy-zotero-uri').live('click', function (ev) {
    ev.preventDefault();
    $this = $(this);
    var $inputField = $this.parent("div.short-title-wrapper").find("input");
    var $resultDiv = $this.parent("div.short-title-wrapper").find(".zotero-api-result");
    var $bibliographicURIField = $this.closest("fieldset").find('input[id$="bibliographic_uri"]');
    var currentValue = $inputField.val();
    if (currentValue && ! $this.attr("data-fetching")) {
      var url = 'https://api.zotero.org/groups/2533/items?limit=10&itemType=-attachment&q=' + encodeURIComponent(currentValue);
      // Send a request to the backend using the fetch api, and log the result to the console
      setIcon($this, "⏳");
      $this.css("opacity", "0.5");
      $this.attr("data-fetching", "true");
      $resultDiv.text("");
      fetch(url).then(function(response) {
        return response.json();
      }).then(function(data) {
        $this.attr("data-fetching", "")
        $this.css("opacity", "1");
        setIcon($this, "🔽");
        if (data.length == 1) {
          $inputField.val(data[0].data.shortTitle);
          $bibliographicURIField.val(data[0].links.alternate.href);
          $resultDiv.css("background-color", "white");
        } else if (data.length == 0) {
          $resultDiv.text("No results found searching for " + currentValue);
          $resultDiv.css("background-color", "lightpink");
        } else {
          $resultDiv.html("Results found for <i>" + currentValue + "</i>:");
          $resultDiv.css("background-color", "lightgrey");
          // Loop over data
          data.forEach(function(item) {
            var item_url = 'https://www.zotero.org/groups/pleiades/items/' + item.key;
            var link_text = '<a data-short-title="' + item.data.shortTitle + '" class="zotero-choice zotero-item-' + item.key;
            link_text += '" href="' + item_url + '">⏳'+ (item.data.shortTitle || item.data.title) + '</a>'
            $resultDiv[0].innerHTML += '<br />' + link_text;
            $.getJSON(
              fetch_url,
              { "url": item_url },
              function (data) {
                if (data.error) { $(".zotero-item-" + item.key).css("color", "red").attr("data-invalid", "true"); return }
                $(".zotero-item-" + item.key).html(data.formatted_citation);
              }).fail(function () {
                markError($(".zotero-item-" + item.key))
            });
        });
      }
    }).catch(function(err) {
        console.log('Fetch Error :-S', err);
      });
    }
    return false;
  });
  function markError($link) {
    $link.css("color", "red").attr("data-invalid", "true");
    var body = $link.html();
    $link.html(body.replace(/⏳/g, "⚠️"));
  }
  $("a.zotero-choice").live("click", function (ev) {
    ev.preventDefault();
    var $this = $(this);
    if ($this.attr("data-invalid")) { return false; }
    var $bibliographicURIField = $this.closest("fieldset").find('input[id$="bibliographic_uri"]');
    $bibliographicURIField.val($this.attr("href"));
    var $formattedCitationField = $this.closest("fieldset").find('input[id$="formatted_citation"]');
    $formattedCitationField.val($this.html());
    var $shortTitleField = $this.closest("div.short-title-wrapper").find("input");
    $shortTitleField.val($this.attr("data-short-title"));
    return false;
  });
  const default_works = pleiades_default_works.map(function(el) {return el.short_title})
  //$('.short-title-wrapper input').autocomplete({source: [default_works]});
});
