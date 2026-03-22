TEXT_MODEL={"name":"name","key":"key","api":"api","promat":""}
IMAGE_MODEL={"name":"name","key":"key","api":"api","promat":""}

def user_config():
    TEXT_MODEL["name"]=input("文本模型名称：")
    TEXT_MODEL["key"]=input("文本模型密钥：")
    TEXT_MODEL["api"]=input("文本模型调用网址：")

    IMAGE_MODEL["name"]=input("识图模型名称：")
    IMAGE_MODEL["key"]=input("识图模型密钥：")
    IMAGE_MODEL["api"]=input("识图模型调用网址：")
    
