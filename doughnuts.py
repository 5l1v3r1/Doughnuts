"""
@Description: parse
@Author: Longlone
@LastEditors: Longlone
@Date: 2020-03-02 17:27:08
@LastEditTime: 2020-03-04 13:31:37
"""
from libs.app import Loop_init, run_loop
from libs.myapp import banner
from libs.config import gget, color, add_namespace_callback


class My_Loop_init(Loop_init):
    def set_platforms(self) -> dict:
        return {"main": "main_plugins", "webshell": "webshell_plugins", "general": "general", "encode": "encode"}

    def set_prompts(self) -> dict:
        return {"main": ":>", "webshell": "=>"}


@add_namespace_callback
def change_prompt():
    namespace = gget("namespace")
    if (namespace == "main"):
        print(color.yellow("[help] ") + color.cyan("Get a help doc for command"))
        print(color.yellow("[s|show] ") + color.cyan("Show log webshells"))
        print(color.yellow("[se|show_encoders] ") + color.cyan("Show available encoders"))
        print(color.yellow("[l|load] ") + color.cyan("Load a webshell from log. eg: load / load {_id}"))
        print(color.yellow("[c|connect] ") + color.cyan("Connect to a webshell. eg: connect {url} {method} {pass} {encoders...}"))
        print(color.yellow("[quit|exit] ") + color.cyan("Quit this program\n"))
    elif (namespace == "webshell"):
        print(color.yellow("[help] ") + color.cyan("Get a help doc for command"))
        print(color.yellow("[i|info] ") + color.cyan("Print webshell info"))
        print(color.yellow("[s|shell] ") + color.cyan("Enter interactive shell"))
        print(color.yellow("[re|reverse] ") + color.cyan("Reverse shell. eg: reverse {ip} {port} {type=php}"))
        print(color.yellow("[ws|webshell] ") + color.cyan("Enter interactive webshell"))
        print(color.yellow("[r|read] ") + color.cyan("Read file/files. eg: read {web_file_path1} {web_file_path2} .."))
        print(color.yellow("[w|write] ") + color.cyan("Write file. eg: write {web_file_path}"))
        print(color.yellow("[u|upload] ") + color.cyan("Upload file. eg: upload {file_path} {web_file_path=file_name} {force=False}"))
        print(color.yellow("[d|download] ") + color.cyan("Download file. eg: download {web_file_path} {local_path=./site.com/...}"))
        print(color.yellow("[del|delete] ") + color.cyan("Delete file/files. eg: read {web_file_path1} {web_file_path2} .."))
        print(color.yellow("[dump] ") + color.cyan("Package and compress files in a folder and download it. eg: dump {web_file_path} {local_path=./site.com/...}"))
        print(color.yellow("[fwpf] ") + color.cyan("Find writable php file. eg: fwpf {web_file_path=webroot}"))
        print(color.yellow("[fc] ") + color.cyan("Find config file. eg: fwpf {web_file_path=webroot}"))
        print(color.yellow("[pdf] ") + color.cyan("Print disable functions"))
        print(color.yellow("[ps|portscan] ") + color.cyan("Scan intranet ports. eg: portscan {ip} {ports} {timeout=0.5}"))
        print(color.yellow("[b|back] ") + color.cyan("Back to main menu\n"))


if __name__ == "__main__":
    banner()
    run_loop(My_Loop_init(), leave_message="Bye! Doughnuts:)")