# Used to test the REST API's for the reader app get's
# Note - the forwarded port for the application is 31025

print_flags () {
    echo "========================================================================================================================="
    echo "Usage: test_car_tag_api.sh"
    echo "========================================================================================================================="
    echo "Helper utility to setup everything to use this repo"
    echo "========================================================================================================================="
    echo "How to use:"
    echo "  To Start: ./test_car_tag_api.sh [flags]"
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
echo "Testing against URL $url"

# $1 cmd to run
function run_test() {
    echo "$1 ..."
    $1 #| python -c "import sys,json; print(json.load(sys.stdin)['new_tag_id'])"
    echo "" # newline
}

echo "TEST 1 - Adding User (this will fail if user already added in another test)"
run_test "curl -X POST $url/user/signup?fname=test_fname&lname=test_lname&username=test_username&password=test_pwd&password2=test_pwd --output /dev/null"

# echo "TEST 2 - Changing User Password"
run_test "curl -X POST $url/user/forgot_password?uname=test_username&new_pwd=reset_pwd --output /dev/null"

# echo "TEST 3 - Logging in with User (using reset password)"
run_test "curl -X POST $url/user/login?username=test_username&pwd=reset_pwd  --output /dev/null"
