document.addEventListener('DOMContentLoaded', () => {
  const badge = document.getElementById('host-status-badge');
  const statusBox = document.getElementById('status-box');
  const statusIcon = document.getElementById('status-icon');
  const statusTitle = document.getElementById('status-title');
  const statusDesc = document.getElementById('status-desc');
  const btnRecheck = document.getElementById('btn-recheck');

  function checkNativeHost() {
    badge.className = 'badge';
    badge.textContent = 'Checking...';
    statusIcon.textContent = '🔄';
    statusTitle.textContent = 'Testing Native Host...';
    statusDesc.textContent = 'Attempting connection to Python host.';
    statusBox.className = 'status-box';

    chrome.runtime.sendNativeMessage('com.vlc.open', { ping: true }, (response) => {
      if (chrome.runtime.lastError || !response || response.status !== 'ok') {
        const errDesc = chrome.runtime.lastError ? chrome.runtime.lastError.message : 'No response from host.';
        badge.className = 'badge error';
        badge.textContent = 'Not Found';
        statusIcon.textContent = '⚠️';
        statusTitle.textContent = 'Native Host Not Found';
        statusDesc.textContent = errDesc;
        statusBox.className = 'status-box disconnected';
      } else {
        badge.className = 'badge success';
        badge.textContent = 'Connected';
        statusIcon.textContent = '✅';
        statusTitle.textContent = 'Native Host Connected';
        statusDesc.textContent = 'Backend is registered and active on this PC.';
        statusBox.className = 'status-box connected';
      }
    });
  }

  if (btnRecheck) {
    btnRecheck.addEventListener('click', checkNativeHost);
  }
  checkNativeHost();
});
