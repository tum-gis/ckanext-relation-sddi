/* Behaviour of the "Connected Entries" relationship editor.
 *
 * Without JavaScript the editor still works: the search forms are submitted
 * as normal GET requests and the results are rendered on the server.
 */
(function () {
  'use strict';

  var SEARCH_DELAY = 250;
  var MIN_CHARS = 2;

  function each(list, fn) {
    Array.prototype.forEach.call(list, fn);
  }

  function init(root) {
    var searchUrl = root.getAttribute('data-search-url');
    var i18n = {};
    try {
      i18n = JSON.parse(root.getAttribute('data-i18n') || '{}');
    } catch (e) { /* keep defaults */ }

    // --- Sections: collapse / expand ----------------------------------------

    function setExpanded(section, expanded) {
      var toggle = section.querySelector('[data-rel-toggle]');
      var body = section.querySelector('.rel-section-body');
      body.hidden = !expanded;
      toggle.setAttribute('aria-expanded', expanded ? 'true' : 'false');
      section.classList.toggle('is-collapsed', !expanded);
    }

    // --- Add panel -----------------------------------------------------------

    function openPanel(section) {
      setExpanded(section, true);
      section.querySelector('[data-rel-add]').hidden = true;
      section.querySelector('[data-rel-panel]').hidden = false;
      section.querySelector('[data-rel-search]').focus();
    }

    function closePanel(section) {
      var input = section.querySelector('[data-rel-search]');
      section.querySelector('[data-rel-panel]').hidden = true;
      section.querySelector('[data-rel-results]').innerHTML = '';
      input.value = '';
      var addBtn = section.querySelector('[data-rel-add]');
      addBtn.hidden = false;
      addBtn.focus();
    }

    function message(list, text) {
      list.innerHTML = '';
      var li = document.createElement('li');
      li.className = 'rel-results-msg';
      li.textContent = text;
      list.appendChild(li);
    }

    function resultItem(result, relType) {
      var li = document.createElement('li');
      li.className = 'rel-result';

      var dot = document.createElement('span');
      dot.className = 'rel-dot rel-marker-' + result.marker;
      dot.setAttribute('aria-hidden', 'true');
      li.appendChild(dot);

      var text = document.createElement('span');
      text.className = 'rel-result-text';
      var title = document.createElement('a');
      title.className = 'rel-result-title';
      title.href = result.url;
      title.target = '_blank';
      title.textContent = result.title;
      text.appendChild(title);
      if (result.organization) {
        var org = document.createElement('span');
        org.className = 'rel-result-org';
        org.textContent = result.organization;
        text.appendChild(org);
      }
      li.appendChild(text);

      var add = document.createElement('button');
      add.type = 'submit';
      add.className = 'rel-btn rel-btn-sm rel-btn-add';
      add.setAttribute('form', 'rel-action-form');
      add.name = 'relation_add.' + relType + '.' + result.id;
      add.value = '1';
      add.textContent = '+ ' + (i18n.add || 'Add');
      li.appendChild(add);

      return li;
    }

    function setupSearch(section) {
      var relType = section.getAttribute('data-rel-type');
      var form = section.querySelector('[data-rel-search-form]');
      var input = section.querySelector('[data-rel-search]');
      var list = section.querySelector('[data-rel-results]');
      var timer = null;
      var requestId = 0;

      function search() {
        var q = input.value.trim();
        var current = ++requestId;

        if (q.length < MIN_CHARS) {
          if (q.length) {
            message(list, i18n.minChars || 'Type at least 2 characters to search.');
          } else {
            list.innerHTML = '';
          }
          return;
        }

        message(list, i18n.searching || 'Searching…');
        var url = searchUrl + '?type=' + encodeURIComponent(relType) + '&q=' + encodeURIComponent(q);

        fetch(url, { credentials: 'same-origin', headers: { 'Accept': 'application/json' } })
          .then(function (response) {
            if (!response.ok) { throw new Error(response.status); }
            return response.json();
          })
          .then(function (data) {
            if (current !== requestId) { return; } // a newer search is running
            list.innerHTML = '';
            if (!data.results.length) {
              message(list, i18n.noResults || 'No matching entries found.');
              return;
            }
            data.results.forEach(function (result) {
              list.appendChild(resultItem(result, relType));
            });
          })
          .catch(function () {
            if (current === requestId) {
              message(list, i18n.error || 'The search failed. Please try again.');
            }
          });
      }

      input.addEventListener('input', function () {
        clearTimeout(timer);
        timer = setTimeout(search, SEARCH_DELAY);
      });

      input.addEventListener('keydown', function (event) {
        if (event.key === 'Escape') {
          event.preventDefault();
          closePanel(section);
        }
      });

      form.addEventListener('submit', function (event) {
        event.preventDefault();
        clearTimeout(timer);
        search();
      });
    }

    each(root.querySelectorAll('.rel-section'), function (section) {
      section.querySelector('[data-rel-toggle]').addEventListener('click', function () {
        setExpanded(section, section.classList.contains('is-collapsed'));
      });
      section.querySelector('[data-rel-add]').addEventListener('click', function () {
        openPanel(section);
      });
      section.querySelector('[data-rel-cancel]').addEventListener('click', function () {
        closePanel(section);
      });
      setupSearch(section);
    });

    // --- Confirmation before removing a connection ---------------------------

    each(root.querySelectorAll('[data-rel-confirm]'), function (button) {
      button.addEventListener('click', function (event) {
        if (!window.confirm(button.getAttribute('data-rel-confirm'))) {
          event.preventDefault();
        }
      });
    });

    // --- "Add connection" dropdown --------------------------------------------

    var menuToggle = root.querySelector('[data-rel-menu-toggle]');
    var menu = root.querySelector('#rel-add-menu');

    function setMenu(open) {
      menu.hidden = !open;
      menuToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      if (open) {
        menu.querySelector('[role="menuitem"]').focus();
      }
    }

    menuToggle.addEventListener('click', function () {
      setMenu(menu.hidden);
    });

    document.addEventListener('click', function (event) {
      if (!menu.hidden && !menu.contains(event.target) && !menuToggle.contains(event.target)) {
        setMenu(false);
      }
    });

    menu.addEventListener('keydown', function (event) {
      var items = Array.prototype.slice.call(menu.querySelectorAll('[role="menuitem"]'));
      var index = items.indexOf(document.activeElement);
      if (event.key === 'Escape') {
        setMenu(false);
        menuToggle.focus();
      } else if (event.key === 'ArrowDown') {
        event.preventDefault();
        items[(index + 1) % items.length].focus();
      } else if (event.key === 'ArrowUp') {
        event.preventDefault();
        items[(index - 1 + items.length) % items.length].focus();
      }
    });

    each(menu.querySelectorAll('[data-rel-open]'), function (item) {
      item.addEventListener('click', function () {
        var section = root.querySelector('.rel-section[data-rel-type="' + item.getAttribute('data-rel-open') + '"]');
        setMenu(false);
        openPanel(section);
        section.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
    });

    // --- Highlight the section we came back to after add / remove -------------

    if (window.location.hash.indexOf('#rel-section-') === 0) {
      var target = root.querySelector(window.location.hash);
      if (target) {
        target.classList.add('is-flash');
      }
    }
  }

  function start() {
    each(document.querySelectorAll('.rel-editor'), init);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();
