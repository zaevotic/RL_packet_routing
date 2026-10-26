import datetime
import inspect
from enum import Enum

class LogType(Enum):
    INFO="INFO"
    ERROR="ERROR"
    DEBUG="DEBUG"
    WARNING="WARNING"
    CRITICAL="CRITICAL"


def log(message,log_type=LogType.INFO,status="Success",
        general_logfile_path="app.log",print_log=False):
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


def traffic_generated(network,source,destination,packets):
    log(
        f"Traffic generated: {source} -> {destination}, "
        f"packets={packets}, t={network.time}",
        general_logfile_path=NETWORK_LOG
    )


def node_added(node_id):
    log(
        f"Node {node_id} added",
        general_logfile_path=NETWORK_LOG
    )


def edge_added(edge_id,A,B):
    log(
        f"Edge {edge_id} added: {A} <-> {B}",
        general_logfile_path=NETWORK_LOG
    )


def simulation_error(message):
    log(
        message,
        LogType.ERROR,
        status="Failure",
        general_logfile_path=NETWORK_LOG
    )

# Packets:

PACKET_LOG="packets.log"


def packet_created(packet):
    log(
        f"Packet {packet.id} created: "
        f"{packet.start_loc} -> {packet.end_loc}, "
        f"size={packet.size}, ttl={packet.ttl}",
        general_logfile_path=PACKET_LOG
    )


def packet_moved(packet,previous_node,current_node,time):
    log(
        f"Packet {packet.id} moved: "
        f"{previous_node} -> {current_node} at t={time}",
        general_logfile_path=PACKET_LOG
    )


def packet_delivered(packet,time):
    log(
        f"Packet {packet.id} delivered to {packet.end_loc} at t={time}",
        general_logfile_path=PACKET_LOG
    )


def packet_dropped(packet,reason,time=None):
    log(
        f"Packet {packet.id} dropped: {reason}, t={time}",
        LogType.WARNING,
        status="Failure",
        general_logfile_path=PACKET_LOG
    )


def packet_loop(packet,node,time=None):
    log(
        f"Packet {packet.id} loop detected at node {node}, t={time}",
        LogType.WARNING,
        status="Failure",
        general_logfile_path=PACKET_LOG
    )
