from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import IPAddr

log = core.getLogger()

class PacketDropSimulator (object):
    """
    POX Controller Application for SDN Packet Drop Simulator
    Implements a Layer 2 learning switch and injects OpenFlow rules
    to drop specific traffic flows.
    """
    def __init__ (self, connection):
        self.connection = connection
        self.mac_to_port = {}
        connection.addListeners(self)
        
        # INSTALL DROP RULES
        # Project objective: Simulate packet loss using SDN flow rules.
        # We explicitly select a specific flow (ICMP coming from h1 to h2) and DROP it.
        log.info("Installing specific flow drop rules for 10.0.0.1 to 10.0.0.2")
        
        # Match ICMP (ping) traffic from h1 (10.0.0.1) to h2 (10.0.0.2)
        msg1 = of.ofp_flow_mod()
        msg1.priority = 100
        msg1.match.dl_type = 0x0800 # IPv4
        msg1.match.nw_src = IPAddr("10.0.0.1")
        msg1.match.nw_dst = IPAddr("10.0.0.2")
        msg1.match.nw_proto = 1 # ICMP
        # Empty actions list = DROP
        self.connection.send(msg1)

        # Match ICMP traffic from h2 to h1 (reverse)
        msg2 = of.ofp_flow_mod()
        msg2.priority = 100
        msg2.match.dl_type = 0x0800
        msg2.match.nw_src = IPAddr("10.0.0.2")
        msg2.match.nw_dst = IPAddr("10.0.0.1")
        msg2.match.nw_proto = 1
        self.connection.send(msg2)

    def _handle_PacketIn (self, event):
        """
        Handles incoming packets sent from the switch.
        Implements L2 Switching logic.
        """
        packet = event.parsed
        if not packet.parsed:
            log.warning("Ignoring incomplete packet")
            return

        if packet.type == packet.LLDP_TYPE:
            return

        self.mac_to_port[packet.src] = event.port

        if packet.dst in self.mac_to_port:
            out_port = self.mac_to_port[packet.dst]
            
            msg = of.ofp_flow_mod()
            msg.match.dl_src = packet.src
            msg.match.dl_dst = packet.dst
            msg.idle_timeout = 10
            msg.hard_timeout = 30
            msg.actions.append(of.ofp_action_output(port = out_port))
            msg.data = event.ofp
            self.connection.send(msg)
            log.debug("Installing flow for %s -> %s output %i" % (packet.src, packet.dst, out_port))
        else:
            # Flood
            msg = of.ofp_packet_out()
            msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
            msg.data = event.ofp
            msg.in_port = event.port
            self.connection.send(msg)

def launch ():
    def start_switch (event):
        log.info("Controlling switch %s" % (event.connection,))
        PacketDropSimulator(event.connection)
    core.openflow.addListenerByName("ConnectionUp", start_switch)
