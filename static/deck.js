(function () {
'use strict';
var $ = function(id){return document.getElementById(id)};
var token='', buttons=[], revision=0, editing=false, selected=-1;
try { token=localStorage.getItem('deckToken')||sessionStorage.getItem('deckToken')||''; } catch(e){}
var actions={mic_toggle:'Toggle microphone',volume_up:'Volume up',volume_down:'Volume down',mute_audio:'Mute speakers',play_pause:'Play / pause',next_track:'Next track',previous_track:'Previous track',launch_obs:'Open OBS',lock_screen:'Lock screen',website:'Open website on PC',command:'Launch app / command on PC'};
Object.keys(actions).forEach(function(k){var o=document.createElement('option');o.value=k;o.textContent=actions[k];$('action').appendChild(o)});
function message(s){$('message').textContent=s}
function request(path,body){return fetch(path,{method:body?'POST':'GET',headers:{'X-Deck-Token':token,'Content-Type':'application/json'},body:body?JSON.stringify(body):undefined}).then(function(r){return r.json().then(function(d){if(!r.ok)throw Error(d.error||'Request failed');return d})})}
function remember(){try{localStorage.setItem('deckToken',token);sessionStorage.setItem('deckToken',token)}catch(e){}}
function load(){return request('/api/buttons').then(function(d){buttons=d.buttons;revision=d.revision;remember();$('setup').hidden=true;$('app').hidden=false;render()})}
function render(){var grid=$('grid');grid.textContent='';buttons.forEach(function(b,i){var wrap=document.createElement('div');wrap.className='tilewrap';var tile=document.createElement('button');tile.className='tile';tile.style.borderColor=b.color||'#30475e';var icon=document.createElement('span');icon.className='emoji';icon.textContent=b.icon;var label=document.createElement('span');label.className='label';label.textContent=b.label;tile.appendChild(icon);tile.appendChild(label);tile.onclick=function(){if(editing){open(i);return}tile.disabled=true;request('/api/action',{id:b.id}).then(function(){message('✓ '+b.label+' — action sent')}).catch(function(e){message(e.message)}).then(function(){tile.disabled=false})};wrap.appendChild(tile);if(editing){var order=document.createElement('div');order.className='order';[-1,1].forEach(function(delta){var move=document.createElement('button');move.className='ghost';move.textContent=delta<0?'←':'→';move.setAttribute('aria-label',delta<0?'Move earlier':'Move later');move.disabled=i+delta<0||i+delta>=buttons.length;move.onclick=function(){var j=i+delta;buttons[i]=buttons[j];buttons[j]=b;$('buttonForm').hidden=true;render()};order.appendChild(move)});wrap.appendChild(order)}grid.appendChild(wrap)});if(!buttons.length)message(editing?'Tap Add button to build your deck.':'Your deck is empty. Tap Edit deck to add buttons.')}
function mode(on){editing=on;$('editor').hidden=!on;$('buttonForm').hidden=true;$('edit').hidden=on;render()}
function hint(){var a=$('action').value;var custom=a==='website'||a==='command';$('valueLabel').hidden=!custom;$('value').required=custom;$('hint').textContent=a==='command'?'Runs on your PC as your user. Example: firefox or flatpak run com.spotify.Client. Quote arguments containing spaces. Shell pipes and redirects are not interpreted. Only enter commands you trust.':a==='website'?'Opens in your PC’s default browser. Include https://.':''}
function open(i){selected=i;var b=i<0?{label:'New button',icon:'⌘',color:'#30475e',action:'launch_obs',value:''}:buttons[i];['label','icon','color','action','value'].forEach(function(k){$(k).value=b[k]||(k==='color'?'#30475e':'')});$('remove').hidden=i<0;$('buttonForm').hidden=false;hint();$('label').focus()}
$('action').onchange=hint;
$('add').onclick=function(){if(buttons.length>=60){message('Maximum 60 buttons');return}open(-1)};
$('edit').onclick=function(){mode(true);message('Edit your deck, then tap Save deck.')};
$('closeForm').onclick=function(){$('buttonForm').hidden=true};
$('buttonForm').onsubmit=function(e){e.preventDefault();var b={id:selected<0?'b'+Date.now().toString(36)+Math.random().toString(36).slice(2):buttons[selected].id};['label','icon','color','action','value'].forEach(function(k){b[k]=$(k).value.trim()});if(!b.label||!b.icon){message('Enter a name and icon');return}if(selected<0)buttons.push(b);else buttons[selected]=b;$('buttonForm').hidden=true;render();message('Draft updated. Tap Save deck to keep your changes.')};
$('remove').onclick=function(){buttons.splice(selected,1);$('buttonForm').hidden=true;render()};
$('save').onclick=function(){if(!$('buttonForm').hidden){message('Apply your button to the draft or close its editor first.');return}var button=this;button.disabled=true;request('/api/buttons',{buttons:buttons,revision:revision}).then(function(d){buttons=d.buttons;revision=d.revision;mode(false);message('Deck saved on your PC.')}).catch(function(e){message(e.message)}).then(function(){button.disabled=false})};
$('cancel').onclick=function(){load().then(function(){mode(false);message('Changes discarded.')}).catch(function(e){message(e.message)})};
$('pairForm').onsubmit=function(e){e.preventDefault();$('setupError').textContent='Connecting…';request('/api/pair',{code:$('token').value.trim()}).then(function(d){token=d.token;return load()}).catch(function(e){$('setupError').textContent=e.message})};
$('disconnect').onclick=function(){try{localStorage.removeItem('deckToken');sessionStorage.removeItem('deckToken')}catch(e){}token='';location.reload()};
window.addEventListener('beforeunload',function(e){if(editing){e.preventDefault();e.returnValue=''}});
if(token)load().catch(function(e){$('setupError').textContent=e.message});
})();
