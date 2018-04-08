var LAI = LAI || {};

LAI.Tabs = (function () {
  var tabs = document.querySelectorAll('[data-tab]');
  var totalTabs = tabs.length;
  var tabPanels = document.querySelectorAll('.tab-panels > div');
  var totalPanels = tabPanels.length;

  function bindControls() {
    for (var i = 0; i < totalTabs; i++) {
      tabs[i].addEventListener('click', function (e) {
        e.preventDefault();
        deactivateAllTabs()
        hideAllPanels();
        activateTab(this);
        showPanel(this.hash);
      })
    }
  }

  function deactivateAllTabs() {
    for (var i = 0; i < totalTabs; i++) {
    tabs[i].classList.remove('dark-blue', 'bg-white');
    tabs[i].classList.add('bg-dark-blue', 'white');
    }
  }

  function activateTab(tab) {
    tab.classList.add('bg-white', 'dark-blue');
    tab.classList.remove('bg-dark-blue', 'white');
  }

  function hideAllPanels() {
    for (var i = 0; i < totalPanels; i++) {
      tabPanels[i].classList.add('dn');
    }
  }

  function showPanel(id) {
    document.querySelector(id).classList.remove('dn');
  }

  function init() {
    bindControls();
  }

  return {
    init: init,
  }
}());

LAI.Tabs.init();
