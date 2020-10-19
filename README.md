## 功能
在图像上寻找已知人脸，基于Flask实现web服务，支持本地人脸库热更新，使用热工信功能后，需调用post.py调用的接口后热更新才会完全生效

## 环境
参考项目[https://github.com/ageitgey/face_recognition]

## 运行
python server_face2.py

## API文档
* 寻找人脸：http://wiki.ccwb.cn/web/#/73?page_id=2343
* 添加人脸：http://wiki.ccwb.cn/web/#/73?page_id=2257
* 删除人脸：http://wiki.ccwb.cn/web/#/73?page_id=2349

## 其他
* 首次运行需创建文件夹：del_faces（暂存删除人脸数据），pictures_of_people_i_know4（存放一直人脸，一个人一个文件夹），images（暂存待识别图像），updata_faces（暂存添加人脸数据）
* post.py # 寻找人脸调用示例
* post2.py # 热更新-添加人脸调用示例
* post3.py # 热更新-删除人脸调用示例
