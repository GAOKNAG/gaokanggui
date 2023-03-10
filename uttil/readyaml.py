"""
    解读yaml文件
"""
import yaml
import traceback
import os


class ReadYaml(object):
    yaml_file: object

    def __init__(self, yaml_file):
        """
        通过init方法把yaml文件传入到这个类
        :param yaml_file: yaml文件
        """
        self.yaml_file = yaml_file

    # 读取yaml文件,把yaml转化成json
    def read_yaml(self):
        """
        读取yaml，对yaml反序列化
        :return:
        """
        if os.path.exists(self.yaml_file) and os.path.getsize(self.yaml_file) != 0:
            try:
                with open(self.yaml_file, encoding='utf-8') as f:
                    yaml_value = yaml.load(f, Loader=yaml.SafeLoader)
                    print(yaml_value)
                    return yaml_value
            except FileNotFoundError:
                traceback.print_exc()
            finally:
                f.close()
        else:
            traceback.print_exc()
if __name__ == '__main__':
    ReadYaml("aaaa.yaml").read_yaml()
