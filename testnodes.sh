python3 ./run_node.py 7000 &
python3 ./run_node.py 7001 &
# Modification according to advice of chatGPT
echo ""
echo "Press any key to stop all instances."
read -n 1 -s
pkill -f "python ./run_nodes.py"
