from typing import List
from sc_client.client import generate_elements, search_links_by_contents, search_by_template, erase_elements, generate_by_template, search_by_template
from sc_client.constants import sc_type
from sc_client.models import ScLinkContent, ScLinkContentType, ScConstruction, ScTemplate, ScAddr
from sc_kpm import ScKeynodes
from sc_kpm.utils import get_link_content_data
import random


def delete_previous_measurement(measurement: ScAddr) -> None:
    if not measurement.is_valid():
        return
        
    templ = ScTemplate()
    templ.quintuple(
        measurement,
        sc_type.VAR_COMMON_ARC,
        (sc_type.VAR_NODE, "_temp_link"),
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_temp", sc_type.CONST_NODE_NON_ROLE)
    )
    templ.quintuple(
        measurement,
        sc_type.VAR_COMMON_ARC,
        (sc_type.VAR_NODE, "_hum_link"),
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_hum", sc_type.CONST_NODE_NON_ROLE)
    )
    templ.quintuple(
        measurement,
        sc_type.VAR_COMMON_ARC,
        (sc_type.VAR_NODE, "_co2_link"),
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_co2", sc_type.CONST_NODE_NON_ROLE)
    )
    search_results = search_by_template(templ)
    if not search_results: 
        return None
    
    erase_elements(
        search_results[0].get("_temp_link"),
        search_results[0].get("_hum_link"),
        search_results[0].get("_co2_link")
    )
    return None


def create_measurement(room_id: str, temp: float, hum: float, co2: float) -> bool:
    def generate_link_with_content(content, type) -> None:
        construction = ScConstruction()  
        link_content1 = ScLinkContent(content, type)
        construction.generate_link(sc_type.CONST_NODE_LINK, link_content1)
        link = generate_elements(construction)[0]
        return link
    

    templ = ScTemplate()
    templ.quintuple(
        (sc_type.VAR_NODE, "_room"),
        sc_type.VAR_COMMON_ARC,
        (sc_type.VAR_NODE_LINK, "_id"),
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_id", sc_type.CONST_NODE_NON_ROLE)
    )
    templ.triple(
        ScKeynodes.resolve("concept_room", sc_type.CONST_NODE_CLASS),
        sc_type.VAR_PERM_POS_ARC,
        "_room"
    )
    
    search_results = search_by_template(templ)
    room_node = None
    for result in search_results:
        searched_id = get_link_content_data(result.get("_id"))
        if room_id == searched_id:
            room_node = result.get("_room")
            break
    
    if not room_node or not room_node.is_valid():
        return False
    
    templ = ScTemplate()
    templ.quintuple(
        (sc_type.VAR_NODE, "_measurement"),
        sc_type.ACTUAL_TEMP_POS_ARC,
        room_node,
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("rrel_current_measurement", sc_type.CONST_NODE_ROLE)
    )

    search_results = search_by_template(templ)
    measurement_node = None
    if search_results:
        measurement_node = search_results[0].get("_measurement")
        if measurement_node.is_valid():
            delete_previous_measurement(measurement_node)

    temp_link = generate_link_with_content(float(temp), ScLinkContentType.FLOAT)
    hum_link = generate_link_with_content(float(hum), ScLinkContentType.FLOAT)
    co2_link = generate_link_with_content(float(co2), ScLinkContentType.FLOAT)
    
    if not all([temp_link, hum_link, co2_link]):
        return False

    if not measurement_node or not measurement_node.is_valid():
        templ = ScTemplate()
        templ.quintuple(
            (sc_type.VAR_NODE, "_measurement"),
            sc_type.ACTUAL_TEMP_POS_ARC,
            room_node,
            sc_type.VAR_PERM_POS_ARC,
            ScKeynodes.resolve("rrel_current_measurement", sc_type.CONST_NODE_ROLE)
        )
        
        generation_results = generate_by_template(templ)
        measurement_node = generation_results.get("_measurement")
        
        if not measurement_node or not measurement_node.is_valid():
            return False
    
    templ_temp = ScTemplate()
    templ_temp.quintuple(
        measurement_node,
        sc_type.VAR_COMMON_ARC,
        temp_link,
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_temp", sc_type.CONST_NODE_NON_ROLE)
    )
    generate_by_template(templ_temp)
    
    templ_hum = ScTemplate()
    templ_hum.quintuple(
        measurement_node,
        sc_type.VAR_COMMON_ARC,
        hum_link,
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_hum", sc_type.CONST_NODE_NON_ROLE)
    )
    generate_by_template(templ_hum)
    
    templ_co2 = ScTemplate()
    templ_co2.quintuple(
        measurement_node,
        sc_type.VAR_COMMON_ARC,
        co2_link,
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_co2", sc_type.CONST_NODE_NON_ROLE)
    )
    generate_by_template(templ_co2)
    
    return True