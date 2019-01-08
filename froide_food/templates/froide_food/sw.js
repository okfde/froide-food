{% load static %}
var CACHE_NAME = 'froide-food';

var STATIC_FILES = [
  '{% static "js/main.js" %}',
  '{% static "js/common.js" %}',
  '{% static "js/food.js" %}',
  '{% static "css/food.css" %}',
  '{% static "css/main.css" %}',
  '{% static "img/okfde.svg" %}',
  '{% static "img/spinner.gif" %}',
  '{% static "img/spinner.svg" %}',
  '{% static "food/manifest.json" %}',
  '{% static "food/images/yelp_stars.png" %}',
  '{% static "food/images/yelp_stars@2x.png" %}',
  '{% static "food/images/yelp_logo.png" %}',
  '{% static "food/icons/apple-touch-icon.png" %}',
  '{% static "food/icons/favicon-32x32.png" %}',
  '{% static "food/icons/favicon-16x16.png" %}',
  '{% static "food/icons/favicon.ico" %}',
];

var OTHER_FILES = [
  '{% url "food-index" %}',
]

var MAIN_DOMAIN = '{{ SITE_URL }}';
var STATIC_URL = '{{ STATIC_URL }}';
var STATIC_HTTP = STATIC_FILES[0].indexOf('http') === 0;

var API_CACHE = new Date()
var API_PATH = '/api/v1/venue'

var CACHE_DICT = {}
for (var i = 0; i < STATIC_FILES.length; i += 1) {
  CACHE_DICT[STATIC_FILES[i]] = true;
}

function clearAPICache() {
  caches.open(CACHE_NAME).then(function (cache) {
    cache.keys().then(function(keys) {
      keys.forEach(function(request, index, array) {
        if (request.url.indexOf(API_PATH) !== -1) {
          cache.delete(request);
        }
      })
    })
  })
}

self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME).then(function (cache) {
      cache.addAll(STATIC_FILES);
    })
  );
});


self.addEventListener('fetch', function(event) {
  if (event.request.method !== 'GET') {
    return
  }
  if (event.request.url.indexOf(STATIC_URL) === -1) {
    return
  }
  if (event.request.url.indexOf(API_PATH) !== -1) {
    return
  }
  event.respondWith(
    caches.open(CACHE_NAME).then(function(cache) {
      return cache.match(event.request).then(function (response) {
        return response || fetch(event.request).then(function(response) {
          cache.put(event.request, response.clone());
          return response;
        });
      });
    })
  );
});

self.addEventListener('activate', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME).then(function (cache) {
      cache.keys().then(function(keys) {
        keys.forEach(function(request, index, array) {
          var key = request.url;
          if (!STATIC_HTTP) {
            key = key.replace(MAIN_DOMAIN, '');
          }
          if (CACHE_DICT[key] === undefined) {
            cache.delete(request);
          }
        });
      });
    })
  );
});
