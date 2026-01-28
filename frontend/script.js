// script.js - объединённый (большой + фрагменты из малого)
// Взята за основу версия с объектом state; добавлены элементы из второго файла:
// - PRESET_ICONS, icon chooser, upload preview, clear custom icon
// - сценарии: карточки + запуск/удаление

console.log('🚀 Загрузка скрипта...');

const SERVER_URL = 'http://localhost:2000';
const DEFAULT_COMFORT = {
    tempMin: 18.0,
    tempMax: 24.0,
    humMin: 40,
    humMax: 60,
    co2Threshold: 800
};

const state = {
    rooms: [],
    devices: [],
    deviceTypes: [],
    scenarios: [],
    comfort: {...DEFAULT_COMFORT},
    userPreferences: {
        tempMin: 18.0,
        tempMax: 24.0,
        humMin: 40,
        humMax: 60,
        co2Threshold: 800
    }
};

/* ========== УТИЛИТЫ ========== */
function $(selector) { return document.querySelector(selector); }
function $$(selector) { return Array.from(document.querySelectorAll(selector)); }

function showMessage(text, type = 'info') {
    console.log(`${type}: ${text}`);
    alert(text);
}

function getTemperatureStatus(temp) {
    if (temp >= state.comfort.tempMin && temp <= state.comfort.tempMax) {
        return { status: 'good', text: 'НОРМА' };
    } else if (temp < state.comfort.tempMin - 2 || temp > state.comfort.tempMax + 2) {
        return { status: 'bad', text: 'ПЛОХО' };
    } else {
        return { status: 'normal', text: 'СРЕДНЕ' };
    }
}
function getHumidityStatus(humidity) {
    if (humidity >= state.comfort.humMin && humidity <= state.comfort.humMax) {
        return { status: 'good', text: 'НОРМА' };
    } else if (humidity < state.comfort.humMin - 10 || humidity > state.comfort.humMax + 10) {
        return { status: 'bad', text: 'ПЛОХО' };
    } else {
        return { status: 'normal', text: 'СРЕДНЕ' };
    }
}
function getCO2Status(co2) {
    if (co2 <= state.comfort.co2Threshold) {
        return { status: 'good', text: 'ХОРОШО' };
    } else if (co2 > state.comfort.co2Threshold + 200) {
        return { status: 'bad', text: 'ПЛОХО' };
    } else {
        return { status: 'normal', text: 'ПОВЫШЕН' };
    }
}

/* ========== API ФУНКЦИИ ========== */
async function apiRequest(func, args = [], method = 'POST') {
    const url = `${SERVER_URL}/api/dispatch`;
    const body = method == 'POST' ? JSON.stringify({ func, args }) : null
    try {
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: body
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('❌ API ошибка:', error);
        return { status: 'error', message: error.message };
    }
}

async function loadStateFromServer() {
    const res = await apiRequest('', [], 'GET');
    if (res.status !== 'success') {
        console.warn('Не удалось загрузить данные с сервера');
        return;
    }

    const data = res.data;

    state.rooms = data.rooms || [];
    state.devices = data.devices || [];
    state.scenarios = data.scenarios || [];
    state.deviceTypes = data.device_types || [];
    state.comfort = data.comfort_settings || {...DEFAULT_COMFORT};

    console.log('📥 State загружен с сервера');
    renderAll();
}

//setInterval(()=>{ loadStateFromServer(); }, 10000);

/* ========== DOM references (включая элементы выбора иконок) ========= */
const roomsContainer = $('#rooms-container');
const devicesContainer = $('#devices-container');
const typesContainer = $('#types-container');
const scenariosContainer = $('#scenarios-container');

const avgTempEl = $('#avg-temp');
const avgHumEl = $('#avg-humidity');
const avgCo2El = $('#avg-co2');

const addRoomBtn = $('#add-room-btn');
const roomModal = $('#room-modal');
const roomForm = $('#room-form');

const addDeviceBtn = $('#add-device-btn');
const deviceModal = $('#device-modal');
const deviceForm = $('#device-form');

const addTypeBtn = $('#add-type-btn');
const typeModal = $('#type-modal');
const typeForm = $('#type-form');

const comfortModal = $('#comfort-modal');
const openComfortBtn = $('#open-comfort-btn');
const comfortForm = $('#comfort-form');

const addScenarioBtn = $('#add-scenario-btn');
const scenarioModal = $('#scenario-modal');
const scenarioForm = $('#scenario-form');

// icon chooser elements (добавлено из второго файла)
const PRESET_ICONS = ['thermometer-half','microchip','tint','wind','fan','bolt','snowflake','broom','plug','lightbulb','leaf','house'];
const iconChooserEl = $('#icon-chooser');
const iconUploadInput = $('#device-icon-upload');
const iconPreviewEl = $('#device-icon-preview');
const clearCustomBtn = $('#clear-custom-icon');

/* ========== РЕНДЕРИНГ: комнаты, устройства, типы, сценарии ========= */

function renderRooms() {
    const container = $('#rooms-container');
    if (!container) return;
    
    if (state.rooms.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-door-closed"></i>
                <p>Нет комнат. Добавьте первую!</p>
            </div>
        `;
        container.style.display = 'block';
        return;
    }
    
    let html = '';
    state.rooms.forEach(room => {
        const devicesInRoom = state.devices.filter(d => d.roomId === room.id);
        const tempStatus = getTemperatureStatus(room.temperature);
        const humStatus = getHumidityStatus(room.humidity);
        const co2Status = getCO2Status(room.co2);
        
        html += `
            <div class="room-card">
                <div class="room-card-header">
                    <h3>${room.name}</h3>
                    <button class="delete delete-room" id="${room.id}">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
                <div class="room-metrics-grid">
                    <div class="metric-item">
                        <div class="metric-info">
                            <div class="metric-label">Температура</div>
                            <div class="metric-value temp-value">${room.temperature}°C</div>
                        </div>
                        <div class="metric-status status-${tempStatus.status}">
                            ${tempStatus.text}
                        </div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-info">
                            <div class="metric-label">Влажность</div>
                            <div class="metric-value hum-value">${room.humidity}%</div>
                        </div>
                        <div class="metric-status status-${humStatus.status}">
                            ${humStatus.text}
                        </div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-info">
                            <div class="metric-label">CO₂</div>
                            <div class="metric-value co2-value">${room.co2} ppm</div>
                        </div>
                        <div class="metric-status status-${co2Status.status}">
                            ${co2Status.text}
                        </div>
                    </div>
                </div>
                <div class="room-devices-count">
                    <i class="fas fa-plug"></i> Устройств: ${devicesInRoom.length}
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
    container.style.display = 'grid';
    
    // Обработчики удаления комнат
    $$('.delete-room').forEach(btn => {
        btn.addEventListener('click', function() {
            const roomId = btn.id;
            console.log(roomId);
            const room = state.rooms.find(r => r.id === roomId);
            console.log(room.name);
            if (confirm(`Удалить комнату "${room?.name}"?`)) {
                state.rooms = state.rooms.filter(r => r.id !== roomId);
                state.devices = state.devices.filter(d => d.roomId !== roomId);
                renderAll();
            }
        });
    });
}

function renderDevices() {
    const container = $('#devices-container');
    if (!container) return;
    
    if (state.devices.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-plug"></i>
                <p>Нет устройств. Добавьте первое!</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    state.devices.forEach(device => {
        const room = state.rooms.find(r => r.id === device.roomId);
        const type = state.deviceTypes.find(t => t.id === device.type);
        const iconHtml = device.customIcon ? `<div class="device-img"><img src="${device.customIcon}" alt=""></div>` : `<div class="device-icon"><i class="fas fa-${device.icon || getDeviceIcon(device.type)}"></i></div>`;
        html += `
            <div class="device-item">
                <div class="device-info">
                    ${iconHtml}
                    <div class="device-details">
                        <h4>${device.name}</h4>
                        <p>${type ? type.label : device.type} | ${room ? room.name : 'Без комнаты'}</p>
                    </div>
                </div>
                <div class="device-actions device-status">
                    <button class="toggle-device ${device.power ? 'on' : 'off'}" data-id="${device.id}">
                        ${device.power ? 'ВКЛ' : 'ВЫКЛ'}
                    </button>
                    <button class="delete icon-btn" data-id="${device.id}">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
    
    // Обработчики устройств
    $$('.toggle-device').forEach(btn => {
        btn.addEventListener('click', function() {
            const deviceId = parseInt(this.dataset.id);
            const device = state.devices.find(d => d.id === deviceId);
            if (device) {
                device.power = !device.power;
                renderAll();
                apiRequest('change_device_state', [device.id, device.power]);
            }
        });
    });
    
    $$('.delete-device').forEach(btn => {
        btn.addEventListener('click', function() {
            const deviceId = parseInt(this.dataset.id);
            const device = state.devices.find(d => d.id === deviceId);
            if (confirm(`Удалить устройство "${device?.name}"?`)) {
                state.devices = state.devices.filter(d => d.id !== deviceId);
                renderAll();
                apiRequest('delete_device_by_id', [deviceId]);
            }
        });
    });
}

function renderDeviceTypes() {
    const container = $('#types-container');
    if (!container) return;
    
    if (state.deviceTypes.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-cubes"></i>
                <p>Нет типов устройств</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    state.deviceTypes.forEach(type => {
        html += `
            <div class="device-type-item device-item">
                <div class="device-info">
                    <div class="device-icon"><i class="fas fa-${type.icon || 'plug'}"></i></div>
                    <div class="device-details">
                        <h4>${type.nameRu}</h4>
                        <p>ID: ${type.nameEn}</p>
                        <p style="margin-top:6px;color:var(--muted)">fixes: ${type.fixes?.join(', ') || '—'} • causes: ${type.causes?.join(', ') || '—'}</p>
                    </div>
                </div>
                <div class="device-status">
                    <button class="icon-btn delete" data-id="${type.nameEn}" title="Удалить тип"><i class="fas fa-trash"></i></button>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
    
    $$('.delete-type').forEach(btn=>{
      btn.addEventListener('click', ()=>{
        const id = btn.dataset.id;
        if (!confirm('Удалить тип устройства? Устройства с этим типом останутся, но без типа.')) return;
        state.deviceTypes = state.deviceTypes.filter(x=>x.id!==id);
        renderAll();
      });
    });
}

function renderScenarios() {
    const container = $('#scenarios-container');
    if (!container) return;
    
    if (state.scenarios.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-play-circle"></i>
                <p>Нет сценариев. Создайте первый!</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    state.scenarios.forEach(scenario => {
        const room = scenario.roomId === 'all' 
            ? 'Все комнаты' 
            : state.rooms.find(r => r.id === scenario.roomId)?.name || 'Комната не найдена';
        
        html += `
            <div class="device-item scenario-item">
                <div class="device-info">
                    <div class="device-icon"><i class="fas fa-clock"></i></div>
                    <div class="device-details">
                        <h4>${scenario.name}</h4>
                        <p>${room} • t=${scenario.temp}°C • h=${scenario.hum}%</p>
                        <p style="margin-top:6px;color:var(--muted)">
                            Время: ${scenario.startTime} — ${scenario.endTime}
                        </p>
                    </div>
                </div>
                <div class="device-status">
                    <button class="icon-btn delete" data-id="${scenario.id}" title="Удалить"><i class="fas fa-trash"></i></button>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
    
    $$('.run-scenario').forEach(btn=>{
        btn.addEventListener('click', ()=>{
            const id = btn.dataset.id;
            const s = state.scenarios.find(x=>x.id==id);
            if (s) { applyScenario(s); renderAll(); alert('Сценарий применён'); }
        });
    });

    $$('.delete-scenario').forEach(btn => {
        btn.addEventListener('click', () => {
            const id = btn.dataset.id;
            const s = state.scenarios.find(x => x.id === id);
            if (!confirm('Удалить сценарий?')) return;
            state.scenarios = state.scenarios.filter(x => x.id !== id);
            renderAll();
        });
    });
}

function updateAverageMetrics() {
    if (!avgTempEl || !avgHumEl || !avgCo2El) return;
    
    if (state.rooms.length === 0) {
        avgTempEl.textContent = "— °C";
        avgHumEl.textContent = "— %";
        avgCo2El.textContent = "— ppm";
        return;
    }
    
    const avgTemp = (state.rooms.reduce((sum, r) => sum + r.temperature, 0) / state.rooms.length).toFixed(1);
    const avgHum = Math.round(state.rooms.reduce((sum, r) => sum + r.humidity, 0) / state.rooms.length);
    const avgCo2 = Math.round(state.rooms.reduce((sum, r) => sum + r.co2, 0) / state.rooms.length);
    
    avgTempEl.textContent = `${avgTemp}°C`;
    avgHumEl.textContent = `${avgHum}%`;
    avgCo2El.textContent = `${avgCo2} ppm`;
}

/* ========== Популяция селектов (комнаты/типы) ========= */
function populateSelects() {
    const deviceRoomSelect = $('#device-room');
    if (deviceRoomSelect) {
        deviceRoomSelect.innerHTML = '<option value="">Выберите комнату...</option>';
        state.rooms.forEach(room => {
            const option = document.createElement('option');
            option.value = room.id;
            option.textContent = `${room.name}`;
            deviceRoomSelect.appendChild(option);
        });
    }
    
    const scenarioRoomSelect = $('#scenario-room');
    if (scenarioRoomSelect) {
        scenarioRoomSelect.innerHTML = ''
        state.rooms.forEach(room => {
            const option = document.createElement('option');
            option.value = room.id;
            option.textContent = `${room.name}`;
            scenarioRoomSelect.appendChild(option);
        });
    }
    
    const deviceTypeSelect = $('#device-type');
    if (deviceTypeSelect) {
        deviceTypeSelect.innerHTML = '<option value="">Выберите тип...</option>';
        state.deviceTypes.forEach(type => {
            const option = document.createElement('option');
            option.value = type.id;
            option.textContent = type.label;
            deviceTypeSelect.appendChild(option);
        });
    }
}

/* ========== Icon chooser logic (взято из малого файла) ========= */
function initIconChooser(){
  if (!iconChooserEl) return;
  iconChooserEl.innerHTML = '';
  PRESET_ICONS.forEach(ic => {
    const btn = document.createElement('div');
    btn.className = 'icon-option';
    btn.dataset.icon = ic;
    btn.innerHTML = `<i class="fas fa-${ic}"></i>`;
    btn.addEventListener('click', ()=>{
      $$('.icon-option').forEach(x=>x.classList.remove('selected'));
      btn.classList.add('selected');
      clearCustomIconPreview(false);
    });
    iconChooserEl.appendChild(btn);
  });
  const first = iconChooserEl.querySelector('.icon-option');
  if (first) first.classList.add('selected');
}

function resetIconUploadUI(){
  if (!iconUploadInput) return;
  iconUploadInput.value = '';
  if (clearCustomBtn) clearCustomBtn.style.display = 'none';
  clearCustomIconPreview(true);
}

if (iconUploadInput) {
  iconUploadInput.addEventListener('change', e=>{
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = function(ev){
      const url = ev.target.result;
      if (iconPreviewEl) iconPreviewEl.innerHTML = `<img src="${url}" alt="preview" style="width:64px;height:64px;border-radius:8px;object-fit:cover">`;
      if (clearCustomBtn) clearCustomBtn.style.display = 'inline-block';
      $$('.icon-option').forEach(x=>x.classList.remove('selected'));
    };
    reader.readAsDataURL(file);
  });
}

if (clearCustomBtn) {
  clearCustomBtn.addEventListener('click', ()=>{
    if (iconUploadInput) iconUploadInput.value='';
    clearCustomIconPreview(true);
    const first = iconChooserEl?.querySelector('.icon-option');
    if (first) first.classList.add('selected');
  });
}

function clearCustomIconPreview(hidePreview){
  if (!iconPreviewEl) return;
  iconPreviewEl.innerHTML = '';
  if (hidePreview && clearCustomBtn) clearCustomBtn.style.display = 'none';
}

/* ========== БИЗНЕС-ЛОГИКА (комнаты, устройства, типы, сценарии) ========= */

function addRoom(name) {
    const room = {
        id: 1,
        name: name,
        temperature: Math.round((22.0 + (Math.random() * 10 - 5)) * 10) / 10,
        humidity: Math.round(45 + (Math.random() * 40 - 20)),
        co2: Math.round(600 + (Math.random() * 200 - 100)),
        devices: []
    };
    
    state.rooms.push(room);
    renderAll();
    apiRequest('create_room', [name]);
    return room;
}

function getDeviceIcon(typeKey){
  const t = state.deviceTypes.find(x=>x.id===typeKey);
  return t ? t.icon : 'plug';
}

function addDevice(name, type, roomId, power = true, presetIcon = null, customDataUrl = null) {
    const device = {
        name: name,
        type: type,
        roomId: roomId,
        power: power,
        icon: presetIcon || getDeviceIcon(type),
        customIcon: customDataUrl || null
    };
    
    state.devices.push(device);
    renderAll();
    apiRequest('create_device', [name, type, roomId, power, device.icon || device.customIcon]);
    return device;
}

function addDeviceType(nameEn, nameRu, fixes = [], causes = []) {
    const type = {
        nameEn : nameEn,
        nameRu: nameRu,
        fixes: fixes,
        causes: causes
    };
    
    state.deviceTypes.push(type);
    renderAll();
    apiRequest('create_device_type', [nameEn, nameRu, fixes, causes]);
    return type;
}

/* ========== Сценарии (планирование) ========= */
function addScenario({ name, roomId, temp, hum, startTime, endTime }) {
    const s = {
        name : name,
        roomId : roomId,
        temp : temp,
        hum : hum,
        startTime : startTime,
        endTime : endTime,
    };

    scheduleScenario(s);
    state.scenarios.push(s);
    apiRequest('create_scenario', [name, roomId, temp, hum, startTime, endTime]);
    renderAll();
}

function scheduleScenario(s) {
    const now = new Date();
    const start = buildNextTime(s.startTime);
    const end = buildNextTime(s.endTime);

    // если конец раньше начала — считаем, что он на следующий день
    if (end <= start) {
        end.setDate(end.getDate() + 1);
    }

    setTimeout(() => {
        applyScenario(s);
        renderAll();
        alert(`Сценарий "${s.name}" запущен`);
    }, start - now);

    setTimeout(() => {
        rollbackScenario(s);
        renderAll();
        alert(`Сценарий "${s.name}" завершён`);
        scheduleScenario(s); // перепланируем на следующий день
    }, end - now);
}

function buildNextTime(timeStr) {
    const [hh, mm] = timeStr.split(':').map(Number);
    const now = new Date();
    const t = new Date(now);
    t.setHours(hh, mm, 0, 0);
    if (t <= now) t.setDate(t.getDate() + 1);
    return t;
}


function applyScenario(s){
    const r = state.rooms.find(x=>x.id===s.roomId);
    if (r){ r.temperature = parseFloat(s.temp); r.humidity = parseInt(s.humidity); }
}

function rollbackScenario(s) {
    // возвращаем в комфортные значения
    const temp = state.userPreferences.comfortableTemp;
    const hum = state.userPreferences.comfortableHumidity;
    const r = state.rooms.find(x => x.id === s.roomId);
    if (r) {
        r.temperature = temp;
        r.humidity = hum;
    }
}

/* ========== Поддержка селектов (используется в модалках) ========= */
function populateDeviceRoomSelect(){
  const sel = $('#device-room');
  if (!sel) return;
  sel.innerHTML = '';
  state.rooms.forEach(r => {
    const o = document.createElement('option'); o.value = r.id; o.textContent = r.name; sel.appendChild(o);
  });
}

function populateDeviceTypeSelect(){
  const sel = $('#device-type');
  if (!sel) return;
  sel.innerHTML = '<option value="">Выберите тип...</option>';
  state.deviceTypes.forEach(t=>{
    const o = document.createElement('option'); o.value = t.id; o.textContent = t.label; sel.appendChild(o);
  });
}

function populateScenarioRoomSelect(){
  const sel = $('#scenario-room');
  if (!sel) return;
  sel.innerHTML = '';
  state.rooms.forEach(r=>{
    const o = document.createElement('option'); o.value = r.id; o.textContent = r.name; sel.appendChild(o);
  });
}

/* ========== СИМУЛЯЦИЯ (текущие значения изменяются) ========= */
function updateRoomMetrics(roomId){
  const idx = state.rooms.findIndex(r=>r.id===roomId);
  if (idx===-1) return;
  state.rooms[idx].temperature = Math.round((state.rooms[idx].temperature + (Math.random()*2 -1))*10)/10;
  state.rooms[idx].humidity = Math.round(state.rooms[idx].humidity + (Math.random()*10 -5));
  state.rooms[idx].co2 = Math.round(state.rooms[idx].co2 + (Math.random()*100 -50));
  state.rooms[idx].temperature = Math.max(12, Math.min(30, state.rooms[idx].temperature));
  state.rooms[idx].humidity = Math.max(20, Math.min(80, state.rooms[idx].humidity));
  state.rooms[idx].co2 = Math.max(350, Math.min(2000, state.rooms[idx].co2));
}

/* ========== МОДАЛЬНЫЕ ОКНА и обработчики (setup) ========= */
function setupModalHandlers() {
    console.log('🔧 Настройка обработчиков...');
    
    // Комната
    $('#add-room-btn')?.addEventListener('click', () => {
        $('#room-modal').style.display = 'flex';
        $('#room-name')?.focus();
    });
    $('#room-form')?.addEventListener('submit', function(e) {
        e.preventDefault();
        const name = $('#room-name').value.trim();
        if (name) {
            addRoom(name);
            $('#room-modal').style.display = 'none';
            this.reset();
            showMessage(`Комната "${name}" добавлена!`, 'success');
        }
    });

    // Устройство (здесь учитываем пресеты/загрузку иконки)
    $('#add-device-btn')?.addEventListener('click', () => {
        populateSelects();
        if (state.rooms.length === 0) {
            showMessage('Сначала добавьте комнату!', 'warning');
            return;
        }
        initIconChooser();
        resetIconUploadUI();
        $('#device-modal').style.display = 'flex';
        $('#device-name')?.focus();
    });

    $('#device-form')?.addEventListener('submit', function(e) {
        e.preventDefault();
        const name = $('#device-name').value.trim();
        const type = $('#device-type').value;
        const roomId = parseInt($('#device-room').value);
        const power = $('#device-power') ? $('#device-power').checked : true;

        if (!name || !type || !roomId) {
            showMessage('Заполните все поля!', 'warning');
            return;
        }

        // Получим выбранный пресет и кастомный dataURL (если есть)
        const selectedPreset = iconChooserEl?.querySelector('.icon-option.selected')?.dataset.icon || null;
        const customDataUrl = iconPreviewEl?.querySelector('img') ? iconPreviewEl.querySelector('img').src : null;

        addDevice(name, type, roomId, power, selectedPreset, customDataUrl);
        $('#device-modal').style.display = 'none';
        this.reset();
        showMessage(`Устройство "${name}" добавлено!`, 'success');
    });

    // Тип устройства (чекбоксы)
    $('#add-type-btn')?.addEventListener('click', () => {
        $('#type-modal').style.display = 'flex';
        $('#type-key')?.focus();
    });

    $('#type-form')?.addEventListener('submit', function(e) {
        e.preventDefault();
        const nameEn = $('#type-key').value.trim().toLowerCase();
        const nameRu = $('#type-label').value.trim();
        if (!nameEn || !nameRu) {
            showMessage('Заполните обязательные поля!', 'warning');
            return;
        }
        if (state.deviceTypes.some(t => t.nameEn === nameEn)) {
            showMessage(`Тип устройства с ID "${nameEn}" уже существует!`, 'warning');
            return;
        }
        const fixes = [];
        $$('input[name="fixes"]:checked').forEach(cb => fixes.push(cb.value));
        const causes = [];
        $$('input[name="causes"]:checked').forEach(cb => causes.push(cb.value));

        addDeviceType(nameEn, nameRu, fixes, causes);
        $('#type-modal').style.display = 'none';
        this.reset();
        showMessage(`Тип устройства "${nameRu}" создан!`, 'success');
    });

    // Сценарий
    $('#add-scenario-btn')?.addEventListener('click', () => {
        if (state.rooms.length === 0) {
            showMessage('Сначала добавьте комнату!', 'warning');
            return;
        }
        populateSelects();
        $('#scenario-modal').style.display = 'flex';
        $('#scenario-name')?.focus();
    });

    $('#scenario-form')?.addEventListener('submit', function(e) {
        e.preventDefault();
        const name = $('#scenario-name').value.trim();
        const roomId = $('#scenario-room').value;
        const temperature = $('#scenario-temp').value;
        const humidity = $('#scenario-humidity').value;
        const startTime = $('#scenario-start-time').value;
        const endTime = $('#scenario-end-time').value;

        if (!name || !temperature || !humidity || !startTime || !endTime) {
            showMessage('Заполните все обязательные поля!', 'warning');
            return;
        }

        addScenario({ name, roomId: roomId, temp: temperature, humidity, startTime, endTime });
        $('#scenario-modal').style.display = 'none';
        this.reset();
        showMessage(`Сценарий "${name}" создан!`, 'success');
    });

    // Комфортные настройки
    $('#open-comfort-btn')?.addEventListener('click', () => {
        $('#comfort-temp-min').value = state.comfort.tempMin;
        $('#comfort-temp-max').value = state.comfort.tempMax;
        $('#comfort-hum-min').value = state.comfort.humMin;
        $('#comfort-hum-max').value = state.comfort.humMax;
        $('#comfort-co2-threshold').value = state.comfort.co2Threshold;
        $('#comfort-modal').style.display = 'flex';
    });

    $('#comfort-form')?.addEventListener('submit', async function(e) {
        e.preventDefault();
        state.comfort = {
            tempMin: parseFloat($('#comfort-temp-min').value) || DEFAULT_COMFORT.tempMin,
            tempMax: parseFloat($('#comfort-temp-max').value) || DEFAULT_COMFORT.tempMax,
            humMin: parseInt($('#comfort-hum-min').value) || DEFAULT_COMFORT.humMin,
            humMax: parseInt($('#comfort-hum-max').value) || DEFAULT_COMFORT.humMax,
            co2Threshold: parseInt($('#comfort-co2-threshold').value) || DEFAULT_COMFORT.co2Threshold
        };
        await apiRequest('create_preferencies', [
            [state.comfort.tempMin, state.comfort.tempMax],
            [state.comfort.humMin, state.comfort.humMax],
            state.comfort.co2Threshold,
        ]);
        $('#comfort-modal').style.display = 'none';
        showMessage('Настройки сохранены!', 'success');
        renderAll();
    });

    // device-power UI label (если есть)
    $('#device-power')?.addEventListener('change', function() {
        const statusEl = $('#device-power-status');
        if (statusEl) {
            statusEl.textContent = this.checked ? 'Включено' : 'Выключено';
        }
    });

    // Закрытие модалок
    $$('.close-modal, .btn-danger[data-close]').forEach(btn => {
        btn.addEventListener('click', function() {
            const modalId = this.dataset.close;
            if (modalId) {
                $(`#${modalId}`).style.display = 'none';
            }
        });
    });
    // Клик вне модалки
    $$('.modal').forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) this.style.display = 'none';
        });
    });
}

/* ========== РЕНДЕР / НАЧАЛО ========= */
function renderAll() {
    renderRooms();
    renderDevices();
    renderDeviceTypes();
    renderScenarios();
    updateAverageMetrics();
    populateSelects();
}

async function initializeApp() {
    console.log('🚀 Инициализация приложения...');
    await loadStateFromServer();
    setupModalHandlers();
    renderAll();
}

// Очистка таймеров (если есть)
window.addEventListener('beforeunload', ()=>{
  state.scenarios.forEach(s=> s.timeoutId && clearTimeout(s.timeoutId));
});

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}