from google.protobuf.descriptor import FieldDescriptor
from pprint import pprint

import kipy.board_types as board_types
from kipy.common_types import *
from kipy.proto.board import board_types_pb2
from kipy.proto.common.types import KiCadObjectType



descriptor_type_map = {
    FieldDescriptor.TYPE_DOUBLE: 'float',
    FieldDescriptor.TYPE_FLOAT: 'float',
    FieldDescriptor.TYPE_INT64: 'int',
    FieldDescriptor.TYPE_UINT64: 'int',
    FieldDescriptor.TYPE_INT32: 'int',
    FieldDescriptor.TYPE_FIXED64: 'float',
    FieldDescriptor.TYPE_FIXED32: 'float',
    FieldDescriptor.TYPE_BOOL: 'bool',
    FieldDescriptor.TYPE_STRING: 'string',
    FieldDescriptor.TYPE_GROUP: 'None',
    FieldDescriptor.TYPE_MESSAGE: 'message',
    FieldDescriptor.TYPE_BYTES: 'bytes',
    FieldDescriptor.TYPE_UINT32: 'int',
    FieldDescriptor.TYPE_ENUM: 'enum',
    FieldDescriptor.TYPE_SFIXED32: 'float',
    FieldDescriptor.TYPE_SFIXED64: 'float',
    FieldDescriptor.TYPE_SINT32: 'int',
    FieldDescriptor.TYPE_SINT64: 'int',
    FieldDescriptor.MAX_TYPE: 'max',
}


WRAPPER_CLASS_OVERRIDES = {
    "Arc": "ArcTrack",
    "BoardGraphicShape": "BoardShape",
}

OBJECT_TYPE_OVERRIDES = {
    "Footprint3DModel": None,
    "FootprintInstance": "KOT_PCB_FOOTPRINT",
    "Net": None,
    "Track": "KOT_PCB_TRACE",
}


def _iter_proto_message_classes():
    for name in board_types_pb2.DESCRIPTOR.message_types_by_name:
        proto_class = getattr(board_types_pb2, name, None)
        if proto_class is None:
            continue
        yield name, proto_class


def _resolve_wrapper_class(type_name: str):
    wrapper_name = WRAPPER_CLASS_OVERRIDES.get(type_name, type_name)
    return getattr(board_types, wrapper_name, None)


def _resolve_object_type(type_name: str):
    override = OBJECT_TYPE_OVERRIDES.get(type_name)
    if override is None and type_name in OBJECT_TYPE_OVERRIDES:
        return None
    if override is not None:
        return getattr(KiCadObjectType, override, None)

    candidate_names = [f"KOT_PCB_{type_name.upper()}"]
    if type_name.startswith("Board"):
        candidate_names.append(f"KOT_PCB_{type_name[5:].upper()}")
    if type_name.startswith("BoardGraphic"):
        candidate_names.append(f"KOT_PCB_{type_name[len('BoardGraphic'):].upper()}")
    if type_name.startswith("Graphic"):
        candidate_names.append(f"KOT_PCB_{type_name[len('Graphic'):].upper()}")

    for candidate in candidate_names:
        if hasattr(KiCadObjectType, candidate):
            return getattr(KiCadObjectType, candidate)

    return None


def build_kicad_type_mapping():
    mapping = {}
    for type_name, proto_class in _iter_proto_message_classes():
        wrapper_class = _resolve_wrapper_class(type_name)
        if wrapper_class is None:
            continue
        mapping[type_name] = {
            "proto_class": proto_class,
            "wrapper_class": wrapper_class,
            "object_type": _resolve_object_type(type_name),
        }
    return mapping


KICAD_TYPE_MAPPING = build_kicad_type_mapping()

def get_proto_class(type_name):
    """Return proto class by string type name"""
    return KICAD_TYPE_MAPPING[type_name]['proto_class']

def get_wrapper_class(type_name):
    """Return wrapper class by string type name"""
    return KICAD_TYPE_MAPPING[type_name]['wrapper_class']

def get_object_type(type_name):
    """Return KiCad object type by string type name"""
    return KICAD_TYPE_MAPPING[type_name]['object_type']

def get_wrapper_from_proto(proto_obj):
    """Find wrapper class from proto object"""
    proto_type = type(proto_obj)
    for type_info in KICAD_TYPE_MAPPING.values():
        if type_info['proto_class'] == proto_type:
            return type_info['wrapper_class']
    return None


def convert_int(value):
    return int(value)
    
def convert_float(value):
    return float(value)

def convert_bool(value):
    return bool(value)

def convert_string(value):
    return str(value)

def convert_enum(enum_descriptor):
    enum_map = {}
    for value in enum_descriptor.values:
        enum_map[value.number] = value.name
    return enum_map

def convert_message(descriptor):
    args_dict = {}
    for field in descriptor.fields:
        args_dict[field.name] = {}
        if field.type == 11:  # FieldDescriptor.TYPE_MESSAGE
            args_dict[field.name][field.message_type.name] = convert_message(field.message_type)
        elif field.type == 14: # FieldDescriptor.TYPE_ENUM
            args_dict[field.name][field.enum_type.name] = convert_enum(field.enum_type)
        else:
            args_dict[field.name]['base_type'] = descriptor_type_map[field.type]
    return args_dict


def convert_proto_to_dict():
    """
    Convert a protobuf message to a dictionary representation.
    
    Args:
        proto_message: A protobuf message instance.
        
    Returns:
        dict: A dictionary representation of the protobuf message.
    """
    result = {}
    for name, message_class in KICAD_TYPE_MAPPING.items():
        result[name] = convert_message(message_class['proto_class'].DESCRIPTOR)

    return result 


BOARDITEM_TYPE_CONFIGS = convert_proto_to_dict()

# Define the required arguments for each item type.
REQUIRED_ARGS = {
    "Arc": ["start", "end", "center", "angle"],
    "BoardGraphicShape": ["shape"],
    "BoardText": ["text"],
    "BoardTextBox": ["textbox"],
    "Dimension": ["text", "text_position"],
    "Field": ["name", "text"],
    "Footprint3DModel": ["filename", "position", "offset"],
    "FootprintInstance": ["position", "definition"],  # TODO
    "Net": ["code", "name"],
    "Pad": ["type"],
    "Track": ["start", "end"],
    "Via": ["position"],
    "Zone": ["name", "layers", "outline"],
    # "Group": ["items"],
}

for type_name, required in REQUIRED_ARGS.items():
    if type_name in BOARDITEM_TYPE_CONFIGS:
        BOARDITEM_TYPE_CONFIGS[type_name]["required_args"] = required
    

if __name__ == "__main__":
    pprint(convert_proto_to_dict().keys())
