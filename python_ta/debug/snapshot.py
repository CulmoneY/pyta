"""
Use the 'inspect' module to extract local variables from
 multiple stack frames. Useful for dynamic debugging.
"""

from __future__ import annotations

import inspect
import json
import logging
import re
import shutil
import subprocess
import sys
from typing import TYPE_CHECKING, Any, Iterable, Optional

from packaging.version import Version, parse

from .id_tracker import IDTracker

if TYPE_CHECKING:
    from types import FrameType


def get_filtered_global_variables(frame: FrameType) -> dict:
    """
    Helper function for retriving global variables
    (i.e. top level variables in "__main__" frame's scope)
    excluding, certain types (types of data that is
    irrelevant in an intro level to Python programming language).
    """
    global_vars = frame.f_globals
    true_global_vars = {
        var: global_vars[var]
        for var in global_vars
        if not var.startswith("__")
        and not inspect.ismodule(global_vars[var])
        and not inspect.isfunction(global_vars[var])
        and not inspect.isclass(global_vars[var])
        and getattr(inspect.getmodule(global_vars[var]), "__name__", "__main__") == "__main__"
    }
    return {"__main__": true_global_vars}


def get_filtered_local_variables(
    frame: FrameType, exclude_vars: Optional[Iterable[str | re.Pattern]]
) -> dict:
    """
    Helper function for filtering local variables in a frame.
    """
    if exclude_vars:
        return {
            var: frame.f_locals[var]
            for var in frame.f_locals
            if not any(re.search(regex, var) for regex in exclude_vars)
        }
    return frame.f_locals


def snapshot(
    save: bool = False,
    memory_viz_args: Optional[list[str]] = None,
    memory_viz_version: str = "latest",
    include_frames: Optional[Iterable[str | re.Pattern]] = None,
    exclude_frames: Optional[Iterable[str | re.Pattern]] = None,
    exclude_vars: Optional[Iterable[str | re.Pattern]] = None,
    id_tracker: Optional[IDTracker] = None,
):
    """Capture a snapshot of local variables from the current and outer stack frames
    where the 'snapshot' function is called. Returns a list of dictionaries,
    each mapping function names to their respective local variables.
    Excludes the global module context.

    When save is True, a MemoryViz-created svg is produced.
    memory_viz_args can be used to pass in options to the MemoryViz CLI.
    For details on the MemoryViz CLI, see https://www.cs.toronto.edu/~david/memory-viz/docs/cli.
    memory_viz_version can be used to dictate version, with a default of the latest version.
    Note that this function is compatible only with MemoryViz version 0.3.1 and above.
    include_frames can be used to specify a collection of function names, either as strings or regular expressions,
    whose variables will be captured. By default, all variables in all functions will be captured if no `include_frames`
    argument is provided.
    exclude_frames can be used to specify a collection of function names, either as strings or regular expressions,
    whose variables should be excluded.
    exclude_vars can be used to specify a collection of variable names, either as strings or regular expressions,
    that will be excluded from the snapshot. By default, all variables will be captured if no `exclude_vars` is provided.
    id_tracker can be used to allow long-term tracking of IDs across multiple snapshots.
    """
    if id_tracker is None:
        id_tracker = IDTracker()

    variables = []
    frame = inspect.currentframe().f_back

    while frame:
        frame_name = frame.f_code.co_name

        # Check whether frame_name is included
        if include_frames is not None and all(
            not re.search(regex, frame_name) for regex in include_frames
        ):
            frame = frame.f_back
            continue

        # Check whether frame_name is excluded
        if exclude_frames is not None and any(
            re.search(regex, frame_name) for regex in exclude_frames
        ):
            frame = frame.f_back
            continue

        if frame_name != "<module>":
            local_vars = get_filtered_local_variables(frame, exclude_vars)
            variables.append({frame_name: local_vars})
        else:
            global_vars = get_filtered_global_variables(frame)
            variables.append(global_vars)
        frame = frame.f_back

    if save:
        json_compatible_vars = snapshot_to_json(variables, id_tracker=id_tracker)

        # Set up command
        command = ["npx", f"memory-viz@{memory_viz_version}", "--width", "800"]
        if memory_viz_args:
            command.extend(memory_viz_args)

        # Ensure valid memory_viz version
        if memory_viz_version != "latest" and parse(memory_viz_version) < Version("0.3.1"):
            logging.warning("PythonTA only supports MemoryViz versions 0.3.1 and later.")

        # Create a child to call the MemoryViz CLI
        npx_path = shutil.which("npx")
        subprocess.run(
            command,
            input=json.dumps(json_compatible_vars),
            executable=npx_path,
            stdout=sys.stdout,
            stderr=sys.stderr,
            encoding="utf-8",
            text=True,
            check=True,
        )

    return variables


def snapshot_to_json(
    snapshot_data: list[dict], id_tracker: Optional[IDTracker] = None
) -> list[dict]:
    """
    Convert the snapshot data into a simplified JSON format, where each value
    has its own entry with a matching ID. This includes nesting the process_value
    function to handle recursive processing of data types.

    id_tracker can be used to ensure that each value is assigned a unique ID, across multiple snapshots.
    """
    if id_tracker is None:
        id_tracker = IDTracker()

    json_data = []  # This will store the converted frames and their variables
    value_entries = []  # Stores additional processed value entries

    def process_value(val: Any) -> int:
        """
        Recursively processes a value, handling compound built-in data types
        (lists, sets, tuples, and dicts) by creating a list or dict of IDs for their elements.
        This process assigns a unique ID to the input value. This ID, which uniquely identifies
        the processed value in a global context, is returned by the function. The returned ID
        ensures that each value is processed only once, facilitating the reconstruction of
        the original data structure with its elements uniquely identified.

        """
        nonlocal value_entries

        if id_tracker.is_snapshot_object(val):
            return id_tracker[val]
        else:
            value_id_diagram = id_tracker.add(val)

            # Handle compound built-in data types
            if isinstance(val, (list, set, tuple)):
                element_ids = [process_value(element) for element in val]
                value_entry = {
                    "type": type(val).__name__,
                    "id": value_id_diagram,
                    "value": element_ids,
                }
            elif isinstance(val, dict):
                dict_ids = {}
                for key, v in val.items():
                    key_id = process_value(key)
                    val_id = process_value(v)
                    dict_ids[key_id] = val_id
                value_entry = {
                    "type": "dict",
                    "id": value_id_diagram,
                    "value": dict_ids,
                }
            # Handle user-defined classes
            elif hasattr(val, "__dict__"):  # Check if val is a user-defined class instance
                attr_ids = {}
                for attr_name, attr_val in vars(val).items():
                    attr_id = process_value(attr_val)
                    attr_ids[attr_name] = attr_id
                value_entry = {
                    "type": ".class",
                    "name": type(val).__name__,
                    "id": value_id_diagram,
                    "value": attr_ids,
                }
            elif val is None:
                value_entry = {
                    "type": "NoneType",
                    "id": value_id_diagram,
                    "value": "None",
                }
            else:  # Handle primitives and other types
                try:
                    json.dumps(val)
                    jsonable_val = val
                except TypeError:
                    jsonable_val = repr(val)
                value_entry = {
                    "type": type(val).__name__,
                    "id": value_id_diagram,
                    "value": jsonable_val,
                }
            value_entries.append(value_entry)

        return value_id_diagram

    for frame in snapshot_data:
        frame_variables = {}
        for frame_name, frame_data in frame.items():
            for var_name, value in frame_data.items():
                var_id_diagram = process_value(value)
                frame_variables[var_name] = var_id_diagram

            json_object_frame = {
                "type": ".frame",
                "name": frame_name,
                "id": None,
                "value": frame_variables,
            }
            json_data.append(json_object_frame)

    json_data.extend(value_entries)
    id_tracker.clear_snapshot_objects()
    return json_data
