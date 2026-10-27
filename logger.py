import datetime
import inspect
import json
import os
from enum import Enum

class LogType(Enum):
    INFO="INFO"
    ERROR="ERROR"
    DEBUG="DEBUG"
    WARNING="WARNING"
    CRITICAL="CRITICAL"


TRACE_LOG = "trace.json"
ENABLE_TRACE = True


def emit_trace_event(event_dict, mode="a"):
    """Appends or writes a structured JSON trace event line to trace.json."""
    if not ENABLE_TRACE:
        return
    try:
        with open(TRACE_LOG, mode, encoding="utf-8") as f:
            f.write(json.dumps(event_dict) + "\n")
    except Exception as e:
        pass


def log(message,log_type=LogType.INFO,status="Success",
        general_logfile_path="app.log",print_log=False):
    if not ENABLE_TRACE:
        return
    if not isinstance(log_type,LogType):
        raise ValueError("log_type must be a LogType")

    timestamp=datetime.datetime.now().isoformat(timespec="milliseconds")
    frame=inspect.currentframe()
    caller=frame.f_back.f_code.co_name
    log_entry=f"{timestamp} {log_type.value} {caller} {status} {message}"

    if print_log:
        print(log_entry)

    with open(general_logfile_path,"a",encoding="utf-8") as f:
        f.write(log_entry+"\n")

# Network:

NETWORK_LOG="network.log"


def graph_generated(network):
    log(
        f"Graph generated: {network.nodes} nodes, "
        f"{network.edges} edges",
        general_logfile_path=NETWORK_LOG
    )

    # Extract edge topology [A, B] for the visualizer
    edges = []
    if hasattr(network, "edge_list"):
        for e in network.edge_list:
            A = getattr(e, "A", -1)
            B = getattr(e, "B", -1)
            if A != -1 and B != -1:
                edges.append([A, B])

    nodes_count = getattr(network, "nodes", 0)
    nodes = [{"id": i} for i in range(nodes_count)]

    # Reset trace.json on new graph generation
    emit_trace_event({
        "type": "GRAPH_INIT",
        "t": getattr(network, "time", 0),
        "nodes": nodes,
        "edges": edges
    }, mode="w")


def traffic_generated(network,source,destination,packets):
    log(
        f"Traffic generated: {source} -> {destination}, "
        f"packets={packets}, t={network.time}",
        general_logfile_path=NETWORK_LOG
    )
    emit_trace_event({
        "type": "traffic",
        "source": source,
        "destination": destination,
        "packets": packets,
        "t": getattr(network, "time", 0)
    })


def node_added(node_id):
    log(
        f"Node {node_id} added",
        general_logfile_path=NETWORK_LOG
    )
    emit_trace_event({
        "type": "node_add",
        "node": node_id
    })


def edge_added(edge_id,A,B):
    log(
        f"Edge {edge_id} added: {A} <-> {B}",
        general_logfile_path=NETWORK_LOG
    )
    emit_trace_event({
        "type": "edge_add",
        "id": edge_id,
        "from": A,
        "to": B
    })


def simulation_error(message):
    log(
        message,
        LogType.ERROR,
        status="Failure",
        general_logfile_path=NETWORK_LOG
    )
    emit_trace_event({
        "type": "error",
        "message": message
    })

# Packets:

PACKET_LOG="packets.log"


def packet_created(packet=None):
    if packet is None:
        return
    log(
        f"Packet {packet.id} created: "
        f"{packet.start_loc} -> {packet.end_loc}, "
        f"size={packet.size}, ttl={packet.ttl}",
        general_logfile_path=PACKET_LOG
    )
    t = packet.history_time[0] if getattr(packet, "history_time", None) else 0
    emit_trace_event({
        "type": "spawn",
        "p": getattr(packet, "id", None),
        "node": getattr(packet, "start_loc", None),
        "size": getattr(packet, "size", 0),
        "ttl": getattr(packet, "ttl", 50),
        "t": t
    })


def packet_moved(packet=None, previous_node=None, current_node=None, time=None):
    if packet is None:
        return
    if time is None and hasattr(packet, "history_time") and packet.history_time:
        time = packet.history_time[-1]
    log(
        f"Packet {packet.id} moved: "
        f"{previous_node} -> {current_node} at t={time}",
        general_logfile_path=PACKET_LOG
    )
    emit_trace_event({
        "type": "hop",
        "p": getattr(packet, "id", None),
        "from": previous_node,
        "to": current_node,
        "t": time if time is not None else 0
    })


def packet_delivered(packet=None, time=None):
    if packet is None:
        return
    if time is None and hasattr(packet, "history_time") and packet.history_time:
        time = packet.history_time[-2] if len(packet.history_time) > 1 and packet.history_time[-1] == -1 else packet.history_time[-1]
    log(
        f"Packet {packet.id} delivered to {packet.end_loc} at t={time}",
        general_logfile_path=PACKET_LOG
    )
    emit_trace_event({
        "type": "deliver",
        "p": getattr(packet, "id", None),
        "node": getattr(packet, "end_loc", None),
        "t": time if time is not None else 0
    })


def packet_dropped(packet=None, reason="dropped", time=None):
    if packet is None:
        return
    if time is None and hasattr(packet, "history_time") and packet.history_time:
        time = packet.history_time[-2] if len(packet.history_time) > 1 and packet.history_time[-1] == -1 else packet.history_time[-1]
    log(
        f"Packet {packet.id} dropped: {reason}, t={time}",
        LogType.WARNING,
        status="Failure",
        general_logfile_path=PACKET_LOG
    )
    node = packet.history_loc[-1] if getattr(packet, "history_loc", None) else None
    emit_trace_event({
        "type": "drop",
        "p": getattr(packet, "id", None),
        "node": node,
        "reason": str(reason),
        "t": time if time is not None else 0
    })


def packet_loop(packet=None, node=None, time=None):
    if packet is None:
        return
    if time is None and hasattr(packet, "history_time") and packet.history_time:
        time = packet.history_time[-1]
    log(
        f"Packet {packet.id} loop detected at node {node}, t={time}",
        LogType.WARNING,
        status="Failure",
        general_logfile_path=PACKET_LOG
    )
    emit_trace_event({
        "type": "loop",
        "p": getattr(packet, "id", None),
        "node": node,
        "t": time if time is not None else 0
    })
