# [2023 1113]client_new是单线程版

使用'''python3 client_new.py --server_ip 127.0.0.1 --id 123456 --f files/ToSend'''在命令行测试






# [2023 1024]全部主要代码已完成

不使用Git

-----

`client.py` 

-> 客户端 

-> 如有更新直接上传并覆盖

-----

`server_with_bugs_fixed.py` 

-> 服务器 

-> 如有更新加后缀上传，不要覆盖

-----

`server_simple.py` 

-> 一个根据server_with_bugs_fixed精简的性能测试服务器，仅保留`file receive`与`save`功能，且与server_with_bugs_fixed行为完全一致

-> 在代码没完全写完时用这个测试，不要用server_with_bugs_fixed 

-> 如有更新直接上传并覆盖

-----

`client_login.py`

-> 用于登录获得token，以及进行其他交互活动

-> 如有更新直接上传并覆盖

-----
