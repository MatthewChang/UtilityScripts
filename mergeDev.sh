branch=$(git rev-parse --abbrev-ref HEAD)
git checkout development
git pull origin development
git checkout $branch
git merge development
