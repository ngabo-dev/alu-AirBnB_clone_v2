#!/usr/bin/python3
"""
Fabric script that generates a .tgz archive and distributes it to web servers
"""

from datetime import datetime
from fabric.api import env, local, put, run
from os.path import isdir, exists

# IPs of your web servers
env.hosts = ['54.227.26.33', '23.22.249.71']
env.user = "ubuntu"
env.key_filename = "~/.ssh/id_rsa"

def do_pack():
    """Generates a .tgz archive from the contents of the web_static folder"""
    try:
        date = datetime.now().strftime("%Y%m%d%H%M%S")
        if not isdir("versions"):
            local("mkdir versions")
        file_name = "versions/web_static_{}.tgz".format(date)
        local("tar -cvzf {} web_static".format(file_name))
        return file_name
    except Exception as e:
        print("Archive creation failed: {}".format(e))
        return None

def do_deploy(archive_path):
    """Distributes an archive to your web servers"""
    if not exists(archive_path):
        return False

    try:
        file_name = archive_path.split("/")[-1]
        name = file_name.split(".")[0]
        path_name = "/data/web_static/releases/" + name
        tmp_path = "/tmp/" + file_name

        # Upload the archive to the /tmp/ directory of the web server
        put(archive_path, tmp_path)

        # Uncompress the archive to the folder on the web server
        run("mkdir -p {}/".format(path_name))
        run('tar -xzf {} -C {}/'.format(tmp_path, path_name))

        # Delete the archive from the web server
        run("rm {}".format(tmp_path))

        # Move the content from web_static to the new path
        run("mv {}/web_static/* {}".format(path_name, path_name))
        run("rm -rf {}/web_static".format(path_name))

        # Delete the symbolic link
        run('rm -rf /data/web_static/current')

        # Create a new symbolic link
        run('ln -s {}/ /data/web_static/current'.format(path_name))

        print("Deployment succeeded")
        return True
    except Exception as e:
        print("Deployment failed: {}".format(e))
        return False

if __name__ == "__main__":
    archive_path = do_pack()
    if archive_path:
        print("Archive created: {}".format(archive_path))
        result = do_deploy(archive_path)
        if result:
            print("Deployment succeeded")
        else:
            print("Deployment failed")
    else:
        print("Failed to create archive")
