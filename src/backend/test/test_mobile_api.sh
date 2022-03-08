# Used to test the REST API's for the mobile app get's
# Note - the forwarded port for the application is 31025

print_flags () {
    echo "========================================================================================================================="
    echo "Usage: test_mobile_api.sh"
    echo "========================================================================================================================="
    echo "Helper utility to setup everything to use this repo"
    echo "========================================================================================================================="
    echo "How to use:"
    echo "  To Start: ./test_mobile_api.sh [flags]"
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

echo -n "Test 1 - Get coords of some spots"
# /reader/get_spot_coord/<int:spot_id>
run_test "curl $url/reader/get_spot_coord/1"
run_test "curl $url/reader/get_spot_coord/2"
run_test "curl $url/reader/get_spot_coord/3"

echo -n "TEST 2 - Getting the meters within the radius. "
echo "For now the readers are at: (42.340989, -71.091054), (42.341061, -71.091008)"
# make its center be the same as a reader
echo "TEST 2.1.1 - Test center MATCHING a reader"
run_test "curl $url/mobile/get_local_readers?latitude=42.340989&longitude=-71.091054&radius=15"

echo "TEST 2.1.2 - Test center being NEAR a reader"
run_test "curl $url/mobile/get_local_readers?latitude=42.340960&longitude=-71.0910540&radius=15"

echo "TEST 2.1.3 - Test getting ALL readers with large radius"
run_test "curl $url/mobile/get_local_readers?latitude=42.340989&longitude=-71.091054&radius=100"

# echo ""
# echo "TEST 2.2.1 - Test Getting the meters within the radius but not giving the radius (should error)"
# curl $url'/mobile/get_local_readers?latitude=42.340989&longitude=-71.091054'

# echo ""
# echo "TEST 2.2.1 - Test Getting the meters within the radius but not giving the lat (should error)"
# curl $url'/mobile/get_local_readers?radius=20&longitude=-71.091054'

# echo ""
# echo "TEST 2.2.1 - Test Getting the meters within the radius but not giving the long (should error)"
# curl $url'/mobile/get_local_readers?latitude=42.340989&radius=20'


# echo ""
# echo -n "TEST 3 - Given Reader ID, RETURN its status."
# echo "Only available readers are reader 0 = free, reader 1 = taken."
# echo "Testing reader 0...expect a return of False because it is free"
# curl $url'/mobile/get_is_spot_taken/0'

# echo ""
# echo "Testing reader 1...expect a return of True because it is taken"
# curl $url'/mobile/get_is_spot_taken/1'

# echo ""
# echo "Testing reader 500(doesn't exist)...expect a return of None/Null because reader does not exist"
# curl $url'/mobile/get_is_spot_taken/500'
