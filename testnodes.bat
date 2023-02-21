:: Run two memcache nodes

start /b python ./run_node.py 7002
start /b python ./run_node.py 7001
timeout /t 2 > NUL
echo Press any key to close
pause
exit
