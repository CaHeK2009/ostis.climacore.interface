from sc_client.client import generate_elements, search_links_by_contents, search_by_template, erase_elements, generate_by_template
from sc_client.constants import sc_type
from sc_client.models import ScLinkContent, ScLinkContentType, ScConstruction, ScTemplate, ScAddr
from sc_kpm import ScKeynodes
from sc_kpm.utils import get_link_content_data
import random

def create_measurement(room_id: str, temp: float, hum: float, co2: float):
    """
    Создает измерение для комнаты
    """
    print(f"Создание измерения для комнаты {room_id}: t={temp}, h={hum}, co2={co2}")
    
    # Проверяем, что co2 не равен 0 или None
    if co2 is None or co2 == 0:
        print(f"⚠️ Внимание: CO₂ равен {co2}, устанавливаю значение по умолчанию 400")
        co2 = 400.0
    
    def generate_link_with_content(content, content_type) -> ScAddr:
        construction = ScConstruction()  
        link_content = ScLinkContent(content, content_type)
        construction.create_link(sc_type.CONST_LINK, link_content)
        return generate_elements(construction)[0]
    
    # Ищем комнату по ID
    templ = ScTemplate()
    templ.triple(
        ScKeynodes.resolve("concept_room", sc_type.CONST_NODE_CLASS),
        sc_type.VAR_PERM_POS_ARC,
        (sc_type.VAR_NODE, "_room")
    )
    templ.quintuple(
        "_room",
        sc_type.VAR_COMMON_ARC,
        (sc_type.VAR_NODE_LINK, "_id"),
        sc_type.VAR_PERM_POS_ARC,
        ScKeynodes.resolve("nrel_id", sc_type.CONST_NODE_NON_ROLE)
    )
    search_results = search_by_template(templ)
    
    room_node = ScAddr(0)
    for result in search_results:
        searched_id = get_link_content_data(result.get("_id"))
        if room_id == searched_id:
            room_node = result.get("_room")
            print(f"Найдена комната: {room_id}")
            break
    
    if room_node == ScAddr(0):
        print(f"❌ Комната с ID {room_id} не найдена")
        return
    
    # Создаем линки с измерениями
    temp_link = generate_link_with_content(float(temp), ScLinkContentType.FLOAT)
    hum_link = generate_link_with_content(float(hum), ScLinkContentType.FLOAT)
    co2_link = generate_link_with_content(float(co2), ScLinkContentType.FLOAT)  # Исправлено: FLOAT для CO₂
    
    # Удаляем старое измерение (если есть)
    templ = ScTemplate()
    templ.triple(
        (sc_type.VAR_NODE, "_measurement"),
        sc_type.ACTUAL_TEMP_POS_ARC,
        room_node
    )
    search_results = search_by_template(templ)
    if search_results:
        for result in search_results:
            measurement_node = result.get("_measurement")
            # Удаляем связи измерения
            erase_elements([measurement_node])
            print(f"Удалено старое измерение для комнаты {room_id}")
    
    # Создаем новое измерение
    constr = ScConstruction()
    constr.create_node(sc_type.CONST_NODE, "_measurement")
    constr.create_edge(
        sc_type.CONST_POS_PERM_ARC,
        ScKeynodes.resolve("concept_measurement", sc_type.CONST_NODE_CLASS),
        "_measurement"
    )
    constr.create_edge(
        sc_type.ACTUAL_TEMP_POS_ARC,
        "_measurement",
        room_node
    )
    constr.create_edge(
        sc_type.CONST_POS_PERM_ARC,
        "_measurement",
        ScKeynodes.resolve("rrel_current_measurement", sc_type.CONST_NODE_ROLE)
    )
    
    # Создаем связи с данными
    constr.create_edge(
        sc_type.CONST_POS_PERM_ARC,
        "_measurement",
        temp_link
    )
    constr.create_edge(
        sc_type.CONST_POS_PERM_ARC,
        temp_link,
        ScKeynodes.resolve("nrel_temp", sc_type.CONST_NODE_NON_ROLE)
    )
    
    constr.create_edge(
        sc_type.CONST_POS_PERM_ARC,
        "_measurement",
        hum_link
    )
    constr.create_edge(
        sc_type.CONST_POS_PERM_ARC,
        hum_link,
        ScKeynodes.resolve("nrel_hum", sc_type.CONST_NODE_NON_ROLE)
    )
    
    constr.create_edge(
        sc_type.CONST_POS_PERM_ARC,
        "_measurement",
        co2_link
    )
    constr.create_edge(
        sc_type.CONST_POS_PERM_ARC,
        co2_link,
        ScKeynodes.resolve("nrel_co2", sc_type.CONST_NODE_NON_ROLE)
    )
    
    generate_elements(constr)
    print(f"✅ Создано измерение для комнаты {room_id}: t={temp}, h={hum}, co2={co2}")