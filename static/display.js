const $ = id => document.getElementById(id);
let rfb = null, busy = false;
const token = localStorage.getItem('deckToken') || sessionStorage.getItem('deckToken');
const say = text => { $('status').textContent = text; };
async function api(path, body) {
  const response = await fetch(path, {method: body ? 'POST' : 'GET', headers: {'X-Deck-Token': token || '', 'Content-Type':'application/json'}, body: body ? JSON.stringify(body) : undefined});
  const data = await response.json();
  if (!response.ok) throw Error(data.error || 'Request failed');
  return data;
}
function disconnect() { if (rfb) { const old = rfb; rfb = null; old.disconnect(); } }
async function connect(data) {
  disconnect();
  const {default: RFB} = await import('/vendor/novnc/core/rfb.js');
  const url = new URL(location.href);
  url.protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
  url.port = String(data.port); url.pathname = '/'; url.search = ''; url.hash = '';
  const client = new RFB($('screen'), url.href, {credentials: {password:data.password}});
  rfb = client;
  client.scaleViewport = true; client.resizeSession = false;
  client.viewOnly = !$('control').checked;
  client.addEventListener('credentialsrequired', () => client.sendCredentials({password:data.password}));
  client.addEventListener('connect', () => { if (rfb === client) say('Connected · ' + data.resolution + '. Arrange Side-Panel in KDE Display Configuration.'); });
  client.addEventListener('disconnect', () => { if (rfb === client) { rfb = null; say('Display connection ended. Tap Start / reconnect. The virtual monitor may still be running.'); } });
  client.addEventListener('securityfailure', () => { if (rfb === client) say('Display authentication failed. Stop the display, then start again.'); });
}
async function operation(fn) {
  if (busy) return;
  busy = true; $('start').disabled = $('stop').disabled = true;
  try { await fn(); } catch (err) { say(err.message + ' See DISPLAY.md for setup and troubleshooting.'); }
  finally { busy = false; $('start').disabled = $('stop').disabled = false; }
}
$('start').onclick = () => operation(async () => {
  if (!token) throw Error('Return to Deck and pair first');
  // Check the browser client before creating a monitor, so a missing install leaves no stray display.
  await import('/vendor/novnc/core/rfb.js');
  say('Starting virtual monitor…');
  const data = await api('/api/display/start', {resolution:$('resolution').value});
  await connect(data);
});
$('stop').onclick = () => operation(async () => {
  await api('/api/display/stop', {}); disconnect(); say('Display stopped.');
});
$('control').onchange = () => { if (rfb) rfb.viewOnly = !$('control').checked; };
$('full').onclick = async () => {
  try {
    if (document.fullscreenElement) await document.exitFullscreen();
    else if ($('screen').requestFullscreen) await $('screen').requestFullscreen();
    else say('Fullscreen is unavailable in this Safari version. Try Add to Home Screen.');
  } catch (_) { say('Safari blocked fullscreen. Try Add to Home Screen.'); }
};
if (!token) say('Return to Deck and enter your pairing code first.');
else operation(async () => {
  const data = await api('/api/display');
  if (data.running) { $('resolution').value = data.resolution; say('Virtual display is running. Tap Start / reconnect.'); }
  else say(data.problems.length ? data.problems.join(' ') : 'Ready. Start a virtual monitor, then arrange it in KDE Display Configuration.');
});
