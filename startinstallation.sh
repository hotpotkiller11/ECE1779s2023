
#!/bin/bash

pip3 install --upgrade pip
while read line;
	do
		echo " ---------- installing ---------------> $i "
		sudo pip3 install line;
		while [ $? -ne 0 ];
			do
				echo " ---------- Error，try manual installation ---------------> $i "
				sudo pip3 install $i;
			done
	done < requirements.txt

python "run.py"