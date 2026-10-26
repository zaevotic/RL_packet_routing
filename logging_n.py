from logger import log,LogType

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
