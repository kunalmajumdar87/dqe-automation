git clone https://github.com/DanyaHDanny/dqe-automation.git
git remote set-url origin https://git.epam.com/kunal_majumdar/personal_project_epam.git

git pull origin main
git pull origin main --allow-unrelated-histories
git push -u origin main


git clone https://github.com/DanyaHDanny/dqe-automation.git
cd dqe-automation
git remote rename origin upstream
git remote add origin https://git.epam.com/kunal_majumdar/project_epam_dqe_automation.git
git push -u origin main

git remote -v
git remote set-url origin https://git.epam.com/kunal_majumdar/project_epam_dqe_automation.git
git remote -v
git fetch origin