import json
from sc_client.client import generate_elements, search_links_by_contents, search_by_template, erase_elements, generate_by_template, search_by_template
from sc_client.constants import sc_type
from sc_client.models import ScLinkContent, ScLinkContentType, ScConstruction, ScTemplate, ScAddr
from sc_kpm import ScKeynodes
from sc_kpm.utils import get_link_content_data, get_element_system_identifier
import random
from sc_client.client import connect
from typing import Dict, List

connect("ws://localhost:8090")


def get_all_device_data() -> List[Dict]:
    print("🔍 Поиск всех устройств...")
    
    # Находим все узлы, которые являются экземплярами concept_device
    templ = ScTemplate()
    templ.triple(
        ScKeynodes.resolve("concept_device", sc_type.CONST_NODE_CLASS),
        sc_type.VAR_PERM_POS_ARC,
        (sc_type.VAR_NODE, "_device")
    )
    
    search_results = search_by_template(templ)
    devices = []
    
    print(f"🔍 Найдено узлов устройств: {len(search_results)}")
    
    for i, result in enumerate(search_results):
        device_node = result.get("_device")
        
        # Получаем ID устройства - используем более гибкий поиск
        device_id = f"unknown_{i}"
        # Пробуем разные способы найти ID
        id_patterns = [
            ("nrel_id", sc_type.CONST_NODE_NON_ROLE),  # Стандартный способ
            ("nrel_main_idtf", sc_type.CONST_NODE_NON_ROLE),  # Альтернативный
            ("nrel_system_identifier", sc_type.CONST_NODE_NON_ROLE),  # Еще вариант
        ]
        
        for rel_name, rel_type in id_patterns:
            id_templ = ScTemplate()
            id_templ.quintuple(
                device_node,
                sc_type.VAR_PERM_POS_ARC,
                (sc_type.VAR_NODE_LINK, "_id_link"),
                sc_type.VAR_PERM_POS_ARC,
                ScKeynodes.resolve(rel_name, rel_type)
            )
            id_results = search_by_template(id_templ)
            if id_results:
                try:
                    device_id = get_link_content_data(id_results[0].get("_id_link"))
                    if device_id:
                        break
                except:
                    continue
        
        # Получаем имя устройства - также используем гибкий поиск
        device_name = "Без имени"
        name_patterns = [
            ("nrel_name", sc_type.CONST_NODE_NON_ROLE),
            ("nrel_main_idtf", sc_type.CONST_NODE_NON_ROLE),
            ("nrel_user", sc_type.CONST_NODE_NON_ROLE),
        ]
        
        for rel_name, rel_type in name_patterns:
            name_templ = ScTemplate()
            name_templ.quintuple(
                device_node,
                sc_type.VAR_PERM_POS_ARC,
                (sc_type.VAR_NODE_LINK, "_name_link"),
                sc_type.VAR_PERM_POS_ARC,
                ScKeynodes.resolve(rel_name, rel_type)
            )
            name_results = search_by_template(name_templ)
            if name_results:
                try:
                    device_name = get_link_content_data(name_results[0].get("_name_link"))
                    if device_name:
                        break
                except:
                    continue
        
        # Если все еще не нашли имя, пробуем получить системный идентификатор самого узла
        if device_name == "Без имени":
            try:
                sys_id = get_element_system_identifier(device_node)
                if sys_id and not sys_id.startswith("_"):  # Исключаем технические имена
                    device_name = sys_id
            except:
                pass
        
        # Получаем тип устройства (ищем все классы, экземпляром которых является устройство)
        device_type = "unknown"
        type_templ = ScTemplate()
        type_templ.triple(
            (sc_type.VAR_NODE_CLASS, "_device_class"),
            sc_type.VAR_PERM_POS_ARC,
            device_node
        )
        type_results = search_by_template(type_templ)
        
        if type_results:
            # Ищем конкретный тип устройства (исключаем concept_device)
            for res in type_results:
                class_addr = res.get("_device_class")
                try:
                    sys_id = get_element_system_identifier(class_addr)
                    if sys_id and "concept_" in sys_id and sys_id != "concept_device":
                        device_type = sys_id.split("concept_")[1]
                        break
                except:
                    continue
        
        # Получаем комнату - исправленный поиск
        room_id = ""
        room_templ = ScTemplate()
        room_templ.quintuple(
            device_node,
            sc_type.VAR_PERM_POS_ARC,
            (sc_type.VAR_NODE, "_room"),
            sc_type.VAR_PERM_POS_ARC,
            ScKeynodes.resolve("rrel_located_at", sc_type.CONST_NODE_ROLE)
        )
        room_results = search_by_template(room_templ)
        
        if room_results:
            room_node = room_results[0].get("_room")
            # Получаем ID комнаты - также гибко
            room_id_patterns = [
                ("nrel_id", sc_type.CONST_NODE_NON_ROLE),
                ("nrel_main_idtf", sc_type.CONST_NODE_NON_ROLE),
            ]
            
            for rel_name, rel_type in room_id_patterns:
                room_id_templ = ScTemplate()
                room_id_templ.quintuple(
                    room_node,
                    sc_type.VAR_COMMON_ARC,
                    (sc_type.VAR_NODE_LINK, "_room_id_link"),
                    sc_type.VAR_PERM_POS_ARC,
                    ScKeynodes.resolve(rel_name, rel_type)
                )
                room_id_results = search_by_template(room_id_templ)
                if room_id_results:
                    try:
                        room_id = get_link_content_data(room_id_results[0].get("_room_id_link"))
                        if room_id:
                            break
                    except:
                        continue
            
            # Если не нашли по ID, пробуем получить имя комнаты
            if not room_id:
                for rel_name, rel_type in room_id_patterns:
                    room_name_templ = ScTemplate()
                    room_name_templ.quintuple(
                        room_node,
                        sc_type.VAR_COMMON_ARC,
                        (sc_type.VAR_NODE_LINK, "_room_name_link"),
                        sc_type.VAR_PERM_POS_ARC,
                        ScKeynodes.resolve(rel_name, rel_type)
                    )
                    room_name_results = search_by_template(room_name_templ)
                    if room_name_results:
                        try:
                            room_id = get_link_content_data(room_name_results[0].get("_room_name_link"))
                            if room_id:
                                break
                        except:
                            continue
        
        # Получаем состояние устройства (is_on / is_off)
        power = False
        # Проверяем is_on
        on_templ = ScTemplate()
        on_templ.triple(
            ScKeynodes.resolve("is_on", sc_type.CONST_NODE),
            sc_type.VAR_PERM_POS_ARC,
            device_node
        )
        on_results = search_by_template(on_templ)
        if on_results:
            power = True
        else:
            # Проверяем is_off
            off_templ = ScTemplate()
            off_templ.triple(
                ScKeynodes.resolve("is_off", sc_type.CONST_NODE),
                sc_type.VAR_PERM_POS_ARC,
                device_node
            )
            off_results = search_by_template(off_templ)
            if off_results:
                power = False
        
        # Дополнительно: проверяем через состояние "state"
        if not on_results and not off_results:
            state_templ = ScTemplate()
            state_templ.triple(
                device_node,
                sc_type.VAR_PERM_POS_ARC,
                (sc_type.VAR_NODE, "_state")
            )
            state_results = search_by_template(state_templ)
            for state_res in state_results:
                state_node = state_res.get("_state")
                try:
                    state_sys_id = get_element_system_identifier(state_node)
                    if state_sys_id == "is_on":
                        power = True
                        break
                    elif state_sys_id == "is_off":
                        power = False
                        break
                except:
                    continue
        
        devices.append({
            "id": str(device_id),
            "name": str(device_name),
            "type": str(device_type),
            "roomId": str(room_id),
            "power": power,
            "icon": "plug",
            "customIcon": None
        })
        
        print(f"  📱 Устройство {i+1}: {device_name} (ID: {device_id}, тип: {device_type}, комната: {room_id}, состояние: {'ВКЛ' if power else 'ВЫКЛ'})")
    
    return devices


def get_all_rooms_data() -> List[Dict]:
    templ = ScTemplate()
    templ.triple(
        ScKeynodes.resolve("concept_room", sc_type.CONST_NODE_CLASS),
        sc_type.VAR_PERM_POS_ARC,
        (sc_type.VAR_NODE, "_room")
    )
    
    # Ищем ID комнаты разными способами
    templ.quintuple(
        "_room",
        sc_type.VAR_COMMON_ARC,
        (sc_type.VAR_NODE_LINK, "_room_id"),
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_id", sc_type.CONST_NODE_NON_ROLE)
    )
    
    # Ищем имя комнаты разными способами
    templ.quintuple(
        "_room",
        sc_type.VAR_COMMON_ARC,
        (sc_type.VAR_NODE_LINK, "_room_idtf"),
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_main_idtf", sc_type.CONST_NODE_NON_ROLE)
    )
    
    search_results = search_by_template(templ)
    data = []
    
    print(f"🔍 Найдено комнат: {len(search_results)}")
    
    for i, result in enumerate(search_results):
        room = result.get("_room")
        
        # Получаем ID комнаты
        room_id = ""
        try:
            room_id = get_link_content_data(result.get("_room_id"))
        except:
            pass
            
        if not room_id:
            try:
                room_id = get_link_content_data(result.get("_room_idtf"))
            except:
                room_id = f"room_{i}"
        
        # Получаем имя комнаты
        room_name = f"Комната {i+1}"
        try:
            room_name = get_link_content_data(result.get("_room_idtf"))
        except:
            pass
            
        # Если не нашли имя, пробуем другие способы
        if room_name == f"Комната {i+1}":
            name_patterns = [
                ("nrel_name", sc_type.CONST_NODE_NON_ROLE),
                ("nrel_user", sc_type.CONST_NODE_NON_ROLE),
            ]
            
            for rel_name, rel_type in name_patterns:
                name_templ = ScTemplate()
                name_templ.quintuple(
                    room,
                    sc_type.VAR_COMMON_ARC,
                    (sc_type.VAR_NODE_LINK, "_name_link"),
                    sc_type.VAR_PERM_POS_ARC,
                    ScKeynodes.resolve(rel_name, rel_type)
                )
                name_results = search_by_template(name_templ)
                if name_results:
                    try:
                        room_name = get_link_content_data(name_results[0].get("_name_link"))
                        break
                    except:
                        continue
        
        # Получаем измерения (температура, влажность, CO2)
        templ = ScTemplate()
        templ.quintuple(
            (sc_type.VAR_NODE, "_measurements"),
            sc_type.ACTUAL_TEMP_POS_ARC,
            "_room",
            sc_type.VAR_PERM_POS_ARC,
            ScKeynodes.resolve("rrel_current_measurement", sc_type.CONST_NODE_ROLE)
        )
        templ.quintuple(
            "_measurements",
            sc_type.VAR_COMMON_ARC,
            (sc_type.VAR_NODE_LINK, "_temp_link"),
            sc_type.VAR_PERM_POS_ARC,
            ScKeynodes.resolve("nrel_temp", sc_type.CONST_NODE_NON_ROLE)
        )
        templ.quintuple(
            "_measurements",
            sc_type.VAR_COMMON_ARC,
            (sc_type.VAR_NODE_LINK, "_hum_link"),
            sc_type.VAR_PERM_POS_ARC,
            ScKeynodes.resolve("nrel_hum", sc_type.CONST_NODE_NON_ROLE)
        )
        templ.quintuple(
            "_measurements",
            sc_type.VAR_COMMON_ARC,
            (sc_type.VAR_NODE_LINK, "_co2_link"),
            sc_type.VAR_PERM_POS_ARC,
            ScKeynodes.resolve("nrel_co2", sc_type.CONST_NODE_NON_ROLE)
        )
        search_results_meas = search_by_template(templ)
        
        temp = 22.0 + random.uniform(-2, 2)
        hum = 50 + random.uniform(-10, 10)
        co2 = 400 + random.uniform(-50, 50)
        
        if search_results_meas: 
            try:
                temp = float(get_link_content_data(search_results_meas[0].get("_temp_link")))
                hum = float(get_link_content_data(search_results_meas[0].get("_hum_link")))
                co2 = float(get_link_content_data(search_results_meas[0].get("_co2_link")))
            except:
                pass
        
        # Получаем устройства в комнате
        templ = ScTemplate()
        templ.quintuple(
            (sc_type.VAR_NODE, "_device"),
            sc_type.VAR_PERM_POS_ARC,
            room,
            sc_type.VAR_PERM_POS_ARC,
            ScKeynodes.resolve("rrel_located_at", sc_type.CONST_NODE_ROLE)
        )
        templ.triple(
            ScKeynodes.resolve("concept_device", sc_type.CONST_NODE_CLASS),
            sc_type.VAR_PERM_POS_ARC,
            "_device"
        )
        
        # Ищем ID устройства
        templ.quintuple(
            "_device",
            sc_type.VAR_COMMON_ARC,
            (sc_type.VAR_NODE_LINK, "_device_id"),
            sc_type.VAR_PERM_POS_ARC,
            ScKeynodes.resolve("nrel_id", sc_type.CONST_NODE_NON_ROLE)
        )
        
        another_search_results = search_by_template(templ)
        devices = []
        
        for res in another_search_results:
            try:
                device_id = get_link_content_data(res.get("_device_id"))
                if device_id:
                    devices.append(device_id)
            except:
                continue
        
        data.append(
            {
                "id": str(room_id),
                "name": str(room_name),
                "devices": devices,
                "temp": float(temp),
                "hum": float(hum),
                "co2": float(co2)
            }
        )
        
        print(f"  🏠 Комната {i+1}: {room_name} (ID: {room_id}, устройств: {len(devices)})")
    
    return data


def get_all_device_types_data() -> List[Dict]:
    print("🔍 Поиск типов устройств...")
    
    templ = ScTemplate()
    templ.triple(
        ScKeynodes.resolve("concept_device_type", sc_type.CONST_NODE_CLASS),
        sc_type.VAR_PERM_POS_ARC,
        (sc_type.VAR_NODE, "_device_type")
    )
    
    # Ищем русское название
    templ.quintuple(
        "_device_type",
        sc_type.VAR_COMMON_ARC,
        (sc_type.VAR_NODE_LINK, "_ru_idtf"),
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_main_idtf", sc_type.CONST_NODE_NON_ROLE)
    )
    
    search_results = search_by_template(templ)
    data = []
    
    print(f"🔍 Найдено типов устройств: {len(search_results)}")
    
    for i, result in enumerate(search_results):
        device_type = result.get("_device_type")
        
        # Получаем русское название
        device_ru_idtf = f"Тип устройства {i+1}"
        try:
            device_ru_idtf = get_link_content_data(result.get("_ru_idtf"))
        except:
            pass
        
        # Получаем английское название из системного идентификатора
        device_en_idtf = f"device_type_{i+1}"
        try:
            sys_id = get_element_system_identifier(device_type)
            if sys_id and "concept_" in sys_id:
                device_en_idtf = sys_id.split("concept_")[1]
        except:
            pass
        
        # Ищем состояния, которые может исправлять устройство
        fixes = []
        templ = ScTemplate()
        templ.quintuple(
            device_type,
            sc_type.VAR_PERM_POS_ARC,
            (sc_type.VAR_NODE, "_state"),
            sc_type.VAR_PERM_POS_ARC,
            ScKeynodes.resolve("rrel_fixes_state", sc_type.VAR_NODE_ROLE)
        )
        another_search_results = search_by_template(templ)
        
        for res in another_search_results:
            try:
                state_node = res.get("_state")
                state_sys_id = get_element_system_identifier(state_node)
                if state_sys_id and "concept_" in state_sys_id:
                    fixes.append(state_sys_id.split("concept_")[1])
            except:
                continue
        
        # Ищем состояния, которые может вызывать устройство
        causes = []
        templ = ScTemplate()
        templ.quintuple(
            device_type,
            sc_type.VAR_PERM_POS_ARC,
            (sc_type.VAR_NODE, "_state"),
            sc_type.VAR_PERM_POS_ARC,
            ScKeynodes.resolve("rrel_causes_state", sc_type.VAR_NODE_ROLE)
        )
        another_search_results = search_by_template(templ)
        
        for res in another_search_results:
            try:
                state_node = res.get("_state")
                state_sys_id = get_element_system_identifier(state_node)
                if state_sys_id and "concept_" in state_sys_id:
                    causes.append(state_sys_id.split("concept_")[1])
            except:
                continue
        
        data.append(
            {
                "nameEn": str(device_en_idtf),
                "nameRu": str(device_ru_idtf),
                "fixes": fixes,
                "causes": causes
            }
        )
        
        print(f"  🔧 Тип {i+1}: {device_ru_idtf} ({device_en_idtf})")
    
    return data


def get_all_scenario_data() -> List[Dict]:
    print("🔍 Поиск сценариев...")
    
    templ = ScTemplate()
    templ.triple(
        ScKeynodes.resolve("concept_scenario", sc_type.CONST_NODE_CLASS),
        sc_type.VAR_PERM_POS_ARC,
        (sc_type.VAR_NODE, "_scenario")
    )
    
    # Ищем ID сценария
    templ.quintuple(
        "_scenario",
        sc_type.VAR_COMMON_ARC,
        (sc_type.VAR_NODE_LINK, "_id"),
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_id", sc_type.CONST_NODE_NON_ROLE)
    )
    
    # Ищем название сценария
    templ.quintuple(
        "_scenario",
        sc_type.VAR_COMMON_ARC,
        (sc_type.VAR_NODE_LINK, "_name"),
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_main_idtf", sc_type.CONST_NODE_NON_ROLE)
    )
    
    # Ищем время начала
    templ.quintuple(
        "_scenario",
        sc_type.VAR_COMMON_ARC,
        (sc_type.VAR_NODE_LINK, "_start_time"),
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_start_time", sc_type.CONST_NODE_NON_ROLE)
    )
    
    # Ищем время окончания
    templ.quintuple(
        "_scenario",
        sc_type.VAR_COMMON_ARC,
        (sc_type.VAR_NODE_LINK, "_finish_time"),
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_finish_time", sc_type.CONST_NODE_NON_ROLE)
    )

    search_results = search_by_template(templ)
    data = []
    
    print(f"🔍 Найдено сценариев: {len(search_results)}")
    
    for i, result in enumerate(search_results):
        scenario = result.get("_scenario")
        
        # Получаем данные сценария с обработкой ошибок
        id_val = f"scenario_{i+1}"
        name_val = f"Сценарий {i+1}"
        start_time_val = "08:00"
        finish_time_val = "22:00"
        
        try:
            id_val = get_link_content_data(result.get("_id"))
        except:
            pass
            
        try:
            name_val = get_link_content_data(result.get("_name"))
        except:
            pass
            
        try:
            start_time_val = get_link_content_data(result.get("_start_time"))
        except:
            pass
            
        try:
            finish_time_val = get_link_content_data(result.get("_finish_time"))
        except:
            pass
        
        # Получаем инструкции сценария
        temp = 22.0
        hum = 50.0
        room_id = ""
        
        templ = ScTemplate()
        templ.quintuple(
            scenario,
            sc_type.VAR_COMMON_ARC,
            (sc_type.VAR_NODE, "_instructions_set"),
            sc_type.VAR_PERM_POS_ARC,
            ScKeynodes.resolve("nrel_instructions", sc_type.CONST_NODE_ROLE)
        )
        templ.triple(
            "_instructions_set",
            sc_type.VAR_PERM_POS_ARC,
            (sc_type.VAR_NODE, "_instruction")
        )
        templ.quintuple(
            "_instruction",
            sc_type.VAR_COMMON_ARC,
            (sc_type.VAR_NODE_LINK, "_temp"),
            sc_type.VAR_PERM_POS_ARC,
            ScKeynodes.resolve("nrel_temp", sc_type.CONST_NODE_NON_ROLE)
        )
        templ.quintuple(
            "_instruction",
            sc_type.VAR_COMMON_ARC,
            (sc_type.VAR_NODE_LINK, "_hum"),
            sc_type.VAR_PERM_POS_ARC,
            ScKeynodes.resolve("nrel_hum", sc_type.CONST_NODE_NON_ROLE)
        )
        templ.quintuple(
            "_instruction",
            sc_type.VAR_COMMON_ARC,
            (sc_type.VAR_NODE, "_room"),
            sc_type.VAR_PERM_POS_ARC,
            ScKeynodes.resolve("nrel_room", sc_type.CONST_NODE_NON_ROLE)
        )
        templ.triple(
            ScKeynodes.resolve("concept_room", sc_type.CONST_NODE_CLASS),
            sc_type.VAR_PERM_POS_ARC,
            "_room"
        )
        templ.quintuple(
            "_room",
            sc_type.VAR_COMMON_ARC,
            (sc_type.VAR_NODE_LINK, "_room_id"),
            sc_type.VAR_PERM_POS_ARC,
            ScKeynodes.resolve("nrel_id", sc_type.CONST_NODE_NON_ROLE)
        )
        
        another_results = search_by_template(templ)
        
        if another_results:
            try:
                temp = float(get_link_content_data(another_results[0].get("_temp")))
            except:
                pass
                
            try:
                hum = float(get_link_content_data(another_results[0].get("_hum")))
            except:
                pass
                
            try:
                room_id = get_link_content_data(another_results[0].get("_room_id"))
            except:
                pass
        
        data.append(
            {
                "id": str(id_val),
                "name": str(name_val),
                "roomId": str(room_id),
                "temp": float(temp),
                "hum": float(hum),
                "startTime": str(start_time_val),
                "endTime": str(finish_time_val)
            }
        )
        
        print(f"  📝 Сценарий {i+1}: {name_val} (ID: {id_val})")
    
    return data


def get_preferences() -> Dict:
    print("🔍 Поиск предпочтений пользователя...")
    
    templ = ScTemplate()
    user = ScKeynodes.resolve("misha", sc_type.CONST_NODE)
    
    # Если пользователь не найден, возвращаем значения по умолчанию
    if not user.is_valid():
        print("⚠️ Пользователь 'misha' не найден")
        return {
            "tempMin": 18.0,
            "tempMax": 24.0,
            "humMin": 40,
            "humMax": 60
        }
    
    templ.quintuple(
        user,
        sc_type.VAR_COMMON_ARC,
        (sc_type.VAR_NODE, "_prefs"),
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_prefs", sc_type.CONST_NODE_NON_ROLE)
    )
    templ.quintuple(
        "_prefs",
        sc_type.VAR_COMMON_ARC,
        (sc_type.VAR_NODE, "_temp_range"),
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_temp_range", sc_type.CONST_NODE_NON_ROLE)
    )
    templ.quintuple(
        "_temp_range",
        sc_type.VAR_COMMON_ARC,
        (sc_type.VAR_NODE_LINK, "_temp_min"),
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_min", sc_type.CONST_NODE_NON_ROLE)
    )
    templ.quintuple(
        "_temp_range",
        sc_type.VAR_COMMON_ARC,
        (sc_type.VAR_NODE_LINK, "_temp_max"),
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_max", sc_type.CONST_NODE_NON_ROLE)
    )
    templ.quintuple(
        "_prefs",
        sc_type.VAR_COMMON_ARC,
        (sc_type.VAR_NODE, "_hum_range"),
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_humidity_range", sc_type.CONST_NODE_NON_ROLE)
    )
    templ.quintuple(
        "_hum_range",
        sc_type.VAR_COMMON_ARC,
        (sc_type.VAR_NODE_LINK, "_hum_min"),
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_min", sc_type.CONST_NODE_NON_ROLE)
    )
    templ.quintuple(
        "_hum_range",
        sc_type.VAR_COMMON_ARC,
        (sc_type.VAR_NODE_LINK, "_hum_max"),
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_max", sc_type.CONST_NODE_NON_ROLE)
    )

    search_results = search_by_template(templ)
    
    if not search_results:
        print("⚠️ Предпочтения пользователя не найдены")
        return {
            "tempMin": 18.0,
            "tempMax": 24.0,
            "humMin": 40,
            "humMax": 60
        }
    
    try:
        temp_min = float(get_link_content_data(search_results[0].get("_temp_min")))
        temp_max = float(get_link_content_data(search_results[0].get("_temp_max")))
        hum_min = float(get_link_content_data(search_results[0].get("_hum_min")))
        hum_max = float(get_link_content_data(search_results[0].get("_hum_max")))
        
        print(f"✅ Найдены предпочтения: t={temp_min}-{temp_max}°C, h={hum_min}-{hum_max}%")
        
        return {
            "tempMin": temp_min,
            "tempMax": temp_max,
            "humMin": hum_min,
            "humMax": hum_max
        }
    except Exception as e:
        print(f"⚠️ Ошибка при получении предпочтений: {e}")
        return {
            "tempMin": 18.0,
            "tempMax": 24.0,
            "humMin": 40,
            "humMax": 60
        }


def get_all_data() -> Dict:
    print("🚀 Начало загрузки всех данных...")
    
    try:
        devices = get_all_device_data()
    except Exception as e:
        print(f"❌ Ошибка при получении устройств: {e}")
        devices = []
    
    try:
        rooms = get_all_rooms_data()
    except Exception as e:
        print(f"❌ Ошибка при получении комнат: {e}")
        rooms = []
    
    try:
        device_types = get_all_device_types_data()
    except Exception as e:
        print(f"❌ Ошибка при получении типов устройств: {e}")
        device_types = []
    
    try:
        scenarios = get_all_scenario_data()
    except Exception as e:
        print(f"❌ Ошибка при получении сценариев: {e}")
        scenarios = []
    
    try:
        prefs = get_preferences()
    except Exception as e:
        print(f"❌ Ошибка при получении предпочтений: {e}")
        prefs = {
            "tempMin": 18.0,
            "tempMax": 24.0,
            "humMin": 40,
            "humMax": 60
        }
    
    result = {
        "rooms": rooms,
        "devices": devices,
        "deviceTypes": device_types,
        "scenarios": scenarios,
        "preferences": prefs
    }
    
    print(f"✅ Данные успешно загружены:")
    print(f"   Комнаты: {len(rooms)}")
    print(f"   Устройства: {len(devices)}")
    print(f"   Типы устройств: {len(device_types)}")
    print(f"   Сценарии: {len(scenarios)}")
    
    return result