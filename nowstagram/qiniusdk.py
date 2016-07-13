#   -*- encoding=UTF-8 -*-
from nowstagram import  app
from qiniu import  Auth,put_stream,put_file
import  os

access_key = app.config['QINIU_ACCESS_KEY']
secret_key = app.config['QINIU_SECRET_KEY']

q = Auth(access_key=access_key,secret_key=secret_key)

bucket_name = app.config['QINIU_BUCTKET_NAME']
save_dir = app.config['UPLOAD_DIR']
domain_prefix = app.config['QINIU_DOMAIN_PREFIX']

def qiniu_upload(source_file,save_file_name):
    token = q.upload_token(bucket_name,save_file_name)
    source_file.save(os.path.join(save_dir,save_file_name))
    ret,info = put_file(token,save_file_name,os.path.join(save_dir,save_file_name))
    # ret,info = put_stream(token,save_file_name,source_file.stream,
    #                       'qiniu',os.fstat(source_file.stream.fileno()).st_size)
    # ret, info = put_stream(token, save_file_name, source_file.stream,
    #                        'qiniu', source_file.stream.tell())

    print  info

    if info.status_code == 200 :
        return domain_prefix+save_file_name
    return None

