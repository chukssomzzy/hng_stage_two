#!/usr/bin/python3

"""Referencing and schema from file system"""

from pathlib import Path
import json

from referencing import Registry, Resource

SCHEMAS = Path(__file__).parent


def retrieve_from_dir(uri: str):
    """Retrieve a json schema from filesystem"""
    schema_path = SCHEMAS / uri
    content = json.loads(schema_path.read_text())
    return Resource.from_contents(content)


registry = Registry(retrieve=retrieve_from_dir)


def get_schema(uri: str):
    """Get a schema from registry"""
    resolver = registry.resolver()
    resolved = resolver.lookup(uri)
    return (resolved.contents)
