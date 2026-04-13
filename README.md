# Packet Drop Simulator - SDN Mininet Project

This project satisfies the requirements for the **Packet Drop Simulator** assignment using Mininet and **POX** SDN Controller.
It demonstrates packet loss simulation utilizing SDN flow rules (OpenFlow) on a custom topology.

## Objective
Simulate packet loss using SDN flow rules by installing explicit match+action OpenFlow drop rules.

## Requirements
* Mininet Network Emulator
* POX SDN Framework
* Python 3

## Topology
The network uses a Single-Switch topology containing:
* 1 Open vSwitch (`s1`)
* 3 Hosts (`h1`, `h2`, `h3`) with IPs `10.0.0.1`, `10.0.0.2`, `10.0.0.3` respectively.

## Execution Steps

### 1. Download POX
If you haven't already downloaded POX, clone it inside your project folder:
```bash
git clone https://github.com/noxrepo/pox.git
```

### 2. Copy the Controller to POX
Copy our custom controller script directly into the POX extension directory so POX can find it:
```bash
cp controller_pox.py pox/ext/controller_pox.py
```

### 3. Start the Controller
In the first terminal window, start the POX controller utilizing our script:
```bash
cd pox
python3 pox.py controller_pox
```
*Note: Our controller initializes a Layer 2 learning switch and inserts high priority OpenFlow rules (priority=100) to explicitly drop all ICMP (ping) traffic originating from `h1` and destined for `h2`, mimicking targeted packet loss.*

### 4. Start the Mininet Topology
In a second terminal window, execute the Python mininet script with `sudo`:
```bash
sudo python3 topology.py
```

### 5. Verification & Evaluation
Inside the Mininet CLI (`mininet>`), verify the intended behavior:

#### Normal Behavior
Test regular communication between `h1` and `h3`, as well as `h2` and `h3`.
```bash
mininet> h1 ping -c 3 h3
mininet> h2 ping -c 3 h3
```
*Expected Result:* 0% packet loss. Communication succeeds because no drop rules match this flow.

#### Simulated Packet Loss (Drop Rules Evaluation)
Test communication between `h1` and `h2`, which the controller expects to block.
```bash
mininet> h1 ping -c 3 h2
```
*Expected Result:* **100% packet loss**. The packets are intercepted by the priority=100 rule in Open vSwitch and dropped (no action), validating the correct installation of our simulation rules.

#### Regression Test (Rule Persistence)
To prove that the OpenFlow rule has been correctly installed and persists on the data plane, dump the flows on `s1` bridging to OVS.
```bash
mininet> sh dpctl dump-flows
```
*Expected Result:* You will observe the permanent drop flows matching `icmp` metrics `nw_src=10.0.0.1` and `nw_dst=10.0.0.2` without any associated output `actions`.
