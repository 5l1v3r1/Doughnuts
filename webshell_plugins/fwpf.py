"""
@Description: command-function: whoami
@Author: Longlone
@LastEditors: Longlone
@Date: 2020-01-07 18:42:00
@LastEditTime: 2020-03-03 13:01:31
"""
from libs.config import alias, gget
from libs.myapp import send, print_tree


def get_php(file_path: str):
    return """function listAllFiles($dir){
    if(is_dir($dir)){
        if($handle=opendir($dir)){
            while(false!==($file=readdir($handle))){
                if($file!="."&&$file!=".."){
                    if(is_dir($dir."/".$file)){
                        $files[$file]=listAllFiles($dir."/".$file);
                    }else if(strtolower(end(explode('.', $file))) == "php"){
                        $files[]=$dir."/".$file;
                    }
                }
            }
            closedir($handle);
        }
    }
    return $files;
}
print(json_encode(listAllFiles("%s")));""" % file_path


@alias(True, fp="file_path")
def run(web_file_path: str = ''):
    """
    fwpf

    Find writable php files from website
    """
    web_file_path = web_file_path if (len(web_file_path)) else gget("webshell.root", "webshell")
    php = get_php(web_file_path)
    file_tree = send(f'{php}').r_json
    print_tree(web_file_path, file_tree)