/**
* Template Name: NiceAdmin
* Template URL: https://bootstrapmade.com/nice-admin-bootstrap-admin-html-template/
* Updated: Apr 20 2024 with Bootstrap v5.3.3
* Author: BootstrapMade.com
* License: https://bootstrapmade.com/license/
*/

(function() {
  "use strict";

  /**
   * Easy selector helper function
   */
  const select = (el, all = false) => {
    el = el.trim()
    if (all) {
      return [...document.querySelectorAll(el)]
    } else {
      return document.querySelector(el)
    }
  }

  /**
   * Easy event listener function
   */
  const on = (type, el, listener, all = false) => {
    if (all) {
      select(el, all).forEach(e => e.addEventListener(type, listener))
    } else {
      select(el, all).addEventListener(type, listener)
    }
  }

  /**
   * Easy on scroll event listener 
   */
  const onscroll = (el, listener) => {
    el.addEventListener('scroll', listener)
  }

  if (window.jQuery) {
    window.jQuery.ajaxSetup({
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
  }

  /**
   * App shell interactions
   */
  const body = select('body')
  const sidebarToggle = select('.toggle-sidebar-btn')
  const sidebarBackdrop = select('.sidebar-backdrop')
  const searchBar = select('.search-bar')
  const appLoader = select('#app-loader')
  const mobileSidebarQuery = window.matchMedia('(max-width: 1199px)')
  const sidebarStateKey = 'cm.sidebar.state'
  const pageLinks = [
    { label: 'Dashboard', path: '/QR/Dashboard', keywords: 'home stock command center analytics' },
    { label: 'Cylinder Inward', path: '/QR/Cylinder-Inward-Form', keywords: 'inward scan receive cylinder stock in' },
    { label: 'Cylinder Outward', path: '/QR/Cylinder-Outward-Form', keywords: 'outward issue return cylinder stock out' },
    { label: 'Vendors', path: '/QR/Vendors', keywords: 'vendor master supplier directory' },
    { label: 'Inward / Outward Report', path: '/QR/Cylinder-Inward-Outward-History', keywords: 'report history movement ledger analytics' }
  ]

  const isSidebarOpen = () => {
    if (!body) return false
    return mobileSidebarQuery.matches
      ? body.classList.contains('toggle-sidebar')
      : !body.classList.contains('toggle-sidebar')
  }

  const syncSidebarToggleIcon = () => {
    if (!sidebarToggle) return
    const isOpen = isSidebarOpen()
    body.classList.toggle('sidebar-open', isOpen)
    body.classList.toggle('sidebar-closed', !isOpen)
    body.classList.toggle('sidebar-scroll-locked', isOpen && mobileSidebarQuery.matches)
    sidebarToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false')
    const icon = sidebarToggle.querySelector('i')
    if (icon) {
      icon.className = isOpen ? 'bi bi-chevron-left' : 'bi bi-chevron-right'
    }
  }

  const setSidebarState = (isOpen) => {
    if (!body) return
    body.classList.toggle('toggle-sidebar', mobileSidebarQuery.matches ? isOpen : !isOpen)
    syncSidebarToggleIcon()
  }

  const persistSidebarState = (isOpen) => {
    try {
      window.sessionStorage.setItem(sidebarStateKey, isOpen ? 'open' : 'closed')
    } catch (error) {
      console.warn('Unable to persist sidebar state.', error)
    }
  }

  const getStoredSidebarState = () => {
    try {
      return window.sessionStorage.getItem(sidebarStateKey)
    } catch (error) {
      return null
    }
  }

  const applyStoredSidebarState = () => {
    const storedState = getStoredSidebarState()
    const shouldOpen = storedState ? storedState === 'open' : !mobileSidebarQuery.matches
    setSidebarState(shouldOpen)
  }

  const closeSidebar = (persist = true) => {
    setSidebarState(false)
    if (persist) persistSidebarState(false)
  }

  if (sidebarToggle) {
    sidebarToggle.addEventListener('click', function(e) {
      e.preventDefault()
      const nextState = !isSidebarOpen()
      setSidebarState(nextState)
      persistSidebarState(nextState)
    })
  }

  applyStoredSidebarState()
  mobileSidebarQuery.addEventListener('change', () => {
    body.classList.remove('sidebar-open')
    body.classList.remove('sidebar-closed')
    body.classList.remove('sidebar-scroll-locked')
    applyStoredSidebarState()
  })

  select('[data-sidebar-close]', true).forEach(closeControl => {
    closeControl.addEventListener('click', closeSidebar)
  })

  select('#sidebar .nav-link', true).forEach(navLink => {
    navLink.addEventListener('click', () => {
      if (window.matchMedia('(max-width: 1199px)').matches) {
        closeSidebar(false)
      }
    })
  })

  if (sidebarBackdrop) {
    sidebarBackdrop.addEventListener('click', closeSidebar)
  }

  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') {
      closeSidebar()
      if (searchBar) searchBar.classList.remove('search-bar-show')
    }
  })

  /**
   * Search bar toggle
   */
  if (select('.search-bar-toggle')) {
    on('click', '.search-bar-toggle', function(e) {
      e.preventDefault()
      searchBar.classList.toggle('search-bar-show')
      const searchInput = searchBar.querySelector('input')
      if (searchBar.classList.contains('search-bar-show') && searchInput) {
        setTimeout(() => searchInput.focus(), 80)
      }
    })
  }

  if (searchBar) {
    const searchForm = searchBar.querySelector('[data-page-search-form]')
    const searchInput = searchBar.querySelector('[data-page-search-input]')
    const searchResults = searchBar.querySelector('[data-page-search-results]')
    const currentPageLabel = searchBar.querySelector('[data-current-page-label]')
    const normalizePath = (value) => (value || '').replace(/\/$/, '')
    const currentPage = pageLinks.find(page => normalizePath(window.location.pathname) === normalizePath(page.path)) || pageLinks[0]
    const setSearchOpen = (isOpen) => {
      if (searchResults) searchResults.classList.toggle('search-results-show', isOpen)
    }
    const goToFirstSearchResult = () => {
      const firstResult = searchResults ? searchResults.querySelector('a.search-result-item') : null
      const href = firstResult ? firstResult.getAttribute('href') : null
      if (href) {
        window.location.href = href
      }
    }
    const renderSearchResults = (query = '') => {
      if (!searchResults) return
      const cleanQuery = query.trim().toLowerCase()
      const matches = cleanQuery
        ? pageLinks.filter(page => `${page.label} ${page.keywords}`.toLowerCase().includes(cleanQuery))
        : []
      searchResults.innerHTML = matches.length
        ? matches.map(page => {
          if (page.path === currentPage.path) {
            return `
              <div class="search-result-item current-page-result" aria-disabled="true">
                <i class="bi bi-dash-circle"></i>
                <span>${page.label}</span>
                <small>Current page</small>
              </div>
            `
          }

          return `
            <a href="${page.path}" class="search-result-item">
              <i class="bi bi-arrow-right-short"></i>
              <span>${page.label}</span>
            </a>
          `
        }).join('')
        : cleanQuery
          ? '<div class="search-result-empty">No matching pages</div>'
          : ''
      setSearchOpen(Boolean(cleanQuery))
    }

    if (searchInput) {
      searchInput.value = ''
      if (currentPageLabel) currentPageLabel.textContent = currentPage.label
      searchInput.addEventListener('focus', () => {
        renderSearchResults(searchInput.value)
      })
      searchInput.addEventListener('input', () => renderSearchResults(searchInput.value))
    }

    if (searchForm) {
      searchForm.addEventListener('submit', event => {
        event.preventDefault()
        goToFirstSearchResult()
      })

      const searchSubmitButton = searchForm.querySelector('button[type="submit"]')
      if (searchSubmitButton) {
        searchSubmitButton.addEventListener('click', event => {
          event.preventDefault()
          goToFirstSearchResult()
        })
      }
    }

    searchBar.addEventListener('click', event => event.stopPropagation())
    document.addEventListener('click', event => {
      if (
        searchBar.classList.contains('search-bar-show') &&
        !event.target.closest('.search-bar') &&
        !event.target.closest('.search-bar-toggle')
      ) {
        searchBar.classList.remove('search-bar-show')
        setSearchOpen(false)
      }
    })
  }

  /**
   * Page flash loader
   */
  const hideAppLoader = () => {
    if (!body || !appLoader) return
    body.classList.remove('app-loading')
    appLoader.classList.add('app-loader-hidden')
  }

  const showAppLoader = () => {
    if (!body || !appLoader) return
    body.classList.add('app-loading')
    appLoader.classList.remove('app-loader-hidden')
  }

  const hideLocalPreloaders = () => {
    select('#preloader', true).forEach(loader => {
      loader.style.display = 'none'
    })
  }

  document.addEventListener('show.bs.modal', event => {
    if (event.target && event.target.parentElement !== document.body) {
      document.body.appendChild(event.target)
    }
    if (mobileSidebarQuery.matches) {
      closeSidebar(false)
    }
    body.classList.remove('sidebar-scroll-locked')
    hideAppLoader()
    hideLocalPreloaders()
    if (appLoader) {
      appLoader.style.display = 'none'
    }
    if (searchBar) searchBar.classList.remove('search-bar-show')
  })

  document.addEventListener('hidden.bs.modal', () => {
    if (appLoader) {
      appLoader.style.display = ''
    }
  })

  const connectionStatus = select('[data-connection-status]')
  const connectionStatusText = select('[data-connection-status-text]')
  const setConnectionStatus = (state) => {
    if (!connectionStatus) return
    connectionStatus.classList.remove('connection-status-active', 'connection-status-slow', 'connection-status-inactive')
    connectionStatus.classList.add(`connection-status-${state}`)
    const labels = {
      active: 'Active',
      slow: 'Slow internet',
      inactive: 'Inactive'
    }
    connectionStatus.setAttribute('aria-label', `Server connection ${labels[state]}`)
    if (connectionStatusText) connectionStatusText.textContent = labels[state]
  }
  const checkConnectionStatus = async () => {
    if (!connectionStatus) return
    const startedAt = performance.now()
    const controller = new AbortController()
    const timeout = window.setTimeout(() => controller.abort(), 5000)
    try {
      const response = await fetch('/health/', {
        cache: 'no-store',
        credentials: 'same-origin',
        signal: controller.signal,
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
      const elapsed = performance.now() - startedAt
      setConnectionStatus(response.ok ? (elapsed > 1800 ? 'slow' : 'active') : 'inactive')
    } catch (error) {
      setConnectionStatus(error && error.name === 'AbortError' && navigator.onLine !== false ? 'slow' : 'inactive')
    } finally {
      window.clearTimeout(timeout)
    }
  }

  checkConnectionStatus()
  window.setInterval(checkConnectionStatus, 30000)
  window.addEventListener('online', checkConnectionStatus)
  window.addEventListener('offline', () => setConnectionStatus('inactive'))

  window.addEventListener('load', () => {
    setTimeout(hideAppLoader, 260)
  })

  select('a[href]', true).forEach(link => {
    link.addEventListener('click', event => {
      const href = link.getAttribute('href') || ''
      const target = link.getAttribute('target')
      if (!href || href.startsWith('#') || href.startsWith('javascript:') || target === '_blank' || event.defaultPrevented) {
        return
      }
      showAppLoader()
    })
  })

  select('form', true).forEach(form => {
    form.addEventListener('submit', () => {
      if (form.hasAttribute('data-ajax-form')) {
        return
      }
      if (form.checkValidity()) {
        showAppLoader()
      }
    })
  })

  /**
   * Navbar links active state on scroll
   */
  let navbarlinks = select('#navbar .scrollto', true)
  const navbarlinksActive = () => {
    let position = window.scrollY + 200
    navbarlinks.forEach(navbarlink => {
      if (!navbarlink.hash) return
      let section = select(navbarlink.hash)
      if (!section) return
      if (position >= section.offsetTop && position <= (section.offsetTop + section.offsetHeight)) {
        navbarlink.classList.add('active')
      } else {
        navbarlink.classList.remove('active')
      }
    })
  }
  window.addEventListener('load', navbarlinksActive)
  onscroll(document, navbarlinksActive)

  /**
   * Toggle .header-scrolled class to #header when page is scrolled
   */
  let selectHeader = select('#header')
  if (selectHeader) {
    const headerScrolled = () => {
      if (window.scrollY > 100) {
        selectHeader.classList.add('header-scrolled')
      } else {
        selectHeader.classList.remove('header-scrolled')
      }
    }
    window.addEventListener('load', headerScrolled)
    onscroll(document, headerScrolled)
  }

  /**
   * Back to top button
   */
  let backtotop = select('.back-to-top')
  if (backtotop) {
    const toggleBacktotop = () => {
      if (window.scrollY > 100) {
        backtotop.classList.add('active')
      } else {
        backtotop.classList.remove('active')
      }
    }
    window.addEventListener('load', toggleBacktotop)
    onscroll(document, toggleBacktotop)
  }

  /**
   * Initiate tooltips
   */
  var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
  var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl)
  })

  /**
   * Initiate quill editors
   */
  if (select('.quill-editor-default')) {
    new Quill('.quill-editor-default', {
      theme: 'snow'
    });
  }

  if (select('.quill-editor-bubble')) {
    new Quill('.quill-editor-bubble', {
      theme: 'bubble'
    });
  }

  if (select('.quill-editor-full')) {
    new Quill(".quill-editor-full", {
      modules: {
        toolbar: [
          [{
            font: []
          }, {
            size: []
          }],
          ["bold", "italic", "underline", "strike"],
          [{
              color: []
            },
            {
              background: []
            }
          ],
          [{
              script: "super"
            },
            {
              script: "sub"
            }
          ],
          [{
              list: "ordered"
            },
            {
              list: "bullet"
            },
            {
              indent: "-1"
            },
            {
              indent: "+1"
            }
          ],
          ["direction", {
            align: []
          }],
          ["link", "image", "video"],
          ["clean"]
        ]
      },
      theme: "snow"
    });
  }

  /**
   * Initiate TinyMCE Editor
   */

  const useDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const isSmallScreen = window.matchMedia('(max-width: 1023.5px)').matches;

  tinymce.init({
    selector: 'textarea.tinymce-editor',
    plugins: 'preview importcss searchreplace autolink autosave save directionality code visualblocks visualchars fullscreen image link media codesample table charmap pagebreak nonbreaking anchor insertdatetime advlist lists wordcount help charmap quickbars emoticons accordion',
    editimage_cors_hosts: ['picsum.photos'],
    menubar: 'file edit view insert format tools table help',
    toolbar: "undo redo | accordion accordionremove | blocks fontfamily fontsize | bold italic underline strikethrough | align numlist bullist | link image | table media | lineheight outdent indent| forecolor backcolor removeformat | charmap emoticons | code fullscreen preview | save print | pagebreak anchor codesample | ltr rtl",
    autosave_ask_before_unload: true,
    autosave_interval: '30s',
    autosave_prefix: '{path}{query}-{id}-',
    autosave_restore_when_empty: false,
    autosave_retention: '2m',
    image_advtab: true,
    link_list: [{
        title: 'My page 1',
        value: 'https://www.tiny.cloud'
      },
      {
        title: 'My page 2',
        value: 'http://www.moxiecode.com'
      }
    ],
    image_list: [{
        title: 'My page 1',
        value: 'https://www.tiny.cloud'
      },
      {
        title: 'My page 2',
        value: 'http://www.moxiecode.com'
      }
    ],
    image_class_list: [{
        title: 'None',
        value: ''
      },
      {
        title: 'Some class',
        value: 'class-name'
      }
    ],
    importcss_append: true,
    file_picker_callback: (callback, value, meta) => {
      /* Provide file and text for the link dialog */
      if (meta.filetype === 'file') {
        callback('https://www.google.com/logos/google.jpg', {
          text: 'My text'
        });
      }

      /* Provide image and alt text for the image dialog */
      if (meta.filetype === 'image') {
        callback('https://www.google.com/logos/google.jpg', {
          alt: 'My alt text'
        });
      }

      /* Provide alternative source and posted for the media dialog */
      if (meta.filetype === 'media') {
        callback('movie.mp4', {
          source2: 'alt.ogg',
          poster: 'https://www.google.com/logos/google.jpg'
        });
      }
    },
    height: 600,
    image_caption: true,
    quickbars_selection_toolbar: 'bold italic | quicklink h2 h3 blockquote quickimage quicktable',
    noneditable_class: 'mceNonEditable',
    toolbar_mode: 'sliding',
    contextmenu: 'link image table',
    skin: useDarkMode ? 'oxide-dark' : 'oxide',
    content_css: useDarkMode ? 'dark' : 'default',
    content_style: 'body { font-family:Helvetica,Arial,sans-serif; font-size:16px }'
  });

  /**
   * Initiate Bootstrap validation check
   */
  var needsValidation = document.querySelectorAll('.needs-validation')

  Array.prototype.slice.call(needsValidation)
    .forEach(function(form) {
      form.addEventListener('submit', function(event) {
        if (!form.checkValidity()) {
          event.preventDefault()
          event.stopPropagation()
          form.reportValidity()
        }

        form.classList.add('was-validated')
      }, false)
    })

  /**
   * Initiate Datatables
   */
  const datatables = select('.datatable', true)
  datatables.forEach(datatable => {
    new simpleDatatables.DataTable(datatable, {
      perPageSelect: [5, 10, 15, ["All", -1]],
      columns: [{
          select: 2,
          sortSequence: ["desc", "asc"]
        },
        {
          select: 3,
          sortSequence: ["desc"]
        },
        {
          select: 4,
          cellClass: "green",
          headerClass: "red"
        }
      ]
    });
  })

  /**
   * Autoresize echart charts
   */
  const mainContainer = select('#main');
  if (mainContainer) {
    setTimeout(() => {
      new ResizeObserver(function() {
        select('.echart', true).forEach(getEchart => {
          echarts.getInstanceByDom(getEchart).resize();
        })
      }).observe(mainContainer);
    }, 200);
  }

})();
