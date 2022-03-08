# Used to test the REST API's for the detection algo
# Note - the forwarded port for the application is 31025

print_flags () {
    echo "========================================================================================================================="
    echo "Usage: test_detection_algo.sh"
    echo "========================================================================================================================="
    echo "Helper utility to test the detection algorithm"
    echo "========================================================================================================================="
    echo "How to use:"
    echo "  To Start: ./test_detection_algo.sh [flags]"
    echo "========================================================================================================================="
    echo "Available Flags (mutually exclusive):"
    echo "    -r | --remote_test: If used, runs the test assuming the Server is running remotely and uses the forwarded IP and port"
    echo "    -lr | --local_remote_test: If used, runs the test assuming you are ON the Server, but attempting to access via forwarded Port"
    echo "    -p | --port <port_num>: If used, sets the port to try access the application on"
    echo "    -h | --help: This message"
    echo "========================================================================================================================="
}

# parse command line args
local=true
local_remote=false
port=31025
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -r | --remote_test )
            local=false
            ;;
        -lr | --local_remote_test )
            local=false
            local_remote=true
            ;;
        -p | --port )
            port="$2"
            shift # remove -p flag
            ;;
        -h | --help )
            print_flags
            exit 0
            ;;
        * )
            echo "... Unrecognized Command: $1"
            print_flags
            exit 1
    esac
    shift # remove flag (or arg to flag)
done

url=""
if [[ ${local} = true ]]; then
# TEST ON LOCAL MACHINE
    url="http://127.0.0.1:${port}"
# On server, but trying forwarded port
elif [[ ${local_remote} = true ]]; then
    # Will return the external ip address of this machine
    url="http://$(curl ifconfig.me && echo):${port}"
else
# TEST ON remote server
    url="http://71.167.9.86:${port}"
fi

# $1 cmd to run
function run_test() {
    echo "$1 ..."
    $1
    echo "" # newline
}

# after second curl, should detect car2
echo -e "Testing a Reader Detecting a Tag..."
run_test "curl -X POST $url/reader/send_event_data?reader_id=2&tag_id=4"
run_test "curl -X POST $url/reader/send_event_data?reader_id=2&tag_id=5"
run_test "curl -X POST $url/reader/send_event_data?reader_id=2&tag_id=6"

echo -e "\nTesting a Reader Detecting a Tag in a NEW Location..."
run_test "curl -X POST $url/reader/send_event_data?reader_id=1&tag_id=4"
run_test "curl -X POST $url/reader/send_event_data?reader_id=1&tag_id=5"
run_test "curl -X POST $url/reader/send_event_data?reader_id=1&tag_id=6"
