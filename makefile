git:
		git add .
		git commit -m "$m"	
		git push -u origin master 

resume:
		(git pull)
		(source chattier/bin/activate)
		(pip install -r requirements.txt)