import logging as logger

class TemplateBox(object):
    
    def putTemplate(self, name, file):
        self.__dict__[name] = file

class UrlSegment(object):
    
    def __init__(self, name, url, childs=(), templates={}):
        assert(name != None)
        self.__name = name
        self.__url = url
        self.__handler = None
        self.__father = None

        self.__childs = []
        for child in childs:
            child.setFather(self)
            self.__childs.append(child)
            self.__dict__[child.getName()] = child

        self.t = TemplateBox()
        for template in templates.keys():
            self.t.putTemplate(template, templates[template])

    def setHandler(self, handler):
        self.__handler = handler
        return self

    def setFather(self, father):
        self.__father = father
        return self

    def getName(self):
        return self.__name

    def isLeaf(self):
        if len(self.__childs) == 0:
            return True

        return False

    def generateUrl(self):
        returnUrl = ''
        if self.__father:
            fatherUrl = self.__father.generateUrl()
            if fatherUrl:
                returnUrl += fatherUrl + '/'
        if self.__url:
            returnUrl += self.__url
        return returnUrl

    def url(self):
        return '/' + self.generateUrl()

    def generateUrlHandler(self, list, url=''):
        # URL fuer den Browser generieren
        if self.__url:
            url += self.__url

        # Rekursiv alle Kinder aufrufen um die Tabelle zu generieren
        for child in self.__childs:
            urlToken = url
            if self.__url:
                urlToken += '/'
            child.generateUrlHandler(list, urlToken)

        # Prueft ob der eigene Knoten einen Request-Handler enthuelt
        if self.__handler:
            entry = ('/' + url, self.__handler)
            list.append(entry)

    def generate_url_map(self, map, separator='.', name='', url=''):
        if self.__url:
            url += self.__url

        name += self.__name

        for child in self.__childs:
            urlToken = url
            if self.__url:
                urlToken += '/'
            child.generate_url_map(map, separator, name + separator, urlToken)

        map[name] = '/' + url

ROOT = None
def __initTree():
    global ROOT
    if ROOT is not None:
        return

    ROOT = UrlSegment('ROOT', None,
        childs = [
        UrlSegment('DASHBOARD', 'dashboard').setHandler(handler.Dashboard),
        ]
    ).setHandler(handler.SmartCoin)


def dumpMap(map):
    for k in map.keys():
        logger.info("key %s is %s" % (k, map[k]))


def generate_url_map(separator='.'):
    __initTree()
    map = {}
    ROOT.generate_url_map(map, separator)
    return map


def generateUrlHandlerList():
    __initTree()
    list = []
    ROOT.generateUrlHandler(list)
    return list
