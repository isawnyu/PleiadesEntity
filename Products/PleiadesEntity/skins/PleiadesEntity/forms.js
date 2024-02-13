
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
  $('#archetypes-fieldname-referenceCitations').on(
    'keyup',
    '.short-title-wrapper input',
    function (ev) {
      var currentValue = ev.target.value;
      // Since autocomplete added its structure we need to climb up the DOM twice
      $button = $(ev.target).parent().parent().next();
      if (currentValue == "") {
        $button.css("opacity", "0.5");
      } else {
        $button.css("opacity", "1");
        // If the key pressed was enter press the button
        if (ev.keyCode == 13) {
          $button.click();
          ev.preventDefault();
          return false;
        }
      }
  });

  const setIcon = (button, icon) => {
    button.text(button.text().trim().replace(/^[^ ]* /, icon + ' '));
  }

  $('#archetypes-fieldname-referenceCitations').on(
    'click',
    '.short-title-wrapper .copy-zotero-uri',
    function (ev) {
      ev.preventDefault();
      if (ev.view && ev.view.$button && ev.view.$button[0] !== this) {
        // When this is triggered by the user hitting enter, the event is triggered twice
        // once by the browser and once by our code above (search for keyCode == 13).
        // This condition prevents the code from running twice.
        return;
      }
      $this = $(this);
      var $inputField = $this.parent("div.short-title-wrapper").find("input");
      var $resultDiv = $this.parent("div.short-title-wrapper").find(".zotero-api-result");
      var $bibliographicURIField = $this.closest("fieldset").find('input[id$="bibliographic_uri"]');
      var currentValue = $inputField.val();
      if (currentValue && ! $this.attr("data-fetching")) {
        var url = 'https://api.zotero.org/groups/2533/items/top?limit=10&itemType=-attachment&q=' + encodeURIComponent(currentValue);
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
    }
  );
  function markError($link) {
    $link.css("color", "red").attr("data-invalid", "true");
    var body = $link.html();
    $link.html(body.replace(/⏳/g, "⚠️"));
  }
  $('#archetypes-fieldname-referenceCitations').on(
    "click",
    "a.zotero-choice",
    function (ev) {
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
    }
  );

  // Autocomplete for Short Title
  var default_works = [];
  if (typeof(window.pleiades_default_works) !== 'undefined') {
      default_works = Object.keys(pleiades_default_works);
  } else {
    console.error("pleiades_default_works is not defined")
  }
  // We hook to the `focusin` event to instantiate the autocomplete widget.
  // We don't do it on page load because fields can be created dynamically.
  $("#archetypes-fieldname-referenceCitations").on('focusin', '.short-title-wrapper input', function() {
    // The user just clicked on a field reuireing autocomplete. Let's get to work!
    var $this = $(this);

    if (!$this.data('ui-autocomplete-initialized')) {
        var $bibliographicURIField = $this.closest("fieldset").find('input[id$="bibliographic_uri"]');

        $this.autocomplete({
            source: [default_works],
            afterSelected: function () {
                $bibliographicURIField.val(pleiades_default_works[$this.val()]);
            }
        });
        // Great! We're done. But oh, no! The user clicked on the field to put focus there
        // but the $this.autocomplete invocation above has stolen the focus away from the field.
        // First let's make sure we're not triggering an endless loop!
        $this.data('ui-autocomplete-initialized', true);
        // Now let's give the focus back to the field.
        $this.focus();
    }
  });
});
