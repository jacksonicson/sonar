var url = require('url')

getHandler = function(rawUrl, urlMap) {
    if(!rawUrl)
        throw 'invalid url';

    var parsedUrl = url.parse(rawUrl)

    console.log('parsed url: ' + parsedUrl.pathname);

    for(var i in urlMap)
    {
        var entry = urlMap[i];
        if(entry[0] == parsedUrl.pathname) {
            console.log("match " + entry[0]);
            console.log(entry[1]);
            return entry[1];
        }
    }

    return null;
}

// Connect middleware module
exports = module.exports = function router(options) {

    return function router(req, res, next) {

        try {
            var urlHandler = getHandler(req.url, options.generateUrlHandler());
            if (urlHandler != undefined && urlHandler != null) {
                urlHandler(req, res);
                return;
            }
        } catch (err) {
            console.log(err);
        }

        next();
    };
};

exports.errorHandler = function(req, resp) {
    resp.end("not implemented exception");
}


exports.directoryHandler = function(req, resp) {
    resp.end("not implemented exception")
}


exports.UrlNode = function(name, params, childs) {
    var parent = null

    // Add this pointer
    this[name.toUpperCase()] = this;

    // Add childs
    this.add = function (childs) {
        for (var i in childs) {
            var child = childs[i]

            // Update parent pointer from the child
            child.setParent(this)

            // Add local variable
            this[child.getName().toUpperCase()] = child;
        }
    }

    this.add(childs)

    this.getName = function () {
        return name;
    }

    this.setParent = function (ref) {
        parent = ref
    }

    this.isLeaf = function () {
        return childs.length == 0
    }

    this.generateUrl = function () {
        var currentUrl = '';

        if (parent != null) {
            var parentUrl = parent.generateUrl();
            if (parentUrl != '')
                currentUrl += parentUrl + '/';
        }

        if (params.url)
            currentUrl += params.url;

        return currentUrl;
    }

    this.url = function () {
        return '/' + this.generateUrl();
    }

    this.generateUrlHandler = function (list, url) {
        if (!list)
            list = new Array();
        if (!url)
            url = ''

        if (params.url != undefined)
            url += params.url

        if (childs)
            childs.forEach(function (child) {
                var urlToken = url;
                if (params.url != undefined)
                    urlToken += '/';

                child.generateUrlHandler(list, urlToken)
            })

        if (params.handler != undefined) {
            var entry = ['/' + url, params.handler];
            list.push(entry);
        }

        return list;
    }

    this.generateUrlMap = function (map, path, url) {
        if (!map)
            map = {};

        if (!url)
            url = ''

        if (!path)
            path = name;
        else
            path += '_' + name;

        if (params.url)
            url += params.url

        if (childs)
            childs.forEach(function (child) {
                var urlToken = url;
                if (params.url)
                    urlToken += '/';

                child.generateUrlMap(map, path, urlToken);
            })

        map[path] = '/' + url;

        return map;
    }

    this.dump = function (intend) {
        if (intend == undefined)
            intend = ""

        console.log(intend + name);
        intend = intend + " ";

        if (childs)
            childs.forEach(function (child) {
                child.dump(intend)
            })
    }
}



/*
 // Tests

 urls.dump();
 console.log(urls.ROOT.INDEX.TEST.url());

 handlerList = urls.generateUrlHandler();
 console.log("Handler:");
 console.log(handlerList);

 urlMap = urls.generateUrlMap();
 console.log("Url Map:");
 console.log(urlMap);
 */