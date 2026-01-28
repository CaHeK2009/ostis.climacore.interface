import json
from sc_client.client import generate_elements, search_links_by_contents, search_by_template, erase_elements, generate_by_template, search_by_template
from sc_client.constants import sc_type
from sc_client.models import ScLinkContent, ScLinkContentType, ScConstruction, ScTemplate, ScAddr
from sc_kpm import ScKeynodes
from sc_kpm.utils import get_link_content_data, get_element_system_identifier
import random
from sc_client.client import connect
from typing import Dict, List


def get_all_device_data() -> List[Dict]:
    templ = ScTemplate()
    templ.triple(
        ScKeynodes.resolve("concept_device", sc_type.CONST_NODE_CLASS),
        sc_type.VAR_PERM_POS_ARC,
        (sc_type.VAR_NODE, "_device")
    )
    templ.quintuple(
        "_device",
        sc_type.VAR_COMMON_ARC,
        (sc_type.VAR_NODE_LINK, "_id"),
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_id", sc_type.CONST_NODE_NON_ROLE)
    )
    templ.triple(
        (sc_type.VAR_NODE_CLASS, "_device_type"),
        sc_type.VAR_PERM_POS_ARC,
        "_device"
    )
    templ.triple(
        ScKeynodes.resolve("concept_device_type", sc_type.CONST_NODE_CLASS),
        sc_type.VAR_PERM_POS_ARC,
        "_device_type"
    )
    templ.quintuple(
        "_device_type",
        sc_type.VAR_COMMON_ARC,
        (sc_type.VAR_NODE_LINK, "_device_type_name"),
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_main_idtf", sc_type.CONST_NODE_NON_ROLE)
    )
    templ.quintuple(
        "_device_type",
        sc_type.VAR_COMMON_ARC,
        (sc_type.VAR_NODE_LINK, "_device_type_id"),
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_id", sc_type.CONST_NODE_NON_ROLE)
    )
    templ.triple(
        (sc_type.VAR_NODE, "_device_state"),
        sc_type.VAR_PERM_POS_ARC,
        "_device"
    )
    templ.triple(
        ScKeynodes.resolve("concept_device_state", sc_type.CONST_NODE_CLASS),
        sc_type.VAR_PERM_POS_ARC,
        "_device_state"
    )
    templ.quintuple(
        "_device",
        sc_type.VAR_PERM_POS_ARC,
        (sc_type.VAR_NODE, "_room"),
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("rrel_located_at", sc_type.CONST_NODE_ROLE)
    )
    templ.triple(
        ScKeynodes.resolve("concept_room", sc_type.CONST_NODE_ROLE),
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
    search_results = search_by_template(templ)
    res = []
    for result in search_results:
        device_id = get_link_content_data(result.get("_id"))
        device_type_name = get_link_content_data(result.get("_device_type_name"))
        device_type_id = get_element_system_identifier(result.get("_device_type")).split("concept_")[1]
        room_id = get_link_content_data(result.get("_room_id"))
        power = False
        if result.get("_device_state") == ScKeynodes.resolve("is_on", sc_type.CONST_NODE): power = True
        res.append(
            {
                "id": device_id,
                "name": device_type_name,
                "type": device_type_id,
                "roomId": room_id,
                "power": power,
                "icon": "fan",
                "customIcon": None
            }
        )
    return res


def get_all_rooms_data() -> List[Dict]:
    templ = ScTemplate()
    templ.triple(
        ScKeynodes.resolve("concept_room", sc_type.CONST_NODE_CLASS),
        sc_type.VAR_PERM_POS_ARC,
        (sc_type.VAR_NODE, "_room")
    )
    templ.quintuple(
        "_room",
        sc_type.VAR_COMMON_ARC,
        (sc_type.VAR_NODE_LINK, "_room_id"),
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_id", sc_type.CONST_NODE_NON_ROLE)
    )
    templ.quintuple(
        "_room",
        sc_type.VAR_COMMON_ARC,
        (sc_type.VAR_NODE_LINK, "_room_idtf"),
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_main_idtf", sc_type.CONST_NODE_NON_ROLE)
    )
    search_results = search_by_template(templ)
    data = []
    for result in search_results:
        room = result.get("_room")
        room_id = get_link_content_data(result.get("_room_id"))
        room_name = get_link_content_data(result.get("_room_idtf"))
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
            device_id = get_link_content_data(res.get("_device_id"))
            devices.append(device_id)
        data.append(
            {
                "id": room_id,
                "name": room_name,
                "devices": devices
            }
        )
    return data
    
    

def get_all_device_types_data() -> List[Dict]:
    templ = ScTemplate()
    templ.triple(
        ScKeynodes.resolve("concept_device_type", sc_type.CONST_NODE_CLASS),
        sc_type.VAR_PERM_POS_ARC,
        (sc_type.VAR_NODE, "_device_type")
    )
    templ.quintuple(
        "_device_type",
        sc_type.VAR_COMMON_ARC,
        (sc_type.VAR_NODE_LINK, "_ru_idtf"),
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_main_idtf", sc_type.CONST_NODE_NON_ROLE)
    )
    search_results = search_by_template(templ)
    data = []
    for result in search_results:
        device_type = result.get("_device_type")
        device_ru_idtf = get_link_content_data(result.get("_ru_idtf"))
        device_en_idtf = get_element_system_identifier(device_type).split("concept_")[1]
        templ = ScTemplate()
        templ.quintuple(
            device_type,
            sc_type.VAR_PERM_POS_ARC,
            (sc_type.VAR_NODE, "_state"),
            sc_type.VAR_PERM_POS_ARC,
            ScKeynodes.resolve("rrel_fixes_state", sc_type.VAR_NODE_ROLE)
        )
        another_search_results = search_by_template(templ)
        fixes = []
        for res in another_search_results: fixes.append(get_element_system_identifier(res.get("_state")).split("concept_")[1])
        templ = ScTemplate()
        templ.quintuple(
            device_type,
            sc_type.VAR_PERM_POS_ARC,
            (sc_type.VAR_NODE, "_state"),
            sc_type.VAR_PERM_POS_ARC,
            ScKeynodes.resolve("rrel_causes_state", sc_type.VAR_NODE_ROLE)
        )
        another_search_results = search_by_template(templ)
        causes = []
        for res in another_search_results: causes.append(get_element_system_identifier(res.get("_state")).split("concept_")[1])
        data.append(
            {
                "nameEn": device_en_idtf,
                "nameRu": device_ru_idtf,
                "fixes": fixes,
                "causes": causes
            }
        )
    return data


def get_all_scenario_data() -> List[Dict]:
    templ = ScTemplate()
    templ.triple(
        ScKeynodes.resolve("concept_scenario", sc_type.CONST_NODE_CLASS),
        sc_type.VAR_PERM_POS_ARC,
        (sc_type.VAR_NODE, "_scenario")
    )
    templ.quintuple(
        "_scenario",
        sc_type.VAR_COMMON_ARC,
        (sc_type.VAR_NODE_LINK, "_id"),
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_id", sc_type.CONST_NODE_NON_ROLE)
    )
    templ.quintuple(
        "_scenario",
        sc_type.VAR_COMMON_ARC,
        (sc_type.VAR_NODE_LINK, "_name"),
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_main_idtf", sc_type.CONST_NODE_NON_ROLE)
    )
    templ.quintuple(
        "_scenario",
        sc_type.VAR_COMMON_ARC,
        (sc_type.VAR_NODE_LINK, "_start_time"),
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_start_time", sc_type.CONST_NODE_NON_ROLE)
    )
    templ.quintuple(
        "_scenario",
        sc_type.VAR_COMMON_ARC,
        (sc_type.VAR_NODE_LINK, "_finish_time"),
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_finish_time", sc_type.CONST_NODE_NON_ROLE)
    )

    search_results = search_by_template(templ)
    data = []
    for result in search_results:
        scenario = result.get("_scenario")
        id = get_link_content_data(result.get("_id"))
        name = get_link_content_data(result.get("_name"))
        start_time = get_link_content_data(result.get("_start_time"))
        finish_time = get_link_content_data(result.get("_finish_time"))
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
        another_result = search_by_template(templ)[0]
        if not search_results: return []
        temp = get_link_content_data(another_result.get("_temp"))
        hum = get_link_content_data(another_result.get("_hum"))
        room_id = get_link_content_data(another_result.get("_room_id"))
        data.append(
            {
                "id": id,
                "name": name,
                "roomId": room_id,
                "temp": float(temp),
                "hum": float(hum),
                "startTime": start_time,
                "endTime": finish_time
            }
        )
    return data





def get_all_data() -> json:
    devices = get_all_device_data()
    rooms = get_all_rooms_data()
    device_types = get_all_device_types_data()
    scenarios = get_all_scenario_data()
    result = {
        "rooms": rooms,
        "devices": devices,
        "deviceTypes": device_types,
        "scenarios": scenarios
    }
    json_ = json.dumps(result, ensure_ascii=False, indent=2)
    print(json_)
    return json_
