console.log('🚀 Загрузка скрипта...');

const SERVER_URL = 'http://localhost:2000';
const DEFAULT_COMFORT = {
    tempMin: 18.0,
    tempMax: 24.0,
    humMin: 40,
    humMax: 60,
    co2Threshold: 800
};
const USER_ID = 'U1451484818';

const state = {
    rooms: [],
    devices: [],
    deviceTypes: [],
    scenarios: [],
    comfort: {...DEFAULT_COMFORT}
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
    const threshold = state.comfort.co2Threshold || 800;
    if (co2 <= threshold) {
        return { status: 'good', text: 'ХОРОШО' };
    } else if (co2 > threshold + 200) {
        return { status: 'bad', text: 'ПЛОХО' };
    } else {
        return { status: 'normal', text: 'ПОВЫШЕН' };
    }
}

/* ========== API ФУНКЦИИ ========== */
async function apiRequest(func, args = [], method = 'POST') {
    const url = `${SERVER_URL}/api/dispatch`;
    
    try {
        const options = {
            method: method,
            headers: { 'Content-Type': 'application/json' }
        };
        
        if (method === 'POST') {
            options.body = JSON.stringify({ func, args });
        }
        
        console.log(`📤 API ${method} ${func}:`, args);
        const response = await fetch(url, options);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        console.log(`📥 Ответ API ${func}:`, data);
        return data;
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
    const measurements = [];

    // Симулируем данные с учетом устройств
    if (data.rooms && data.rooms.length > 0) {
        data.rooms.forEach(room => {
            let temp = room.temperature || 22.0;
            let hum = room.humidity || 50;
            let co2 = room.co2 || 400;
            
            // Добавляем случайные колебания только для показаний датчиков
            temp += (Math.random() * 4 - 2);
            hum += (Math.random() * 10 - 5);
            co2 += (Math.random() * 40 - 20);
            
            // УБРАТЬ АВТОМАТИЧЕСКОЕ ИЗМЕНЕНИЕ СОСТОЯНИЯ УСТРОЙСТВ
            // ЭТО БЫЛО ИСТОЧНИКОМ ПРОБЛЕМЫ
            
            // Ограничиваем значения
            temp = Math.max(15, Math.min(30, temp));
            hum = Math.max(20, Math.min(80, hum));
            co2 = Math.max(300, Math.min(1500, co2));
            
            // Обновляем комнату
            room.temperature = parseFloat(temp.toFixed(1));
            room.humidity = Math.round(hum);
            room.co2 = Math.round(co2);
            
            // Добавляем измерение
            measurements.push([room.id, room.temperature, room.humidity, room.co2]);
        });
    }

    // Обновляем состояние
    state.rooms = data.rooms || [];
    state.devices = data.devices || [];
    state.scenarios = data.scenarios || [];
    state.deviceTypes = data.deviceTypes || [];
    state.comfort = data.preferences || {...DEFAULT_COMFORT};

    // Отправляем измерения на сервер
    if (measurements.length > 0) {
        apiRequest('create_measurement', measurements);
        console.log(`📊 Отправлено ${measurements.length} измерений`);
    }

    console.log('📥 State загружен с сервера');
    renderAll();
}

/* ========== РЕНДЕРИНГ ========== */
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
        return;
    }
    
    let html = '';
    state.rooms.forEach(room => {
        const devicesInRoom = state.devices.filter(d => d.roomId === room.id);
        const tempStatus = getTemperatureStatus(room.temperature || room.temp || 22);
        const humStatus = getHumidityStatus(room.humidity || room.hum || 50);
        const co2Status = getCO2Status(room.co2 || 400);
        
        html += `
            <div class="room-card">
                <div class="room-card-header">
                    <h3>${room.name}</h3>
                    <button class="delete delete-room" data-id="${room.id}">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
                <div class="room-metrics-grid">
                    <div class="metric-item">
                        <div class="metric-info">
                            <div class="metric-label">Температура</div>
                            <div class="metric-value temp-value">${room.temperature || room.temp || 22}°C</div>
                        </div>
                        <div class="metric-status status-${tempStatus.status}">
                            ${tempStatus.text}
                        </div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-info">
                            <div class="metric-label">Влажность</div>
                            <div class="metric-value hum-value">${room.humidity || room.hum || 50}%</div>
                        </div>
                        <div class="metric-status status-${humStatus.status}">
                            ${humStatus.text}
                        </div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-info">
                            <div class="metric-label">CO₂</div>
                            <div class="metric-value co2-value">${room.co2 || 400} ppm</div>
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
    
    // Обработчики удаления комнат
    $$('.delete-room').forEach(btn => {
        btn.addEventListener('click', function() {
            const roomId = this.dataset.id;
            const room = state.rooms.find(r => r.id === roomId);
            if (confirm(`Удалить комнату "${room?.name}"?`)) {
                state.rooms = state.rooms.filter(r => r.id !== roomId);
                state.devices = state.devices.filter(d => d.roomId !== roomId);
                apiRequest('delete_room', [roomId]);
                renderAll();
                showMessage(`Комната "${room?.name}" удалена`, 'success');
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
        const type = state.deviceTypes.find(t => t.id === device.type || t.nameEn === device.type);
        html += `
            <div class="device-item">
                <div class="device-info">
                    <div class="device-details">
                        <h4>${device.name}</h4>
                        <p>${type ? type.nameRu : device.type} | ${room ? room.name : 'Без комнаты'}</p>
                    </div>
                </div>
                <div class="device-actions">
                    <button class="toggle-device ${device.power ? 'on' : 'off'}" data-id="${device.id}">
                        ${device.power ? 'ВКЛ' : 'ВЫКЛ'}
                    </button>
                    <button class="delete delete-device" data-id="${device.id}">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
    
    // Обработчики устройств - ИСПРАВЛЕНО
    $$('.toggle-device').forEach(btn => {
        btn.addEventListener('click', async function() {
            const deviceId = this.dataset.id;
            const device = state.devices.find(d => d.id === deviceId);
            if (device) {
                // Сохраняем предыдущее состояние на случай ошибки
                const previousState = device.power;
                
                // Меняем состояние локально для быстрого отклика UI
                device.power = !device.power;
                this.textContent = device.power ? 'ВКЛ' : 'ВЫКЛ';
                this.classList.toggle('on', device.power);
                this.classList.toggle('off', !device.power);
                
                // Отправляем запрос на сервер
                try {
                    const result = await apiRequest('change_device_state', [device.id, device.power]);
                    if (result.status !== 'ok') {
                        // Если ошибка - возвращаем предыдущее состояние
                        device.power = previousState;
                        this.textContent = device.power ? 'ВКЛ' : 'ВЫКЛ';
                        this.classList.toggle('on', device.power);
                        this.classList.toggle('off', !device.power);
                        showMessage(`Ошибка: ${result.message}`, 'error');
                    } else {
                        showMessage(`Устройство "${device.name}" ${device.power ? 'включено' : 'выключено'}`, 'success');
                    }
                } catch (error) {
                    // Если ошибка сети - возвращаем предыдущее состояние
                    device.power = previousState;
                    this.textContent = device.power ? 'ВКЛ' : 'ВЫКЛ';
                    this.classList.toggle('on', device.power);
                    this.classList.toggle('off', !device.power);
                    showMessage(`Ошибка сети: ${error.message}`, 'error');
                }
            }
        });
    });
    
    $$('.delete-device').forEach(btn => {
        btn.addEventListener('click', async function() {
            const deviceId = this.dataset.id;
            const device = state.devices.find(d => d.id === deviceId);
            if (confirm(`Удалить устройство "${device?.name}"?`)) {
                const result = await apiRequest('delete_device_by_id', [deviceId]);
                if (result.status === 'ok') {
                    state.devices = state.devices.filter(d => d.id !== deviceId);
                    renderAll();
                    showMessage(`Устройство "${device?.name}" удалено`, 'success');
                } else {
                    showMessage(`Ошибка при удалении: ${result.message}`, 'error');
                }
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
                        <p>ID: ${type.id || type.nameEn}</p>
                        <p style="margin-top:6px;color:var(--muted)">
                            fixes: ${type.fixes?.join(', ') || '—'} • causes: ${type.causes?.join(', ') || '—'}
                        </p>
                    </div>
                </div>
                <div class="device-status">
                    <button class="icon-btn delete delete-type" data-id="${type.id || type.nameEn}" title="Удалить тип">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
    
    $$('.delete-type').forEach(btn => {
        btn.addEventListener('click', function() {
            const id = this.dataset.id;
            const type = state.deviceTypes.find(t => (t.id || t.nameEn) === id);
            if (confirm(`Удалить тип устройства "${type?.nameRu}"?`)) {
                state.deviceTypes = state.deviceTypes.filter(t => (t.id || t.nameEn) !== id);
                renderAll();
                apiRequest('delete_device_type', [id]);
                showMessage(`Тип устройства "${type?.nameRu}" удален`, 'success');
            }
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
            <div class="device-item">
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
                    <button class="btn run-scenario" data-id="${scenario.id}" title="Запустить">
                        <i class="fas fa-play"></i> Запустить
                    </button>
                    <button class="delete delete-scenario" data-id="${scenario.id}" title="Удалить">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
    
    $$('.run-scenario').forEach(btn => {
        btn.addEventListener('click', function() {
            const id = this.dataset.id;
            const scenario = state.scenarios.find(x => x.id === id);
            if (scenario) {
                applyScenario(scenario);
                renderAll();
                showMessage(`Сценарий "${scenario.name}" запущен`, 'success');
            }
        });
    });

    $$('.delete-scenario').forEach(btn => {
        btn.addEventListener('click', function() {
            const id = this.dataset.id;
            const scenario = state.scenarios.find(x => x.id === id);
            if (confirm(`Удалить сценарий "${scenario?.name}"?`)) {
                state.scenarios = state.scenarios.filter(x => x.id !== id);
                renderAll();
                apiRequest('delete_scenario', [id]);
                showMessage(`Сценарий "${scenario?.name}" удален`, 'success');
            }
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
    
    const avgTemp = (state.rooms.reduce((sum, r) => sum + (r.temperature || r.temp || 22), 0) / state.rooms.length).toFixed(1);
    const avgHum = Math.round(state.rooms.reduce((sum, r) => sum + (r.humidity || r.hum || 50), 0) / state.rooms.length);
    const avgCo2 = Math.round(state.rooms.reduce((sum, r) => sum + (r.co2 || 400), 0) / state.rooms.length);
    
    avgTempEl.textContent = `${avgTemp}°C`;
    avgHumEl.textContent = `${avgHum}%`;
    avgCo2El.textContent = `${avgCo2} ppm`;
}

/* ========== ДОМ ЭЛЕМЕНТЫ ========== */
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

/* ========== ПОПУЛЯЦИЯ СЕЛЕКТОВ ========== */
function populateSelects() {
    const deviceRoomSelect = $('#device-room');
    if (deviceRoomSelect) {
        deviceRoomSelect.innerHTML = '<option value="">Выберите комнату...</option>';
        state.rooms.forEach(room => {
            const option = document.createElement('option');
            option.value = room.id;
            option.textContent = room.name;
            deviceRoomSelect.appendChild(option);
        });
    }
    
    const scenarioRoomSelect = $('#scenario-room');
    if (scenarioRoomSelect) {
        scenarioRoomSelect.innerHTML = '<option value="">Выберите комнату...</option>';
        state.rooms.forEach(room => {
            const option = document.createElement('option');
            option.value = room.id;
            option.textContent = room.name;
            scenarioRoomSelect.appendChild(option);
        });
    }
    
    const deviceTypeSelect = $('#device-type');
    if (deviceTypeSelect) {
        deviceTypeSelect.innerHTML = '<option value="">Выберите тип...</option>';
        state.deviceTypes.forEach(type => {
            const option = document.createElement('option');
            option.value = type.id || type.nameEn;
            option.textContent = type.nameRu;
            deviceTypeSelect.appendChild(option);
        });
    }
}

/* ========== БИЗНЕС-ЛОГИКА ========== */
function addRoom(name) {
    const room = {
        id: 'room_' + Date.now(), // Временный ID для фронтенда
        name: name,
        temperature: parseFloat((22.0 + (Math.random() * 4 - 2)).toFixed(1)),
        humidity: Math.round(50 + (Math.random() * 20 - 10)),
        co2: Math.round(500 + (Math.random() * 200 - 100))
    };
    
    state.rooms.push(room);
    renderAll();
    
    // Отправляем запрос на создание комнаты
    apiRequest('create_room', [name, room.temperature, room.humidity, room.co2])
        .then(result => {
            if (result.status === 'ok' && result.result) {
                // Обновляем ID комнаты с тем, что вернул сервер
                const createdRoom = state.rooms.find(r => r.name === name);
                if (createdRoom) {
                    createdRoom.id = result.result; // Используем ID с сервера
                    console.log(`Комната создана с ID: ${result.result}`);
                }
            }
        })
        .catch(error => {
            console.error('Ошибка при создании комнаты:', error);
        });
    
    return room;
}

function addDevice(name, type, roomId, power = true) {
    const device = {
        id: 'device_' + Date.now(),
        name: name,
        type: type,
        roomId: roomId,
        power: power
    };
    
    state.devices.push(device);
    renderAll();
    apiRequest('create_device', [name, type, roomId, power]);
    return device;
}

function addDeviceType(nameEn, nameRu, fixes = [], causes = [], dependsOnWeather = false) {
    const type = {
        id: nameEn,
        nameEn: nameEn,
        nameRu: nameRu,
        fixes: fixes,
        causes: causes,
        dependsOnWeather: dependsOnWeather
    };
    
    state.deviceTypes.push(type);
    renderAll();
    apiRequest('create_device_type', [nameEn, nameRu, fixes, causes, dependsOnWeather]);
    return type;
}

function addScenario({ name, roomId, temp, hum, startTime, endTime }) {
    const scenario = {
        id: 'scenario_' + Date.now(),
        name: name,
        roomId: roomId,
        temp: parseFloat(temp),
        hum: parseFloat(hum),
        startTime: startTime,
        endTime: endTime
    };

    state.scenarios.push(scenario);
    scheduleScenario(scenario);
    apiRequest('create_scenario', [USER_ID, name, startTime, endTime, roomId, hum, temp]);
    renderAll();
    
    return scenario;
}

function scheduleScenario(s) {
    const now = new Date();
    const start = buildNextTime(s.startTime);
    const end = buildNextTime(s.endTime);

    if (end <= start) {
        end.setDate(end.getDate() + 1);
    }

    setTimeout(() => {
        applyScenario(s);
        renderAll();
        showMessage(`Сценарий "${s.name}" запущен`, 'success');
    }, start - now);

    setTimeout(() => {
        rollbackScenario(s);
        renderAll();
        showMessage(`Сценарий "${s.name}" завершён`, 'info');
        scheduleScenario(s);
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

function applyScenario(s) {
    const room = state.rooms.find(r => r.id === s.roomId);
    if (room) {
        room.temperature = s.temp;
        room.humidity = s.hum;
    }
}

function rollbackScenario(s) {
    const room = state.rooms.find(r => r.id === s.roomId);
    if (room) {
        room.temperature = state.comfort.tempMin + (state.comfort.tempMax - state.comfort.tempMin) / 2;
        room.humidity = state.comfort.humMin + (state.comfort.humMax - state.comfort.humMin) / 2;
    }
}

/* ========== МОДАЛЬНЫЕ ОКНА ========== */
function setupModalHandlers() {
    console.log('🔧 Настройка обработчиков...');
    
    // Комната
    $('#add-room-btn')?.addEventListener('click', () => {
        $('#room-modal').style.display = 'flex';
        $('#room-name').value = '';
        $('#room-name').focus();
    });
    
    $('#room-form')?.addEventListener('submit', function(e) {
        e.preventDefault();
        const name = $('#room-name').value.trim();
        if (name) {
            addRoom(name);
            $('#room-modal').style.display = 'none';
            this.reset();
        }
    });

    // Устройство
    $('#add-device-btn')?.addEventListener('click', () => {
        populateSelects();
        if (state.rooms.length === 0) {
            showMessage('Сначала добавьте комнату!', 'warning');
            return;
        }
        if (state.deviceTypes.length === 0) {
            showMessage('Сначала добавьте тип устройства!', 'warning');
            return;
        }
        $('#device-modal').style.display = 'flex';
        $('#device-name').value = '';
        $('#device-name').focus();
    });

    $('#device-form')?.addEventListener('submit', function(e) {
        e.preventDefault();
        const name = $('#device-name').value.trim();
        const type = $('#device-type').value;
        const roomId = $('#device-room').value;
        const power = $('#device-power').checked;

        if (!name || !type || !roomId) {
            showMessage('Заполните все поля!', 'warning');
            return;
        }

        addDevice(name, type, roomId, power);
        $('#device-modal').style.display = 'none';
        this.reset();
    });

    // Тип устройства
    $('#add-type-btn')?.addEventListener('click', () => {
        $('#type-modal').style.display = 'flex';
        $('#type-key').value = '';
        $('#type-key').focus();
    });

    $('#type-form')?.addEventListener('submit', function(e) {
        e.preventDefault();
        const nameEn = $('#type-key').value.trim().toLowerCase();
        const nameRu = $('#type-label').value.trim();
        const dependsOnWeather = $('#type-weather').checked;

        if (!nameEn || !nameRu) {
            showMessage('Заполните обязательные поля!', 'warning');
            return;
        }
        
        if (state.deviceTypes.some(t => t.id === nameEn || t.nameEn === nameEn)) {
            showMessage(`Тип устройства с ID "${nameEn}" уже существует!`, 'warning');
            return;
        }
        
        const fixes = [];
        $$('input[name="fixes"]:checked').forEach(cb => fixes.push(cb.value));
        const causes = [];
        $$('input[name="causes"]:checked').forEach(cb => causes.push(cb.value));

        addDeviceType(nameEn, nameRu, fixes, causes, dependsOnWeather);
        $('#type-modal').style.display = 'none';
        this.reset();
    });

    // Сценарий
    $('#add-scenario-btn')?.addEventListener('click', () => {
        if (state.rooms.length === 0) {
            showMessage('Сначала добавьте комнату!', 'warning');
            return;
        }
        populateSelects();
        $('#scenario-modal').style.display = 'flex';
        $('#scenario-name').value = '';
        $('#scenario-name').focus();
    });

    $('#scenario-form')?.addEventListener('submit', function(e) {
        e.preventDefault();
        const name = $('#scenario-name').value.trim();
        const roomId = $('#scenario-room').value;
        const temperature = $('#scenario-temp').value;
        const humidity = $('#scenario-humidity').value;
        const startTime = $('#scenario-start-time').value;
        const endTime = $('#scenario-end-time').value;

        if (!name || !temperature || !humidity || !startTime || !endTime || !roomId) {
            showMessage('Заполните все обязательные поля!', 'warning');
            return;
        }

        addScenario({ name, roomId, temp: temperature, hum: humidity, startTime, endTime });
        $('#scenario-modal').style.display = 'none';
        this.reset();
    });

    // Комфортные настройки
    $('#open-comfort-btn')?.addEventListener('click', () => {
        $('#comfort-temp-min').value = state.comfort.tempMin;
        $('#comfort-temp-max').value = state.comfort.tempMax;
        $('#comfort-hum-min').value = state.comfort.humMin;
        $('#comfort-hum-max').value = state.comfort.humMax;
        $('#comfort-modal').style.display = 'flex';
    });

    $('#comfort-form')?.addEventListener('submit', async function(e) {
        e.preventDefault();
        state.comfort = {
            tempMin: parseFloat($('#comfort-temp-min').value) || DEFAULT_COMFORT.tempMin,
            tempMax: parseFloat($('#comfort-temp-max').value) || DEFAULT_COMFORT.tempMax,
            humMin: parseInt($('#comfort-hum-min').value) || DEFAULT_COMFORT.humMin,
            humMax: parseInt($('#comfort-hum-max').value) || DEFAULT_COMFORT.humMax,
            co2Threshold: 800
        };
        
        await apiRequest('create_preferencies', [
            USER_ID,
            [state.comfort.tempMin, state.comfort.tempMax],
            [state.comfort.humMin, state.comfort.humMax]
        ]);
        
        $('#comfort-modal').style.display = 'none';
        showMessage('Настройки сохранены!', 'success');
        renderAll();
    });

    // Статус устройства в модалке
    $('#device-power')?.addEventListener('change', function() {
        const statusEl = $('#device-power-status');
        if (statusEl) {
            statusEl.textContent = this.checked ? 'Включено' : 'Выключено';
        }
    });

    // Кнопка обновления
    $('#reload-btn')?.addEventListener('click', function() {
        loadStateFromServer();
    });

    // Закрытие модалок
    $$('.close-modal, .btn-danger[data-close]').forEach(btn => {
        btn.addEventListener('click', function() {
            const modalId = this.dataset.close;
            if (modalId) {
                $(`#${modalId}`).style.display = 'none';
            } else {
                this.closest('.modal').style.display = 'none';
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

/* ========== РЕНДЕР ========== */
function renderAll() {
    renderRooms();
    renderDevices();
    renderDeviceTypes();
    renderScenarios();
    updateAverageMetrics();
    populateSelects();
}

/* ========== ИНИЦИАЛИЗАЦИЯ ========== */
async function initializeApp() {
    console.log('🚀 Инициализация приложения...');
    setupModalHandlers();
    await loadStateFromServer();
    
    // Обновление каждые 10 секунд
    setInterval(() => {
        loadStateFromServer();
    }, 10000);
}

// Запуск приложения
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}