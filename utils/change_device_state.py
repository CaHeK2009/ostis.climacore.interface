from sc_client.client import generate_elements, search_links_by_contents, search_by_template, erase_elements, generate_by_template
from sc_client.constants import sc_type
from sc_client.models import ScLinkContent, ScLinkContentType, ScConstruction, ScTemplate, ScAddr
from sc_kpm import ScKeynodes
from sc_kpm.utils import get_link_content_data
import random

def change_device_state(device_id: str, is_on: bool = True) -> None:
    # Ищем устройство по ID
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
    search_results = search_by_template(templ)
    device_node = ScAddr(0)
    for result in search_results:
        searched_id = get_link_content_data(result.get("_id"))
        if device_id == searched_id:
            device_node = result.get("_device")
            break
    if device_node == ScAddr(0): 
        print(f"Device with id {device_id} not found")
        return None

    # Сначала удаляем текущее состояние (если есть)
    # Проверяем, есть ли связь с is_on
    templ = ScTemplate()
    templ.triple(
        ScKeynodes.resolve("is_on", sc_type.CONST_NODE),
        sc_type.VAR_PERM_POS_ARC,
        device_node
    )
    on_results = search_by_template(templ)
    if on_results:
        erase_elements([on_results[0][1]])  # Удаляем дугу
    
    # Проверяем, есть ли связь с is_off
    templ = ScTemplate()
    templ.triple(
        ScKeynodes.resolve("is_off", sc_type.CONST_NODE),
        sc_type.VAR_PERM_POS_ARC,
        device_node
    )
    off_results = search_by_template(templ)
    if off_results:
        erase_elements([off_results[0][1]])  # Удаляем дугу
    
    # Создаем новое состояние
    if is_on:
        constr = ScConstruction()
        constr.create_edge(
            sc_type.CONST_POS_PERM_ARC,
            ScKeynodes.resolve("is_on", sc_type.CONST_NODE),
            device_node
        )
    else:
        constr = ScConstruction()
        constr.create_edge(
            sc_type.CONST_POS_PERM_ARC,
            ScKeynodes.resolve("is_off", sc_type.CONST_NODE),
            device_node
        )
    
    generate_elements(constr)
    print(f"Device {device_id} state changed to {'on' if is_on else 'off'}")
    return None