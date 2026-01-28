from sc_client.constants import sc_type
from sc_client.models import ScConstruction, ScAddr
from sc_client.client import generate_elements
from sc_kpm.sc_keynodes import ScKeynodes


def create_action(action_class_name: str, *args: ScAddr) -> ScAddr:
    
    action_class = ScKeynodes.resolve(action_class_name, sc_type.CONST_NODE_CLASS)
    
    action_initiated = ScKeynodes.resolve("action_initiated", sc_type.CONST_NODE_CLASS)

    action_metaclass = ScKeynodes.resolve("action", sc_type.CONST_NODE_CLASS)


    constr = ScConstruction()
    constr.create_node(sc_type.CONST_NODE, "action_node")

    constr.create_edge(
        sc_type.CONST_PERM_POS_ARC,  
        action_class,                
        "action_node",               
        "class_edge"                 
    )

    constr.create_edge(
        sc_type.CONST_PERM_POS_ARC,
        action_metaclass,            
        "action_node",               
        "meta_edge"                  
    )
    if args:  
        for i, arg in enumerate(args):
            arc_alias = f"arg_arc_{i+1}"
            
            constr.create_edge(
                sc_type.CONST_PERM_POS_ARC,
                "action_node",      
                arg,                
                arc_alias           
            )
            
            rrel_alias = f"rrel_edge_{i+1}"
            
            constr.create_edge(
                sc_type.CONST_PERM_POS_ARC,
                ScKeynodes.rrel_index(i + 1),  
                arc_alias,                     
                rrel_alias                     
            )

    constr.create_edge(
        sc_type.CONST_PERM_POS_ARC,
        action_initiated,           
        "action_node",              
        "initiated_edge"            
    ) 
    result = generate_elements(constr)
    
    return result[0]  
