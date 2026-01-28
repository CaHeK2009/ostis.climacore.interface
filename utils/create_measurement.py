from typing import List
from sc_client.client import generate_elements, search_links_by_contents, search_by_template, erase_elements, generate_by_template, search_by_template
from sc_client.constants import sc_type
from sc_client.models import ScLinkContent, ScLinkContentType, ScConstruction, ScTemplate, ScAddr
from sc_kpm import ScKeynodes
from sc_kpm.utils import get_link_content_data
import random


def delete_previous_measurement(measurement: ScAddr) -> None:
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
    if not search_results: return None
    erase_elements(
        search_results[0].get("_temp_link"),
        search_results[0].get("_hum_link"),
        search_results[0].get("_co2_link")
    )
    return None



def create_measurement(room_id: str, temp: float, hum: float, co2: float) -> None:
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
        ScKeynodes.resolve("concept_room", sc_type.VAR_NODE_CLASS),
        sc_type.VAR_PERM_POS_ARC,
        "_room"
    )
    search_results = search_by_template(templ)
    room_node = ScAddr(0)
    for result in search_results:
        searched_id = get_link_content_data(result.get("_id"))
        if room_id == searched_id:
            room_node = result.get("_room")
            break
    if room_node == ScAddr(0): return False

    templ = ScTemplate()
    templ.quintuple(
        (sc_type.VAR_NODE, "_measurements"),
        sc_type.ACTUAL_TEMP_POS_ARC,
        room_node,
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("rrel_current_measurement", sc_type.CONST_NODE_ROLE)
    )

    search_results = search_by_template(templ)
    measurement_node = ScAddr(0)
    if search_results: measurement_node = search_results[0].get("_measurements")
    temp_link = generate_link_with_content(temp, ScLinkContentType.FLOAT)
    hum_link = generate_link_with_content(hum, ScLinkContentType.FLOAT)
    co2_link = generate_link_with_content(co2, ScLinkContentType.FLOAT)
    if measurement_node != ScAddr(0): delete_previous_measurement(measurement_node)
    templ = ScTemplate()
    if measurement_node == ScAddr(0):
        templ = ScTemplate()
        templ.quintuple(
            (sc_type.VAR_NODE, "_measurements"),
            sc_type.ACTUAL_TEMP_POS_ARC,
            room_node,
            sc_type.VAR_PERM_POS_ARC,
            ScKeynodes.resolve("rrel_current_measurement", sc_type.CONST_NODE_ROLE)
        )

        generation_results = generate_by_template(templ)
        measurement_node = generation_results.get("_measurements")

    templ.quintuple(
        measurement_node,
        sc_type.VAR_COMMON_ARC,
        temp_link,
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_temp", sc_type.CONST_NODE_NON_ROLE)
    )
    templ.quintuple(
        measurement_node,
        sc_type.VAR_COMMON_ARC,
        hum_link,
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_hum", sc_type.CONST_NODE_NON_ROLE)
    )
    templ.quintuple(
        measurement_node,
        sc_type.VAR_COMMON_ARC,
        co2_link,
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_co2", sc_type.CONST_NODE_NON_ROLE)
    )
    return None
