# -*- coding: utf-8 -*-
import yaml
import time
import logging
import tornado.ioloop
from xml.etree import ElementTree as ET
import tornado.web

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    filename='xlchen_wechat.log', filemode='a')


def parse_request_xml(rootElem):
    msg = {}
    if rootElem.tag == 'xml':
        for child in rootElem:
            msg[child.tag] = child.text  # 获得内容
    return msg


def read_yaml_info(file_path):
    f = open(file_path)
    x = yaml.load(f)
    return x


def handle_event_msg(msg):
    from_user_name = msg.get("FromUserName").encode('utf-8')
    to_user_name = msg.get("ToUserName").encode('utf-8')
    event_type = msg.get("Event")
    if event_type == "CLICK":
        click_key = msg.get("EventKey")
        if click_key == 'V1001_GOOD':
            data = '''<xml>
                        <ToUserName><![CDATA[%s]]></ToUserName>
                        <FromUserName><![CDATA[%s]]></FromUserName>
                        <CreateTime>%s</CreateTime>
                        <MsgType><![CDATA[%s]]></MsgType>
                        <Content><![CDATA[%s]]></Content>
                    </xml> ''' % (from_user_name, to_user_name,
                                  int(time.time()), 'text', '你的肯定，将是我前进的动力')
        else:
            data = '''<xml>
                        <ToUserName><![CDATA[%s]]></ToUserName>
                        <FromUserName><![CDATA[%s]]></FromUserName>
                        <CreateTime>%s</CreateTime>
                        <MsgType><![CDATA[%s]]></MsgType>
                        <Content><![CDATA[%s]]></Content>
                    </xml> ''' % (from_user_name, to_user_name,
                                  int(time.time()), 'text', '亲，你的Style我不懂！')
    else:
        content = "歡迎您使用！"
        data = '''<xml>
                    <ToUserName><![CDATA[%s]]></ToUserName>
                    <FromUserName><![CDATA[%s]]></FromUserName>
                    <CreateTime>%s</CreateTime>
                    <MsgType><![CDATA[%s]]></MsgType>
                    <Content><![CDATA[%s]]></Content>
                </xml> ''' % (from_user_name, to_user_name, int(time.time()), 'text', content)
    return data


def handle_text_msg(msg):
    content = msg.get("Content").encode('utf-8')
    from_user_name = msg.get("FromUserName").encode('utf-8')
    to_user_name = msg.get("ToUserName").encode('utf-8')
    if not content:
        content = "歡迎您使用！"
    phones_info = read_yaml_info('./phone_info.yaml')
    names_info = phones_info.keys()
    content = content.decode('utf-8')
    if content in names_info:
        content = u'年龄：%s\n电话：%s' % (phones_info[content]['age'], phones_info[content]['phone'])
    data = '''<xml>
        <ToUserName><![CDATA[%s]]></ToUserName>
        <FromUserName><![CDATA[%s]]></FromUserName>
        <CreateTime>%s</CreateTime>
        <MsgType><![CDATA[%s]]></MsgType>
        <Content><![CDATA[%s]]></Content>
    </xml> ''' % (from_user_name, to_user_name, int(time.time()), 'text', content)
    return data


class MainHandler(tornado.web.RequestHandler):

    def get(self):
        request_args = self.request.arguments
        print request_args
        self.write(self.get_argument("echostr"))

    def post(self):
        raw_str = self.request.body
        logger.info(raw_str)
        msg = parse_request_xml(ET.fromstring(raw_str))
        msg_type = msg.get("MsgType").encode('utf-8')
        if msg_type == 'text':
            data = handle_text_msg(msg)
        elif msg_type == 'event':
            data = handle_event_msg(msg)
        else:
            data = ''

        self.write(data)


def make_app():
    return tornado.web.Application([
        (r"/xlchen_WeChat", MainHandler),
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(55556)
    tornado.ioloop.IOLoop.current().start()
