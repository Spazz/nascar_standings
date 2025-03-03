#!/bin/bash
# auto_bt_services.sh - Handles pairing and service authorization

echo "===== BLUETOOTH AUTO-PAIRING AND AUTHORIZATION ====="

# Install dependencies if needed
if ! command -v expect &> /dev/null; then
    echo "Installing required dependencies..."
    sudo apt-get update
    sudo apt-get install -y expect
fi

# Stop Bluetooth services
echo "Configuring Bluetooth..."
sudo systemctl stop bluetooth

# Create a specific iOS-compatible configuration
echo "Creating iOS-compatible configuration..."
sudo tee /etc/bluetooth/main.conf > /dev/null << 'EOF'
[General]
Name = NASCAR Tower
Class = 0x000100
DiscoverableTimeout = 0
PairableTimeout = 0
JustWorksRepairing = always
Privacy = device

# Automatically accept all authorized service requests
AutoEnable=true

[Policy]
AutoEnable=true
EOF

# Start Bluetooth with modified settings
echo "Starting Bluetooth with special settings..."
sudo systemctl start bluetooth
sleep 3

# Reset Bluetooth adapter with CLI tools
echo "Resetting Bluetooth adapter..."
sudo hciconfig hci0 down
sudo hciconfig hci0 up
sudo hciconfig hci0 piscan
sleep 2

# Create an expect script to automate bluetoothctl responses
echo "Creating automated pairing and authorization script..."
cat > /tmp/auto_bt.exp << 'EOF'
#!/usr/bin/expect -f

set timeout -1

# Spawn bluetoothctl
spawn sudo bluetoothctl

expect "#"
send "power on\r"
expect "#"
send "discoverable on\r"
expect "#"
send "pairable on\r"
expect "#"
send "agent on\r"
expect "#"
send "default-agent\r"
expect "#"
send "trust\r"

puts "\nNASCAR Tower is now discoverable and will auto-accept all requests"
puts "Try pairing from your iPhone now"
puts "Press Ctrl+C to exit when done"
puts "-----------------------------------------"

# Handle all types of requests
while {1} {
    expect {
        -re "Request confirmation.*yes/no" {
            send "yes\r"
            exp_continue
        }
        -re "Request authorization.*yes/no" {
            send "yes\r"
            exp_continue
        }
        -re "Authorize service.*yes/no" {
            send "yes\r"
            exp_continue
        }
        -re "Confirm passkey.*yes/no" {
            send "yes\r"
            exp_continue
        }
        -re "Confirm PIN code.*yes/no" {
            send "yes\r"
            exp_continue
        }
        -re "Enter PIN code:" {
            send "0000\r"
            exp_continue
        }
        -re "Enter passkey:" {
            send "0000\r"
            exp_continue
        }
        -re "Device.* paired: yes" {
            # When a device is paired, automatically trust it
            regexp {Device ([0-9A-F:]+) paired} $expect_out(0,string) -> mac
            if {[info exists mac]} {
                send "trust $mac\r"
            }
            exp_continue
        }
        timeout {
            # Just continue looping
            exp_continue
        }
    }
}
EOF

chmod +x /tmp/auto_bt.exp

echo "===== READY FOR iPHONE PAIRING ====="
echo "Your device will appear as 'NASCAR Tower'"
echo "The script will automatically accept ALL requests"
echo "Press Ctrl+C to exit when done"
echo "-----------------------------------------"

# Run the expect script
/tmp/auto_bt.exp