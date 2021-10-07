
直接运行genproto.py， 即可生成pb文件

这里注意将 hello_pb2_grpc.py 中的导入改成如下：
```python
from jnpy.app.grpc_service.proto import hello_pb2 as hello__pb2
```
