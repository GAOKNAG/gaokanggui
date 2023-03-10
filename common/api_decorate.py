import inspect
from collections import OrderedDict, defaultdict
from functools import wraps
from types import FunctionType
from urllib.parse import urljoin, urlencode
from requests import Session, Response
from .exceptions import ApifunctionReturnValueError
from .logger import Logger
from .utils import format_json
import json

logger = Logger()


class Method:
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


def request_mapping(path="", method=Method.GET, before_request=None, after_response=None):
    """:param path:请求路径
        :param method:请求方法，当该装饰器作用类时，不需要传
        :param after_response:只能作用方法
        :param before_request:只能作用方法
    """

    def decorate(cls_or_func):
        @wraps(cls_or_func)
        def wrapper_cls(*args, **kwargs):
            cls = cls_or_func
            obj = cls(*args, **kwargs)
            try:
                obj.path = path
            except KeyError as e:
                raise ValueError("%s格式不对，找不到%s配置" % (path, e))
            return obj

        @wraps(cls_or_func)
        def wrapper_func(*args, **kwargs):
            func = cls_or_func
            func_res = func(*args, **kwargs)
            if func_res is not None and not isinstance(func_res, Requester):
                raise ApifunctionReturnValueError("%s方法返回值错误，为Request对象或者为None" % func.__name__)
            requester = func_res or Requester()
            func_args = inspect.getfullargspec(func).args
            "If该方法是不是在类里面，如果在类里面，则将类中的定义的Path和session赋值给request"
            if len(func_args) > 0 and func_args[0] == "self":
                self = args[0]
                requester.base_path = getattr(self, "path", "")
                requester.session = getattr(self, "session", Session())
                "把类实例本赋值给request的api_obj变量"
                requester.api_obj = self
            if before_request is not None:
                if isinstance(before_request, FunctionType):
                    requester.before_request = before_request
                else:
                    raise ValueError("方法只能传涵数")
            if after_response is not None:
                if isinstance(after_response, FunctionType):
                    requester.after_response = after_response
                else:
                    raise ValueError("方法只能传涵数")
            requester.func = func
            try:
                requester.path = path
            except:
                requester.path = path
            requester.method = method
            "执行请求"
            requester.do()
            return requester

        if isinstance(cls_or_func, type):
            return wrapper_cls
        else:
            return wrapper_func

    return decorate


hook_func_dict = defaultdict(list)
BEFORE_REQUEST_FUNC_NAME = "before_request_func"
AFTER_RESPONSE_FUNC_NAME = "after_response_func"


def register_func(func_name, func):
    """

    """
    func_qualname_tuple = func.__qualname__.split(".")

    if len(func_qualname_tuple) > 1:
        func_key = ".".join([func.__module__, func_qualname_tuple[0], func_name])
        hook_func_dict[func_key].append(func)
    else:
        hook_func_dict[func_name].append(func)


def before_request(func):
    register_func(BEFORE_REQUEST_FUNC_NAME, func)
    return func


def after_response(func):
    register_func(AFTER_RESPONSE_FUNC_NAME, func)
    return func


def get_class_registered_funcs(cls, func_name):
    if not cls:
        return []
    func_key = ".".join([cls.__module__, cls.__class__.__name__, func_name])
    return hook_func_dict[func_key]


def get_global_registered_funcs(func_name):
    return hook_func_dict[func_name]


def add_header(self, key, value):
    session = getattr(self, "session", None)
    if not session:
        raise ValueError("在api类上加requermapping才能用")
    session.headers[key] = value


def add_headers(self, headers):
    session = getattr(self, "sesion", None)
    if not session:
        raise ValueError("在api类上加requermapping才能用")
    session.headers.update(headers)


def get_session(self) -> Session:
    return getattr(self, "session", None)


class RequestObject:
    def __init__(self, method, url, pqrams, headers, data, files, _json, others):
        self.method = method
        self.url = url
        self.params = pqrams
        self.headers = headers
        self.data = data
        self.files = files
        self.others = others

    def get_encoded_params(self):
        return urlencode(self.params)

    def get_encoded_data(self):
        return urlencode(self.data)

    def get_dumped_json(self):
        return json.dumps()

    def __repr__(self):
        return format_json(self.__dict__)

    def __str__(self):
        return self.__repr__()


ResponseObject = Response


class Requester:
    def __init__(self, **kwargs):
        self.api_obj = None
        self.func = None
        self.session = None
        self.base_path = ""
        self.path = ""
        self.method = ""
        self.url = ""
        self.kwargs = kwargs
        self.params = None
        self.headers = None
        self.data = None
        self.files = None
        self._json = None
        self.request_params = None
        self.before_request = None
        self.after_response = None
        self.res = None

    @staticmethod
    def fixation_order(d):
        o = OrderedDict()
        for i in d:
            o[i] = d[i]
            return o

    def __prepare_session(self):
        self.session = self.session or Session()

    def __prepare_url(self):
        if self.path.startswith("http"):
            self.url = self.path
        else:
            if not self.base_path.endswith("/"):
                self.base_path = self.base_path + "/"
            self.url = urljoin(self.base_path, self.path)
        pv = self.kwargs.pop("path_var", {})
        self.url = self.url.format(**pv)

    def __prepare_params(self):
        self.params = self.fixation_order(self.kwargs.pop("params", {}))

    def __prepare_headers(self):
        self.headers = self.session.headers
        self.headers.update(self.kwargs.pop("headers", {}))
        self.headers = self.fixation_order(self.headers)

    def __prepare_data(self):
        self.data = self.fixation_order(self.kwargs.pop("files", {}))

    def __prepare_files(self):
        self.files = self.fixation_order(self.kwargs.pop("files", {}))

    def __prepare_json(self):
        self._json = self.fixation_order(self.kwargs.pop("json", {}))

    def __prepare_request(self):
        self.__prepare_session()
        self.__prepare_url()
        self.__prepare_params()
        self.__prepare_headers()
        self.__prepare_data()
        self.__prepare_files()
        self.__prepare_json()

    def __process_before_request(self):
        before_request_class_funcs = get_class_registered_funcs(self.api_obj, BEFORE_REQUEST_FUNC_NAME)
        before_request_global_funcs = get_global_registered_funcs(BEFORE_REQUEST_FUNC_NAME)

        for before_request_global_funcs in before_request_class_funcs:
            before_request_global_funcs(self.request_params)

        for before_request_class_funcs in before_request_class_funcs:
            before_request_class_funcs(self.api_obj, self.request_params)

        if self.before_request:
            self.before_request(self.request_params)

    def __process_after_response(self):
        after_response_class_funcs = get_class_registered_funcs(self.api_obj, AFTER_RESPONSE_FUNC_NAME)
        after_response_global_funcs = get_global_registered_funcs(AFTER_RESPONSE_FUNC_NAME)
        for after_response_global_funcs in after_response_global_funcs:
            after_response_global_funcs(self.res)

        for after_response_class_funcs in after_response_class_funcs:
            after_response_class_funcs(self.api_obj, self.res)
        if self.after_response:
            self.after_response(self.res)

    def __process_log(self):
        logger.info("\n************************************************")
        logger.info('请求URL:\n%s %s\n' % (self.method, self.res.request.url))
        logger.info('api描述:\n%s\n' % (self.func.__doc__ or self.func.__name__).strip())
        logger.info('请求headers:\n%s\n' % format_json(dict(self.res.request.headers)))
        logger.info('请求boby:\n%s\n' % format_json(self.res.request.body))
        logger.info("响应体:\n%s\n" % format_json(self.res.content))

    def do(self):
        self.__prepare_request()
        self.__process_before_request()
        self.res = self.session.request(self.method, self.url,
                                        data=self.data,
                                        files=self.files,
                                        headers=self.headers,
                                        json=self._json,
                                        params=self.params,
                                        **self.kwargs)
        self.__process_after_response()
        self.__process_log()

    def __getattr__(self, item):
        return getattr(self.res, item)

    @property
    def content(self):
        return self.res.content

    def json(self):
        return self.res.json()
