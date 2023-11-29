from mininet.net import Mininet
from mininet.cli import CLI
from mininet.term import makeTerm
from mininet.log import setLogLevel
from mininet.link import Link, TCLink
from mininet.node import Controller, OVSKernelSwitch, RemoteController, Host



def create_network():
    # Create an instance of the network
    net = Mininet( link=TCLink)

    # Add a controller
    controller = net.addController('controller', RemoteController)

    # Add a single switch_1
    switch_1 = net.addSwitch('s1', cls=OVSKernelSwitch, failMode='secure')

    # Add hosts with specified IP and MAC addresses
    server_1 = net.addHost('server_1', ip='10.0.1.2/24', mac='00:00:00:00:00:01', cls=Host, defaultRoute=None)
    server_2 = net.addHost('server_2', ip='10.0.1.3/24', mac='00:00:00:00:00:02', cls=Host, defaultRoute=None)
    client_1 = net.addHost('client_1', ip='10.0.1.5/24', mac='00:00:00:00:00:03', cls=Host, defaultRoute=None)

    # Connect hosts to the switch_1
    net.addLink(client_1, switch_1)
    net.addLink(server_1, switch_1)
    net.addLink(server_2, switch_1)

    # Start the network
    net.build()
    controller.start()
    switch_1.start([controller])

    # Run CLI for interactive commands
    net.terms += makeTerm(server_1)
    net.terms += makeTerm(server_2)
    net.terms += makeTerm(client_1)
    CLI(net)

    # Stop the network
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')  # Set the log level to info to see details
    create_network()  # Build and start the network
