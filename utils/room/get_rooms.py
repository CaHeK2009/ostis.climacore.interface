from typing import List
from sc_client.client import generate_elements, search_links_by_contents, search_by_template, erase_elements, generate_by_template, search_by_template
from sc_client.constants import sc_type
from sc_client.models import ScLinkContent, ScLinkContentType, ScConstruction, ScTemplate, ScAddr
from sc_kpm import ScKeynodes
from sc_kpm.utils import get_link_content_data
import random


def get_rooms(house: ScAddr) -> List[ScAddr]:
    templ = ScTemplate()
    templ.quintuple(
        house,
        sc_type.VAR_COMMON_ARC,
        (sc_type.VAR_NODE, "_room_set"),
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_rooms", sc_type.CONST_NODE_NON_ROLE)
    )
    templ.triple(
        "_room_set",
        sc_type.VAR_PERM_POS_ARC,
        (sc_type.VAR_NODE, "_room")
    )
    templ.triple(
        ScKeynodes.resolve("concept_room", sc_type.CONST_NODE_CLASS),
        sc_type.VAR_PERM_POS_ARC,
        "_room"
    )
    search_results = search_by_template(templ)
    rooms = []
    for result in search_results: rooms.append(result.get("_room"))
    return rooms