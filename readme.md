不使用Git

`client.py` 
  -> 客户端
​	-> 如有更新直接上传并覆盖

  
`server_with_bugs_fixed.py` 
  -> 服务器
  -> 如有更新加后缀上传，不要覆盖


`sever_simple.py` 
  -> 一个简单的性能测试服务器，收到一个包后立即打印，可计算收发时间
  -> 在代码没完全写完时用这个测试，不要用server_with_bugs_fixed
  -> 如有更新直接上传并覆盖
