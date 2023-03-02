python3 ./run_node.py 7002 &
python3 ./run_node.py 7001 &

echo ""
echo "Press any key to stop all instances."
read -n 1 -s
pkill -f "python3 ./run_nodes.py"
