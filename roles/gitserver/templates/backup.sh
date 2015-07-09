#!/bin/bash

REPODIR="{{ gitserver_home }}"
BACKUPDIR="{{ gitserver_backup_dir }}"
GIT_LOG_ARGS="--graph --all --pretty=fuller"
REMOTES=(
{% for remote in gitserver_backup_remotes %}
  "{{ remote }}"
{% endfor %}
)

git init "$BACKUPDIR"
cd "$BACKUPDIR"

log_message=$(mktemp --tmpdir=/dev/shm)
echo "==============================" >> $log_message
echo "= Started backup at $(date)"    >> $log_message
echo "==============================" >> $log_message

for repo_path in $(dirname $(find "$REPODIR" -name HEAD -type f))
do
    rela_repo_path=$(echo $repo_path | sed "s;$REPODIR/;;")
    cd $repo_path
    rela_backup_path="$rela_repo_path.tar"
    backup_path="$BACKUPDIR/$rela_backup_path"
    mkdir -p $(dirname $backup_path)
    last_backup="$(stat -c "%z" "$backup_path" 2> /dev/null || echo 1999)"

    numcommits=$(git log \
                   --pretty=oneline \
                   --since "$last_backup" 2> /dev/null \
                     | wc -l)
    if [ $numcommits ]
    then
        echo "------------------------------"        >> $log_message
        echo "- $rela_repo_path"                     >> $log_message
        echo "------------------------------"        >> $log_message
        echo "$numcommits commits since last backup" >> $log_message

        log=$(git log $GIT_LOG_ARGS --since "$last_backup" 2> /dev/null)
        if [ "$log" ]
        then
            echo                        >> $log_message
            echo "$log" | sed 's/^/  /' >> $log_message
        fi
    fi

    cd "$REPODIR"
    bsdtar cf "$backup_path" "$rela_repo_path"
    cd "$(dirname "$backup_path")"
    git add "$backup_path"

done

# commit
cd $(dirname "$backup_path")
git commit -F "$log_message"
rm "$log_message"

# update remotes
for remote in "${REMOTES[@]}"
do
    git remote add $remote 2> /dev/null
    git push --mirror $(echo "$remote" | sed 's/ .*//')
done
