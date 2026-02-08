from typing import TypeAliasType

from pydantic import TypeAdapter

from .message import WebSocketClientMessage, WebSocketServerMessage


def _fix_refs(obj: list[object] | dict[str, object] | object) -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and v.startswith("#/$defs/"):
                obj[k] = f"#/components/schemas/{v.split('#/$defs/')[1]}"
            else:
                _fix_refs(v)
    elif isinstance(obj, list):
        for v in obj:
            _fix_refs(v)


def _get_schema(type_alias: TypeAliasType, components: dict[str, object]) -> dict[str, object]:
    schema = TypeAdapter(type_alias).json_schema()

    # Extract and merge defs at top level
    defs = schema.pop("$defs", {})
    components.update(defs)

    return schema


def add_websocket_schema(schema: dict[str, object]) -> None:
    components = schema["components"]
    if not isinstance(components, dict):
        msg = "Expected 'components' to be dict"
        raise TypeError(msg)

    component_schemas = components["schemas"]
    if not isinstance(component_schemas, dict):
        msg = "Expected 'schemas' to be dict"
        raise TypeError(msg)

    info = schema["info"]
    if not isinstance(info, dict):
        msg = "Expected 'info' to be dict"
        raise TypeError(msg)

    server_msg_schema = _get_schema(WebSocketServerMessage, component_schemas)
    component_schemas[WebSocketServerMessage.__name__] = server_msg_schema

    client_msg_schema = _get_schema(WebSocketClientMessage, component_schemas)
    component_schemas[WebSocketClientMessage.__name__] = client_msg_schema

    info["x-websockets"] = [
        {
            "name": "Session",
            "path": "/api/ws/{session_id}",
            "messages": {
                "send": {"$ref": f"#/components/schemas/{WebSocketServerMessage.__name__}"},
                "receive": {"$ref": f"#/components/schemas/{WebSocketClientMessage.__name__}"},
            },
        },
    ]

    _fix_refs(schema)
