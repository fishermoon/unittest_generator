import openai
import os
import re
from os import walk

openai.api_key = "OPEN_API_KEY"

framework = "cmocka"
language = "c"
messages = [
    {"role": "system", "content": "You are a great programmer."},
    {"role": "system", "content": "You will write unittest and mock for {} framework in {} language.".format(framework, language)},
    {"role": "system", "content": "Project's name is DPVS(DPDK-LVS) and Layer-4 load balancer.".format(framework, language)},
    {"role": "system", "content": "DPVS support lite IP-stack ".format(framework, language)},
    {"role": "system", "content": "You completely understand the following code in ."},
]

whitelist = ["ipv", "neigh", "route", "stats", "inetaddr", "icmp", "linux_ipv6"]
blacklist_dir = ["conf", "keepalived", "dpip", "ipvs"]
mypath = "./"


def get_learning_filelist():
    learning_filelist = []
    for (dirpath, dirnames, filenames) in walk(mypath):
        is_blacklist = False
        for black in blacklist_dir:
            if black in dirpath:
                is_blacklist = True
                break

        if is_blacklist:
            continue

        for filename in filenames:
            if not ".c" in filename[-2:] and not ".h" in filename[-2:]:
                continue

            for white in whitelist:
                if white in filename:
                    learning_filelist.append([dirpath, filename])
                    break
    return learning_filelist
    

def comment_remover(text):
    def replacer(match):
        s = match.group(0)
        if s.startswith('/'):
            return " " # note: a space and not an empty string
        else:
            return s
    pattern = re.compile(
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
        re.DOTALL | re.MULTILINE
    )
    return re.sub(pattern, replacer, text)


def learn(learning_filelist):
    for dirpath, filename in learning_filelist:
        filepath = os.path.join(dirpath, filename)
        with open(filepath, "rt", encoding="UTF8") as file:
            code = comment_remover(file.read())
            content = "filename is {} and and the contetns are below. \n{}".format(filename, code)
            message = {"role": "system", "content": content}
            messages.append(message)


def make_unittest(target_file, target_functions, score=False):
    content = ""
    if score:
        content += "Previous your writing unittest quality score is {}/5.0.".format(score)
        
    content += "Please write 2 unittests which are positive and negative per function to a level that can be bulit.\n" + \
                "- target filename: {}".format(target_file) + \
                "- target functions: {}".format(target_functions)
    message = {"role": "user", "content": content}
    messages.append(message)
    
    completion = openai.ChatCompletion.create(model="gpt-4-1106-preview", messages=messages)
    assistant_content = completion.choices[0].message["content"].strip()
    print(assistant_content)


def main():
    target_file = "ipv4.c"
    target_functions = "ipv4_local_in, ipv4_local_in_fin, ipv4_output_fin2, ipv4_output_fin"

    learning_filelist = get_learning_filelist()
    learn(learning_filelist)
    make_unittest(target_file, target_functions)

    # 이전에 사용했던 토큰 정보를 잘 기억하지 않음.
    # make_unittest(target_file, target_functions, 1.0)


if __name__ == "__main__":
    main()
