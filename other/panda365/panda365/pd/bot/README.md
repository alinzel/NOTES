## 添加bot流程

-   运营提供两个数据:
    1.  一个包含机器人名字的文本文件，格式是每行一个名字
    2.  一个包含机器人头像的文件夹。其中的每个文件是一个图片，格式为jpg, jpeg或png
-   在开发机上:

    1.  用uuid将头像文件全部重命名:

           flask bot rename_images path_to_images_dir

    2.  将头像文件上传到相应服务器的admin s3 bucket. 注意机器人头像都放在bucket/images/

           aws s3 sync path_to_images_dir s3://admin_bucket/images/b-icons

    3.  生成添加bot的命令列表。因为这些命令需要在线上执行，我们预先准备好这些命令:

           flask create_bot_commands  path_to_images_dir names.txt> commands.sh

-   在线上:
    1.  将刚才生成的命令上传到服务器上
    2.  `sudo su - panda`
    3.  `cd src`
    4.  `bash commands.sh`
