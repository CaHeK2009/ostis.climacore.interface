from sc_client.client import generate_elements, search_links_by_contents, search_by_template, erase_elements
from sc_client.constants import sc_type
from sc_client.models import ScLinkContent, ScLinkContentType, ScConstruction, ScTemplate
from sc_kpm import ScKeynodes

def delete_device_by_id(id: str) -> bool:
    construction = ScConstruction()  
    link_content1 = ScLinkContent(id, ScLinkContentType.STRING)
    construction.generate_link(sc_type.CONST_NODE_LINK, link_content1)
    links = search_links_by_contents(id)[0]
    if len(links) != 1: return False
    link = links[0]
    templ = ScTemplate()
    templ.triple(
        ScKeynodes.resolve("concept_device", sc_type.VAR_NODE),
        sc_type.VAR_PERM_POS_ARC,
        (sc_type.VAR_NODE, "_device")
    )
    templ.quintuple(
        "_device",
        sc_type.VAR_COMMON_ARC,
        link,
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_id", sc_type.CONST_NODE_NON_ROLE)
    )
    search_results = search_by_template(templ)
    if len(search_results) == 0: return True
    if len(search_results) != 1: return False
    erase_elements(search_results[0].get("_device"))
    return True