from sc_client.client import generate_elements, search_links_by_contents, search_by_template, erase_elements, generate_by_template, search_by_template
from sc_client.constants import sc_type
from sc_client.models import ScLinkContent, ScLinkContentType, ScConstruction, ScTemplate, ScAddr
from sc_kpm import ScKeynodes
from sc_kpm.utils import get_link_content_data
import random

def change_device_state(device_id: str, is_on: bool = True) -> None:
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
    if device_node == ScAddr(0): return None

    templ = ScTemplate()
    templ.triple(
        ScKeynodes.resolve("concept_device_state", sc_type.CONST_NODE_CLASS),
        sc_type.VAR_PERM_POS_ARC,
        (sc_type.VAR_NODE, "_state")
    )
    templ.triple(
        "_state",
        (sc_type.VAR_PERM_POS_ARC, "_arc"),
        device_node
    )
    search_results = search_by_template(templ)
    if search_results: erase_elements(search_results[0].get("_arc"))
    templ = ScTemplate()
    if is_on:
        templ.triple(
            ScKeynodes.resolve("is_on", sc_type.CONST_NODE),
            sc_type.VAR_PERM_POS_ARC,
            device_node
        )
    else:
        templ.triple(
            ScKeynodes.resolve("is_off", sc_type.CONST_NODE),
            sc_type.VAR_PERM_POS_ARC,
            device_node
        )
    generate_by_template(templ)
    return None