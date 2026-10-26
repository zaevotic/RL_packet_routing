from logger import log,LogType

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
